"""Tests for TenantRepository."""
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.repo.tenant_repository import TenantNotFoundError, TenantRepository


class TestTenantNotFoundError:
    """Tests for TenantNotFoundError."""

    def test_error_message(self) -> None:
        err = TenantNotFoundError("Tenant abc not found")
        assert "abc" in str(err)

    def test_is_exception(self) -> None:
        err = TenantNotFoundError("x")
        assert isinstance(err, Exception)


class TestTenantRepositoryInit:
    """Tests for TenantRepository initialization."""

    def test_init_stores_session(self) -> None:
        session = MagicMock()
        repo = TenantRepository(session=session)
        assert repo._session is session
