"""
Test the migration system locally
Run this to test migrations without Docker
"""

import os
import sys
from pathlib import Path

# Add db directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.migrate import MigrationManager


def main():
    print("=" * 70)
    print("TESTING DATABASE MIGRATIONS")
    print("=" * 70)
    
    # Use local database URL (adjust as needed)
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://trading_user:trading_pass@localhost:5432/trading_db"
    )
    
    print(f"\nDatabase URL: {database_url}")
    
    # Get migrations directory
    migrations_dir = Path(__file__).parent.parent / "db" / "migrations"
    print(f"Migrations directory: {migrations_dir}")
    
    if not migrations_dir.exists():
        print(f"❌ Migrations directory not found!")
        return 1
    
    # List migration files
    migration_files = sorted(migrations_dir.glob("*.sql"))
    print(f"\nFound {len(migration_files)} migration file(s):")
    for f in migration_files:
        print(f"  - {f.name}")
    
    # Create migration manager
    try:
        manager = MigrationManager(database_url, migrations_dir=str(migrations_dir))
        print("\n✅ Connected to database")
    except Exception as e:
        print(f"\n❌ Failed to connect to database: {e}")
        return 1
    
    # Show current status
    print("\n" + "=" * 70)
    print("CURRENT MIGRATION STATUS")
    print("=" * 70)
    
    status = manager.get_migration_status()
    print(f"\nApplied migrations: {status['applied_count']}")
    if status.get('applied_migrations'):
        for migration in status['applied_migrations']:
            print(f"  ✅ {migration}")
    
    print(f"\nPending migrations: {status['pending_count']}")
    if status.get('pending_migrations'):
        for migration in status['pending_migrations']:
            print(f"  ⏳ {migration}")
    
    # Ask user if they want to proceed
    if status['pending_count'] > 0:
        print("\n" + "=" * 70)
        response = input("\nDo you want to apply pending migrations? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            print("\n" + "=" * 70)
            print("APPLYING MIGRATIONS")
            print("=" * 70)
            
            successful, failed = manager.run_migrations()
            
            if failed > 0:
                print(f"\n❌ Migration failed!")
                return 1
            elif successful > 0:
                print(f"\n✅ Successfully applied {successful} migration(s)")
            
            # Show updated status
            print("\n" + "=" * 70)
            print("UPDATED STATUS")
            print("=" * 70)
            
            status = manager.get_migration_status()
            print(f"Applied migrations: {status['applied_count']}")
            print(f"Pending migrations: {status['pending_count']}")
        else:
            print("\n⏭️  Skipping migrations")
    else:
        print("\n✅ Database is up to date - no migrations needed")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
