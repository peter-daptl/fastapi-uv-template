{% if cookiecutter.include_example_item_crud == "y" %}
"""
SQLAlchemy ORM model for the Item entity.
"""

from sqlalchemy import Column, Integer, String

from database.core import Base


class Item(Base):
    """
    Represents an Item in the database.

    Attributes:
        id (int): Primary key for the item.
        name (str): Unique name of the item.
        description (str, optional): Description of the item.
    """

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
{% endif %}
