# Recommendation Generator Module

## Overview
The `reco_generator.py` module generates realistic trading recommendations with full support for multi-target recommendations and options strategies.

## Features

### Symbol Universe
- **80+ symbols** across multiple sectors:
  - Mega Cap Tech (AAPL, MSFT, GOOGL, NVDA, TSLA, etc.)
  - Software & Cloud (CRM, SNOW, PLTR, NOW, etc.)
  - Finance (JPM, GS, V, MA, etc.)
  - Healthcare & Biotech (LLY, ABBV, MRNA, VRTX, etc.)
  - Energy (XOM, CVX, COP)
  - Semiconductors (TSM, AMD, MU, AMAT, etc.)
  - Industrials & Aerospace
  - Crypto-related (COIN, MSTR, HOOD)

### Horizons
- **intraday**: 1-day trades
- **swing**: 1-5 day trades
- **position**: 5-20 day trades

### Side Distribution
- BUY: ~60%
- SELL: ~30%
- HOLD: ~10%

### Options Generation (60%+ of recommendations)

#### Strike Selection
Based on delta buckets:
- High confidence (≥0.85): 55-65Δ (near ATM)
- Medium confidence (≥0.75): 45-55Δ (slightly OTM)
- Lower confidence (<0.75): 35-45Δ (more OTM)

#### Expiry Selection
- **intraday**: 2-5 DTE (nearest weekly)
- **swing**: 7-14 DTE (1-2 weeks out)
- **position**: 14-42 DTE (2-6 weeks out)
- All expiries rounded to nearest Friday

#### Greeks Simulation
- **Delta**: Based on target delta bucket
- **Gamma**: Higher for ATM, decreases with DTE
- **Theta**: Accelerates closer to expiry
- **Vega**: Higher for longer DTE
- **Rho**: Scales with DTE and delta

#### IV Estimation
Sector-based implied volatility:
- Tech: ~35% (higher for TSLA, NVDA: ~45-50%)
- Finance: ~25%
- Healthcare: ~40%
- Energy: ~32%
- Consumer: ~22%
- Random variation ±15%

### Rationale Generation

#### Thesis Templates
**BUY**:
- "Strong [sector theme] supports upside"
- "Technical breakout with [confirmation]"
- "Undervalued relative to [metric]"
- "Positive [catalyst type]"

**SELL**:
- "Overextended rally due for [correction]"
- "Weakening [sector theme] signals downside"
- "Technical [breakdown/reversal] confirmed"
- "Negative [fundamental shift]"

#### Event Tags (2-4 per recommendation)
- earnings_beat, earnings_miss
- guidance_raise, guidance_lower
- product_launch, regulatory_approval
- analyst_upgrade, analyst_downgrade
- sector_rotation, technical_breakout
- volume_surge, short_squeeze
- insider_buying/selling
- clinical_trial_success
- margin_expansion, debt_reduction
- And 20+ more...

#### Sentiment Score
- BUY: 0.65 to 0.90
- SELL: -0.90 to -0.65

### Quality Metrics
- **liquidity_score**: 0.70-0.98 (higher for mega caps)
- **data_quality**: "high" or "medium"
- **model_version**: v2.0-v3.5
- **signal_strength**: 0.65-0.95

## Usage

### Generate Batch
```python
from reco_generator import generate_batch

# Generate 50 recommendations, 70% with options
recommendations = generate_batch(
    num_recommendations=50,
    option_pct=0.70
)
```

### Generate for Specific Symbols
```python
from reco_generator import generate_for_symbol_set

symbols = ["AAPL", "NVDA", "TSLA"]
horizons = ["intraday", "swing"]

# One reco per symbol per horizon
recommendations = generate_for_symbol_set(
    symbols=symbols,
    horizons=horizons
)
# Returns 6 recommendations (3 symbols × 2 horizons)
```

### API Integration

The seed endpoint now uses the generator:

```bash
# Default: 20 recommendations, 65% with options
POST http://localhost:8000/recommendations/seed

# Custom: 100 recommendations, 80% with options
POST http://localhost:8000/recommendations/seed?count=100&option_pct=0.8
```

## Output Format

Each generated recommendation includes:

