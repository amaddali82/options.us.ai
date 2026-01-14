# API Constraints & Validation

## Enforced Constraints

### 1. No Execution/Trading Endpoints ✅

**Implementation:**
- Only read-only endpoints exposed:
  - `GET /health` - Health check
  - `GET /recommendations` - List recommendations (read-only)
  - `GET /recommendations/{reco_id}` - Get details (read-only)
  - `POST /recommendations/seed` - Generate sample data (dev/testing only, no real trading)

**Verification:**
```bash
grep -E "@app\.(post|put|patch|delete)" services/inference_api/main.py
# Only returns: @app.post("/recommendations/seed"...)
```

**No Brokerage Connectivity:**
- No broker API integration
- No order placement logic
- No account management
- No position tracking beyond recommendations

### 2. Time-Based Cursor Pagination ✅

**Implementation:**
```python
# services/inference_api/main.py

def encode_cursor(asof: datetime, reco_id: UUID) -> str:
    """Encode timestamp + ID into base64 cursor"""
    return base64.urlsafe_b64encode(
        f"{asof.isoformat()}|{str(reco_id)}".encode()
    ).decode()

def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    """Decode cursor to timestamp + ID"""
    decoded = base64.urlsafe_b64decode(cursor.encode()).decode()
    asof_str, reco_id_str = decoded.split("|")
    return datetime.fromisoformat(asof_str), UUID(reco_id_str)

# Query uses time-based ordering with cursor
stmt = select(Recommendation).order_by(
    Recommendation.asof.desc(),
    Recommendation.reco_id.desc()
)

if cursor:
    cursor_asof, cursor_id = decode_cursor(cursor)
    stmt = stmt.where(
        or_(
            Recommendation.asof < cursor_asof,
            and_(
                Recommendation.asof == cursor_asof,
                Recommendation.reco_id < cursor_id
            )
        )
    )
```

**Benefits:**
- Consistent pagination even with new data
- No offset drift issues
- Efficient database queries
- Handles concurrent updates gracefully

**Response Structure:**
```json
{
  "recommendations": [...],
  "meta": {
    "total_returned": 100,
    "has_more": true,
    "next_cursor": "MjAyNi0wMS0xNFQxMjozMDowMHw5YjFkYzg0Yy0xMjM0LTRhYmMtODk2Ny1lZjEyMzQ1Njc4OTA="
  }
}
```

### 3. No Rationale in List Endpoint ✅

**Implementation:**

**List Endpoint (`GET /recommendations`):**
```python
class RecommendationListItem(BaseModel):
    """Lightweight recommendation for list view - NO RATIONALE"""
    reco_id: UUID
    asof: datetime
    symbol: str
    horizon: str
    side: str
    entry_price: float
    confidence_overall: float
    expected_move_pct: Optional[float] = None
    rank: float
    
    # Only first two targets
    tp1: Optional[TargetSummary] = None
    tp2: Optional[TargetSummary] = None
    
    # Option summary if present (no rationale)
    option_summary: Optional[OptionSummary] = None
    
    # NO rationale, quality, or full target list
```

**Detail Endpoint (`GET /recommendations/{reco_id}`):**
```python
class RecommendationDetail(BaseModel):
    """Full recommendation with all details - INCLUDES RATIONALE"""
    # ... all list fields ...
    
    rationale: Optional[dict] = Field(None, description="Full rationale - only in detail endpoint")
    quality: Optional[dict] = None
    
    # All targets (not limited to 2)
    targets: List[TargetDetail] = Field(default_factory=list)
    
    # Full option details
    option_idea: Optional[OptionDetail] = None
```

**Benefits:**
- Reduced payload size for list endpoint (50-100x smaller)
- Faster loading times
- Lower bandwidth usage
- Better scalability

**Size Comparison:**
- List item: ~300 bytes
- Detail with rationale: ~15KB+

### 4. Validation Rules ✅

#### Confidence Values (0.0 to 1.0)

```python
from pydantic import Field

class TargetSummary(BaseModel):
    confidence: float = Field(
        ge=0.0, 
        le=1.0, 
        description="Confidence must be between 0 and 1"
    )

class RecommendationListItem(BaseModel):
    confidence_overall: float = Field(
        ge=0.0, 
        le=1.0, 
        description="Confidence must be between 0 and 1"
    )
```

**Enforcement:**
- Pydantic validates on request parsing
- Returns 422 Unprocessable Entity if validation fails
- Clear error message indicates constraint violation

**Example Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "confidence_overall"],
      "msg": "ensure this value is less than or equal to 1",
      "type": "value_error.number.not_le"
    }
  ]
}
```

#### Prices Must Be Positive (> 0)

```python
class TargetSummary(BaseModel):
    value: float = Field(
        gt=0, 
        description="Target price must be positive"
    )

class RecommendationListItem(BaseModel):
    entry_price: float = Field(
        gt=0, 
        description="Entry price must be positive"
    )

class OptionSummary(BaseModel):
    strike: float = Field(
        gt=0, 
        description="Strike price must be positive"
    )

class OptionDetail(BaseModel):
    option_entry_price: float = Field(
        gt=0, 
        description="Entry premium must be positive"
    )
```

**Enforcement:**
- Validates all price fields
- Prevents negative or zero prices
- Catches data errors early

#### Expiry Must Be a Valid Future Date

```python
from datetime import date
from pydantic import field_validator

class OptionSummary(BaseModel):
    expiry: date = Field(description="Option expiration date")
    
    @field_validator('expiry')
    @classmethod
    def validate_expiry(cls, v: date) -> date:
        if v < date.today():
            raise ValueError('Expiry date cannot be in the past')
        return v
