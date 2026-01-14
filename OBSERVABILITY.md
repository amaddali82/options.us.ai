# Observability Features

## Overview

The Trading Intelligence Platform now includes comprehensive observability features for monitoring application health, performance, and usage patterns.

## Backend Observability (FastAPI)

### 1. Request Logging Middleware

All HTTP requests are automatically logged with:
- **Method**: GET, POST, etc.
- **Path**: Endpoint path
- **Status Code**: HTTP response status
- **Latency**: Request duration in seconds

**Example log output:**
```
2026-01-14 10:23:45 - main - INFO - GET /recommendations - Status: 200 - Latency: 0.342s
2026-01-14 10:23:46 - main - INFO - GET /recommendations/abc-123 - Status: 200 - Latency: 0.156s
2026-01-14 10:23:47 - main - INFO - POST /seed - Status: 200 - Latency: 2.451s
```

### 2. Prometheus Metrics

Access metrics at: **http://localhost:8000/metrics**

#### Available Metrics

**Request Metrics:**
- `http_requests_total{method, endpoint, status}` - Counter of total HTTP requests
- `http_request_duration_seconds{method, endpoint}` - Histogram of request latency
- `http_requests_active` - Gauge of currently active requests

**Database Metrics:**
- `db_query_duration_seconds{endpoint}` - Histogram of database query duration

**Example metrics output:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/recommendations",status="200"} 342.0

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/recommendations",le="0.1"} 12.0
http_request_duration_seconds_bucket{method="GET",endpoint="/recommendations",le="0.5"} 285.0
http_request_duration_seconds_sum{method="GET",endpoint="/recommendations"} 98.45
http_request_duration_seconds_count{method="GET",endpoint="/recommendations"} 342.0

# HELP db_query_duration_seconds Database query duration
# TYPE db_query_duration_seconds histogram
db_query_duration_seconds_bucket{endpoint="/recommendations",le="0.1"} 180.0
db_query_duration_seconds_sum{endpoint="/recommendations"} 52.3
```

### 3. Database Query Timing

The `/recommendations` endpoint now logs detailed query performance:

**Example log output:**
```
2026-01-14 10:23:45 - main - INFO - DB query for recommendations list took 0.234s (returned 150 rows)
2026-01-14 10:24:12 - main - INFO - DB query for recommendations list took 0.089s (returned 25 rows)
```

## Frontend Observability (React UI)

### Health Status Indicator

A real-time health status indicator appears in the top-right corner of the dashboard:

**Features:**
- **Green pulsing dot** 🟢 - Backend healthy and responsive
- **Yellow dot** 🟡 - Backend degraded (database issues)
- **Red dot** 🔴 - Backend offline or unreachable
- **Auto-refresh**: Checks health every 30 seconds
- **Hover tooltip**: Shows detailed status information

**Status Details (on hover):**
- Backend status (ok/degraded/error)
- Database connection status
- Last check timestamp

**Visual Location:**
```
┌─────────────────────────────────────────────────┐
│ Trading Recommendations           250 recs  🟢 │
│                                            Online│
├─────────────────────────────────────────────────┤
│ Filters: [Horizon] [Confidence] [Symbol]        │
└─────────────────────────────────────────────────┘
```

## Monitoring Setup

### Prometheus Integration

To scrape metrics with Prometheus, add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'trading_api'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Grafana Dashboards

Create dashboards using these queries:

**Request Rate:**
```promql
rate(http_requests_total[5m])
```

**Average Latency:**
```promql
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

**95th Percentile Latency:**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Active Requests:**
```promql
http_requests_active
```

**Database Query Duration (P95):**
```promql
histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m]))
```

## Docker Compose Integration

The observability features work automatically with the Docker setup. Metrics are exposed on the API container and can be accessed from the host.

To view metrics from Docker:
```bash
curl http://localhost:8000/metrics
```

## Development Usage

### View Logs
```bash
# Local development
cd services/inference_api
python -m uvicorn main:app --reload

# Docker
make logs-api
```

### Test Health Endpoint
```bash
curl http://localhost:8000/health
# Response: {"status":"ok","timestamp":"2026-01-14T10:23:45.123Z","database":"connected"}
```

### View Metrics
```bash
curl http://localhost:8000/metrics
# Returns Prometheus-format metrics
```

## Alert Rules (Example)

Create alerting rules in Prometheus:

```yaml
groups:
  - name: trading_api_alerts
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency detected"
          description: "95th percentile latency is {{ $value }}s"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} req/s"

      - alert: APIDown
        expr: up{job="trading_api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Trading API is down"
```

## Performance Baseline

Expected performance metrics:

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| Request latency (p95) | < 500ms | < 1s | > 2s |
| DB query time (p95) | < 200ms | < 500ms | > 1s |
| Error rate | < 0.1% | < 1% | > 5% |
| Uptime | 99.9% | 99% | < 99% |

## Troubleshooting

### High Latency
1. Check DB query duration in logs
2. Review slow queries in PostgreSQL
3. Check for missing indexes
4. Monitor database connection pool

### Health Check Failing
1. Verify database connectivity: `make logs-db`
2. Check PostgreSQL is running: `docker ps`
3. Test DB connection: `docker-compose exec postgres pg_isready`
4. Review API logs: `make logs-api`

### Metrics Not Updating
1. Verify `/metrics` endpoint is accessible
2. Check Prometheus scrape configuration
3. Review Prometheus targets page
4. Verify network connectivity

## Future Enhancements

Planned observability improvements:
- [ ] Distributed tracing with OpenTelemetry
- [ ] Structured JSON logging
- [ ] Custom business metrics (recommendations generated, filters used)
- [ ] Real-time alerting integration (PagerDuty/Slack)
- [ ] Performance profiling endpoints
- [ ] Query plan analysis for slow queries
- [ ] Client-side performance metrics (React)
- [ ] Error tracking integration (Sentry)

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/docs/)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [prometheus_client Python](https://github.com/prometheus/client_python)
