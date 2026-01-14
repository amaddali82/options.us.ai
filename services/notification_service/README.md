# Notification Service

Background notification and alerting service for trading recommendations.

## Status: 🚧 Skeleton Implementation

This service is currently **disabled by default** and contains only stub implementations for future development.

## Features (Planned)

### ✅ Implemented (Logging Mode)
- FastAPI service skeleton
- `NotificationAdapter` interface with logging stubs
- Alert rule engine with threshold-based rules
- Manual notification trigger endpoint
- Health check endpoint

### 🔜 Future Implementation
- External notification providers (SendGrid, Twilio, FCM)
- Background message queue consumer (Redis/RabbitMQ)
- User preference management
- Rate limiting and throttling
- Notification templates
- Delivery tracking and retry logic

## Architecture

```
┌──────────────────────────────────┐
│    Inference API                 │
│  (generates recommendations)     │
└─────────────┬────────────────────┘
              │ (future: pub/sub)
              ▼
┌──────────────────────────────────┐
│   Message Queue (Redis/RMQ)      │
│   (recommendation events)        │
└─────────────┬────────────────────┘
              │
              ▼
┌──────────────────────────────────┐
│  Notification Service            │
│  ┌────────────────────────────┐  │
│  │   Consumer (background)    │  │
│  │  - Consumes events         │  │
│  │  - Evaluates rules         │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │   Rule Engine              │  │
│  │  - Alert rules             │  │
│  │  - Threshold checks        │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │   Notification Adapter     │  │
│  │  - Email (stub)            │  │
│  │  - SMS (stub)              │  │
│  │  - Push (stub)             │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

## Components

### 1. NotificationAdapter (`notification_adapter.py`)

Interface for sending notifications across multiple channels:

```python
class NotificationAdapter:
    async def send_email(to, subject, body, html=None)
    async def send_sms(to, message)
    async def send_push(user_id, title, body, data=None)
```

**Current Implementation:** Logs notifications instead of sending them.

### 2. AlertRuleEngine (`rule_engine.py`)

Evaluates recommendations against configurable alert rules:

**Default Rules:**
- **High Confidence** (80%+ overall and TP1 confidence)
- **Very High Confidence** (90%+ overall and TP1 confidence)
- **Moderate Confidence** (70%+ overall and TP1 confidence) - disabled by default

**Features:**
- Threshold-based evaluation
- Multi-channel notifications (email, SMS, push)
- Multiple recipients per rule
- Enable/disable rules

### 3. Background Consumer (`consumer.py`)

Placeholder for future message queue integration:
- Will consume recommendation events
- Process alerts asynchronously
- Non-blocking notification delivery

## API Endpoints

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2026-01-14T10:30:00Z",
  "service": "notification_service",
  "adapter_mode": "logging"
}
```

### Manual Notification (Testing)
```http
POST /notifications/send
```

Request:
```json
{
  "notification_type": "email",
  "recipient": "trader@example.com",
  "message": "High confidence trade alert for AAPL",
  "subject": "Trading Alert: AAPL"
}
```

### Evaluate Alert Rules
```http
POST /alerts/evaluate
```

Request:
```json
{
  "reco_id": "abc-123",
  "symbol": "AAPL",
  "confidence_overall": 0.85,
  "tp1_confidence": 0.82,
  "entry_price": 150.00,
  "tp1_price": 160.00
}
```

## Running Locally

```bash
cd services/notification_service

# Install dependencies
pip install -r requirements.txt

# Start service
python main.py
# or
uvicorn main:app --reload --port 8001
```

Access docs: http://localhost:8001/docs

## Testing

### Test Manual Notification
```bash
curl -X POST http://localhost:8001/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "email",
    "recipient": "test@example.com",
    "message": "Test alert",
    "subject": "Test"
  }'
```

Check logs to see the "notification" that would be sent.

### Test Alert Evaluation
```bash
curl -X POST "http://localhost:8001/alerts/evaluate?reco_id=test-123&symbol=AAPL&confidence_overall=0.85&tp1_confidence=0.82&entry_price=150.00&tp1_price=160.00"
```

## Docker

Build:
```bash
docker build -t notification-service .
```

Run:
```bash
docker run -p 8001:8001 notification-service
```

## Enabling in Production

The service is **disabled by default** in docker-compose.yml. To enable:

1. Uncomment the `notification_service` section in `docker-compose.yml`
2. Configure environment variables
3. Integrate external notification providers
4. Set up message queue (Redis/RabbitMQ)
5. Connect inference API to publish events

## Configuration

Environment variables (future):
```bash
# Email Provider (SendGrid)
SENDGRID_API_KEY=your_key
SENDGRID_FROM_EMAIL=alerts@trading.com

# SMS Provider (Twilio)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=+1234567890

# Push Notifications (Firebase)
FCM_SERVER_KEY=your_key

# Message Queue
REDIS_URL=redis://localhost:6379
QUEUE_NAME=trading_recommendations
```

## Future Enhancements

- [ ] Integrate SendGrid for email
- [ ] Integrate Twilio for SMS
- [ ] Integrate Firebase Cloud Messaging for push
- [ ] Implement Redis/RabbitMQ consumer
- [ ] Add user notification preferences
- [ ] Add rate limiting (max 10 alerts/hour per user)
- [ ] Add notification templates (Jinja2)
- [ ] Add delivery tracking and analytics
- [ ] Add retry logic with exponential backoff
- [ ] Add notification history database
- [ ] Add webhook support for custom integrations
- [ ] Add notification scheduling (quiet hours)
- [ ] Add alert grouping/batching

## Development Notes

This service is designed to be extended with real notification providers. The current implementation provides:
1. Clean interface (`NotificationAdapter`)
2. Business logic (`AlertRuleEngine`)
3. Async-ready architecture
4. Logging for testing

When ready to integrate real providers:
1. Extend `ProductionNotificationAdapter`
2. Add provider credentials to environment
3. Implement actual API calls
4. Add error handling and retries
5. Enable in docker-compose

## Security Considerations

When implementing production notifications:
- Store API keys in secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Use environment variables, never commit credentials
- Implement rate limiting to prevent abuse
- Validate recipient addresses/numbers
- Add opt-out mechanism for users
- Comply with CAN-SPAM, GDPR regulations
- Encrypt sensitive data in transit and at rest
