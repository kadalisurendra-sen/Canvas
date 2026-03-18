"""Tests for user type schemas."""
import pytest

from src.types.enums import UserRole, UserStatus
from src.types.user import (
    InviteUserRequest,
    InviteUserResponse,
    UpdateUserRequest,
    UserListResponse,
    UserResponse,
)


class TestUserStatus:
    """Tests for UserStatus enum."""

    def test_active_value(self) -> None:
        assert UserStatus.ACTIVE.value == "active"

    def test_invited_value(self) -> None:
        assert UserStatus.INVITED.value == "invited"

    def test_deactivated_value(self) -> None:
        assert UserStatus.DEACTIVATED.value == "deactivated"

    def test_all_statuses(self) -> None:
        assert len(UserStatus) == 3


class TestUserResponse:
    """Tests for UserResponse schema."""

    def test_create_user_response(self) -> None:
        user = UserResponse(
            id="abc-123",
            name="John Doe",
            email="john@example.com",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
        assert user.name == "John Doe"
        assert user.role == UserRole.ADMIN
        assert user.status == UserStatus.ACTIVE

    def test_user_response_optional_last_login(self) -> None:
        user = UserResponse(
            id="abc-123",
            name="Jane",
            email="jane@example.com",
            role=UserRole.VIEWER,
            status=UserStatus.INVITED,
        )
        assert user.last_login is None


class TestUserListResponse:
    """Tests for UserListResponse schema."""

    def test_empty_list(self) -> None:
        resp = UserListResponse(
            users=[], total=0, page=1, page_size=10, total_pages=1
        )
        assert resp.users == []
        assert resp.total == 0

    def test_pagination_metadata(self) -> None:
        resp = UserListResponse(
            users=[], total=24, page=2, page_size=6, total_pages=4
        )
        assert resp.page == 2
        assert resp.total_pages == 4


class TestInviteUserRequest:
    """Tests for InviteUserRequest schema."""

    def test_default_role_is_viewer(self) -> None:
        req = InviteUserRequest(email="test@example.com")
        assert req.role == UserRole.VIEWER

    def test_custom_role(self) -> None:
        req = InviteUserRequest(
            email="admin@example.com", role=UserRole.ADMIN
        )
        assert req.role == UserRole.ADMIN


class TestUpdateUserRequest:
    """Tests for UpdateUserRequest schema."""

    def test_all_fields_optional(self) -> None:
        req = UpdateUserRequest()
        assert req.role is None
        assert req.status is None

    def test_set_role(self) -> None:
        req = UpdateUserRequest(role=UserRole.CONTRIBUTOR)
        assert req.role == UserRole.CONTRIBUTOR


class TestInviteUserResponse:
    """Tests for InviteUserResponse schema."""

    def test_default_message(self) -> None:
        resp = InviteUserResponse(
            id="x", email="a@b.com",
            role=UserRole.VIEWER, status=UserStatus.INVITED,
        )
        assert resp.message == "Invitation sent successfully"
