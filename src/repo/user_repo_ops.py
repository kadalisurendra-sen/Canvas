"""Async operations for user repository — Keycloak API calls."""
import logging

import httpx

from src.repo.user_repository import (
    UserAlreadyExistsError,
    UserRepository,
    make_auth_data,
    make_create_payload,
    make_deactivate_payload,
    make_update_payload,
)

logger = logging.getLogger(__name__)


async def get_admin_token(repo: UserRepository) -> str:
    """Obtain an admin token via master realm password grant."""
    auth_data = make_auth_data(repo._client_id, repo._client_secret)
    master_token_url = f"{repo._base_url}/realms/master/protocol/openid-connect/token"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            master_token_url, data=auth_data, timeout=10.0,
        )
        resp.raise_for_status()
        data: dict[str, str] = resp.json()
        return data["access_token"]


async def list_users(
    repo: UserRepository, search: str = "",
    first: int = 0, max_results: int = 10,
) -> list[dict[str, object]]:
    """List users from the Keycloak realm."""
    token = await get_admin_token(repo)
    params: dict[str, str | int] = {
        "first": first, "max": max_results,
        "briefRepresentation": "false",
    }
    if search:
        params["search"] = search
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{repo._admin_base}/users",
            headers={"Authorization": f"Bearer {token}"},
            params=params, timeout=10.0,
        )
        resp.raise_for_status()
        result: list[dict[str, object]] = resp.json()
        return result


async def count_users(repo: UserRepository, search: str = "") -> int:
    """Count total users in the realm."""
    token = await get_admin_token(repo)
    params: dict[str, str] = {}
    if search:
        params["search"] = search
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{repo._admin_base}/users/count",
            headers={"Authorization": f"Bearer {token}"},
            params=params, timeout=10.0,
        )
        resp.raise_for_status()
        count: int = resp.json()
        return count


async def create_user(
    repo: UserRepository, email: str, role: str,
) -> dict[str, object]:
    """Create a user in Keycloak and return their data."""
    token = await get_admin_token(repo)
    payload = make_create_payload(email, role)
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{repo._admin_base}/users",
            headers={"Authorization": f"Bearer {token}"},
            json=payload, timeout=10.0,
        )
        if resp.status_code == 409:
            raise UserAlreadyExistsError(
                f"User with email {email} already exists"
            )
        resp.raise_for_status()
        location = resp.headers.get("Location", "")
        user_id = location.rsplit("/", 1)[-1] if location else ""
        return {"id": user_id, "email": email, "role": role}


async def update_user(
    repo: UserRepository, user_id: str,
    role: str | None, enabled: bool | None,
) -> None:
    """Update user attributes in Keycloak."""
    token = await get_admin_token(repo)
    payload = make_update_payload(role, enabled)
    async with httpx.AsyncClient() as client:
        resp = await client.put(
            f"{repo._admin_base}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=payload, timeout=10.0,
        )
        resp.raise_for_status()


async def deactivate_user(repo: UserRepository, user_id: str) -> None:
    """Deactivate a user by disabling their Keycloak account."""
    token = await get_admin_token(repo)
    payload = make_deactivate_payload()
    async with httpx.AsyncClient() as client:
        resp = await client.put(
            f"{repo._admin_base}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=payload, timeout=10.0,
        )
        resp.raise_for_status()
