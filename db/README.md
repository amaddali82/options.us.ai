# Database Migrations

PostgreSQL migration system for the Trading Intelligence platform.

## Structure

```
db/
├── migrations/           # SQL migration files (timestamped)
│   ├── 001_create_recommendations_tables.sql
│   └── 002_add_sample_data.sql
├── migrate.py           # Migration runner script
└── README.md           # This file
```

## Schema Overview

### Tables

#### 1. `recommendations` (Main)
Stores trading recommendations with overall confidence and metadata.

**Columns:**
- `reco_id`: UUID primary key
- `asof`: Timestamp when recommendation was generated
- `symbol`: Trading symbol (e.g., AAPL, TSLA)
- `horizon`: Trading timeframe (e.g., 'day', 'swing', '1-2 months')
- `side`: BUY | SELL | HOLD
- `entry_price`: Recommended entry price
- `confidence_overall`: Overall confidence [0.0, 1.0]
- `expected_move_pct`: Expected percentage move
- `rationale`: JSONB with reasoning, catalysts, risks, indicators
- `quality`: JSONB with quality metrics, analyst info

**Indexes:**
- `(symbol, asof DESC)` - Primary query pattern
- `(horizon, confidence_overall DESC)` - Filter by timeframe
- `(side)` - Filter by direction
- `(asof DESC)` - Time-based queries

#### 2. `reco_targets`
Multi-target ladder strategy (1-5 targets per recommendation).

**Columns:**
- `reco_id`: FK to recommendations
- `ordinal`: Target sequence number (1, 2, 3...)
- `name`: Target label (e.g., 'Target 1', 'First Resistance')
- `target_type`: 'price', 'percentage', 'technical'
- `value`: Target price or value
- `confidence`: Confidence [0.0, 1.0]
- `eta_minutes`: Estimated time to achieve (nullable)
- `notes`: Additional notes (nullable)

**Indexes:**
- `(reco_id)` - FK lookup
- `(reco_id, ordinal)` - Composite for ordering

#### 3. `option_ideas`
Optional options strategy (one per recommendation, if present).

**Columns:**
- `reco_id`: FK to recommendations (unique)
- `option_type`: CALL | PUT
- `expiry`: Option expiration date (must be future)
- `strike`: Strike price
- `option_entry_price`: Entry premium
- `greeks`: JSONB with delta, gamma, theta, vega, rho
- `iv`: JSONB with implied volatility details
- `notes`: Additional notes

**Constraints:**
- Unique on `reco_id` (one option per recommendation)
- Check: `expiry > CURRENT_DATE`

#### 4. `option_targets`
Premium targets for options (1-3 targets per option).

**Columns:**
- `reco_id`: FK to option_ideas
- `ordinal`: Target sequence number
- `name`: Target label
- `value`: Premium target
- `confidence`: Confidence [0.0, 1.0]
- `eta_minutes`: Estimated time to achieve (nullable)
- `notes`: Additional notes (nullable)

**Indexes:**
- `(reco_id)` - FK lookup
- `(reco_id, ordinal)` - Composite for ordering

## Usage

### Running Migrations

**Option 1: From command line**
```bash
# Set database URL
set DATABASE_URL=postgresql://trading_user:trading_pass@localhost:5432/trading_db

# Run all pending migrations
python db/migrate.py

# Check migration status
python db/migrate.py --status
```

**Option 2: From Python code**
```python
from db.migrate import MigrationManager

# Initialize manager
manager = MigrationManager(
    database_url="postgresql://user:pass@host:5432/dbname"
)

# Run migrations
successful, failed = manager.run_migrations()

# Check status
status = manager.get_migration_status()
print(f"Applied: {status['applied_count']}")
print(f"Pending: {status['pending_count']}")
```

**Option 3: On application startup**
```python
# In main.py or startup script
import os
from db.migrate import MigrationManager

def run_startup_migrations():
    database_url = os.getenv("DATABASE_URL")
    manager = MigrationManager(database_url)
    successful, failed = manager.run_migrations()
    if failed > 0:
        raise Exception("Database migrations failed!")
    return successful

# Run before starting app
run_startup_migrations()
```

### Creating New Migrations

1. Create a new SQL file in `db/migrations/` with naming pattern:
   ```
   {number}_{descriptive_name}.sql
   ```
   Example: `003_add_user_tracking.sql`

2. Add migration header comment:
   ```sql
   -- Migration: 003_add_user_tracking
   -- Description: Add user tracking and audit tables
   -- Created: 2026-01-14
   ```

3. Write your SQL statements:
   ```sql
   CREATE TABLE user_actions (
       action_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       user_id UUID NOT NULL,
       action_type TEXT NOT NULL,
       created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
   );
   ```

4. Run migrations:
   ```bash
   python db/migrate.py
   ```

## Migration Tracking

Migrations are tracked in the `schema_migrations` table:

