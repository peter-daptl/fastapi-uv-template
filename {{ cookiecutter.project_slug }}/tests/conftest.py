from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.v1.items.services import ItemService
from api.v1.items.views import get_item_service as actual_get_item_service
from config.settings import settings
from database.core import Base
from main import app as fastapi_app

TEST_DATABASE_URL = settings.DATABASE_URL.replace("app.db", "test.db")

test_async_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """
    Fixture to set up and tear down the test database for the entire test session.
    This ensures tables are created before tests and dropped after all tests run.
    """
    # Ensure the test database exists and tables are created
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # This line should now be covered
    yield
    # Drop tables after all tests in the session are complete
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # This line should now be covered


@pytest.fixture(scope="function")
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a fresh session for each test, suitable for direct service testing
    or if a view test needs a *real* session without mocking the service.
    """
    async with TestAsyncSessionLocal() as session:
        try:
            async with session.begin():  # Start a transaction
                yield session
                # No rollback needed if the transaction ensures isolation
        finally:
            await session.close()  # This line should now be covered when test_db_session is used


# NEW FIXTURE: This fixture will provide a mock ItemService for FastAPI's dependency injection
@pytest.fixture
def mock_item_service():
    """
    Fixture that provides an AsyncMock for ItemService for testing views.
    """
    from unittest.mock import AsyncMock

    return AsyncMock(spec=ItemService)


@pytest.fixture(scope="function")
async def client(mock_item_service: AsyncMock):  # Now takes mock_item_service
    """
    Test client for FastAPI application with dependency override for ItemService.
    """
    # Override the get_item_service dependency directly
    fastapi_app.dependency_overrides[actual_get_item_service] = lambda: mock_item_service

    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac
    fastapi_app.dependency_overrides.clear()  # Clear overrides after test
