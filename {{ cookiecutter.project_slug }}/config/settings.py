"""
Application settings and configuration.

Loads environment variables and provides them through a Settings class.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Application settings class.

    Attributes:
        DATABASE_URL (str): The URL for the database connection.
                            Defaults to an in-memory SQLite database.
    """

    DATABASE_URL: str = os.getenv("DATABASE_URL", "{{ cookiecutter.db_url }}")


settings = Settings()
