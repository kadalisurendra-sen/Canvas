"""Tests for database module."""
from src.repo.database import Base, create_platform_engine


class TestBase:
    """Tests for the SQLAlchemy declarative Base."""

    def test_base_has_metadata(self) -> None:
        assert Base.metadata is not None

    def test_base_registry_exists(self) -> None:
        assert Base.registry is not None


class TestCreatePlatformEngine:
    """Tests for the platform engine factory."""

    def test_returns_engine_and_session_factory(self) -> None:
        engine, session_factory = create_platform_engine()
        assert engine is not None
        assert session_factory is not None

    def test_engine_url_contains_database(self) -> None:
        engine, _ = create_platform_engine()
        assert "db_" in str(engine.url)
