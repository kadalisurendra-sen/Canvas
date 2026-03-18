"""Tests for application settings."""
from src.config.settings import Settings, get_settings


class TestSettings:
    """Tests for Settings configuration class."""

    def test_loads_database_url_from_env(self, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        monkeypatch.setenv(
            "DATABASE_URL",
            "postgresql+asyncpg://u:p@host:5432/mydb",
        )
        settings = Settings()
        assert settings.DATABASE_URL == "postgresql+asyncpg://u:p@host:5432/mydb"

    def test_loads_redis_url_from_env(self, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        monkeypatch.setenv("REDIS_URL", "redis://myredis:6379/2")
        settings = Settings()
        assert settings.REDIS_URL == "redis://myredis:6379/2"

    def test_loads_keycloak_url_from_env(self, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        monkeypatch.setenv("KEYCLOAK_URL", "http://kc:9090")
        settings = Settings()
        assert settings.KEYCLOAK_URL == "http://kc:9090"

    def test_default_values(self) -> None:
        settings = Settings()
        assert settings.APP_NAME == "Helio Canvas"
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        assert settings.JWT_ALGORITHM == "RS256"

    def test_cors_origins_default(self) -> None:
        settings = Settings()
        assert "http://localhost:5173" in settings.CORS_ORIGINS

    def test_get_settings_returns_settings_instance(self) -> None:
        get_settings.cache_clear()
        result = get_settings()
        assert isinstance(result, Settings)
        get_settings.cache_clear()
