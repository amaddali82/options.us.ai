"""
Startup script to run database migrations before starting the API server
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from db.migrate import MigrationManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    """Run database migrations on startup"""
    logger.info("🚀 Starting database migration check...")
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set!")
        return False
    
    try:
        # Create migration manager
        migrations_dir = Path(__file__).parent / "db" / "migrations"
        manager = MigrationManager(database_url, migrations_dir=str(migrations_dir))
        
        # Run migrations
        successful, failed = manager.run_migrations()
        
        if failed > 0:
            logger.error("❌ Migration failed! Cannot start API server.")
            return False
        
        if successful > 0:
            logger.info(f"✅ Applied {successful} migration(s) successfully")
        else:
            logger.info("✅ Database is up to date")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        return False


if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
