"""
Background scheduler for automated data updates
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncpg
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import os
import numpy as np

from price_fetcher import (
    fetch_stock_prices,
    calculate_technical_targets,
    calculate_option_metrics,
    get_current_volatility
)

from ml_predictor import (
    predict_option_confidence,
    predict_price_targets,
    calculate_profit_probability
)

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


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


async def update_stock_prices():
    """Update stock prices and recalculate stock targets - runs every 30 minutes"""
    logger.info("🔄 Starting stock price update job...")
    
    try:
        conn = await get_db_connection()
        
        # Get all active recommendations
        rows = await conn.fetch("""
            SELECT DISTINCT r.reco_id, r.symbol, r.horizon, r.entry_price
            FROM recommendations r
            WHERE r.created_at > NOW() - INTERVAL '7 days'
            ORDER BY r.symbol
        """)
        
        if not rows:
            logger.info("No active recommendations to update")
            await conn.close()
            return
        
        # Group by symbol
        symbols = list(set(row['symbol'] for row in rows))
        logger.info(f"Fetching prices for {len(symbols)} symbols...")
        
        # Fetch current prices
        prices = fetch_stock_prices(symbols)
        
        updated_count = 0
        
        for row in rows:
            symbol = row['symbol']
            reco_id = row['reco_id']
            horizon = row['horizon']
            
            if symbol not in prices:
                continue
            
            current_price = prices[symbol]
            
            # Calculate new targets and confidence
            tp1, tp2, confidence = calculate_technical_targets(symbol, current_price, horizon)
            
            # Update recommendation entry price and confidence
            await conn.execute("""
                UPDATE recommendations
                SET entry_price = $1,
                    confidence_overall = $2,
                    updated_at = NOW()
                WHERE reco_id = $3
            """, current_price, confidence, reco_id)
            
            # Update stock targets
            await conn.execute("""
                UPDATE reco_targets
                SET value = $1, confidence = $2
                WHERE reco_id = $3 AND ordinal = 1
            """, tp1, confidence * 0.95, reco_id)
            
            await conn.execute("""
                UPDATE reco_targets
                SET value = $1, confidence = $2
                WHERE reco_id = $3 AND ordinal = 2
            """, tp2, confidence * 0.85, reco_id)
            
            updated_count += 1
        
        await conn.close()
        logger.info(f"✅ Updated {updated_count} recommendations with new stock prices")
        
    except Exception as e:
        logger.error(f"❌ Error updating stock prices: {e}")


async def update_options_data():
    """Update option prices and Greeks - runs every 10 minutes"""
    logger.info("🔄 Starting options data update job...")
    
    try:
        conn = await get_db_connection()
        
        # Get all active option ideas
        rows = await conn.fetch("""
            SELECT oi.reco_id, r.symbol, r.entry_price as stock_price,
                   oi.option_type, oi.strike, oi.expiry
            FROM option_ideas oi
            JOIN recommendations r ON r.reco_id = oi.reco_id
            WHERE oi.expiry > CURRENT_DATE
            AND r.created_at > NOW() - INTERVAL '7 days'
        """)
        
        if not rows:
            logger.info("No active options to update")
            await conn.close()
            return
        
        # Group by symbol for volatility fetching
        symbols = list(set(row['symbol'] for row in rows))
        logger.info(f"Updating options for {len(symbols)} symbols...")
        
        # Fetch current stock prices
        prices = fetch_stock_prices(symbols)
        
        updated_count = 0
        
        for row in rows:
            symbol = row['symbol']
            
            if symbol not in prices:
                continue
            
            stock_price = prices[symbol]
            strike = float(row['strike'])
            option_type = row['option_type']
            expiry = row['expiry']
            
            # Get current volatility
            iv = get_current_volatility(symbol)
            
            # Calculate days until expiration
            days_to_expiry = (expiry - datetime.now().date()).days
            
            # Use ML predictor for advanced confidence calculation
            ml_prediction = predict_option_confidence(
                stock_price=stock_price,
                strike=strike,
                days_to_expiry=days_to_expiry,
                volatility=iv,
                option_type=option_type
            )
            
            # Calculate profit probability using Black-Scholes
            profit_prob = calculate_profit_probability(
                stock_price=stock_price,
                strike=strike,
                days_to_expiry=days_to_expiry,
                volatility=iv,
                is_call=(option_type == 'call')
            )
            
            # Calculate option metrics
            metrics = calculate_option_metrics(
                stock_price=stock_price,
                strike=strike,
                option_type=option_type,
                expiry_date=datetime.combine(expiry, datetime.min.time()),
                volatility=iv
            )
            
            # Use ML confidence instead of simple technical confidence
            ml_confidence = ml_prediction['confidence']
            
            # Update option entry price and confidence
            await conn.execute("""
                UPDATE option_ideas
                SET option_entry_price = $1,
                    updated_at = NOW()
                WHERE reco_id = $2
            """, metrics['option_entry_price'], row['reco_id'])
            
            # Update recommendation with ML confidence
            await conn.execute("""
                UPDATE recommendations
                SET confidence_overall = $1,
                    entry_price = $2,
                    updated_at = NOW()
                WHERE reco_id = $3
            """, ml_confidence, stock_price, row['reco_id'])
            
            # Update option targets with ML-based confidence
            await conn.execute("""
                UPDATE option_targets
                SET value = $1, confidence = $2
                WHERE reco_id = $3 AND ordinal = 1
            """, metrics['tp1'], ml_confidence * 0.95, row['reco_id'])
            
            await conn.execute("""
                UPDATE option_targets
                SET value = $1, confidence = $2
                WHERE reco_id = $3 AND ordinal = 2
            """, metrics['tp2'], ml_confidence * 0.85, row['reco_id'])
            
            updated_count += 1
        
        await conn.close()
        logger.info(f"✅ Updated {updated_count} options with ML predictions and real-time data")
        
    except Exception as e:
        logger.error(f"❌ Error updating options data: {e}")


def start_scheduler():
    """Start the background scheduler"""
    logger.info("🚀 Starting background scheduler...")
    
    # Stock price updates every 30 minutes
    scheduler.add_job(
        update_stock_prices,
        trigger=IntervalTrigger(minutes=30),
        id='stock_price_update',
        name='Update stock prices and targets',
        replace_existing=True
    )
    
    # Options data updates every 10 minutes
    scheduler.add_job(
        update_options_data,
        trigger=IntervalTrigger(minutes=10),
        id='options_data_update',
        name='Update options prices and Greeks',
        replace_existing=True
    )
    
    # Run initial updates after 30 seconds
    scheduler.add_job(
        update_stock_prices,
        trigger='date',
        run_date=datetime.now(timezone.utc) + timedelta(seconds=30),
        id='initial_stock_update',
        name='Initial stock price update'
    )
    
    scheduler.add_job(
        update_options_data,
        trigger='date',
        run_date=datetime.now(timezone.utc) + timedelta(seconds=45),
        id='initial_options_update',
        name='Initial options data update'
    )
    
    scheduler.start()
    logger.info("✅ Scheduler started successfully")


def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")
