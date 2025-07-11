"""
Service layer for Item operations.

This module contains the business logic for creating, retrieving, updating,
and deleting Item entities, interacting directly with the database via ORM models.
"""

from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.item import Item  # Absolute import for ORM model
from schemas.item import ItemCreate, ItemUpdate  # Absolute import for Pydantic schemas


class ItemService:
    """
    Handles CRUD operations for Item objects.

    Args:
        db (AsyncSession): The asynchronous database session.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_item(self, item_id: int) -> Optional[Item]:
        """
        Retrieve a single item by ID.

        Args:
            item_id (int): The ID of the item to retrieve.

        Returns:
            Optional[Item]: The Item object if found, otherwise None.
        """
        result = await self.db.execute(select(Item).where(Item.id == item_id))
        return result.scalars().first()

    async def get_all_items(self) -> List[Item]:
        """
        Retrieve all items.

        Returns:
            List[Item]: A list of all Item objects in the database.
        """
        result = await self.db.execute(select(Item))
        return list(result.scalars().all())

    async def create_item(self, item_data: ItemCreate) -> Item:
        """
        Create a new item in the database.

        Args:
            item_data (ItemCreate): The Pydantic schema containing data for the new item.

        Returns:
            Item: The newly created Item ORM object, including its generated ID.
        """
        db_item = Item(**item_data.model_dump())
        self.db.add(db_item)
        await self.db.commit()
        await self.db.refresh(db_item)
        return db_item

    async def update_item(self, item_id: int, updates: ItemUpdate) -> Optional[Item]:
        """
        Update an existing item.

        Args:
            item_id (int): The ID of the item to update.
            updates (ItemUpdate): The Pydantic schema containing fields to update.

        Returns:
            Optional[Item]: The updated Item object if found, otherwise None.
        """
        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:  # If no data to update, return the item (or None if not found)
            return await self.get_item(item_id)

        stmt = update(Item).where(Item.id == item_id).values(**update_data).returning(Item)
        result = await self.db.execute(stmt)
        updated_item = result.scalar_one_or_none()

        if not updated_item:
            return None

        await self.db.commit()
        return updated_item

    async def delete_item(self, item_id: int) -> bool:
        """
        Delete an item by ID.

        Args:
            item_id (int): The ID of the item to delete.

        Returns:
            bool: True if the item was deleted, False if not found.
        """
        stmt = delete(Item).where(Item.id == item_id)
        result = await self.db.execute(stmt)

        if result.rowcount == 0:
            return False

        await self.db.commit()
        return True
