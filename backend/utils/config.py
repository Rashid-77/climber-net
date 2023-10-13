import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    BaseSettings, from Pydantic, validates the data so that when we create an instance of Settings,
     environment and testing will have types of str and bool, respectively.
    Parameters:
    pg_user (str):
    pg_pass (str):
    pg_host (str):
    pg_database: (str):
    pg_test_database: (str):
    pg_url:  AnyUrl:
    Returns:
    instance of Settings
    """
    pg_user: str = os.getenv("POSTGRES_USER", "")
    pg_pass: str = os.getenv("POSTGRES_PASSWORD", "")
    pg_host: str = os.getenv("POSTGRES_HOST", "")
    pg_port: str = os.getenv("POSTGRES_PORT", "")
    pg_database: str = os.getenv("POSTGRES_DB", "")
    pg_url: str = f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_database}'


def get_settings():
    return Settings()