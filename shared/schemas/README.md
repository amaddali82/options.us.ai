# Shared Schemas

This directory contains shared data schemas and types used across multiple services in the Trading Intelligence System.

## Usage

### Python (Backend)
```python
from shared.schemas import RecommendationRequest, RecommendationResponse

# Use in FastAPI endpoints
@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    ...
```

### TypeScript/JavaScript (Frontend)
Convert these schemas to TypeScript interfaces or use the API directly with proper typing.

## Schemas

- **RecommendationType**: BUY, SELL, HOLD
- **Timeframe**: 1m, 5m, 15m, 1h, 4h, 1d, 1w
- **IndicatorType**: RSI, MACD, EMA, SMA, BOLLINGER_BANDS, STOCHASTIC
- **RecommendationRequest**: Request schema for recommendations
- **RecommendationResponse**: Response schema for recommendations
- **HealthResponse**: Health check response
- **ErrorResponse**: Standard error response
