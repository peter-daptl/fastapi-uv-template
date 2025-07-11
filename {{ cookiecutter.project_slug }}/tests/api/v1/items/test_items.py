"""
Pytest tests for the Item API endpoints.

These tests interact with the FastAPI application via an HTTP client
and use an in-memory database for isolated testing.
"""

from unittest.mock import AsyncMock  # Import AsyncMock for type hinting

import pytest
from httpx import AsyncClient

# Import your Pydantic schemas for assertion
from schemas.item import ItemCreate, ItemResponse, ItemUpdate


# Fixtures for item data (remain the same)
@pytest.fixture
def item_data_1():
    """Fixture for a sample item's data."""
    return {"name": "Laptop", "description": "Powerful computing device"}


@pytest.fixture
def item_data_2():
    """Fixture for another sample item's data."""
    return {"name": "Mouse", "description": "Ergonomic computer mouse"}


# --- Tests for GET /api/v1/items/ (Retrieve all items) ---


@pytest.mark.asyncio
async def test_get_all_items_empty(client: AsyncClient, mock_item_service: AsyncMock):
    """
    Test retrieving all items when the database is empty.
    Covers get_all_items success path in view.
    """
    mock_item_service.get_all_items.return_value = []  # Mock the service call
    response = await client.get("/api/v1/items/")
    assert response.status_code == 200
    assert response.json() == []
    mock_item_service.get_all_items.assert_awaited_once()  # Verify service was called


