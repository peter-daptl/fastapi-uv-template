"""
API endpoints (views) for Item resources.

Uses FastAPI's APIRouter and fastapi-utils's @cbv decorator for class-based views.
"""


from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.items.services import ItemService
from database.core import get_session
from schemas.item import ItemCreate
from schemas.item import ItemResponse, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


async def get_item_service(db: AsyncSession = Depends(get_session)) -> ItemService:
    """
    FastAPI dependency that provides an ItemService instance with a database session.

    Args:
        db (AsyncSession): The asynchronous database session provided by get_session.

    Returns:
        ItemService: An initialized ItemService instance.
    """

    # This function is explicitly mocked in API tests (tests/api/v1/items/test_items.py)
    # via dependency_overrides, so its original execution path is not taken during those tests.
    # The instantiation of ItemService itself is covered by unit tests in
    # tests/unit/test_item_service.py.
    return ItemService(db)  # pragma: no cover


@cbv(router)
class ItemView:
    """
    Class-based view for handling 'item' operations.

    Attributes:
        service (ItemService): The service layer instance for Item operations.
    """

    def __init__(self, service: ItemService = Depends(get_item_service)):
        """
        Initializes the ItemView with an ItemService instance.
        """
        self.service = service

    @router.get("/", response_model=List[ItemResponse])
    async def get_all_items(self):
        """
        Retrieve all items.

        Returns:
            List[ItemResponse]: A list of all items.
        """
        items = await self.service.get_all_items()
        return items

    @router.get("/{item_id}", response_model=ItemResponse)
    async def get_single_item(
        self,
        item_id: int = Path(..., description="The ID of the item to retrieve"),
    ):
        """
        Retrieve a single item by ID.

        Args:
            item_id (int): The unique identifier of the item.

        Raises:
            HTTPException: If the item is not found (404).

        Returns:
            ItemResponse: The retrieved item data.
        """
        item = await self.service.get_item(item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        return item

    @router.post(
        "/",
        response_model=ItemResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_item(self, item_data: ItemCreate):
        """
        Create a new item.

        Args:
            item_data (ItemCreate): The data for the new item.

        Returns:
            ItemResponse: The newly created item data.
        """
        new_item = await self.service.create_item(item_data)
        return new_item

    @router.patch("/{item_id}", response_model=ItemResponse)
    async def update_item(
        self,
        item_data: ItemUpdate,
        item_id: int = Path(..., description="The ID of the item to update"),
    ):
        """
        Partially update an existing item.

        Args:
            item_data (ItemUpdate): The updated data for the item.
            item_id (int): The unique identifier of the item to update.

        Raises:
            HTTPException: If the item is not found (404).

        Returns:
            ItemResponse: The updated item data.
        """
        updated_item = await self.service.update_item(item_id, item_data)
        if not updated_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        return updated_item

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_item(
        self,
        item_id: int = Path(..., description="The ID of the item to delete"),
    ):
        """
        Delete an item by ID.

        Args:
            item_id (int): The unique identifier of the item to delete.

        Raises:
            HTTPException: If the item is not found (404).

        Returns:
            Response: An empty 204 No Content response upon successful deletion.
        """
        deleted = await self.service.delete_item(item_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
