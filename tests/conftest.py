"""Root test configuration and shared fixtures."""
import os

import pytest


@pytest.fixture(autouse=True)
def _set_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set environment variables for all tests."""
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/db_test",
    )
    monkeypatch.setenv("KEYCLOAK_URL", "http://localhost:8080")
    monkeypatch.setenv("KEYCLOAK_REALM", "test-realm")
    monkeypatch.setenv("KEYCLOAK_CLIENT_ID", "test-client")
    monkeypatch.setenv("KEYCLOAK_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/1")
    monkeypatch.setenv("JWT_ALGORITHM", "RS256")
    monkeypatch.setenv("JWT_AUDIENCE", "test-client")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "postgres")