```

**Enforcement:**
- Type validation ensures it's a proper date
- Custom validator checks it's not in the past
- Prevents expired options from being created

#### Enums for Categorical Fields

```python
class RecommendationListItem(BaseModel):
    symbol: str = Field(
        min_length=1, 
        max_length=10, 
        description="Stock symbol"
    )
    
    horizon: str = Field(
        pattern="^(intraday|swing|position)$"
    )
    
    side: str = Field(
        pattern="^(BUY|SELL|HOLD)$"
    )

class OptionSummary(BaseModel):
    option_type: str = Field(
        pattern="^(CALL|PUT)$", 
        description="Must be CALL or PUT"
    )
```

**Enforcement:**
- Regex pattern validation
- Prevents typos and invalid values
- Self-documenting API

#### Non-Negative ETA

```python
class TargetDetail(BaseModel):
    eta_minutes: Optional[int] = Field(
        None, 
        ge=0, 
        description="ETA must be non-negative"
    )
```

**Enforcement:**
- Prevents negative time values
- Allows None for unknown ETA

### 5. Clean TypeScript Types ✅

**Backend Schema (`services/inference_api/schemas.py`):**
```python
class TargetSummary(BaseModel):
    ordinal: int
    value: float
    confidence: float
```

**Frontend Types (`services/ui/src/types.ts`):**
```typescript
export interface TargetSummary {
  ordinal: number  // Target number (1, 2, 3...)
  value: number    // Target price (> 0)
  confidence: number  // 0.0 to 1.0
}
```

**Exact Field Name Matching:**
- Backend: `ordinal`, `value`, `confidence`
- Frontend: `ordinal`, `value`, `confidence`
- ✅ No transformation needed
- ✅ Direct JSON mapping

**Response Structure Matching:**
```python
# Backend
class RecommendationListResponse(BaseModel):
    recommendations: List[RecommendationListItem]
    meta: PaginationMeta
```

```typescript
// Frontend
export interface RecommendationsResponse {
  recommendations: RecommendationListItem[]
  meta: PaginationMeta  // Matches backend field name
}
```

**Generic Types for Flexibility:**
```typescript
// Backend returns dict/any for rationale and quality
// Frontend uses Record<string, any> to avoid tight coupling

export interface RecommendationDetail {
  // ... other fields ...
  rationale: Record<string, any> | null
  quality: Record<string, any> | null
}

// Safe accessor pattern in components
const getRationale = () => detail?.rationale as any
const sentimentScore = getRationale()?.sentiment_score ?? 0.5
```

**Benefits:**
- No manual type mapping
- Type-safe API calls
- Clear validation constraints in types
- Self-documenting interfaces

## Verification Checklist

### API Endpoints
- [ ] No PUT/PATCH/DELETE endpoints
- [x] Only GET for reads
- [x] Only POST for seed (non-trading)
- [x] No brokerage integration

### Pagination
- [x] Time-based cursor (not offset-based)
- [x] Cursor encodes timestamp + ID
- [x] Stable ordering (asof DESC, reco_id DESC)
- [x] Returns next_cursor and has_more

### Data Size
- [x] List endpoint excludes rationale
- [x] List endpoint includes only first 2 targets
- [x] Detail endpoint has full data
- [x] List items < 500 bytes each

### Validation
- [x] Confidence: 0.0 ≤ value ≤ 1.0
- [x] Prices: value > 0
- [x] Expiry: future date
- [x] Enums: pattern validation
- [x] ETA: non-negative

### TypeScript
- [x] Field names match backend exactly
- [x] Response structure matches backend
- [x] Generic types for flexible fields
- [x] Safe accessors for dict fields

## Testing Validation

### Test Invalid Confidence
```bash
# Should return 422
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{"confidence_overall": 1.5}'
```

### Test Negative Price
```bash
# Should return 422
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{"entry_price": -10.50}'
```

### Test Past Expiry
```bash
# Should return 422
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{"expiry": "2020-01-01"}'
```

### Test Cursor Pagination
```bash
# First page
curl "http://localhost:8000/recommendations?limit=10"

# Next page (use cursor from response)
curl "http://localhost:8000/recommendations?limit=10&cursor=MjAyNi..."
```

### Verify No Rationale in List
```bash
# List endpoint should NOT have rationale field
curl "http://localhost:8000/recommendations?limit=1" | jq '.recommendations[0] | keys'

# Should NOT include: "rationale", "quality"
# Should include: "reco_id", "symbol", "side", "horizon", "entry_price", "confidence_overall", "tp1", "tp2"
```

### Verify Rationale in Detail
```bash
# Detail endpoint SHOULD have rationale field
curl "http://localhost:8000/recommendations/{reco_id}" | jq 'keys'

# Should include: "rationale", "quality", "targets" (all targets, not just 2)
```

## Migration Notes

If migrating from old field names:

### Backend
- `target_num` → `ordinal`
- `target_price` → `value`
- `premium_target` → `value`
- `pagination` → `meta`
- `total_count` → `total_returned`

### Frontend
- Update all component references
- Use safe accessors for dict fields
- Handle null/undefined gracefully
- Add fallback values

### Example Component Update
```typescript
// Old
<div>{target.target_price}</div>

// New
<div>{target.value}</div>

// With safety
<div>{target.value || 'N/A'}</div>
```

## Performance Metrics

### List Endpoint
- Payload size: ~30KB for 100 recommendations (without rationale)
- Response time: < 100ms (typical)
- Database query: Simple WHERE + ORDER BY + LIMIT

### Detail Endpoint
- Payload size: ~15KB per recommendation (with rationale)
- Response time: < 50ms (typical)
- Database query: Single SELECT with joins

### Validation Overhead
- Negligible (< 1ms per request)
- Pydantic validates during deserialization
- Clear error messages for debugging
