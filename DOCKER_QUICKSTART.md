# Trading Intelligence Platform - Docker Quick Start

## 🚀 Getting Started in 3 Steps

### 1. Configure Environment
```bash
cd infra
cp .env.example .env
# Edit .env and set secure passwords
```

### 2. Start All Services
```bash
make up
```

This will start:
- PostgreSQL database on port 5432
- FastAPI backend on port 8000
- React UI on port 3000
- Notification service (optional, disabled by default)

### 3. Access the Application
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Notification Service** (if enabled): http://localhost:8001/docs

## 📋 Common Commands

```bash
make help       # Show all available commands
make up         # Start all services
make down       # Stop all services
make logs       # View all logs
make logs-api   # View API logs only
make seed       # Add sample data
make test       # Run tests
make ps         # Show service status
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Browser UI    │  ← React + Vite + Tailwind
│  (Port 3000)    │  ← Nginx (production)
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Inference API  │  ← FastAPI + Uvicorn
│  (Port 8000)    │  ← Auto-migrations on startup
└────────┬────────┘
         │ SQL
         ▼
┌─────────────────┐
│   PostgreSQL    │  ← Database
│  (Port 5432)    │  ← Persistent storage
└─────────────────┘
```

## 📦 What's Included

### Services

1. **PostgreSQL 16**
   - Alpine Linux base
   - Persistent volume storage
   - Health checks enabled
   - Init scripts support

2. **Inference API**
   - Python 3.11 slim
   - Automatic migrations on startup
   - FastAPI + Uvicorn
   - Health endpoint at `/health`
   - Shared utilities included

3. **UI Frontend**
   - Multi-stage Docker build
   - Vite build → Nginx serve
   - Gzip compression
   - SPA routing support
   - Static asset caching

### Files Created

```
options.usa.ai/
├── Makefile                         # Convenience commands
├── infra/
│   ├── docker-compose.yml          # Service orchestration
│   ├── .env                        # Environment variables
│   ├── .env.example                # Environment template
│   └── README.md                   # Detailed documentation
├── services/
│   ├── inference_api/
│   │   └── Dockerfile              # API container image
│   └── ui/
│       ├── Dockerfile              # UI multi-stage build
│       └── nginx.conf              # Nginx configuration
└── scripts/
    └── seed_db.py                  # Database seeding script
```

## 🔧 Configuration

### Environment Variables

Key variables in `infra/.env`:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://user:pass@localhost:5432/trading_db

# API
API_PORT=8000
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:3000

# UI
UI_PORT=3000
VITE_API_BASE_URL=http://localhost:8000
```

## 🧪 Testing the Setup

### 1. Check Service Health
```bash
make ps
```

Should show all services as "Up (healthy)"

### 2. Test API
```bash
curl http://localhost:8000/health
# Response: {"status":"healthy"}

curl http://localhost:8000/docs
# Opens API documentation
```

### 3. Test UI
```bash
curl http://localhost:3000/health
# Response: healthy

open http://localhost:3000
# Opens dashboard in browser
```

### 4. Seed Sample Data
```bash
make seed
```

Generates 50 sample recommendations (5 per symbol × 10 symbols)

### 5. View Logs
```bash
make logs-api     # Watch API logs
make logs-db      # Watch database logs
make logs         # Watch all logs
```

## 🔍 Troubleshooting

### Services Won't Start

Check logs for errors:
```bash
make logs
```

Common issues:
- Port already in use (change in `.env`)
- Invalid DATABASE_URL
- Missing environment variables

### Database Connection Failed

Wait for postgres to become healthy (takes 10-15s):
```bash
make ps
```

Test connection:
```bash
docker-compose exec postgres pg_isready -U trading_user
```

### API Health Check Failing

1. Check migrations succeeded:
   ```bash
   make logs-api | grep migration
   ```

2. Verify database is healthy:
   ```bash
   make ps
   ```

3. Check environment variables:
   ```bash
   docker-compose exec inference_api env | grep DATABASE
   ```

### UI Shows Blank Page

1. Check browser console for errors
2. Verify API is accessible:
   ```bash
   curl http://localhost:8000/health
   ```
3. Check VITE_API_BASE_URL in `.env`

## 📊 Monitoring

### View Resource Usage
```bash
docker stats
```

### Check Container Health
```bash
docker-compose ps
docker inspect trading_postgres | grep -A 5 Health
```

### Database Metrics
```bash
docker-compose exec postgres psql -U trading_user -d trading_db -c "\
  SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size \
  FROM pg_tables WHERE schemaname = 'public';"
```

## 🗄️ Database Management

### Backup
```bash
docker-compose exec postgres pg_dump -U trading_user trading_db > backup_$(date +%Y%m%d).sql
```

### Restore
```bash
cat backup_20260114.sql | docker-compose exec -T postgres psql -U trading_user trading_db
```

### Reset Database
```bash
make down
docker volume rm infra_postgres_data
make up
make seed  # Re-add sample data
```

## 🚨 Production Checklist

Before deploying to production:

- [ ] Change all default passwords in `.env`
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure SSL/TLS certificates
- [ ] Restrict `CORS_ORIGINS` to your domain
- [ ] Set up automated backups
- [ ] Enable monitoring and alerting
- [ ] Configure log aggregation
- [ ] Review and harden security settings
- [ ] Set up CI/CD pipeline
- [ ] Test disaster recovery procedures

## 📚 Additional Documentation

- [Infrastructure README](infra/README.md) - Detailed Docker setup guide
- [API Guide](services/inference_api/API_GUIDE.md) - API endpoints and usage
- [UI README](services/ui/README.md) - Frontend architecture

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `make logs`
2. Verify environment: `cat infra/.env`
3. Check service status: `make ps`
4. Review documentation in `infra/README.md`
5. Test individual components:
   - Database: `docker-compose exec postgres pg_isready`
   - API: `curl http://localhost:8000/health`
   - UI: `curl http://localhost:3000/health`

## 🎯 Next Steps

After successful setup:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **View the Dashboard**: Open http://localhost:3000
3. **Add Data**: Run `make seed` to populate sample recommendations
4. **Run Tests**: Execute `make test` to verify functionality
5. **Monitor Logs**: Use `make logs` to watch real-time activity

---

**Ready to start?**

```bash
make up
```

Your trading intelligence platform will be running in under 2 minutes! 🎉
