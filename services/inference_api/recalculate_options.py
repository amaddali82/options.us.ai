"""
Recalculate option strikes, premiums, and confidence based on current stock prices
"""
import asyncio
import asyncpg
import os
import logging
from datetime import datetime, date
from typing import Dict
import random

from price_fetcher import fetch_stock_prices
from ml_predictor import predict_option_confidence, calculate_profit_probability

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_option_strike(entry_price: float, side: str, delta_target: float) -> float:
    """Calculate strike price based on desired delta"""
    if side == "BUY":  # CALL
        if delta_target >= 0.60:
            strike_pct = random.uniform(0.98, 1.02)  # Near ATM
        elif delta_target >= 0.50:
            strike_pct = random.uniform(1.02, 1.05)  # Slightly OTM
        else:
            strike_pct = random.uniform(1.05, 1.10)  # More OTM
    else:  # SELL -> PUT
        if delta_target >= 0.40:
            strike_pct = random.uniform(0.92, 0.96)  # Moderately OTM
        elif delta_target >= 0.30:
            strike_pct = random.uniform(0.88, 0.92)  # More OTM
        else:
            strike_pct = random.uniform(0.85, 0.88)  # Deep OTM
    
    strike = entry_price * strike_pct
    
    # Round to standard option strike increments
    if strike < 25:
        strike = round(strike / 0.5) * 0.5
    elif strike < 50:
        strike = round(strike / 1) * 1
    elif strike < 100:
        strike = round(strike / 2.5) * 2.5
    else:
        strike = round(strike / 5) * 5
    
    return strike


def estimate_option_price(entry_price: float, strike: float, iv: float, dte: int, option_type: str) -> float:
    """Rough option pricing estimate"""
    moneyness = strike / entry_price
    
    # Intrinsic value
    if option_type == "CALL":
        intrinsic = max(0, entry_price - strike)
    else:  # PUT
        intrinsic = max(0, strike - entry_price)
    
    # Time value
    time_value = entry_price * iv * (dte / 365) ** 0.5 * 0.4
    
    # Adjust for moneyness
    if option_type == "CALL":
        if moneyness > 1.05:  # OTM
            time_value *= 0.6
        elif moneyness < 0.95:  # ITM
            time_value *= 0.8
    else:  # PUT
        if moneyness < 0.95:  # OTM
            time_value *= 0.6
        elif moneyness > 1.05:  # ITM
            time_value *= 0.8
    
    price = intrinsic + time_value
    
    # Round to reasonable increments
    if price < 1:
        price = round(price, 2)
    elif price < 10:
        price = round(price, 1)
    else:
        price = round(price / 0.5) * 0.5
    
    return max(0.05, price)


async def get_db_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL', 'postgresql://trading_user:trading_pass@postgres:5432/trading_db')
    parts = database_url.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    user = user_pass[0]
    password = user_pass[1]
    host_port_db = parts[1].split('/')
    host_port = host_port_db[0].split(':')
    host = host_port[0]
    port = int(host_port[1])
    database = host_port_db[1]
    
    return await asyncpg.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )


async def recalculate_all_options():
    """Recalculate all option parameters based on current stock prices"""
    logger.info("🔄 Starting option recalculation based on current stock prices...")
    
    try:
        conn = await get_db_connection()
        
        # Get all recommendations with options
        rows = await conn.fetch("""
            SELECT r.reco_id, r.symbol, r.side, r.entry_price,
                   oi.option_type, oi.expiry, 
                   oi.strike, oi.option_entry_price
            FROM recommendations r
            JOIN option_ideas oi ON r.reco_id = oi.reco_id
            WHERE r.created_at > NOW() - INTERVAL '7 days'
            ORDER BY r.symbol
        """)
        
        if not rows:
            logger.info("No options to recalculate")
            await conn.close()
            return
        
        # Get unique symbols
        symbols = list(set(row['symbol'] for row in rows))
        logger.info(f"Fetching current prices for {len(symbols)} symbols...")
        
        # Fetch current prices (fetch_stock_prices is synchronous)
        import asyncio
        loop = asyncio.get_event_loop()
        current_prices = await loop.run_in_executor(None, fetch_stock_prices, symbols)
        
        if not current_prices:
            logger.warning("No prices fetched, cannot recalculate")
            await conn.close()
            return
        
        updated_count = 0
        
        for row in rows:
            symbol = row['symbol']
            
            if symbol not in current_prices:
                logger.warning(f"No current price for {symbol}, skipping...")
                continue
            
            current_price = current_prices[symbol]
            side = row['side']
            option_type = row['option_type']
            expiry = row['expiry']
            reco_id = row['reco_id']
            
            # Calculate days to expiry
            dte = (expiry - date.today()).days
            if dte <= 0:
                logger.warning(f"Option for {symbol} expired, skipping...")
                continue
            
            # Recalculate strike price
            delta_target = 0.55 if side == "BUY" else 0.35
            new_strike = calculate_option_strike(current_price, side, delta_target)
            
            # Estimate implied volatility (simplified)
            iv = 0.35  # Can be enhanced with actual IV calculation
            
            # Calculate new option premium
            new_premium = estimate_option_price(current_price, new_strike, iv, dte, option_type)
            
            # Calculate ML-based confidence
            ml_confidence_result = predict_option_confidence(
                stock_price=current_price,
                strike=new_strike,
                option_type=option_type,
                dte=dte,
                volatility=iv
            )
            ml_confidence = ml_confidence_result['overall'] if isinstance(ml_confidence_result, dict) else ml_confidence_result
            
            # Calculate profit probability
            profit_prob = calculate_profit_probability(
                stock_price=current_price,
                strike=new_strike,
                volatility=iv,
                dte=dte,
                option_type=option_type
            )
            
            # Update option_ideas
            await conn.execute("""
                UPDATE option_ideas
                SET strike = $1,
                    option_entry_price = $2,
                    updated_at = NOW()
                WHERE reco_id = $3
            """, new_strike, new_premium, reco_id)
            
            # Update option targets (20% and 50% profit targets)
            target1 = new_premium * 1.20
            target2 = new_premium * 1.50
            
            await conn.execute("""
                UPDATE option_targets
                SET value = $1, confidence = $2
                WHERE reco_id = $3 AND ordinal = 1
            """, target1, ml_confidence * 0.95, reco_id)
            
            await conn.execute("""
                UPDATE option_targets
                SET value = $1, confidence = $2
                WHERE reco_id = $3 AND ordinal = 2
            """, target2, ml_confidence * 0.85, reco_id)
            
            # Update recommendation confidence
            await conn.execute("""
                UPDATE recommendations
                SET entry_price = $1,
                    confidence_overall = $2,
                    updated_at = NOW()
                WHERE reco_id = $3
            """, current_price, ml_confidence, row['reco_id'])
            
            logger.info(
                f"✅ {symbol}: Updated strike ${new_strike:.2f}, "
                f"premium ${new_premium:.2f}, confidence {ml_confidence:.2%}"
            )
            
            updated_count += 1
        
        await conn.close()
        logger.info(f"✅ Recalculated {updated_count} options based on current prices")
        
    except Exception as e:
        logger.error(f"❌ Error recalculating options: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(recalculate_all_options())
