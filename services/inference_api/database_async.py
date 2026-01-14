"""
Async Database configuration using SQLAlchemy 2.0 + asyncpg
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import os

# Convert postgres:// to postgresql+asyncpg://
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://trading_user:trading_pass@localhost:5432/trading_db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    poolclass=NullPool,  # For development; use proper pooling in production
    pool_pre_ping=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_async_db():
    """Dependency for getting async database sessions"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
