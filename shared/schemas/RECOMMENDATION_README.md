# Trading Recommendation Schema

Comprehensive Pydantic v2 models for multi-target trading recommendations with options support.

## Overview

This module provides strongly-typed, validated data models for sophisticated trading recommendations including:

- **Multi-target ladder strategies** (1-5 targets)
- **Options strategies** with Greeks and premium targets
- **Stop-loss configurations** with confidence levels
- **Comprehensive risk management** metadata

## Models

### 1. `Recommendation` (Main Model)

Complete trading recommendation with validation.

**Required Fields:**
- `symbol`: str (1-10 chars, auto-uppercased)
- `recommendation_type`: "BUY" | "SELL" | "HOLD"
- `confidence_overall`: float [0.0, 1.0]
- `current_price`: float (> 0)
- `targets`: List[Target] (1-5 items)
- `reasoning`: str (10-2000 chars)

**Optional Fields:**
- `entry_price`: float (> 0)
- `stop_loss`: Stop
- `option_idea`: OptionIdea
- `timeframe`: str
- `risk_reward_ratio`: float (> 0)
- `catalysts`: List[str]
- `risks`: List[str]
- `indicators_used`: List[str]
- `analyst`: str

**Validation Rules:**
- For BUY: targets ascending, all above current price
- For SELL: targets descending, all below current price
- Stop loss in correct direction
- Option symbol must match recommendation symbol

### 2. `Target`

Price target with confidence level.

**Fields:**
- `price`: float (> 0, max 4 decimals)
- `confidence`: float [0.0, 1.0]
- `timeframe_days`: int (> 0, optional)
- `reasoning`: str (max 500 chars, optional)

### 3. `Stop`

Stop-loss configuration.

**Fields:**
- `price`: float (> 0, max 4 decimals)
- `confidence`: float [0.0, 1.0]
- `stop_type`: "hard" | "trailing" | "mental"
- `reasoning`: str (max 300 chars, optional)

### 4. `OptionIdea`

Options strategy with 1-3 premium targets.

**Required Fields:**
- `option_type`: "CALL" | "PUT"
- `symbol`: str (1-10 chars, auto-uppercased)
- `expiry`: date (YYYY-MM-DD, must be future)
- `strike`: float (> 0, max 4 decimals)
- `entry_premium`: float (> 0, max 4 decimals)
- `greeks`: Greeks
- `implied_volatility`: float (0, 5.0] as decimal
- `option_targets`: List[OptionTarget] (1-3 items)

**Optional Fields:**
- `contracts`: int (> 0, default: 1)
- `stop_loss_premium`: float (> 0)
- `max_loss_dollars`: float
- `reasoning`: str (max 1000 chars)

**Validation Rules:**
- Expiry must be in the future
- Targets must be sorted by premium (ascending)
- First target must be above entry premium

### 5. `OptionTarget`

Premium target for options.

**Fields:**
- `premium`: float (> 0, max 4 decimals)
- `confidence`: float [0.0, 1.0]
- `profit_percentage`: float (optional)
- `underlying_price`: float (> 0, optional)

### 6. `Greeks`

Option Greeks for risk assessment.

**Fields:**
- `delta`: float [-1.0, 1.0] (required)
- `gamma`: float [0.0, ∞) (optional)
- `theta`: float (optional)
- `vega`: float [0.0, ∞) (optional)
- `rho`: float (optional)

## Usage Examples

### Basic BUY Recommendation

```python
from recommendation import Recommendation, Target, Stop

rec = Recommendation(
    symbol="AAPL",
    recommendation_type="BUY",
    confidence_overall=0.85,
    current_price=175.50,
    targets=[
        Target(price=180.00, confidence=0.85),
        Target(price=185.00, confidence=0.70),
        Target(price=190.00, confidence=0.55),
    ],
    stop_loss=Stop(price=170.00, confidence=0.90, stop_type="hard"),
    reasoning="Strong technical breakout with bullish momentum"
)
```

### With Options Strategy

```python
from recommendation import (
    Recommendation, Target, OptionIdea, OptionTarget, 
    Greeks, OptionType
)
from datetime import date

rec = Recommendation(
    symbol="NVDA",
    recommendation_type="BUY",
    confidence_overall=0.88,
    current_price=495.50,
    targets=[
        Target(price=520.00, confidence=0.85, timeframe_days=15),
        Target(price=545.00, confidence=0.70, timeframe_days=30),
    ],
    option_idea=OptionIdea(
        option_type=OptionType.CALL,
        symbol="NVDA",
        expiry=date(2026, 3, 20),
        strike=510.0,
        entry_premium=28.50,
        contracts=3,
        greeks=Greeks(
            delta=0.62,
            gamma=0.018,
            theta=-0.42,
            vega=0.95
        ),
        implied_volatility=0.45,
        option_targets=[
            OptionTarget(premium=42.00, confidence=0.80, profit_percentage=47.4),
            OptionTarget(premium=58.50, confidence=0.60, profit_percentage=105.3),
            OptionTarget(premium=78.00, confidence=0.40, profit_percentage=173.7),
        ],
        stop_loss_premium=18.00,
        max_loss_dollars=3150.00
    ),
    reasoning="High-momentum setup with favorable risk/reward via options"
)
```

