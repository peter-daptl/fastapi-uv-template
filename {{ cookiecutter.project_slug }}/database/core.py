"""
Core database setup for SQLAlchemy.

This module defines the Base for declarative models, sets up the asynchronous engine,
the sessionmaker, and provides utilities for database initialization and session management.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from config.settings import settings

# Define the base class for declarative models
Base = declarative_base()

# Create the asynchronous engine
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True in development for SQL logging, False in production
    future=True,
    pool_size=5,  # Recommended for connection pooling
    max_overflow=10,  # Max connections beyond pool_size
)

# Create an async sessionmaker
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents objects from being expired after commit
)


async def init_db():
    """
    Initializes the database by creating all tables defined in Base.metadata.

    This function should be called at application startup.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to provide an async database session.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_db_tables():
    """Alias for init_db, kept for backwards compatibility or clarity."""
    await init_db()


async def drop_db_tables():
    """
    Drops all tables defined in Base.metadata from the database.

    This function is primarily for testing and cleanup.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
