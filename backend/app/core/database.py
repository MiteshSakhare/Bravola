"""
Database configuration and session management
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create async engine
# ✅ FIX: Added safety check for DATABASE_ECHO
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=getattr(settings, "DATABASE_ECHO", False),
    future=True,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()

# Import models so 'init_db' knows what tables to create
# (These must be imported after Base is defined)
from app.models.merchant import Merchant
from app.models.discovery import DiscoveryProfile
from app.models.strategy import Strategy
from app.models.feedback import FeedbackEvent

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database - create all tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections
    """
    await engine.dispose()