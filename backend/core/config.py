from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DjangoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DEBUG: bool = Field(default=False)
    SECRET_KEY: str
    ALLOWED_HOSTS: str


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file="postgres.env", env_file_encoding="utf-8")

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)

class  CelerySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file="celery.env", env_file_encoding="utf-8")

    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")


@lru_cache
def get_django_settings() -> DjangoSettings:
    return DjangoSettings()

@lru_cache
def get_postgres_settings() -> PostgresSettings:
    return PostgresSettings()

@lru_cache
def get_celery_settings() -> CelerySettings:
    return CelerySettings()



