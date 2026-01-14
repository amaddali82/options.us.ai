FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY services/inference_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared ./shared

# Copy application code
COPY services/inference_api .
COPY db ./db

# Create startup script that runs migrations then starts server
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🗄️  Running database migrations..."\n\
python run_migrations.py\n\
if [ $? -ne 0 ]; then\n\
  echo "❌ Migration failed, exiting..."\n\
  exit 1\n\
fi\n\
echo "✅ Migrations complete"\n\
echo "🚀 Starting FastAPI server..."\n\
exec uvicorn main:app --host 0.0.0.0 --port 8000' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application with migrations
CMD ["/app/entrypoint.sh"]
