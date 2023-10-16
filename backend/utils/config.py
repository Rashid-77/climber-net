import os

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    pg_user: str = os.getenv("POSTGRES_USER", "")
    pg_pass: str = os.getenv("POSTGRES_PASSWORD", "")
    pg_host: str = os.getenv("POSTGRES_HOST", "")
    pg_port: str = os.getenv("POSTGRES_PORT", "")
    pg_database: str = os.getenv("POSTGRES_DB", "")
    pg_url: str = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_database}"

    first_superuser: EmailStr = os.getenv("FIRST_SUPERUSER", "")
    first_superuser_password: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "")


# TODO Make this settings a global object
def get_settings():
    return Settings()
