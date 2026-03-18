"""Tests for TenantSessionManager."""
from src.repo.session_manager import TenantSessionManager


class TestTenantSessionManager:
    """Tests for dynamic tenant session management."""

    def test_build_dsn(self) -> None:
        mgr = TenantSessionManager()
        dsn = mgr._build_dsn("localhost", 5432, "db_tenant_acme")
        assert "localhost" in dsn
        assert "5432" in dsn
        assert "db_tenant_acme" in dsn
        assert dsn.startswith("postgresql+asyncpg://")

    def test_build_dsn_uses_settings_credentials(self) -> None:
        mgr = TenantSessionManager()
        dsn = mgr._build_dsn("localhost", 5432, "db_test")
        # Should contain credentials from settings, not hardcoded
        assert "postgresql+asyncpg://" in dsn
        assert "@localhost:5432/db_test" in dsn

    def test_get_session_factory_returns_factory(self) -> None:
        mgr = TenantSessionManager()
        factory = mgr.get_session_factory("localhost", 5432, "db_test")
        assert factory is not None

    def test_same_dsn_returns_same_factory(self) -> None:
        mgr = TenantSessionManager()
        f1 = mgr.get_session_factory("host", 5432, "db1")
        f2 = mgr.get_session_factory("host", 5432, "db1")
        assert f1 is f2

    def test_different_dsn_returns_different_factory(self) -> None:
        mgr = TenantSessionManager()
        f1 = mgr.get_session_factory("host", 5432, "db1")
        f2 = mgr.get_session_factory("host", 5432, "db2")
        assert f1 is not f2
