from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import logging
from typing import Optional
import asyncio

from notification_adapter import NotificationAdapter
from rule_engine import AlertRuleEngine
from schemas import HealthResponse, NotificationRequest, NotificationResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Notification Service",
    description="Background notification and alerting service for trading recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
notification_adapter = NotificationAdapter()
rule_engine = AlertRuleEngine(notification_adapter)


@app.on_event("startup")
async def startup_event():
    """Startup event - initialize background workers"""
    logger.info("🚀 Notification Service starting up")
    logger.info("📧 Notification adapter initialized (logging mode)")
    logger.info("⚙️  Rule engine initialized")
    # TODO: Start background consumer when ready
    # asyncio.create_task(start_consumer())


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - cleanup"""
    logger.info("🛑 Notification Service shutting down")


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - returns service health status"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc),
        service="notification_service"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc),
        service="notification_service",
        adapter_mode="logging"
    )


@app.post("/notifications/send", response_model=NotificationResponse)
async def send_notification(request: NotificationRequest):
    """
    Manually trigger a notification (for testing)
    
    Args:
        request: Notification details (type, recipient, message)
        
    Returns:
        Confirmation of notification attempt
    """
    try:
        logger.info(f"📬 Manual notification request: {request.notification_type} to {request.recipient}")
        
        # Route to appropriate adapter method
        if request.notification_type == "email":
            await notification_adapter.send_email(
                to=request.recipient,
                subject=request.subject or "Trading Alert",
                body=request.message
            )
        elif request.notification_type == "sms":
            await notification_adapter.send_sms(
                to=request.recipient,
                message=request.message
            )
        elif request.notification_type == "push":
            await notification_adapter.send_push(
                user_id=request.recipient,
                title=request.subject or "Trading Alert",
                body=request.message
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown notification type: {request.notification_type}")
        
        return NotificationResponse(
            success=True,
            message=f"Notification queued: {request.notification_type}",
            timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to send notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/evaluate")
async def evaluate_recommendation_alert(
    reco_id: str,
    symbol: str,
    confidence_overall: float,
    tp1_confidence: float,
    entry_price: float,
    tp1_price: float
):
    """
    Evaluate if a recommendation triggers alert rules
    
    Args:
        reco_id: Recommendation ID
        symbol: Stock symbol
        confidence_overall: Overall confidence score
        tp1_confidence: TP1 confidence score
        entry_price: Entry price
        tp1_price: Target price 1
        
    Returns:
        Result of rule evaluation
    """
    try:
        alerts_triggered = await rule_engine.evaluate_recommendation(
            reco_id=reco_id,
            symbol=symbol,
            confidence_overall=confidence_overall,
            tp1_confidence=tp1_confidence,
            entry_price=entry_price,
            tp1_price=tp1_price
        )
        
        return {
            "reco_id": reco_id,
            "alerts_triggered": alerts_triggered,
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to evaluate alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
