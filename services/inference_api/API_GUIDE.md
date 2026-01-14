# Trading Intelligence API - Implementation Guide

## Overview
FastAPI-based recommendation service with async SQLAlchemy 2.0 + asyncpg, implementing a sophisticated ranking formula and cursor-based pagination.

## Architecture

### Tech Stack
- **FastAPI 0.104.1**: Async web framework
- **SQLAlchemy 2.0.23**: Async ORM with asyncpg driver
- **asyncpg 0.29.0**: High-performance async PostgreSQL driver
- **Pydantic v2**: Data validation and API schemas
- **PostgreSQL 16**: Database with JSONB support

### Database Models
Located in `models.py`:
- `Recommendation`: Core recommendation with multi-target support
- `RecoTarget`: Price targets with confidence and ETA
- `OptionIdea`: Option strategies (CALL/PUT) with Greeks
- `OptionTarget`: Premium targets for options

### API Schemas
Located in `schemas.py`:
- **List View**: `RecommendationListItem` - Lightweight with TP1/TP2 + option summary
- **Detail View**: `RecommendationDetail` - Full data with rationale and all targets
- **Pagination**: Cursor-based with `(asof, reco_id)` tuple

## Endpoints

### Health Check
```
GET /health
```
Returns API status and database connectivity.

### List Recommendations
```
GET /recommendations?limit=200&horizon=intraday&min_conf=0.60&symbol=AAPL&sort=rank&cursor=...
```

**Query Parameters:**
- `limit` (1-500): Number of results, default 200
- `horizon`: Filter by horizon (intraday, swing, position)
- `min_conf` (0.0-1.0): Minimum confidence threshold, default 0.60
- `symbol`: Filter by ticker symbol (e.g., AAPL)
- `sort`: Sort order - `rank` (default), `confidence`, or `asof`
- `cursor`: Pagination cursor for next page

**Response:**
```json
{
  "recommendations": [
    {
      "reco_id": "uuid",
      "symbol": "NVDA",
      "side": "BUY",
      "confidence_overall": 0.92,
      "rank": 11.27,
      "tp1": { "ordinal": 1, "value": 550.0, "confidence": 0.85 },
      "tp2": { "ordinal": 2, "value": 600.0, "confidence": 0.78 },
      "option_summary": {
        "option_type": "CALL",
        "expiry": "2026-03-20",
        "strike": 520.0,
        "option_targets": [...]
      }
    }
  ],
  "meta": {
    "total_returned": 5,
    "has_more": true,
    "next_cursor": "2026-01-14T18:49:01.385071+00:00|uuid"
  }
}
```

### Get Recommendation Detail
```
GET /recommendations/{reco_id}
```

Returns full recommendation with:
- Complete rationale (thesis, catalysts, risks)
- Quality metrics (liquidity_score, data_quality)
- All targets with ETA and notes
- Full option details with Greeks and IV
- Creation/update timestamps

### Seed Sample Data
```
POST /recommendations/seed
```

Creates 6 diverse recommendations:
- **AAPL**: BUY swing with CALL option (3 targets)
- **TSLA**: SELL swing (2 targets)
- **NVDA**: BUY position with CALL option (3 targets + 3 option targets)
- **MSFT**: HOLD swing (2 range targets)
- **META**: BUY intraday with PUT hedge
- **GOOGL**: BUY position (2 targets)

## Ranking Formula

```python
rank = confidence_overall * abs(expected_move_pct) * liquidity_score * freshness_factor
```

### Components
1. **confidence_overall** [0, 1]: Model confidence in recommendation
2. **expected_move_pct**: Expected percentage move (absolute value for SELL)
3. **liquidity_score** [0, 1]: From quality JSON, default 0.8
4. **freshness_factor** [0.1, 1.0]: Exponential decay after 5 minutes

### Freshness Calculation
- First 5 minutes: `freshness = 1.0` (no decay)
- After 5 minutes: `freshness = exp(-0.0231 * (age_minutes - 5))`
- Half-life: 30 minutes
- Minimum: 0.1 (never fully expires)

### Example
For NVDA recommendation:
- confidence_overall: 0.92
- expected_move_pct: 12.5%
- liquidity_score: 0.98
- freshness_factor: 1.0 (fresh)
- **rank = 0.92 × 12.5 × 0.98 × 1.0 = 11.27**

## Pagination

Cursor-based pagination using `(asof, reco_id)` tuple for stable ordering:

```python
# Parse cursor
asof, reco_id = parse_cursor("2026-01-14T18:49:01.385071+00:00|uuid")

# Apply filter
WHERE (asof < cursor_asof) OR (asof = cursor_asof AND reco_id > cursor_reco_id)
```

Benefits:
- ✅ Stable across insertions
- ✅ No skipped or duplicate records
- ✅ Efficient with proper indexes

## Error Handling

All endpoints implement:
- Try-catch blocks with detailed logging
- HTTP 404 for missing resources
- HTTP 500 with error details for server errors
- Database transaction rollback on failures
- Async session cleanup in finally blocks

## OpenAPI Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Start Application
```bash
cd infra
docker compose up -d --build
```

### Seed Data
```bash
curl -X POST http://localhost:8000/recommendations/seed
```

### Test List Endpoint
```bash
# By rank (default)
curl "http://localhost:8000/recommendations?limit=5&sort=rank"

# By symbol
curl "http://localhost:8000/recommendations?symbol=AAPL"

# By horizon and confidence
curl "http://localhost:8000/recommendations?horizon=intraday&min_conf=0.75"

# With pagination
curl "http://localhost:8000/recommendations?limit=2&cursor=<cursor>"
```

### Test Detail Endpoint
```bash
curl "http://localhost:8000/recommendations/{reco_id}"
```

## Database Queries

### Count Recommendations
```sql
SELECT COUNT(*) FROM recommendations;
```

### Check Rankings
```sql
SELECT 
    symbol, 
    confidence_overall, 
    expected_move_pct, 
    quality->'liquidity_score' as liq_score,
    asof 
FROM recommendations 
ORDER BY asof DESC;
```

### Verify Options
```sql
SELECT r.symbol, oi.option_type, oi.expiry, oi.strike, oi.greeks
FROM recommendations r
JOIN option_ideas oi ON r.reco_id = oi.reco_id;
```

## Performance Considerations

1. **Indexes**: Composite indexes on (symbol, asof), (horizon, confidence)
2. **Connection Pooling**: NullPool for development, configure for production
3. **Eager Loading**: `lazy="selectin"` for relationships to avoid N+1 queries
4. **Async Operations**: Non-blocking I/O for all database operations
5. **Limit Enforcement**: Max 500 recommendations per request

## Next Steps

- [ ] Add WebSocket support for real-time updates
- [ ] Implement Redis caching for frequently accessed recommendations
- [ ] Add authentication and rate limiting
- [ ] Create background task for freshness decay updates
- [ ] Add filtering by date range
- [ ] Implement bulk update endpoints
- [ ] Add recommendation performance tracking
- [ ] Create aggregation endpoints (by symbol, horizon, etc.)
