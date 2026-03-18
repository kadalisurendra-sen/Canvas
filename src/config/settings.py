"""Application settings loaded from environment variables."""
import logging
from functools import lru_cache

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration via environment variables."""

    APP_NAME: str = "Helio Canvas"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/db_platform"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    # Auth
    AUTH_MODE: str = "keycloak"  # "keycloak" or "dev" (dev = no Keycloak needed)

    # Keycloak
    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "helio"
    KEYCLOAK_CLIENT_ID: str = "helio-admin"
    KEYCLOAK_CLIENT_SECRET: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_ALGORITHM: str = "RS256"
    JWT_AUDIENCE: str = "helio-admin"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
