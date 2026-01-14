"""
Pydantic schemas for notification service API
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    service: Optional[str] = None
    adapter_mode: Optional[str] = None


class NotificationRequest(BaseModel):
    """Request to send a notification"""
    notification_type: str = Field(..., description="Type: email, sms, or push")
    recipient: str = Field(..., description="Recipient address/ID")
    message: str = Field(..., description="Notification message body")
    subject: Optional[str] = Field(None, description="Subject line (email only)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "notification_type": "email",
                "recipient": "trader@example.com",
                "message": "High confidence trade alert for AAPL",
                "subject": "Trading Alert: AAPL"
            }
        }


class NotificationResponse(BaseModel):
    """Response after sending notification"""
    success: bool
    message: str
    timestamp: datetime


class AlertRuleSchema(BaseModel):
    """Alert rule configuration schema"""
    rule_id: str
    name: str
    description: str
    min_confidence_overall: float = Field(..., ge=0.0, le=1.0)
    min_tp1_confidence: float = Field(..., ge=0.0, le=1.0)
    enabled: bool = True
    notification_channels: List[str] = ["email"]
    recipients: List[str] = ["admin@trading.com"]


class RecommendationAlertRequest(BaseModel):
    """Request to evaluate recommendation for alerts"""
    reco_id: str
    symbol: str
    confidence_overall: float = Field(..., ge=0.0, le=1.0)
    tp1_confidence: float = Field(..., ge=0.0, le=1.0)
    entry_price: float = Field(..., gt=0)
    tp1_price: float = Field(..., gt=0)
