"""
Main entry point for the FastAPI application.

This module initializes the FastAPI app, sets up lifespan events for database management,
and includes API routers.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1.items.views import router as items_router
{% if cookiecutter.include_example_item_crud == "y" %}
from api.v1.items.views import router as items_router
{% endif %}
from database.core import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.

    This function ensures the database tables are created at startup
    and provides a clean shutdown.
    """
    print("Application startup: Initializing database...")
    os.makedirs("data", exist_ok=True)  # Ensure 'data' directory exists for SQLite file
    await init_db()
    print("Application startup: Database initialized.")
    yield
    print("Application shutdown: Closing resources (if any).")


app = FastAPI(
    title="{{ cookiecutter.project_name }}",
    version="1.0.0",
    lifespan=lifespan,
)

{% if cookiecutter.include_example_item_crud == "y" %}
app.include_router(items_router, prefix="/api/v1")
{% endif %}

@app.get("/api/v1/health")
async def health_check():
    """
    Performs a health check on the API.

    Returns:
        dict: A dictionary indicating the status of the API.
    """
    return {"status": "ok", "message": "API is healthy"}
