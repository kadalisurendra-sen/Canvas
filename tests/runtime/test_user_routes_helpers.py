"""Tests for user route helper functions."""
import uuid

import pytest
from fastapi import HTTPException

from src.runtime.routes.users import (
    _check_self_deactivation,
    _get_user_service,
    _raise_conflict,
    _raise_server_error,
)
from src.service.user_service import UserConflictError, UserServiceError
from src.types.auth import UserContext
from src.types.enums import UserRole


def _make_user_ctx(user_id: uuid.UUID | None = None) -> UserContext:
    uid = user_id or uuid.uuid4()
    return UserContext(
        user_id=uid,
        email="admin@test.com",
        name="Admin",
        roles=[UserRole.ADMIN],
        tenant_id=uuid.uuid4(),
    )


class TestCheckSelfDeactivation:
    """Tests for _check_self_deactivation."""

    def test_raises_when_same_id(self) -> None:
        uid = uuid.uuid4()
        ctx = _make_user_ctx(uid)
        with pytest.raises(HTTPException) as exc_info:
            _check_self_deactivation(str(uid), ctx)
        assert exc_info.value.status_code == 400

    def test_passes_for_different_id(self) -> None:
        ctx = _make_user_ctx()
        # Should not raise
        _check_self_deactivation("other-id", ctx)


class TestRaiseConflict:
    """Tests for _raise_conflict."""

    def test_raises_409(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            _raise_conflict(UserConflictError("exists"))
        assert exc_info.value.status_code == 409


class TestRaiseServerError:
    """Tests for _raise_server_error."""

    def test_raises_500(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            _raise_server_error(UserServiceError("failed"))
        assert exc_info.value.status_code == 500


class TestGetUserService:
    """Tests for _get_user_service."""

    def test_returns_user_service(self) -> None:
        from src.service.user_service import UserService
        svc = _get_user_service(realm="test-realm")
        assert isinstance(svc, UserService)
