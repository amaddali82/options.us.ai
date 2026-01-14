# Trading Intelligence System

A recommendations-only trading intelligence system built with a modern monorepo architecture.

## 🏗️ Architecture

```
options.usa.ai/
├── services/
│   ├── inference_api/       # Python 3.11 + FastAPI backend
│   └── ui/                  # React + Vite + Tailwind frontend
├── shared/
│   └── schemas/             # Shared data schemas
├── infra/
│   ├── docker-compose.yml   # Docker orchestration
│   └── init.sql             # Database initialization
├── .env.example             # Environment variables template
└── README.md
```

## 🚀 Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Pydantic
- **Frontend**: React 18, Vite, Tailwind CSS, Axios
- **Database**: PostgreSQL 16
- **Infrastructure**: Docker, Docker Compose

## 📋 Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine + Docker Compose (Linux)
- Git

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd options.usa.ai
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env with your preferred values (optional - defaults work for local dev)
```

### 3. Start the Services

```bash
# Navigate to the infra directory
cd infra

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

### 4. Verify Services

Once started, the following services will be available:

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

## 🔧 Environment Variables

### Core Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `development` |
| `POSTGRES_USER` | PostgreSQL username | `trading_user` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `trading_pass` |
| `POSTGRES_DB` | PostgreSQL database name | `trading_db` |
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:5173` |

### Frontend Configuration (services/ui/.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-14T12:00:00.000000",
  "service": "inference_api",
  "version": "1.0.0"
}
```

### Get Recommendation
```bash
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "timeframe": "1d",
    "indicators": ["RSI", "MACD"]
  }'
```

Response:
```json
{
  "symbol": "AAPL",
  "recommendation": "BUY",
  "confidence": 0.85,
  "reasoning": "Strong upward trend with positive RSI and MACD crossover",
  "timestamp": "2026-01-14T12:00:00.000000"
}
```

### API Status
```bash
curl http://localhost:8000/api/v1/status
```

Response:
```json
{
  "api_version": "1.0.0",
  "database_connected": true,
  "environment": "development",
  "features": {
    "recommendations": true,
    "real_time_data": false,
    "backtesting": false
  }
}
```

## 🧪 Testing API with curl

### Example 1: Get recommendation for TSLA
```bash
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{"symbol": "TSLA", "timeframe": "1h"}'
```

### Example 2: Get recommendation with specific indicators
```bash
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "MSFT",
    "timeframe": "1d",
    "indicators": ["RSI", "MACD", "BOLLINGER_BANDS"]
  }'
```

### Example 3: Check API status
```bash
curl http://localhost:8000/api/v1/status | python -m json.tool
```

## 🔨 Development

### Backend Development

```bash
# Navigate to backend directory
cd services/inference_api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally (without Docker)
python main.py
```

### Frontend Development

```bash
# Navigate to frontend directory
cd services/ui

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Database Access

```bash
# Connect to PostgreSQL container
docker exec -it trading_postgres psql -U trading_user -d trading_db

# Run SQL queries
SELECT * FROM recommendations;
```

## 📂 Project Structure Details

### Backend (services/inference_api/)
- `main.py` - FastAPI application with endpoints
- `database.py` - Database connection and session management
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `.env.example` - Environment variables template

### Frontend (services/ui/)
- `src/App.jsx` - Main React component
- `src/main.jsx` - Application entry point
- `vite.config.js` - Vite configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `package.json` - Node.js dependencies
- `Dockerfile` - Container configuration

### Shared (shared/schemas/)
- `trading_schemas.py` - Pydantic models for data validation
- Common schemas used across services

### Infrastructure (infra/)
- `docker-compose.yml` - Multi-container orchestration
- `init.sql` - Database initialization script

## 🐛 Troubleshooting

### Services won't start
```bash
# Check if ports are already in use
netstat -an | findstr "5432 8000 5173"

# Check Docker logs
cd infra
docker-compose logs
```

### Database connection issues
```bash
# Verify PostgreSQL is running
docker ps | findstr postgres

# Check database logs
docker-compose logs postgres
```

### Frontend can't connect to API
1. Verify API is running: http://localhost:8000/health
2. Check browser console for CORS errors
3. Ensure `.env` file has correct `VITE_API_URL`

## 🚢 Production Deployment

For production deployment:

1. Update environment variables with secure credentials
2. Configure proper CORS origins
3. Set up SSL/TLS certificates
4. Use production-grade database hosting
5. Implement proper logging and monitoring
6. Add authentication and authorization
7. Configure rate limiting
8. Set up CI/CD pipeline

## 📝 Next Steps

- [ ] Implement actual trading intelligence algorithms
- [ ] Add user authentication and authorization
- [ ] Implement real-time data streaming
- [ ] Add backtesting capabilities
- [ ] Create comprehensive test suite
- [ ] Set up monitoring and alerting
- [ ] Add data visualization charts
- [ ] Implement caching layer (Redis)

## 📄 License

MIT License - feel free to use this project as a starting point for your own trading systems.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
