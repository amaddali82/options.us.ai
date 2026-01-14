"""
Shared schemas for the Trading Intelligence System
These schemas can be used across services for data validation and type safety
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class RecommendationType(str, Enum):
    """Trading recommendation types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Timeframe(str, Enum):
    """Available timeframes for analysis"""
    ONE_MIN = "1m"
    FIVE_MIN = "5m"
    FIFTEEN_MIN = "15m"
    ONE_HOUR = "1h"
    FOUR_HOUR = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"


class IndicatorType(str, Enum):
    """Technical indicators"""
    RSI = "RSI"
    MACD = "MACD"
    EMA = "EMA"
    SMA = "SMA"
    BOLLINGER_BANDS = "BOLLINGER_BANDS"
    STOCHASTIC = "STOCHASTIC"


class RecommendationRequest(BaseModel):
    """Request schema for getting trading recommendations"""
    symbol: str = Field(..., description="Trading symbol (e.g., AAPL, TSLA)")
    timeframe: Timeframe = Field(default=Timeframe.ONE_DAY, description="Analysis timeframe")
    indicators: List[IndicatorType] = Field(default_factory=list, description="Technical indicators to include")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "timeframe": "1d",
                "indicators": ["RSI", "MACD"]
            }
        }


class RecommendationResponse(BaseModel):
    """Response schema for trading recommendations"""
    symbol: str = Field(..., description="Trading symbol")
    recommendation: RecommendationType = Field(..., description="Trading recommendation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    reasoning: str = Field(..., description="Explanation for the recommendation")
    timestamp: datetime = Field(..., description="Timestamp of the recommendation")
    indicators_used: Optional[List[str]] = Field(default=None, description="Indicators used in analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "recommendation": "BUY",
                "confidence": 0.85,
                "reasoning": "Strong upward trend with positive RSI and MACD crossover",
                "timestamp": "2026-01-14T12:00:00Z",
                "indicators_used": ["RSI", "MACD"]
            }
        }


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current timestamp")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    timestamp: str = Field(..., description="Error timestamp")
