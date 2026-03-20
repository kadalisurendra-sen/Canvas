"""Async operations for user repository — Keycloak API calls."""
import asyncio
import logging
import time

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

# Cache admin token to avoid ~700ms token fetch on every request
_token_cache: dict[str, tuple[str, float]] = {}
_TOKEN_TTL = 50  # seconds (Keycloak default is 60s, use 50 for safety)


async def get_admin_token(repo: UserRepository) -> str:
    """Obtain an admin token via master realm password grant (cached)."""
    cache_key = repo._base_url
    cached = _token_cache.get(cache_key)
    if cached and cached[1] > time.monotonic():
        return cached[0]

    auth_data = make_auth_data(repo._client_id, repo._client_secret)
    master_token_url = f"{repo._base_url}/realms/master/protocol/openid-connect/token"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            master_token_url, data=auth_data, timeout=10.0,
        )
        resp.raise_for_status()
        data: dict[str, str] = resp.json()
        token = data["access_token"]
        _token_cache[cache_key] = (token, time.monotonic() + _TOKEN_TTL)
        return token


_APP_ROLES = ("system_admin", "admin", "contributor", "viewer")


async def list_users(
    repo: UserRepository, search: str = "",
    first: int = 0, max_results: int = 10,
) -> list[dict[str, object]]:
    """List users from the Keycloak realm with their realm roles."""
    token = await get_admin_token(repo)
    params: dict[str, str | int] = {
        "first": first, "max": max_results,
        "briefRepresentation": "false",
    }
    if search:
        params["search"] = search
    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = {"Authorization": f"Bearer {token}"}

        # Fetch users and role-to-user mappings in parallel
        async def fetch_users() -> list[dict[str, object]]:
            resp = await client.get(
                f"{repo._admin_base}/users",
                headers=headers, params=params,
            )
            resp.raise_for_status()
            return resp.json()

        async def fetch_role_users(role: str) -> tuple[str, set[str]]:
            try:
                resp = await client.get(
                    f"{repo._admin_base}/roles/{role}/users",
                    headers=headers,
                )
                if resp.status_code == 200:
                    return role, {str(u.get("id", "")) for u in resp.json()}
            except Exception:
                pass
            return role, set()

        users_result, *role_results = await asyncio.gather(
            fetch_users(),
            *(fetch_role_users(r) for r in _APP_ROLES),
        )

        # Build user_id -> roles mapping
        role_map: dict[str, list[str]] = {}
        for role_name, user_ids in role_results:
            for uid in user_ids:
                role_map.setdefault(uid, []).append(role_name)

        # Attach roles to users
        for user in users_result:
            uid = str(user.get("id", ""))
            user["_realm_roles"] = role_map.get(uid, [])

        return users_result


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
    username: str = "", password: str = "",
    first_name: str = "", last_name: str = "",
) -> dict[str, object]:
    """Create a user in Keycloak and return their data."""
    token = await get_admin_token(repo)
    payload = make_create_payload(
        email, role, username=username, password=password,
        first_name=first_name, last_name=last_name,
    )
    logger.info(
        "Creating user in Keycloak: email=%s, username=%s, realm_url=%s",
        email, username or email, repo._admin_base,
    )
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
        if resp.status_code != 201:
            logger.error(
                "Keycloak user creation failed: status=%s, body=%s, admin_base=%s",
                resp.status_code, resp.text, repo._admin_base,
            )
        resp.raise_for_status()
        location = resp.headers.get("Location", "")
        user_id = location.rsplit("/", 1)[-1] if location else ""
        logger.info("User created in Keycloak: id=%s, email=%s", user_id, email)

        # Keycloak 24+ ignores credentials in create payload — set password explicitly
        if user_id:
            actual_password = password or "changeme123"
            pwd_resp = await client.put(
                f"{repo._admin_base}/users/{user_id}/reset-password",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "type": "password",
                    "value": actual_password,
                    "temporary": False,
                },
                timeout=10.0,
            )
            if pwd_resp.status_code == 204:
                logger.info("Password set for user %s", user_id)
            else:
                logger.error(
                    "Failed to set password for user %s: status=%s, body=%s",
                    user_id, pwd_resp.status_code, pwd_resp.text,
                )

        # Assign realm role to the new user
        if user_id and role:
            headers = {"Authorization": f"Bearer {token}"}
            role_resp = await client.get(
                f"{repo._admin_base}/roles/{role}",
                headers=headers, timeout=10.0,
            )
            if role_resp.status_code == 200:
                role_repr = role_resp.json()
                assign_resp = await client.post(
                    f"{repo._admin_base}/users/{user_id}/role-mappings/realm",
                    headers=headers,
                    json=[role_repr], timeout=10.0,
                )
                logger.info(
                    "Role '%s' assigned to user %s: status=%s",
                    role, user_id, assign_resp.status_code,
                )
            else:
                logger.warning(
                    "Role '%s' not found in realm: status=%s",
                    role, role_resp.status_code,
                )

        return {"id": user_id, "email": email, "role": role}


