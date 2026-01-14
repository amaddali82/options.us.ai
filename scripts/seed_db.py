#!/usr/bin/env python3
"""
Seed database with sample recommendations for testing
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "inference_api"))

from reco_generator import RecoGenerator


async def seed_database():
    """Generate sample recommendations"""
    print("🌱 Seeding database with sample recommendations...")
    
    symbols = [
        "AAPL", "TSLA", "NVDA", "MSFT", "GOOGL",
        "AMZN", "META", "AMD", "NFLX", "SPY"
    ]
    
    generator = RecoGenerator()
    
    try:
        # Generate 5 recommendations for each symbol
        count = 0
        for symbol in symbols:
            print(f"Generating recommendations for {symbol}...")
            await generator.generate_batch([symbol], limit=5)
            count += 5
        
        print(f"✅ Successfully seeded {count} recommendations!")
        return 0
        
    except Exception as e:
        print(f"❌ Seed failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(seed_database())
    sys.exit(exit_code)
