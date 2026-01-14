"""
Database Migration System
Manages and applies SQL migrations to PostgreSQL database
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
import logging
from datetime import datetime
from typing import List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self, database_url: str, migrations_dir: str = None):
        """
        Initialize migration manager
        
        Args:
            database_url: PostgreSQL connection URL
            migrations_dir: Path to migrations directory
        """
        self.database_url = database_url
        
        # Default migrations directory relative to this file
        if migrations_dir is None:
            self.migrations_dir = Path(__file__).parent / 'migrations'
        else:
            self.migrations_dir = Path(migrations_dir)
            
        logger.info(f"Migrations directory: {self.migrations_dir}")
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(self.database_url)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def create_migrations_table(self):
        """Create migrations tracking table if it doesn't exist"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        migration_id SERIAL PRIMARY KEY,
                        version VARCHAR(255) NOT NULL UNIQUE,
                        name VARCHAR(500) NOT NULL,
                        applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        checksum VARCHAR(64),
                        execution_time_ms INTEGER
                    )
                """)
                
                # Create index for quick lookups
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_schema_migrations_version 
                    ON schema_migrations(version)
                """)
                
                conn.commit()
                logger.info("Migrations tracking table ready")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create migrations table: {e}")
            raise
        finally:
            conn.close()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of already applied migration versions"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT version FROM schema_migrations ORDER BY version")
                return [row[0] for row in cur.fetchall()]
        except psycopg2.errors.UndefinedTable:
            return []
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            raise
        finally:
            conn.close()
    
    def get_pending_migrations(self) -> List[Tuple[str, Path]]:
        """Get list of pending migrations to apply"""
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory not found: {self.migrations_dir}")
            return []
        
        # Get all .sql files
        migration_files = sorted(self.migrations_dir.glob('*.sql'))
        
        # Get applied migrations
        applied = set(self.get_applied_migrations())
        
        # Filter to pending migrations
        pending = []
        for filepath in migration_files:
            version = filepath.stem  # filename without extension
            if version not in applied:
                pending.append((version, filepath))
        
        return pending
    
    def apply_migration(self, version: str, filepath: Path) -> bool:
        """
        Apply a single migration
        
        Args:
            version: Migration version (filename stem)
            filepath: Path to migration SQL file
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Applying migration: {version}")
        
        # Read migration file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                sql = f.read()
        except Exception as e:
            logger.error(f"Failed to read migration file {filepath}: {e}")
            return False
        
        # Extract name from comments (first line after --)
        name = version
        for line in sql.split('\n'):
            if line.startswith('-- Migration:'):
                name = line.replace('-- Migration:', '').strip()
                break
        
        # Apply migration
        conn = self.get_connection()
        start_time = datetime.utcnow()
        
        try:
            with conn.cursor() as cur:
                # Execute migration SQL
                cur.execute(sql)
                
                # Calculate execution time
                execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                # Record migration
                cur.execute("""
                    INSERT INTO schema_migrations (version, name, execution_time_ms)
                    VALUES (%s, %s, %s)
                """, (version, name, execution_time))
                
                conn.commit()
                logger.info(f"✅ Applied migration {version} in {execution_time}ms")
                return True
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to apply migration {version}: {e}")
            logger.error(f"Error details: {type(e).__name__}")
            return False
        finally:
            conn.close()
    
    def run_migrations(self) -> Tuple[int, int]:
        """
        Run all pending migrations
        
        Returns:
            Tuple of (successful_count, failed_count)
        """
        logger.info("=" * 60)
        logger.info("DATABASE MIGRATION SYSTEM")
        logger.info("=" * 60)
        
        # Ensure migrations table exists
        self.create_migrations_table()
        
        # Get pending migrations
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("✅ No pending migrations - database is up to date")
            return (0, 0)
        
        logger.info(f"Found {len(pending)} pending migration(s)")
        
        successful = 0
        failed = 0
        
        for version, filepath in pending:
            if self.apply_migration(version, filepath):
                successful += 1
            else:
                failed += 1
                logger.error(f"Stopping migration process due to failure")
                break  # Stop on first failure
        
        logger.info("=" * 60)
        logger.info(f"Migration Summary: {successful} successful, {failed} failed")
        logger.info("=" * 60)
        
        return (successful, failed)
    
    def get_migration_status(self) -> dict:
        """Get current migration status"""
        try:
            applied = self.get_applied_migrations()
            pending = self.get_pending_migrations()
            
            return {
                "applied_count": len(applied),
                "pending_count": len(pending),
                "applied_migrations": applied,
                "pending_migrations": [v for v, _ in pending],
                "status": "up_to_date" if not pending else "pending_migrations"
            }
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {
                "error": str(e),
                "status": "error"
            }


def main():
    """Main entry point for migration script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Migration Manager')
    parser.add_argument(
        '--database-url',
        default=os.getenv('DATABASE_URL'),
        help='PostgreSQL connection URL (default: from DATABASE_URL env var)'
    )
    parser.add_argument(
        '--migrations-dir',
        default=None,
        help='Path to migrations directory (default: ./migrations)'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show migration status without applying'
    )
    
    args = parser.parse_args()
    
    if not args.database_url:
        logger.error("Database URL not provided. Set DATABASE_URL env var or use --database-url")
        sys.exit(1)
    
    # Create migration manager
    manager = MigrationManager(args.database_url, args.migrations_dir)
    
    if args.status:
        # Show status only
        status = manager.get_migration_status()
        print(f"\n📊 Migration Status:")
        print(f"   Applied: {status.get('applied_count', 0)}")
        print(f"   Pending: {status.get('pending_count', 0)}")
        if status.get('pending_migrations'):
            print(f"\n   Pending migrations:")
            for migration in status['pending_migrations']:
                print(f"   - {migration}")
    else:
        # Run migrations
        successful, failed = manager.run_migrations()
        
        if failed > 0:
            logger.error("Migration failed!")
            sys.exit(1)
        
        logger.info("✅ All migrations completed successfully")
        sys.exit(0)


if __name__ == '__main__':
    main()
