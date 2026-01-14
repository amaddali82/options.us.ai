"""
API Response Schemas (DTOs) for recommendations
Separate from database models for clean API contracts
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class TargetSummary(BaseModel):
    """Lightweight target for list view"""
    ordinal: int
    value: float = Field(gt=0, description="Target price must be positive")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence must be between 0 and 1")
    
    model_config = ConfigDict(from_attributes=True)


class OptionSummary(BaseModel):
    """Lightweight option summary for list view"""
    option_type: str = Field(pattern="^(CALL|PUT)$", description="Must be CALL or PUT")
    expiry: date = Field(description="Option expiration date")
    strike: float = Field(gt=0, description="Strike price must be positive")
    option_targets: List[TargetSummary] = Field(default_factory=list, max_length=2)
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('expiry')
    @classmethod
    def validate_expiry(cls, v: date) -> date:
        if v < date.today():
            raise ValueError('Expiry date cannot be in the past')
        return v


class RecommendationListItem(BaseModel):
    """Lightweight recommendation for list view - NO RATIONALE"""
    reco_id: UUID
    asof: datetime
    symbol: str = Field(min_length=1, max_length=10, description="Stock symbol")
    horizon: str = Field(pattern="^(intraday|swing|position)$")
    side: str = Field(pattern="^(BUY|SELL|HOLD)$")
    entry_price: float = Field(gt=0, description="Entry price must be positive")
    confidence_overall: float = Field(ge=0.0, le=1.0, description="Confidence must be between 0 and 1")
    expected_move_pct: Optional[float] = None
    rank: float  # Calculated ranking score
    
    # First two targets only
    tp1: Optional[TargetSummary] = None
    tp2: Optional[TargetSummary] = None
    
    # Option summary if present
    option_summary: Optional[OptionSummary] = None
    
    model_config = ConfigDict(from_attributes=True)


class TargetDetail(BaseModel):
    """Full target details"""
    ordinal: int = Field(ge=1, description="Target number must be >= 1")
    name: Optional[str] = None
    target_type: str = "price"
    value: float = Field(gt=0, description="Target value must be positive")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence must be between 0 and 1")
    eta_minutes: Optional[int] = Field(None, ge=0, description="ETA must be non-negative")
    notes: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class OptionTargetDetail(BaseModel):
    """Full option target details"""
    ordinal: int = Field(ge=1, description="Target number must be >= 1")
    name: Optional[str] = None
    value: float = Field(gt=0, description="Premium target must be positive")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence must be between 0 and 1")
    eta_minutes: Optional[int] = Field(None, ge=0, description="ETA must be non-negative")
    notes: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class OptionDetail(BaseModel):
    """Full option details"""
    option_type: str = Field(pattern="^(CALL|PUT)$")
    expiry: date = Field(description="Option expiration date")
    strike: float = Field(gt=0, description="Strike price must be positive")
    option_entry_price: float = Field(gt=0, description="Entry premium must be positive")
    greeks: Optional[dict] = None
    iv: Optional[dict] = None
    notes: Optional[str] = None
    option_targets: List[OptionTargetDetail] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('expiry')
    @classmethod
    def validate_expiry(cls, v: date) -> date:
        if v < date.today():
            raise ValueError('Expiry date cannot be in the past')
        return v


class RecommendationDetail(BaseModel):
    """Full recommendation with all details - INCLUDES RATIONALE"""
    reco_id: UUID
    asof: datetime
    symbol: str = Field(min_length=1, max_length=10)
    horizon: str = Field(pattern="^(intraday|swing|position)$")
    side: str = Field(pattern="^(BUY|SELL|HOLD)$")
    entry_price: float = Field(gt=0, description="Entry price must be positive")
    confidence_overall: float = Field(ge=0.0, le=1.0, description="Confidence must be between 0 and 1")
    expected_move_pct: Optional[float] = None
    rationale: Optional[dict] = Field(None, description="Full rationale - only in detail endpoint")
    quality: Optional[dict] = None
    rank: float  # Calculated ranking score
    
    # All targets (not limited to 2)
    targets: List[TargetDetail] = Field(default_factory=list)
    
    # Full option details if present
    option_idea: Optional[OptionDetail] = None
    
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total_returned: int
    has_more: bool
    next_cursor: Optional[str] = None


class RecommendationListResponse(BaseModel):
    """Response for list endpoint with pagination"""
    recommendations: List[RecommendationListItem]
    meta: PaginationMeta


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    database: str = "connected"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "timestamp": "2026-01-14T12:00:00Z",
                "database": "connected"
            }
        }
    )


class SeedResponse(BaseModel):
    """Response for seed endpoint"""
    message: str
    recommendations_created: int
    sample_reco_ids: List[UUID]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Sample recommendations seeded successfully",
                "recommendations_created": 4,
                "sample_reco_ids": []
            }
        }
    )
