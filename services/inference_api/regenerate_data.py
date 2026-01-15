"""Script to regenerate all recommendations with corrected strike prices"""
import asyncio
import asyncpg
import os
import sys
import json
from datetime import datetime, timezone
import uuid

# Import our modules
from reco_generator import generate_batch

async def insert_recommendations(conn, recos):
    """Insert recommendations into database"""
    for reco in recos:
        # Handle both dict and object formats
        if isinstance(reco, dict):
            reco_id = str(reco['reco_id'])
            symbol = reco['symbol']
            horizon = reco['horizon']
            side = reco['side']  # BUY/SELL/HOLD
            entry_price = float(reco['entry_price'])
            confidence_overall = float(reco['confidence_overall'])
            expected_move_pct = reco.get('expected_move_pct')
            rationale = reco.get('rationale')
            quality = reco.get('quality')
            asof = reco['asof']
            created_at = reco.get('created_at', asof)
            targets = reco.get('targets', [])
            option_idea = reco.get('option_idea')
        else:
            reco_id = str(reco.reco_id)
            symbol = reco.symbol
            horizon = reco.horizon
            side = reco.side
            entry_price = float(reco.entry_price)
            confidence_overall = float(reco.confidence_overall)
            expected_move_pct = reco.expected_move_pct
            rationale = reco.rationale
            quality = reco.quality
            asof = reco.asof
            created_at = reco.created_at
            targets = reco.targets
            option_idea = getattr(reco, 'option_idea', None)
            
        # Insert recommendation
        await conn.execute("""
            INSERT INTO recommendations (
                reco_id, asof, symbol, horizon, side, entry_price, 
                confidence_overall, expected_move_pct, rationale, quality, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb, $10::jsonb, $11)
        """, reco_id, asof, symbol, horizon, side, entry_price, 
            confidence_overall, expected_move_pct, 
            json.dumps(rationale) if rationale else None,
            json.dumps(quality) if quality else None,
            created_at)
        
        # Insert targets
        for target in targets:
            if isinstance(target, dict):
                ordinal = target['ordinal']
                name = target.get('name', '')
                target_type = target.get('target_type', 'price')
                value = float(target['value'])
                conf = float(target['confidence'])
                eta_min = target.get('eta_minutes')
            else:
                ordinal = target.ordinal
                name = target.name
                target_type = target.target_type
                value = float(target.value)
                conf = float(target.confidence)
                eta_min = target.eta_minutes
                
            await conn.execute("""
                INSERT INTO reco_targets (
                    reco_id, ordinal, name, target_type, value, confidence, eta_minutes
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, reco_id, ordinal, name, target_type, value, conf, eta_min)
        
        # Insert option if available
        if option_idea:
            if isinstance(option_idea, dict):
                opt_type = option_idea['option_type']
                strike = float(option_idea['strike'])
                expiry = option_idea['expiry']
                opt_entry = float(option_idea['option_entry_price'])
                stock_price = entry_price  # Use entry price as stock price
                greeks = option_idea.get('greeks')
                iv = option_idea.get('iv')
                notes = option_idea.get('notes', '')
                opt_targets = option_idea.get('option_targets', [])
            else:
                opt_type = option_idea.option_type
                strike = float(option_idea.strike)
                expiry = option_idea.expiry
                opt_entry = float(option_idea.option_entry_price)
                stock_price = entry_price
                greeks = option_idea.greeks
                iv = option_idea.iv
                notes = option_idea.notes
                opt_targets = option_idea.option_targets
                
            await conn.execute("""
                INSERT INTO option_ideas (
                    reco_id, option_type, strike, expiry, 
                    option_entry_price, greeks, iv, notes
                ) VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7::jsonb, $8)
            """, reco_id, opt_type, strike, expiry, opt_entry,
                json.dumps(greeks) if greeks else None,
                json.dumps(iv) if iv else None,
                notes)
            
            # Insert option targets
            for opt_target in opt_targets:
                if isinstance(opt_target, dict):
                    opt_ordinal = opt_target['ordinal']
                    opt_name = opt_target.get('name', '')
                    opt_value = float(opt_target['value'])
                    opt_conf = float(opt_target['confidence'])
                    opt_eta = opt_target.get('eta_minutes')
                else:
                    opt_ordinal = opt_target.ordinal
                    opt_name = opt_target.name
                    opt_value = float(opt_target.value)
                    opt_conf = float(opt_target.confidence)
                    opt_eta = opt_target.eta_minutes
                    
                await conn.execute("""
                    INSERT INTO option_targets (
                        reco_id, ordinal, name, value, confidence, eta_minutes
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                """, reco_id, opt_ordinal, opt_name, opt_value, opt_conf, opt_eta)

async def main():
    # Parse DATABASE_URL environment variable
    database_url = os.getenv('DATABASE_URL', 'postgresql://trading_user:trading_pass@postgres:5432/trading_db')
    # DATABASE_URL format: postgresql://user:password@host:port/database
    parts = database_url.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    user = user_pass[0]
    password = user_pass[1]
    host_port_db = parts[1].split('/')
    host_port = host_port_db[0].split(':')
    host = host_port[0]
    port = int(host_port[1])
    database = host_port_db[1]
    
    conn = await asyncpg.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    
    print("🗑️  Clearing old data...")
    await conn.execute('TRUNCATE TABLE option_targets, option_ideas, reco_targets, recommendations CASCADE')
    print("✅ Cleared old data")
    
    print("🔄 Generating new recommendations with corrected strike prices...")
    recos = generate_batch(num_recommendations=100, option_pct=0.80)
    print(f"✅ Generated {len(recos)} recommendations")
    
    print("💾 Inserting into database...")
    await insert_recommendations(conn, recos)
    print("✅ Data regenerated successfully!")
    
    # Verify NVDA strikes
    result = await conn.fetch("""
        SELECT DISTINCT oi.strike, r.symbol
        FROM option_ideas oi
        JOIN recommendations r ON r.reco_id = oi.reco_id
        WHERE r.symbol = 'NVDA'
        ORDER BY oi.strike
    """)
    
    print("\n📊 NVDA Strike Prices:", [f"${row['strike']:.2f}" for row in result])
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
