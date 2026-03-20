"""User repository — queries Keycloak admin API for user management."""
import logging

import httpx

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class UserRepositoryError(Exception):
    """Raised when a user repository operation fails."""


class UserAlreadyExistsError(UserRepositoryError):
    """Raised when inviting a user that already exists."""


def build_admin_url(base_url: str, realm: str) -> str:
    """Build admin API base URL for a realm."""
    return f"{base_url}/admin/realms/{realm}"


def build_token_url(base_url: str, realm: str) -> str:
    """Build the token endpoint URL for a realm."""
    return f"{base_url}/realms/{realm}/protocol/openid-connect/token"


def build_repo_config() -> dict[str, str]:
    """Build configuration dict from settings."""
    settings = get_settings()
    return {
        "base_url": settings.KEYCLOAK_URL.rstrip("/"),
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
    }


def make_create_payload(
    email: str, role: str,
    username: str = "", password: str = "",
    first_name: str = "", last_name: str = "",
) -> dict[str, object]:
    """Build Keycloak user creation payload."""
    return {
        "email": email,
        "username": username or email,
        "firstName": first_name or username or email.split("@")[0],
        "lastName": last_name or "User",
        "enabled": True,
        "emailVerified": True,
        "credentials": [
            {"type": "password", "value": password or "changeme123", "temporary": False},
        ],
    }


def make_deactivate_payload() -> dict[str, object]:
    """Build payload for deactivating a user."""
    return {"enabled": False, "attributes": {"status": ["deactivated"]}}


def make_update_payload(
    role: str | None, enabled: bool | None,
) -> dict[str, object]:
    """Build payload for updating a user."""
    payload: dict[str, object] = {}
    if enabled is not None:
        payload["enabled"] = enabled
    if role is not None:
        payload["attributes"] = {"role": [role]}
    return payload


def make_auth_data(client_id: str, client_secret: str) -> dict[str, str]:
    """Build auth form data for admin token via master realm."""
    return {
        "grant_type": "password",
        "client_id": "admin-cli",
        "username": "admin",
        "password": "admin",
    }


class UserRepository:
    """Repository for managing users via Keycloak Admin REST API."""

    def __init__(self, realm: str) -> None:
        """Initialize with a Keycloak realm name."""
        self._realm = realm
        cfg = build_repo_config()
        self._base_url = cfg["base_url"]
        self._client_id = cfg["client_id"]
        self._client_secret = cfg["client_secret"]
        self._admin_base = build_admin_url(self._base_url, realm)
        self._token_url = build_token_url(self._base_url, realm)
