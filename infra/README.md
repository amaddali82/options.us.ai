# Docker Deployment Guide

## Overview

This directory contains the Docker configuration for running the Trading Intelligence Platform with three services:

- **postgres**: PostgreSQL 16 database
- **inference_api**: FastAPI backend with uvicorn
- **ui**: React frontend built with Vite and served by nginx

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Make (optional, for convenience commands)

### 1. Configure Environment

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` and set secure passwords:
- `POSTGRES_PASSWORD`: Strong database password
- `DATABASE_URL`: Update with your password

### 2. Start Services

Using Make (recommended):
```bash
make up
```

Or using Docker Compose directly:
```bash
cd infra
docker-compose up -d
```

### 3. Verify Services

Check that all services are healthy:
```bash
make ps
# or
cd infra && docker-compose ps
```

Expected output:
```
NAME                      STATUS              PORTS
trading_postgres          Up (healthy)        0.0.0.0:5432->5432/tcp
trading_inference_api     Up (healthy)        0.0.0.0:8000->8000/tcp
trading_ui                Up (healthy)        0.0.0.0:3000->80/tcp
```

### 4. Access Services

- **UI Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

## Makefile Commands

The root `Makefile` provides convenient shortcuts:

```bash
make help         # Show all available commands
make up           # Start all services
make down         # Stop all services
make restart      # Restart all services
make logs         # Stream logs from all services
make logs-api     # Stream logs from API only
make logs-ui      # Stream logs from UI only
make logs-db      # Stream logs from database only
make build        # Rebuild all Docker images
make ps           # Show container status
make clean        # Remove all containers, volumes, and images
make seed         # Seed database with sample data
make test         # Run API tests
```

## Architecture

### Service Details

#### PostgreSQL Database
- **Image**: postgres:16-alpine
- **Port**: 5432
- **Volumes**: 
  - `postgres_data`: Persistent database storage
  - `../db/init`: Initialization scripts
- **Health Check**: `pg_isready` every 10s

#### Inference API
- **Build Context**: Root directory (to access shared/)
- **Port**: 8000
- **Startup Process**:
  1. Run database migrations (`run_migrations.py`)
  2. Start uvicorn server
- **Health Check**: HTTP GET `/health` every 30s
- **Dependencies**: Waits for postgres to be healthy

#### UI Frontend
- **Build**: Multi-stage Docker build
  - Stage 1: Node.js - Build React app with Vite
  - Stage 2: Nginx - Serve static files
- **Port**: 80 (mapped to 3000 on host)
- **Health Check**: HTTP GET `/health` every 30s
- **Features**:
  - Gzip compression
  - Static asset caching (1 year)
  - SPA fallback routing

## Environment Variables

### Database
- `POSTGRES_USER`: Database username (default: `trading_user`)
- `POSTGRES_PASSWORD`: Database password (default: `trading_pass`)
- `POSTGRES_DB`: Database name (default: `trading_db`)
- `POSTGRES_PORT`: Host port mapping (default: `5432`)

### API
- `DATABASE_URL`: Full PostgreSQL connection string
- `API_PORT`: Host port mapping (default: `8000`)
- `ENVIRONMENT`: Runtime environment (`production` or `development`)
- `LOG_LEVEL`: Logging level (default: `info`)
- `CORS_ORIGINS`: Comma-separated allowed origins

### UI
- `UI_PORT`: Host port mapping (default: `3000`)
- `VITE_API_BASE_URL`: Backend API URL (default: `http://localhost:8000`)

## Migrations

The API service automatically runs migrations on startup using `run_migrations.py`. The migration process:

1. Connects to PostgreSQL database
2. Reads migration files from `db/migrations/`
3. Applies pending migrations in order
4. Logs success/failure
5. Exits with error if migrations fail (prevents API startup)

## Development vs Production

### Development Mode
For local development with hot reloading:

```bash
# Start only postgres
docker-compose up postgres -d

# Run API locally
cd services/inference_api
python -m uvicorn main:app --reload

# Run UI locally
cd services/ui
npm run dev
```

### Production Mode
The default Docker Compose setup is optimized for production:
- UI is built and served by nginx (not dev server)
- No volume mounts (containers are self-contained)
- Health checks enabled
- Automatic restarts configured

## Troubleshooting

### View Logs
```bash
make logs          # All services
make logs-api      # API only
make logs-db       # Database only
```

### Reset Database
```bash
make down          # Stop services
docker volume rm infra_postgres_data  # Delete database
make up            # Restart (fresh database)
```

### Rebuild Images
If code changes aren't reflected:
```bash
make build         # Rebuild all images
make up            # Restart services
```

### Check Health Status
```bash
# API health
curl http://localhost:8000/health

# UI health
curl http://localhost:3000/health

# Database connection
docker-compose exec postgres pg_isready -U trading_user
```

### Common Issues

**API won't start**:
- Check logs: `make logs-api`
- Verify DATABASE_URL is correct
- Ensure postgres is healthy: `make ps`

**UI shows blank page**:
- Check browser console for errors
- Verify VITE_API_BASE_URL is set correctly
- Check API is accessible: `curl http://localhost:8000/health`

**Database connection refused**:
- Wait for health check: postgres takes 10-15s to start
- Check port 5432 isn't already in use
- Verify credentials in .env match DATABASE_URL

## Data Persistence

- **Database**: Data persists in the `postgres_data` volume
- **Logs**: Container logs are ephemeral (use `make logs` to view)
- **Volumes**: Use `make clean` to remove all volumes (WARNING: deletes all data)

## Security Notes

1. **Change default passwords** in production
2. **Use secrets management** for sensitive values
3. **Enable SSL/TLS** for production deployments
4. **Restrict CORS_ORIGINS** to known domains
5. **Use non-root database user** with minimal privileges

## Scaling

To scale services horizontally:

```bash
docker-compose up -d --scale inference_api=3
```

For production, consider:
- Load balancer in front of API instances
- Read replicas for PostgreSQL
- Redis for caching
- Message queue for async tasks

## Backup & Restore

### Backup Database
```bash
docker-compose exec postgres pg_dump -U trading_user trading_db > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker-compose exec -T postgres psql -U trading_user trading_db
```

## Monitoring

Add monitoring services to `docker-compose.yml`:
- Prometheus (metrics collection)
- Grafana (visualization)
- Loki (log aggregation)

## Next Steps

1. Set up CI/CD pipeline for automated deployments
2. Configure reverse proxy (nginx/traefik) with SSL
3. Add application monitoring and alerting
4. Implement automated backups
5. Set up log aggregation and analysis