### SELL Recommendation

```python
rec = Recommendation(
    symbol="XYZ",
    recommendation_type="SELL",
    confidence_overall=0.75,
    current_price=100.00,
    targets=[
        Target(price=95.00, confidence=0.80),  # Descending for SELL
        Target(price=90.00, confidence=0.65),
    ],
    stop_loss=Stop(price=105.00, confidence=0.85, stop_type="hard"),
    reasoning="Bearish technical pattern with negative divergence"
)
```

## JSON Schema Export

```python
from recommendation import get_recommendation_schema, get_all_schemas

# Get single model schema
rec_schema = get_recommendation_schema()

# Get all model schemas
all_schemas = get_all_schemas()

# Export to file
from recommendation import export_schemas_to_file
export_schemas_to_file("schemas.json")
```

## Validation Features

### Automatic Conversions
- Symbols automatically uppercased
- Prices rounded to 4 decimal places

### Boundary Checks
- Confidence values: [0.0, 1.0]
- Prices: > 0
- Delta: [-1.0, 1.0]
- Implied volatility: (0, 5.0]

### Logical Validation
- BUY targets must be above current price (ascending)
- SELL targets must be below current price (descending)
- Stop loss in correct direction based on recommendation type
- Option expiry must be in future
- Option targets sorted by premium
- First option target above entry premium
- Option symbol matches recommendation symbol
- Target/stop lists within size limits (1-5 targets, 1-3 option targets)

### Date Validation
- Expiry dates must be YYYY-MM-DD format
- Expiry must be in the future

## Testing

Run comprehensive validation tests:

```bash
python test_recommendation.py
```

Tests cover:
- ✅ Valid recommendations (BUY/SELL with options)
- ❌ Invalid target ordering
- ❌ Invalid target direction vs current price
- ❌ Past expiry dates
- ❌ Out-of-bounds confidence values
- ❌ Negative prices
- ❌ Unsorted option targets
- ❌ First target below entry
- ❌ Symbol mismatches
- 📋 JSON schema export
- 📊 Complex real-world scenarios

## Integration with FastAPI

```python
from fastapi import APIRouter
from recommendation import Recommendation

router = APIRouter()

@router.post("/recommendations", response_model=Recommendation)
async def create_recommendation(rec: Recommendation):
    # Pydantic automatically validates
    return rec

@router.get("/recommendations/schema")
async def get_schema():
    return get_recommendation_schema()
```

## Error Handling

All validation errors raise `ValidationError` with detailed messages:

```python
try:
    rec = Recommendation(
        symbol="AAPL",
        recommendation_type="BUY",
        confidence_overall=0.85,
        current_price=175.00,
        targets=[Target(price=170.00, confidence=0.80)],  # Below current!
        reasoning="Test"
    )
except ValidationError as e:
    print(e.errors())
    # Output: [{'type': 'value_error', 'msg': 'For BUY recommendation, 
    # target price 170.0 must be above current price 175.0', ...}]
```

## Best Practices

1. **Always include reasoning** - Minimum 10 characters, helps with auditability
2. **Set realistic confidence levels** - Based on backtested probabilities
3. **Use stop losses** - Essential risk management
4. **Include catalysts and risks** - Comprehensive analysis
5. **Validate dates** - Ensure expiry dates are reasonable (not too far in future)
6. **Check Greeks** - Delta around 0.5-0.7 for balanced risk/reward
7. **Size option targets appropriately** - 1-3 targets for clear exit strategy
8. **Document indicators used** - Reproducibility and validation

## File Structure

```
shared/schemas/
├── __init__.py              # Exports all models
├── recommendation.py        # Main models (this file)
├── test_recommendation.py   # Comprehensive tests
├── trading_schemas.py       # Legacy simple schemas
└── README.md               # This documentation
```

## Version

- **Pydantic**: v2.x (using ConfigDict, Field, validators)
- **Python**: 3.11+
- **Type hints**: Full typing support with List, Optional, Literal

## License

MIT License - Part of Trading Intelligence System
