from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.engine import Result, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.items.services import ItemService
from api.v1.items.views import get_item_service
from database.models.item import Item
from schemas.item import ItemCreate, ItemUpdate


# Fixture for a mock AsyncSession
@pytest.fixture
def mock_async_session():
    return AsyncMock(spec=AsyncSession)


# Fixture for an ItemService instance using the mock session
@pytest.fixture
def item_service(mock_async_session):
    return ItemService(mock_async_session)


# Sample data
@pytest.fixture
def sample_item_data():
    return ItemCreate(name="Test Item", description="A description")


@pytest.fixture
def sample_db_item():
    # A mock ORM item instance
    mock_item = MagicMock(spec=Item)
    mock_item.id = 1
    mock_item.name = "Existing Item"
    mock_item.description = "Existing description"
    return mock_item


@pytest.mark.asyncio
async def test_get_item_service_dependency():
    """
    Tests that the get_item_service dependency correctly
    returns an ItemService instance.
    This test ensures coverage for the dependency function's body.
    """
    mock_db_session = MagicMock()  # We only need a mock db session here
    service = await get_item_service(mock_db_session)
    assert isinstance(service, ItemService)
    # Ensure the ItemService was initialized with the mock session
    assert service.db == mock_db_session


# --- Test get_item ---
@pytest.mark.asyncio
async def test_get_item_found(
    item_service: ItemService, mock_async_session: AsyncMock, sample_db_item: Item
):
    """
    Tests get_item when an item is found.
    Covers: return result.scalars().first()
    """
    mock_result = AsyncMock(spec=Result)
    mock_scalar_result = MagicMock(spec=ScalarResult)  # Mock ScalarResult for .first()
    mock_scalar_result.first.return_value = sample_db_item

    mock_result.scalars.return_value = mock_scalar_result
    mock_async_session.execute.return_value = mock_result

    item = await item_service.get_item(1)

    mock_async_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalar_result.first.assert_called_once()
    assert item == sample_db_item


@pytest.mark.asyncio
async def test_get_item_not_found(item_service: ItemService, mock_async_session: AsyncMock):
    """
    Tests get_item when no item is found.
    Covers: return result.scalars().first() when it returns None
    """
    mock_result = AsyncMock(spec=Result)
    mock_scalar_result = MagicMock(spec=ScalarResult)
    mock_scalar_result.first.return_value = None  # Service indicates not found

    mock_result.scalars.return_value = mock_scalar_result
    mock_async_session.execute.return_value = mock_result

    item = await item_service.get_item(999)

    mock_async_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalar_result.first.assert_called_once()
    assert item is None


# --- Test get_all_items ---
@pytest.mark.asyncio
async def test_get_all_items_with_data(
    item_service: ItemService, mock_async_session: AsyncMock, sample_db_item: Item
):
    """
    Tests get_all_items when items exist.
    Covers: return list(result.scalars().all())
    """
    mock_result = AsyncMock(spec=Result)
    mock_scalar_result = MagicMock(spec=ScalarResult)
    mock_scalar_result.all.return_value = [
        sample_db_item,
        sample_db_item,
    ]  # Return a list of items

    mock_result.scalars.return_value = mock_scalar_result
    mock_async_session.execute.return_value = mock_result

    items = await item_service.get_all_items()

    mock_async_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalar_result.all.assert_called_once()
    assert len(items) == 2
    assert items[0] == sample_db_item


@pytest.mark.asyncio
async def test_get_all_items_empty(item_service: ItemService, mock_async_session: AsyncMock):
    """
    Tests get_all_items when no items exist.
    Covers: return list(result.scalars().all()) returning an empty list
    """
    mock_result = AsyncMock(spec=Result)
    mock_scalar_result = MagicMock(spec=ScalarResult)
    mock_scalar_result.all.return_value = []  # Return an empty list

    mock_result.scalars.return_value = mock_scalar_result
    mock_async_session.execute.return_value = mock_result

    items = await item_service.get_all_items()

    mock_async_session.execute.assert_awaited_once()
    mock_result.scalars.assert_called_once()
    mock_scalar_result.all.assert_called_once()
    assert items == []