```sql
SELECT * FROM schema_migrations ORDER BY applied_at DESC;
```

**Columns:**
- `migration_id`: Auto-increment ID
- `version`: Migration filename (e.g., '001_create_tables')
- `name`: Descriptive name from migration file
- `applied_at`: Timestamp when applied
- `checksum`: Reserved for future use
- `execution_time_ms`: How long migration took

## Sample Queries

### Get all recommendations for a symbol
```sql
SELECT r.*, 
       json_agg(json_build_object(
           'ordinal', t.ordinal,
           'value', t.value,
           'confidence', t.confidence
       ) ORDER BY t.ordinal) as targets
FROM recommendations r
LEFT JOIN reco_targets t ON r.reco_id = t.reco_id
WHERE r.symbol = 'AAPL'
GROUP BY r.reco_id
ORDER BY r.asof DESC;
```

### Get recommendations with options
```sql
SELECT r.symbol, r.side, r.confidence_overall,
       o.option_type, o.strike, o.expiry,
       o.greeks->>'delta' as delta
FROM recommendations r
INNER JOIN option_ideas o ON r.reco_id = o.reco_id
WHERE r.asof > NOW() - INTERVAL '7 days'
ORDER BY r.confidence_overall DESC;
```

### Get high-confidence BUY recommendations
```sql
SELECT symbol, entry_price, confidence_overall, 
       rationale->>'reasoning' as reasoning
FROM recommendations
WHERE side = 'BUY' 
  AND confidence_overall >= 0.80
  AND horizon = '1-2 months'
ORDER BY confidence_overall DESC, asof DESC
LIMIT 10;
```

### Get complete recommendation with all targets and options
```sql
WITH targets AS (
    SELECT reco_id, 
           json_agg(json_build_object(
               'ordinal', ordinal,
               'name', name,
               'value', value,
               'confidence', confidence
           ) ORDER BY ordinal) as target_list
    FROM reco_targets
    GROUP BY reco_id
),
option_targets AS (
    SELECT reco_id,
           json_agg(json_build_object(
               'ordinal', ordinal,
               'value', value,
               'confidence', confidence
           ) ORDER BY ordinal) as option_target_list
    FROM option_targets
    GROUP BY reco_id
)
SELECT r.*,
       t.target_list,
       o.option_type, o.strike, o.expiry, o.option_entry_price, o.greeks,
       ot.option_target_list
FROM recommendations r
LEFT JOIN targets t ON r.reco_id = t.reco_id
LEFT JOIN option_ideas o ON r.reco_id = o.reco_id
LEFT JOIN option_targets ot ON r.reco_id = ot.reco_id
WHERE r.symbol = 'NVDA'
ORDER BY r.asof DESC
LIMIT 1;
```

## Docker Integration

The migration system runs automatically when the Docker container starts.

### Update docker-compose.yml

The inference_api service will run migrations on startup:

```yaml
inference_api:
  ...
  environment:
    DATABASE_URL: postgresql://user:pass@postgres:5432/trading_db
  depends_on:
    postgres:
      condition: service_healthy
```

### Startup sequence

1. PostgreSQL container starts and becomes healthy
2. Inference API container starts
3. Migration script runs automatically
4. API server starts after migrations complete

## Best Practices

1. **Never modify applied migrations** - Create a new migration instead
2. **Test migrations locally first** - Before deploying
3. **Keep migrations focused** - One logical change per migration
4. **Use transactions** - Migrations run in a single transaction
5. **Add comments** - Explain complex changes
6. **Version control** - Commit migrations with code changes
7. **Backup before production** - Always backup before applying migrations

## Troubleshooting

### Migration fails
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Check migration status
python db/migrate.py --status

# Connect to database manually
docker exec -it trading_postgres psql -U trading_user -d trading_db

# Check applied migrations
SELECT * FROM schema_migrations ORDER BY applied_at DESC;
```

### Reset database (development only)
```bash
# Stop containers
docker-compose down -v

# Start fresh
docker-compose up -d

# Migrations will run automatically
```

### Manual migration rollback
Migrations don't have automatic rollback. To rollback:

1. Manually write inverse SQL
2. Delete the migration record:
   ```sql
   DELETE FROM schema_migrations WHERE version = '003_migration_name';
   ```
3. Run the rollback SQL

## Security Notes

- Database credentials should be in environment variables
- Use `.env` files for local development (not committed)
- Use secrets management in production
- Restrict database user permissions appropriately
- Enable SSL for production database connections

## Performance Considerations

- Indexes are created for common query patterns
- JSONB columns for flexible metadata storage
- Cascading deletes for referential integrity
- Timestamps with timezone for accurate tracking
- Numeric types for precise financial calculations

## Future Enhancements

- [ ] Add migration rollback support
- [ ] Add migration checksum validation
- [ ] Add dry-run mode
- [ ] Add migration dependencies
- [ ] Add automatic backup before migration
- [ ] Add migration locking for concurrent deploys
