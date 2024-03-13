import os

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V2_STR: str = "/api/v2"

    pg_user: str = os.getenv("POSTGRES_USER", "")
    pg_pass: str = os.getenv("POSTGRES_PASSWORD", "")
    pg_host: str = os.getenv("POSTGRES_HOST", "")
    pg_port: str = os.getenv("POSTGRES_PORT", "")
    pg_database: str = os.getenv("POSTGRES_DB", "")
    pg_url: str = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_database}"

    first_superuser: EmailStr = os.getenv("FIRST_SUPERUSER", "")
    first_superuser_password: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "")

    prod: str = os.getenv("PROD", "")

    redis_host: str = os.getenv("REDIS_HOST", "")
    redis_port: str = os.getenv("REDIS_PORT", "")

    rabit_user: str = os.getenv("RABBITMQ_USER", "")
    rabit_pass: str = os.getenv("RABBITMQ_PASSWORD", "")
    rabbit_host: str = os.getenv("RABBITMQ_HOST", "")
    rabit_url: str = f"amqp://{rabit_user}:{rabit_pass}@{rabbit_host}/"

    app_port: str = os.getenv("APP_PORT", "")
    secret: str = os.getenv("SECRET", "")

    tarantool_url: str = os.getenv("TARANT_URL", "")
    tarantool_port: str = os.getenv("TARANT_PORT", "")


# TODO Make this settings a global object
def get_settings():
    return Settings()
