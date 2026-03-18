"""Tests for UserService business logic."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.repo.user_repository import UserAlreadyExistsError, UserRepository
from src.service.user_service import (
    UserConflictError,
    UserService,
    map_kc_user,
)
from src.types.enums import UserRole, UserStatus


def _make_kc_user(
    uid: str = "u1",
    first: str = "John",
    last: str = "Doe",
    email: str = "john@test.com",
    role: str = "admin",
    status: str = "active",
    enabled: bool = True,
) -> dict:
    return {
        "id": uid,
        "firstName": first,
        "lastName": last,
        "email": email,
        "username": email,
        "enabled": enabled,
        "attributes": {"role": [role], "status": [status]},
    }


class TestListUsers:
    """Tests for listing users."""

    @pytest.mark.asyncio
    @patch("src.service.user_service.repo_count", new_callable=AsyncMock)
    @patch("src.service.user_service.repo_list", new_callable=AsyncMock)
    async def test_list_returns_mapped_users(self, mock_list, mock_count) -> None:
        mock_count.return_value = 1
        mock_list.return_value = [_make_kc_user()]
        repo = MagicMock(spec=UserRepository)
        svc = UserService(repo)
        result = await svc.list_users(page=1, page_size=10)
        assert result.total == 1
        assert len(result.users) == 1
        assert result.users[0].name == "John Doe"

    @pytest.mark.asyncio
    @patch("src.service.user_service.repo_count", new_callable=AsyncMock)
    @patch("src.service.user_service.repo_list", new_callable=AsyncMock)
    async def test_list_empty(self, mock_list, mock_count) -> None:
        mock_count.return_value = 0
        mock_list.return_value = []
        svc = UserService(MagicMock(spec=UserRepository))
        result = await svc.list_users()
        assert result.total == 0
        assert result.users == []

    @pytest.mark.asyncio
    @patch("src.service.user_service.repo_count", new_callable=AsyncMock)
    @patch("src.service.user_service.repo_list", new_callable=AsyncMock)
    async def test_list_pagination_metadata(self, mock_list, mock_count) -> None:
        mock_count.return_value = 25
        mock_list.return_value = [_make_kc_user()]
        svc = UserService(MagicMock(spec=UserRepository))
        result = await svc.list_users(page=2, page_size=10)
        assert result.page == 2
        assert result.total_pages == 3

    @pytest.mark.asyncio
    @patch("src.service.user_service.repo_count", new_callable=AsyncMock)
    @patch("src.service.user_service.repo_list", new_callable=AsyncMock)
    async def test_list_filters_by_role(self, mock_list, mock_count) -> None:
        mock_count.return_value = 2
        mock_list.return_value = [
            _make_kc_user(uid="u1", role="admin"),
            _make_kc_user(uid="u2", role="viewer"),
        ]
        svc = UserService(MagicMock(spec=UserRepository))
        result = await svc.list_users(role="admin")
        assert len(result.users) == 1
        assert result.users[0].role == UserRole.ADMIN

    @pytest.mark.asyncio
    @patch("src.service.user_service.repo_count", new_callable=AsyncMock)
    @patch("src.service.user_service.repo_list", new_callable=AsyncMock)
    async def test_list_filters_by_status(self, mock_list, mock_count) -> None:
        mock_count.return_value = 2
        mock_list.return_value = [
            _make_kc_user(uid="u1", status="active"),
            _make_kc_user(uid="u2", status="invited"),
        ]
        svc = UserService(MagicMock(spec=UserRepository))
        result = await svc.list_users(status="invited")
        assert len(result.users) == 1
        assert result.users[0].status == UserStatus.INVITED


class TestInviteUser:
    """Tests for inviting users."""

    @pytest.mark.asyncio
    @patch("src.service.user_service.repo_create", new_callable=AsyncMock)
    async def test_invite_success(self, mock_create) -> None:
        mock_create.return_value = {"id": "new-id", "email": "a@b.com", "role": "viewer"}
        svc = UserService(MagicMock(spec=UserRepository))
        result = await svc.invite_user("a@b.com", UserRole.VIEWER)
        assert result.id == "new-id"
        assert result.status == UserStatus.INVITED

    @pytest.mark.asyncio
    @patch("src.service.user_service.repo_create", new_callable=AsyncMock)
    async def test_invite_conflict(self, mock_create) -> None:
        mock_create.side_effect = UserAlreadyExistsError("exists")
        svc = UserService(MagicMock(spec=UserRepository))
        with pytest.raises(UserConflictError):
            await svc.invite_user("dup@b.com", UserRole.ADMIN)


class TestUpdateUser:
    """Tests for updating users."""

    @pytest.mark.asyncio
    @patch("src.service.user_service.repo_update", new_callable=AsyncMock)
    async def test_update_role(self, mock_update) -> None:
        svc = UserService(MagicMock(spec=UserRepository))
        result = await svc.update_user("u1", role=UserRole.CONTRIBUTOR)
        assert result["message"] == "User updated successfully"


class TestDeactivateUser:
    """Tests for deactivating users."""

    @pytest.mark.asyncio
    @patch("src.service.user_service.repo_deactivate", new_callable=AsyncMock)
    async def test_deactivate(self, mock_deactivate) -> None:
        svc = UserService(MagicMock(spec=UserRepository))
        result = await svc.deactivate_user("u1")
        assert result["message"] == "User deactivated successfully"


class TestMapKcUser:
    """Tests for map_kc_user module-level function."""

    def test_maps_name_from_first_last(self) -> None:
        user = map_kc_user(_make_kc_user(first="Jane", last="Smith"))
        assert user.name == "Jane Smith"

    def test_falls_back_to_username(self) -> None:
        kc = _make_kc_user()
        kc["firstName"] = ""
        kc["lastName"] = ""
        user = map_kc_user(kc)
        assert user.name == "john@test.com"

    def test_deactivated_when_disabled(self) -> None:
        user = map_kc_user(_make_kc_user(enabled=False))
        assert user.status == UserStatus.DEACTIVATED

    def test_unknown_role_defaults_to_viewer(self) -> None:
        user = map_kc_user(_make_kc_user(role="unknown_role"))
        assert user.role == UserRole.VIEWER
