.PHONY: help up down restart logs logs-api logs-ui logs-db build ps clean seed test

# Default target
help:
	@echo "Trading Intelligence Platform - Docker Management"
	@echo ""
	@echo "Available targets:"
	@echo "  make up          - Start all services (postgres, inference_api, ui)"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - Show logs from all services"
	@echo "  make logs-api    - Show logs from inference_api only"
	@echo "  make logs-ui     - Show logs from ui only"
	@echo "  make logs-db     - Show logs from postgres only"
	@echo "  make build       - Rebuild all Docker images"
	@echo "  make ps          - Show running containers"
	@echo "  make clean       - Remove all containers, volumes, and images"
	@echo "  make seed        - Seed database with sample data"
	@echo "  make test        - Run tests in inference_api"
	@echo ""

# Start all services
up:
	@echo "🚀 Starting all services..."
	cd infra && docker-compose up -d
	@echo "✅ Services started!"
	@echo "   - PostgreSQL: localhost:5432"
	@echo "   - Inference API: http://localhost:8000"
	@echo "   - UI: http://localhost:3000"
	@echo ""
	@echo "Run 'make logs' to view logs"

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	cd infra && docker-compose down
	@echo "✅ Services stopped!"

# Restart all services
restart:
	@echo "🔄 Restarting all services..."
	cd infra && docker-compose restart
	@echo "✅ Services restarted!"

# Show logs from all services
logs:
	cd infra && docker-compose logs -f

# Show logs from inference_api
logs-api:
	cd infra && docker-compose logs -f inference_api

# Show logs from ui
logs-ui:
	cd infra && docker-compose logs -f ui

# Show logs from postgres
logs-db:
	cd infra && docker-compose logs -f postgres

# Rebuild all images
build:
	@echo "🔨 Building Docker images..."
	cd infra && docker-compose build --no-cache
	@echo "✅ Build complete!"

# Show running containers
ps:
	cd infra && docker-compose ps

# Clean up everything (containers, volumes, images)
clean:
	@echo "🧹 Cleaning up Docker resources..."
	cd infra && docker-compose down -v --rmi all
	@echo "✅ Cleanup complete!"

# Seed database with sample data
seed:
	@echo "🌱 Seeding database with sample recommendations..."
	@echo "This will generate ~50 sample recommendations for 10 symbols"
	cd infra && docker-compose exec inference_api python -c "import asyncio; from reco_generator import RecoGenerator; asyncio.run(RecoGenerator().generate_batch(['AAPL','TSLA','NVDA','MSFT','GOOGL','AMZN','META','AMD','NFLX','SPY'], limit=5))"
	@echo "✅ Database seeded!"

# Run tests
test:
	@echo "🧪 Running tests..."
	cd infra && docker-compose exec inference_api python -m pytest tests/ -v
	@echo "✅ Tests complete!"
