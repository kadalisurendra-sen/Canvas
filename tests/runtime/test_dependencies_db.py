"""Tests for database dependency module."""
import pytest

from src.runtime.dependencies.db import get_tenant_session


class TestGetTenantSession:
    """Tests for get_tenant_session context manager."""

    def test_is_async_context_manager(self) -> None:
        """Verify get_tenant_session returns an async context manager."""
        result = get_tenant_session()
        assert hasattr(result, "__aenter__")
        assert hasattr(result, "__aexit__")

    def test_with_none_request(self) -> None:
        """Verify get_tenant_session works with no request."""
        result = get_tenant_session(None)
        assert hasattr(result, "__aenter__")
        assert hasattr(result, "__aexit__")