```python
{
    "reco_id": uuid.UUID,
    "asof": datetime,
    "symbol": str,
    "horizon": str,  # intraday, swing, position
    "side": str,  # BUY, SELL, HOLD
    "entry_price": float,
    "confidence_overall": float,  # 0.68-0.94
    "expected_move_pct": float,  # percentage
    
    "rationale": {
        "thesis": str,
        "catalysts": List[str],
        "risks": List[str],
        "sentiment_score": float,
        "event_tags": List[str]
    },
    
    "quality": {
        "liquidity_score": float,
        "data_quality": str,
        "model_version": str,
        "signal_strength": float
    },
    
    "targets": [
        {
            "ordinal": 1,
            "name": "TP1",
            "target_type": "price",
            "value": float,
            "confidence": float,
            "eta_minutes": int
        },
        {
            "ordinal": 2,
            "name": "TP2",
            "target_type": "price",
            "value": float,
            "confidence": float,
            "eta_minutes": int
        }
    ],
    
    "stop": {
        "stop_type": str,  # hard, trailing, mental
        "value": float,
        "confidence": float
    },
    
    "option_idea": {  # Optional, ~65% of recommendations
        "option_type": str,  # CALL or PUT
        "expiry": date,
        "strike": float,
        "option_entry_price": float,
        "greeks": {
            "delta": float,
            "gamma": float,
            "theta": float,
            "vega": float,
            "rho": float
        },
        "iv": {
            "implied_vol": float,
            "iv_rank": float
        },
        "notes": str,
        "option_targets": [
            {
                "ordinal": 1,
                "name": "Premium TP1",
                "value": float,
                "confidence": float,
                "eta_minutes": int
            },
            {
                "ordinal": 2,
                "name": "Premium TP2",
                "value": float,
                "confidence": float,
                "eta_minutes": int
            }
        ]
    }
}
```

## Realistic Features

### Price Movement Modeling
- Expected move based on:
  - Implied volatility (sector-adjusted)
  - Horizon (time decay)
  - Square root of time scaling
  
### Target Placement
- TP1: 3-10% for swing/position, 3-6% for intraday
- TP2: Additional 3-8% beyond TP1
- Confidence decreases progressively (TP2 < TP1)
- Stop loss: 3-8% against position

### Option Pricing
Simplified Black-Scholes approximation:
- Intrinsic value calculation
- Time value based on IV and DTE
- Moneyness adjustment
- Realistic premium increments ($0.05, $0.10, $0.50, $1.00, $5.00)

### Option Target Returns
- Premium TP1: 40-80% gain
- Premium TP2: 90-150% gain
- Confidence: 5-10% below stock target confidence

## Testing

Run standalone test:
```bash
cd services/inference_api
python reco_generator.py
```

Output example:
```
Generating 10 sample recommendations...

Generated 10 recommendations:
  AAPL   BUY  swing     @ $ 178.50 conf=0.88 + CALL
  NVDA   BUY  position  @ $ 505.00 conf=0.85 + CALL
  TSLA   SELL swing     @ $ 242.80 conf=0.75
  JPM    BUY  intraday  @ $ 168.50 conf=0.74 + CALL
  ...

✅ Generator working correctly!
```

## Statistics from 50-Recommendation Sample

- **Total**: 60 recommendations (50 generated + 10 from migration)
- **Side Distribution**: 35 BUY (58%), 19 SELL (32%), 6 HOLD (10%)
- **Horizon Distribution**: 24 swing (40%), 18 position (30%), 16 intraday (27%)
- **Options Coverage**: 35/60 (58.3%)
- **Symbol Diversity**: 40+ unique symbols

## Performance

- Generation time: <1ms per recommendation
- Database insertion: ~50 recommendations in <500ms
- No external API calls required
- Fully deterministic (uses random seed for reproducibility if needed)

## Future Enhancements

- [ ] Add correlation between related symbols
- [ ] Implement sector rotation logic
- [ ] Add earnings calendar integration
- [ ] Support for spreads (vertical, calendar, iron condor)
- [ ] Historical backtesting data generation
- [ ] Custom volatility surface modeling
- [ ] Risk/reward ratio optimization
- [ ] Position sizing recommendations
