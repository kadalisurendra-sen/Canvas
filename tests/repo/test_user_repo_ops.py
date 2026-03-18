"""Tests for user_repo_ops async Keycloak API calls."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.repo.user_repo_ops import (
    count_users,
    create_user,
    deactivate_user,
    get_admin_token,
    list_users,
    update_user,
)
from src.repo.user_repository import UserAlreadyExistsError, UserRepository


def _mock_repo() -> MagicMock:
    """Create a mock UserRepository."""
    repo = MagicMock(spec=UserRepository)
    repo._client_id = "test-client"
    repo._client_secret = "test-secret"
    repo._token_url = "http://kc:8080/realms/test/protocol/openid-connect/token"
    repo._admin_base = "http://kc:8080/admin/realms/test"
    return repo


class TestGetAdminToken:
    """Tests for get_admin_token."""

    @pytest.mark.asyncio
    @patch("src.repo.user_repo_ops.httpx.AsyncClient")
    async def test_returns_token(self, mock_client_cls: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"access_token": "tok123"}
        mock_resp.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        repo = _mock_repo()
        token = await get_admin_token(repo)
        assert token == "tok123"


class TestListUsers:
    """Tests for list_users."""

    @pytest.mark.asyncio
    @patch("src.repo.user_repo_ops.get_admin_token", new_callable=AsyncMock)
    @patch("src.repo.user_repo_ops.httpx.AsyncClient")
    async def test_returns_user_list(
        self, mock_client_cls: MagicMock, mock_token: AsyncMock
    ) -> None:
        mock_token.return_value = "tok"
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"id": "u1", "email": "a@b.com"}]
        mock_resp.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        repo = _mock_repo()
        result = await list_users(repo, search="test", first=0, max_results=10)
        assert len(result) == 1
        assert result[0]["id"] == "u1"

    @pytest.mark.asyncio
    @patch("src.repo.user_repo_ops.get_admin_token", new_callable=AsyncMock)
    @patch("src.repo.user_repo_ops.httpx.AsyncClient")
    async def test_list_without_search(
        self, mock_client_cls: MagicMock, mock_token: AsyncMock
    ) -> None:
        mock_token.return_value = "tok"
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_resp.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await list_users(_mock_repo())
        assert result == []


class TestCountUsers:
    """Tests for count_users."""

    @pytest.mark.asyncio
    @patch("src.repo.user_repo_ops.get_admin_token", new_callable=AsyncMock)
    @patch("src.repo.user_repo_ops.httpx.AsyncClient")
    async def test_returns_count(
        self, mock_client_cls: MagicMock, mock_token: AsyncMock
    ) -> None:
        mock_token.return_value = "tok"
        mock_resp = MagicMock()
        mock_resp.json.return_value = 42
        mock_resp.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        count = await count_users(_mock_repo(), search="test")
        assert count == 42


class TestCreateUser:
    """Tests for create_user."""

    @pytest.mark.asyncio
    @patch("src.repo.user_repo_ops.get_admin_token", new_callable=AsyncMock)
    @patch("src.repo.user_repo_ops.httpx.AsyncClient")
    async def test_creates_user(
        self, mock_client_cls: MagicMock, mock_token: AsyncMock
    ) -> None:
        mock_token.return_value = "tok"
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.headers = {"Location": "http://kc/users/new-id-123"}
        mock_resp.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await create_user(_mock_repo(), "new@test.com", "viewer")
        assert result["email"] == "new@test.com"
        assert result["id"] == "new-id-123"

    @pytest.mark.asyncio
    @patch("src.repo.user_repo_ops.get_admin_token", new_callable=AsyncMock)
    @patch("src.repo.user_repo_ops.httpx.AsyncClient")
    async def test_conflict_raises(
        self, mock_client_cls: MagicMock, mock_token: AsyncMock
    ) -> None:
        mock_token.return_value = "tok"
        mock_resp = MagicMock()
        mock_resp.status_code = 409
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with pytest.raises(UserAlreadyExistsError):
            await create_user(_mock_repo(), "dup@test.com", "admin")


class TestUpdateUser:
    """Tests for update_user."""

    @pytest.mark.asyncio
    @patch("src.repo.user_repo_ops.get_admin_token", new_callable=AsyncMock)
    @patch("src.repo.user_repo_ops.httpx.AsyncClient")
    async def test_updates_user(
        self, mock_client_cls: MagicMock, mock_token: AsyncMock
    ) -> None:
        mock_token.return_value = "tok"
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.put.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        await update_user(_mock_repo(), "u1", "admin", True)
        mock_client.put.assert_awaited_once()


class TestDeactivateUser:
    """Tests for deactivate_user."""

    @pytest.mark.asyncio
    @patch("src.repo.user_repo_ops.get_admin_token", new_callable=AsyncMock)
    @patch("src.repo.user_repo_ops.httpx.AsyncClient")
    async def test_deactivates_user(
        self, mock_client_cls: MagicMock, mock_token: AsyncMock
    ) -> None:
        mock_token.return_value = "tok"
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.put.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        await deactivate_user(_mock_repo(), "u1")
        mock_client.put.assert_awaited_once()