@pytest.mark.asyncio
async def test_get_all_items_with_data(
    client: AsyncClient,
    mock_item_service: AsyncMock,
    item_data_1: dict,
    item_data_2: dict,
):
    """
    Test retrieving all items when there is data in the database.
    Covers get_all_items success path in view.
    """
    # Mocking returns Pydantic-compatible dicts, but service returns ORM models.
    # Adjust mock to return mock ORM objects if needed, or simple dicts.
    # For now, let's assume service returns simple dicts or models that convert to dicts.
    mock_item_service.get_all_items.return_value = [
        ItemResponse(id=1, **item_data_1),  # Return Pydantic instances for consistency
        ItemResponse(id=2, **item_data_2),
    ]
    response = await client.get("/api/v1/items/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    returned_names = {item["name"] for item in items}
    assert item_data_1["name"] in returned_names
    assert item_data_2["name"] in returned_names
    mock_item_service.get_all_items.assert_awaited_once()


# --- Tests for POST /api/v1/items/ (Create item) ---


@pytest.mark.asyncio
async def test_create_item_success(
    client: AsyncClient, mock_item_service: AsyncMock, item_data_1: dict
):
    """
    Test creating a new item successfully.
    Covers create_item success path in view.
    """
    # The view passes ItemCreate instance to the service
    expected_item_create_arg = ItemCreate(**item_data_1)
    mock_item_service.create_item.return_value = ItemResponse(
        id=1, **item_data_1
    )  # Mock the service call to return Pydantic model

    response = await client.post("/api/v1/items/", json=item_data_1)
    assert response.status_code == 201
    created_item = response.json()
    assert created_item["name"] == item_data_1["name"]
    assert created_item["description"] == item_data_1["description"]
    assert "id" in created_item
    assert isinstance(created_item["id"], int)
    # Assert that the service was called with an ItemCreate instance
    mock_item_service.create_item.assert_awaited_once_with(expected_item_create_arg)


# --- Tests for GET /api/v1/items/{item_id} (Retrieve single item) ---


@pytest.mark.asyncio
async def test_get_single_item_success(
    client: AsyncClient, mock_item_service: AsyncMock, item_data_1: dict
):
    """
    Test retrieving a single item that exists.
    Covers get_item success path in view.
    """
    item_id = 1
    mock_item_service.get_item.return_value = ItemResponse(id=item_id, **item_data_1)
    response = await client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id
    assert response.json()["name"] == item_data_1["name"]
    mock_item_service.get_item.assert_awaited_once_with(item_id)


@pytest.mark.asyncio
async def test_get_single_item_not_found(client: AsyncClient, mock_item_service: AsyncMock):
    """
    Test retrieving a single item that does not exist.
    Covers get_item 404 (not found) path in the view.
    """
    mock_item_service.get_item.return_value = None  # Service returns None when not found
    non_existent_item_id = 99999
    response = await client.get(f"/api/v1/items/{non_existent_item_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}
    mock_item_service.get_item.assert_awaited_once_with(non_existent_item_id)


# --- Tests for PATCH /api/v1/items/{item_id} (Update item) ---


@pytest.mark.asyncio
async def test_update_item_success(
    client: AsyncClient, mock_item_service: AsyncMock, item_data_1: dict
):
    """
    Test updating an existing item successfully.
    Covers update_item success path in view.
    """
    item_id = 1
    update_payload = {"description": "Updated description for laptop"}
    # The view passes ItemUpdate instance to the service
    expected_item_update_arg = ItemUpdate(**update_payload)
    mock_item_service.update_item.return_value = ItemResponse(
        id=item_id, name=item_data_1["name"], description=update_payload["description"]
    )

    response = await client.patch(f"/api/v1/items/{item_id}", json=update_payload)
    assert response.status_code == 200
    updated_item = response.json()
    assert updated_item["id"] == item_id
    assert updated_item["description"] == "Updated description for laptop"
    # Assert that the service was called with an ItemUpdate instance
    mock_item_service.update_item.assert_awaited_once_with(item_id, expected_item_update_arg)


@pytest.mark.asyncio
async def test_update_item_not_found(client: AsyncClient, mock_item_service: AsyncMock):
    """
    Test updating a non-existent item.
    Covers update_item 404 (not found) path in the view.
    """
    mock_item_service.update_item.return_value = None
    update_payload = {"name": "NonExistent"}
    non_existent_item_id = 999
    # The view passes ItemUpdate instance to the service
    expected_item_update_arg = ItemUpdate(**update_payload)

    response = await client.patch(f"/api/v1/items/{non_existent_item_id}", json=update_payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}
    # Assert that the service was called with an ItemUpdate instance
    mock_item_service.update_item.assert_awaited_once_with(
        non_existent_item_id, expected_item_update_arg
    )


@pytest.mark.asyncio
async def test_update_item_no_changes(
    client: AsyncClient, mock_item_service: AsyncMock, item_data_1: dict
):
    """
    Test updating an item with no actual changes, ensuring service is called with proper args.
    Covers the 'if not update_data' branch in service if service is not mocked.
    Since ItemService is mocked, we need to ensure the view still calls the service correctly.
    """
    item_id = 1
    # Mock the service to return the existing item as if no changes were made.
    mock_item_service.update_item.return_value = ItemResponse(id=item_id, **item_data_1)
    # The view passes an empty ItemUpdate instance if the payload is empty
    expected_item_update_arg = ItemUpdate()

    response = await client.patch(f"/api/v1/items/{item_id}", json={})
    assert response.status_code == 200
    assert response.json()["id"] == item_id
    assert response.json()["name"] == item_data_1["name"]
    # Verify the service was called with item_id and an empty ItemUpdate instance
    mock_item_service.update_item.assert_awaited_once_with(item_id, expected_item_update_arg)


# --- Tests for DELETE /api/v1/items/{item_id} (Delete item) ---


@pytest.mark.asyncio
async def test_delete_item_success(client: AsyncClient, mock_item_service: AsyncMock):
    """
    Test deleting an item successfully.
    Covers delete_item success path in view.
    """
    item_id = 1
    mock_item_service.delete_item.return_value = True  # Service returns True on success
    response = await client.delete(f"/api/v1/items/{item_id}")
    assert response.status_code == 204
    mock_item_service.delete_item.assert_awaited_once_with(item_id)


@pytest.mark.asyncio
async def test_delete_item_not_found(client: AsyncClient, mock_item_service: AsyncMock):
    """
    Test deleting a non-existent item.
    Covers delete_item 404 (not found) path in the view.
    """
    mock_item_service.delete_item.return_value = False  # Service returns False when not found
    non_existent_item_id = 999
    response = await client.delete(f"/api/v1/items/{non_existent_item_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}
    mock_item_service.delete_item.assert_awaited_once_with(non_existent_item_id)
