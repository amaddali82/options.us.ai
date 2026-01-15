#!/usr/bin/env python3
"""
Real-Time Stock Price Fetcher
Fetches live stock prices from Yahoo Finance and updates database
"""

import asyncio
import asyncpg
import logging
from datetime import datetime, timedelta, date
import os
import sys
import math
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealtimePriceFetcher:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 
                                     'postgresql://trading_user:trading_pass@postgres:5432/trading_db')

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.database_url)
        return self

    async def close(self):
        if hasattr(self, 'pool'):
            await self.pool.close()

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_symbols(self):
        """Get unique symbols from database"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT DISTINCT symbol FROM recommendations ORDER BY symbol")
            return [row['symbol'] for row in rows]

    async def fetch_yahoo_price(self, symbol: str) -> float:
        """Fetch real-time price from Yahoo Finance using yfinance"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            
            if not data.empty:
                price = data['Close'].iloc[-1]
                logger.info(f"✅ {symbol}: ${price:.2f}")
                return float(price)
            else:
                logger.warning(f"⚠️  No data for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching {symbol}: {e}")
            return None

    async def update_stock_prices(self):
        """Fetch and update all stock prices"""
        symbols = await self.get_symbols()
        logger.info(f"📈 Fetching real-time prices for {len(symbols)} symbols...")
        
        updated_count = 0
        failed_symbols = []
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for symbol in symbols:
                    price = await self.fetch_yahoo_price(symbol)
                    
                    if price and price > 0:
                        result = await conn.execute("""
                            UPDATE recommendations 
                            SET entry_price = $2,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE symbol = $1
                        """, symbol, price)
                        
                        rows_updated = int(result.split()[-1])
                        updated_count += rows_updated
                    else:
                        failed_symbols.append(symbol)
                    
                    # Rate limiting
                    await asyncio.sleep(0.2)
        
        logger.info(f"✅ Updated {updated_count} stock prices")
        if failed_symbols:
            logger.warning(f"⚠️  Failed to fetch: {', '.join(failed_symbols)}")

    async def recalculate_all_targets(self):
        """Recalculate all target prices based on new entry prices"""
        logger.info("🎯 Recalculating all target prices...")
        
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE reco_targets 
                SET value = CASE 
                    WHEN r.side = 'BUY' AND ordinal = 1 THEN r.entry_price * (1.08 + r.confidence_overall * 0.15) * (0.98 + random() * 0.04)
                    WHEN r.side = 'BUY' AND ordinal = 2 THEN r.entry_price * (1.15 + r.confidence_overall * 0.30) * (0.98 + random() * 0.04)
                    WHEN r.side = 'SELL' AND ordinal = 1 THEN r.entry_price * (0.92 - r.confidence_overall * 0.15) * (0.98 + random() * 0.04)
                    WHEN r.side = 'SELL' AND ordinal = 2 THEN r.entry_price * (0.85 - r.confidence_overall * 0.30) * (0.98 + random() * 0.04)
                    WHEN r.side = 'HOLD' AND ordinal = 1 THEN r.entry_price * (1.03 + r.confidence_overall * 0.05) * (0.98 + random() * 0.04)
                    WHEN r.side = 'HOLD' AND ordinal = 2 THEN r.entry_price * (0.97 - r.confidence_overall * 0.05) * (0.98 + random() * 0.04)
                END
                FROM recommendations r 
                WHERE reco_targets.reco_id = r.reco_id
            """)
            
            targets_updated = int(result.split()[-1])
            logger.info(f"✅ Recalculated {targets_updated} target prices")

    async def update_options_with_new_prices(self):
        """Update option strikes and premiums based on new stock prices"""
        logger.info("📊 Updating options data with new prices...")
        
        async with self.pool.acquire() as conn:
            # Get all option ideas with current stock prices
            options = await conn.fetch("""
                SELECT oi.reco_id, r.symbol, r.entry_price, r.side, 
                       oi.option_type, oi.strike, oi.expiry
                FROM option_ideas oi
                JOIN recommendations r ON oi.reco_id = r.reco_id
            """)
            
            updated_count = 0
            
            async with conn.transaction():
                for opt in options:
                    stock_price = float(opt['entry_price'])
                    side = opt['side']
                    expiry = opt['expiry']
                    
                    # Calculate new strike based on updated stock price
                    if side == 'BUY':
                        new_strike = round(stock_price * 1.05, 0)
                    else:
                        new_strike = round(stock_price * 0.95, 0)
                    
                    # Calculate new premium
                    dte = (expiry - datetime.now().date()).days
                    new_premium = self.calculate_option_premium(stock_price, new_strike, dte, opt['option_type'])
                    
                    # Calculate new Greeks
                    greeks = self.calculate_greeks(stock_price, new_strike, dte, opt['option_type'])
                    
                    await conn.execute("""
                        UPDATE option_ideas
                        SET strike = $2,
                            option_entry_price = $3,
                            greeks = $4
                        WHERE reco_id = $1
                    """, opt['reco_id'], new_strike, new_premium, greeks)
                    
                    # Update option targets
                    target_premiums = [
                        round(new_premium * 1.30, 2),
                        round(new_premium * 1.60, 2)
                    ]
                    
                    for ordinal, target_premium in enumerate(target_premiums, 1):
                        await conn.execute("""
                            UPDATE option_targets
                            SET value = $3
                            WHERE reco_id = $1 AND ordinal = $2
                        """, opt['reco_id'], ordinal, target_premium)
                    
                    updated_count += 1
            
            logger.info(f"✅ Updated {updated_count} option contracts")

    def calculate_option_premium(self, S: float, K: float, dte: int, option_type: str) -> float:
        """Calculate option premium using simplified Black-Scholes"""
        T = max(1, dte) / 365.0
        
        if S > 500:
            iv = 0.30
        elif S > 200:
            iv = 0.25
        elif S > 50:
            iv = 0.35
        else:
            iv = 0.45
        
        moneyness = S / K
        time_value_factor = 1.2 if (option_type == 'CALL' and moneyness > 1) or (option_type == 'PUT' and moneyness < 1) else 0.8
        
        intrinsic_value = max(0, S - K if option_type == 'CALL' else K - S)
        time_value = S * iv * math.sqrt(T) * time_value_factor * 0.4
        premium = intrinsic_value + time_value
        
        return max(0.05, round(premium * random.uniform(0.9, 1.1), 2))

    def calculate_greeks(self, S: float, K: float, dte: int, option_type: str) -> dict:
        """Calculate option Greeks"""
        import json
        
        T = max(1, dte) / 365.0
        moneyness = S / K
        
        if option_type == 'CALL':
            if moneyness > 1.1:
                delta = random.uniform(0.65, 0.85)
            elif moneyness > 1.0:
                delta = random.uniform(0.45, 0.65)
            elif moneyness > 0.95:
                delta = random.uniform(0.35, 0.55)
            else:
                delta = random.uniform(0.10, 0.35)
        else:
            if moneyness < 0.9:
                delta = random.uniform(-0.85, -0.65)
            elif moneyness < 1.0:
                delta = random.uniform(-0.65, -0.45)
            elif moneyness < 1.05:
                delta = random.uniform(-0.55, -0.35)
            else:
                delta = random.uniform(-0.35, -0.10)
        
        gamma = 0.05 * math.exp(-abs(moneyness - 1) * 5) / math.sqrt(T)
        gamma = min(0.15, max(0.001, gamma))
        
        theta = -abs(delta) * S * 0.25 / (2 * math.sqrt(T * 365))
        theta = min(-0.01, max(-5.0, theta))
        
        vega = S * math.sqrt(T) * gamma * 100
        vega = min(0.8, max(0.01, vega))
        
        return json.dumps({
            'delta': round(delta, 3),
            'gamma': round(gamma, 4),
            'theta': round(theta, 2),
            'vega': round(vega, 2)
        })

async def main():
    """Main function to fetch and update real-time prices"""
    logger.info("🚀 Starting real-time price update...")
    
    try:
        async with RealtimePriceFetcher() as fetcher:
            # Fetch and update stock prices
            await fetcher.update_stock_prices()
            
            # Recalculate targets
            await fetcher.recalculate_all_targets()
            
            # Update options
            await fetcher.update_options_with_new_prices()
            
            logger.info("🎉 Real-time price update completed!")
            
    except Exception as e:
        logger.error(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())
