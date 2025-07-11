{% if cookiecutter.include_example_item_crud == "y" %}
"""
Pydantic schemas for Item entity.

Defines data structures for API requests and responses related to Item.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    """Base schema for Item, containing common fields."""
    name: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    """Schema for creating a new Item."""
    pass


class ItemUpdate(BaseModel):
    """Schema for updating an existing Item, allowing partial updates."""
    name: Optional[str] = None
    description: Optional[str] = None


class ItemInDB(ItemBase):
    """Schema representing an Item as stored in the database, including its ID."""
    id: int

    model_config = ConfigDict(from_attributes=True)


class ItemResponse(ItemInDB):
    """Schema for Item responses returned by the API."""
    pass
{% endif %}