async def update_user(
    repo: UserRepository, user_id: str,
    role: str | None, enabled: bool | None,
) -> None:
    """Update user attributes and realm role in Keycloak."""
    token = await get_admin_token(repo)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Fetch current user to preserve existing fields
        get_resp = await client.get(
            f"{repo._admin_base}/users/{user_id}",
            headers=headers,
        )
        get_resp.raise_for_status()
        current_user = get_resp.json()

        # Merge changes into existing representation
        if enabled is not None:
            current_user["enabled"] = enabled
        if role is not None:
            attrs = current_user.get("attributes") or {}
            attrs["role"] = [role]
            current_user["attributes"] = attrs

        resp = await client.put(
            f"{repo._admin_base}/users/{user_id}",
            headers=headers, json=current_user,
        )
        resp.raise_for_status()

        # Update realm role if role changed
        if role:
            # Fetch old roles and new role definition in parallel
            old_roles_resp, new_role_resp = await asyncio.gather(
                client.get(
                    f"{repo._admin_base}/users/{user_id}/role-mappings/realm",
                    headers=headers,
                ),
                client.get(
                    f"{repo._admin_base}/roles/{role}",
                    headers=headers,
                ),
            )

            # Remove old app roles
            if old_roles_resp.status_code == 200:
                old_roles = [
                    r for r in old_roles_resp.json()
                    if r.get("name") in ("system_admin", "admin", "contributor", "viewer")
                ]
                if old_roles:
                    await client.request(
                        "DELETE",
                        f"{repo._admin_base}/users/{user_id}/role-mappings/realm",
                        headers=headers, json=old_roles,
                    )

            # Assign new role
            if new_role_resp.status_code == 200:
                await client.post(
                    f"{repo._admin_base}/users/{user_id}/role-mappings/realm",
                    headers=headers, json=[new_role_resp.json()],
                )


async def deactivate_user(repo: UserRepository, user_id: str) -> None:
    """Deactivate a user by disabling their Keycloak account."""
    token = await get_admin_token(repo)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Fetch current user to preserve existing fields
        get_resp = await client.get(
            f"{repo._admin_base}/users/{user_id}",
            headers=headers,
        )
        get_resp.raise_for_status()
        current_user = get_resp.json()

        # Merge deactivation into existing representation
        current_user["enabled"] = False
        attrs = current_user.get("attributes") or {}
        attrs["status"] = ["deactivated"]
        current_user["attributes"] = attrs

        resp = await client.put(
            f"{repo._admin_base}/users/{user_id}",
            headers=headers, json=current_user,
        )
        resp.raise_for_status()


async def delete_user(repo: UserRepository, user_id: str) -> None:
    """Permanently delete a user from Keycloak."""
    token = await get_admin_token(repo)
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.delete(
            f"{repo._admin_base}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
    logger.info("User %s permanently deleted", user_id)
