#!/usr/bin/env python3
"""
Fix Target Prices - Recalculate tp1 and tp2 based on updated stock prices
"""

import asyncio
import asyncpg
import logging
from decimal import Decimal
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TargetPriceUpdater:
    def __init__(self):
        self.database_url = "postgresql://trading_user:trading_pass@postgres:5432/trading_db"

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

    async def recalculate_targets(self):
        """Recalculate target prices based on current entry prices"""
        async with self.pool.acquire() as conn:
            # Get all recommendations with their current targets
            recommendations = await conn.fetch("""
                SELECT r.reco_id, r.symbol, r.entry_price, r.side, r.horizon, r.confidence_overall
                FROM recommendations r
                ORDER BY r.symbol
            """)
            
            logger.info(f"Recalculating targets for {len(recommendations)} recommendations")
            
            async with conn.transaction():
                for rec in recommendations:
                    reco_id = rec['reco_id']
                    entry_price = float(rec['entry_price'])
                    side = rec['side']
                    horizon = rec['horizon']
                    confidence = float(rec['confidence_overall'])
                    
                    # Calculate realistic target prices based on side and horizon
                    if side == 'BUY':
                        # For BUY recommendations, targets should be above entry price
                        if horizon == 'intraday':
                            tp1_mult = 1.02 + (confidence * 0.03)  # 2-5% gain
                            tp2_mult = 1.04 + (confidence * 0.06)  # 4-10% gain
                        elif horizon == 'swing':
                            tp1_mult = 1.05 + (confidence * 0.10)  # 5-15% gain
                            tp2_mult = 1.10 + (confidence * 0.20)  # 10-30% gain
                        else:  # position
                            tp1_mult = 1.08 + (confidence * 0.15)  # 8-23% gain
                            tp2_mult = 1.15 + (confidence * 0.30)  # 15-45% gain
                            
                    elif side == 'SELL':
                        # For SELL recommendations, targets should be below entry price
                        if horizon == 'intraday':
                            tp1_mult = 0.98 - (confidence * 0.03)  # 2-5% drop
                            tp2_mult = 0.96 - (confidence * 0.06)  # 4-10% drop
                        elif horizon == 'swing':
                            tp1_mult = 0.95 - (confidence * 0.10)  # 5-15% drop
                            tp2_mult = 0.90 - (confidence * 0.20)  # 10-30% drop
                        else:  # position
                            tp1_mult = 0.92 - (confidence * 0.15)  # 8-23% drop
                            tp2_mult = 0.85 - (confidence * 0.30)  # 15-45% drop
                            
                    else:  # HOLD
                        # For HOLD, targets are range-bound
                        tp1_mult = 1.03 + (confidence * 0.05)  # Slight upside
                        tp2_mult = 0.97 - (confidence * 0.05)  # Slight downside
                    
                    # Add some randomness for realism
                    tp1_mult *= random.uniform(0.98, 1.02)
                    tp2_mult *= random.uniform(0.98, 1.02)
                    
                    # Calculate target prices
                    tp1 = round(entry_price * tp1_mult, 2)
                    tp2 = round(entry_price * tp2_mult, 2)
                    
                    # Update target 1
                    await conn.execute("""
                        UPDATE reco_targets 
                        SET value = $2, 
                            confidence = $3,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE reco_id = $1 AND ordinal = 1
                    """, reco_id, tp1, 0.75 + (confidence * 0.20))
                    
                    # Update target 2  
                    await conn.execute("""
                        UPDATE reco_targets 
                        SET value = $2, 
                            confidence = $3,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE reco_id = $1 AND ordinal = 2
                    """, reco_id, tp2, 0.65 + (confidence * 0.15))
                    
                    logger.info(f"✅ {rec['symbol']} ({side}): ${entry_price:.2f} → TP1: ${tp1:.2f}, TP2: ${tp2:.2f}")

async def main():
    """Main function to fix target prices"""
    logger.info("🎯 Starting target price recalculation")
    
    try:
        async with TargetPriceUpdater() as updater:
            await updater.recalculate_targets()
            logger.info("🎉 Target price recalculation completed successfully!")
            
    except Exception as e:
        logger.error(f"💥 Error updating target prices: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())