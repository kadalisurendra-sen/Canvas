"""Keycloak admin client for realm and user management."""
import logging
from urllib.parse import urljoin

import httpx

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class KeycloakClient:
    """Client for Keycloak Admin REST API and OIDC endpoints."""

    def __init__(self, realm_override: str = "") -> None:
        """Initialize Keycloak client with settings."""
        settings = get_settings()
        self._base_url = settings.KEYCLOAK_URL.rstrip("/")
        self._realm = realm_override or settings.KEYCLOAK_REALM
        self._client_id = settings.KEYCLOAK_CLIENT_ID
        self._client_secret = settings.KEYCLOAK_CLIENT_SECRET

    @property
    def issuer_url(self) -> str:
        """OIDC issuer URL for the configured realm."""
        return f"{self._base_url}/realms/{self._realm}"

    @property
    def auth_url(self) -> str:
        """Authorization endpoint for OIDC login."""
        return (
            f"{self.issuer_url}/protocol/openid-connect/auth"
        )

    @property
    def token_url(self) -> str:
        """Token endpoint for code exchange."""
        return (
            f"{self.issuer_url}/protocol/openid-connect/token"
        )

    @property
    def logout_url(self) -> str:
        """Logout endpoint for token revocation."""
        return (
            f"{self.issuer_url}/protocol/openid-connect/logout"
        )

    @property
    def jwks_url(self) -> str:
        """JWKS endpoint for JWT validation."""
        return (
            f"{self.issuer_url}/protocol/openid-connect/certs"
        )

    @property
    def userinfo_url(self) -> str:
        """Userinfo endpoint."""
        return (
            f"{self.issuer_url}/protocol/openid-connect/userinfo"
        )

    async def get_jwks(self) -> dict[str, list[dict[str, str]]]:
        """Fetch the JWKS from the Keycloak realm."""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url, timeout=10.0)
            response.raise_for_status()
            result: dict[str, list[dict[str, str]]] = response.json()
            return result

    async def exchange_code(
        self, code: str, redirect_uri: str
    ) -> dict[str, str]:
        """Exchange authorization code for tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            result: dict[str, str] = response.json()
            return result

    async def password_grant(
        self, username: str, password: str
    ) -> dict[str, str]:
        """Authenticate user with direct access grant (password)."""
        data: dict[str, str] = {
            "grant_type": "password",
            "client_id": self._client_id,
            "username": username,
            "password": password,
            "scope": "openid profile email",
        }
        # Include client_secret if configured (required for confidential clients)
        if self._client_secret:
            data["client_secret"] = self._client_secret

        logger.info(
            "password_grant: realm=%s, client=%s, user=%s, token_url=%s",
            self._realm, self._client_id, username, self.token_url,
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url, data=data, timeout=10.0,
            )
            if response.status_code != 200:
                logger.error(
                    "password_grant failed: status=%s, body=%s",
                    response.status_code, response.text,
                )
            response.raise_for_status()
            result: dict[str, str] = response.json()
            return result

    async def refresh_grant(self, refresh_token: str) -> dict[str, str]:
        """Exchange a refresh token for new access + refresh tokens."""
        data: dict[str, str] = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "refresh_token": refresh_token,
        }
        if self._client_secret:
            data["client_secret"] = self._client_secret

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url, data=data, timeout=10.0,
            )
            response.raise_for_status()
            result: dict[str, str] = response.json()
            return result

    async def revoke_token(self, refresh_token: str) -> None:
        """Revoke a refresh token at Keycloak."""
        async with httpx.AsyncClient() as client:
            await client.post(
                self.logout_url,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "refresh_token": refresh_token,
                },
                timeout=10.0,
            )