# --- Test create_item ---
@pytest.mark.asyncio
async def test_create_item(
    item_service: ItemService,
    mock_async_session: AsyncMock,
    sample_item_data: ItemCreate,
):
    """
    Tests creating an item.
    Covers: db_item = Item(**item_data.model_dump()), self.db.add,
    await self.db.commit(), await self.db.refresh(db_item), return db_item
    """

    # Mocking refresh to ensure db_item has an ID after it.
    async def mock_refresh(instance):
        instance.id = 1

    mock_async_session.refresh.side_effect = mock_refresh

    new_item = await item_service.create_item(sample_item_data)

    mock_async_session.add.assert_called_once()
    mock_async_session.commit.assert_awaited_once()
    mock_async_session.refresh.assert_awaited_once()
    assert new_item.name == sample_item_data.name
    assert new_item.id == 1


# --- Test update_item ---
@pytest.mark.asyncio
async def test_update_item_success(
    item_service: ItemService, mock_async_session: AsyncMock, sample_db_item: Item
):
    """
    Tests updating an item successfully.
    Covers: update statement execution, result.scalar_one_or_none(),
    await self.db.commit(), return updated_item
    """
    item_id = sample_db_item.id
    update_data = ItemUpdate(description="New description")

    mock_result = AsyncMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = sample_db_item  # Service returns the updated item

    mock_async_session.execute.return_value = mock_result

    updated_item = await item_service.update_item(item_id, update_data)

    mock_async_session.execute.assert_awaited_once()
    mock_result.scalar_one_or_none.assert_called_once()
    mock_async_session.commit.assert_awaited_once()
    assert updated_item == sample_db_item


@pytest.mark.asyncio
async def test_update_item_not_found(item_service: ItemService, mock_async_session: AsyncMock):
    """
    Tests updating a non-existent item.
    Covers: if not updated_item: return None
    """
    item_id = 999
    update_data = ItemUpdate(description="Non-existent update")

    mock_result = AsyncMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = None  # Service indicates not found

    mock_async_session.execute.return_value = mock_result

    updated_item = await item_service.update_item(item_id, update_data)

    mock_async_session.execute.assert_awaited_once()
    mock_result.scalar_one_or_none.assert_called_once()
    assert updated_item is None
    mock_async_session.commit.assert_not_awaited()  # No commit if item not found


@pytest.mark.asyncio
async def test_update_item_no_changes(
    item_service: ItemService, mock_async_session: AsyncMock, sample_db_item: Item
):
    """
    Tests updating an item with no changes provided.
    Covers: if not update_data: return await self.get_item(item_id)
    """
    item_id = sample_db_item.id
    update_data = ItemUpdate()  # Empty update data

    # Mock get_item as it will be called by update_item in this scenario
    # It needs a real session for this specific test, or mock get_item directly.
    # For simplicity, we'll mock the internal call to get_item
    item_service.get_item = AsyncMock(return_value=sample_db_item)

    updated_item = await item_service.update_item(item_id, update_data)

    item_service.get_item.assert_awaited_once_with(item_id)
    mock_async_session.execute.assert_not_awaited()  # No DB execute if no updates
    assert updated_item == sample_db_item


# --- Test delete_item ---
@pytest.mark.asyncio
async def test_delete_item_success(item_service: ItemService, mock_async_session: AsyncMock):
    """
    Tests deleting an item successfully.
    Covers: delete statement execution, result.rowcount,
    await self.db.commit(), return True
    """
    item_id = 1
    mock_result = AsyncMock(spec=Result)
    mock_result.rowcount = 1  # Indicate one row was deleted

    mock_async_session.execute.return_value = mock_result

    deleted = await item_service.delete_item(item_id)

    mock_async_session.execute.assert_awaited_once()
    mock_async_session.commit.assert_awaited_once()
    assert deleted is True


@pytest.mark.asyncio
async def test_delete_item_not_found(item_service: ItemService, mock_async_session: AsyncMock):
    """
    Tests deleting a non-existent item.
    Covers: if result.rowcount == 0: return False
    """
    item_id = 999
    mock_result = AsyncMock(spec=Result)
    mock_result.rowcount = 0  # Indicate no row was deleted

    mock_async_session.execute.return_value = mock_result

    deleted = await item_service.delete_item(item_id)

    mock_async_session.execute.assert_awaited_once()
    assert deleted is False
    mock_async_session.commit.assert_not_awaited()
