"""JWT validation and user context extraction."""
import logging
import uuid
from datetime import datetime, timezone

from jose import JWTError, jwt
from jose.backends import RSAKey

from src.config.settings import get_settings
from src.types.auth import TokenPayload, UserContext
from src.types.enums import UserRole

logger = logging.getLogger(__name__)


class AuthServiceError(Exception):
    """Raised when authentication fails."""


class TokenExpiredError(AuthServiceError):
    """Raised when the JWT is expired."""


class InvalidTokenError(AuthServiceError):
    """Raised when the JWT is malformed or signature fails."""


class AuthService:
    """JWT validation and role extraction service."""

    def __init__(self) -> None:
        """Initialize with empty JWKS cache."""
        self._jwks: dict[str, list[dict[str, str]]] = {}
        settings = get_settings()
        self._algorithm = settings.JWT_ALGORITHM
        self._audience = settings.JWT_AUDIENCE
        self._issuer = (
            f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}"
        )

    def set_jwks(self, jwks: dict[str, list[dict[str, str]]]) -> None:
        """Cache the JWKS keys for token validation."""
        self._jwks = jwks

    def _get_signing_key(self, token: str) -> dict[str, str]:
        """Extract the signing key from JWKS matching the token header."""
        try:
            header = jwt.get_unverified_header(token)
        except JWTError as exc:
            raise InvalidTokenError("Cannot decode token header") from exc

        kid = header.get("kid")
        if not kid:
            raise InvalidTokenError("Token header missing 'kid'")

        keys = self._jwks.get("keys", [])
        for key in keys:
            if key.get("kid") == kid:
                return key

        raise InvalidTokenError(f"No matching key found for kid={kid}")

    def decode_token(self, token: str) -> TokenPayload:
        """Decode and validate a JWT access token."""
        signing_key = self._get_signing_key(token)

        try:
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=[self._algorithm],
                audience=self._audience,
                issuer=self._issuer,
                options={"verify_aud": False},
            )
        except JWTError as exc:
            error_msg = str(exc)
            if "expired" in error_msg.lower():
                raise TokenExpiredError("Token has expired") from exc
            raise InvalidTokenError(f"Token validation failed: {error_msg}") from exc

        return self._parse_payload(payload)

    def _parse_payload(
        self, payload: dict[str, object]
    ) -> TokenPayload:
        """Parse raw JWT payload into a typed TokenPayload."""
        roles_raw = self._extract_roles(payload)
        roles = []
        for role_str in roles_raw:
            try:
                roles.append(UserRole(role_str))
            except ValueError:
                logger.warning("Unknown role in token: %s", role_str)

        return TokenPayload(
            sub=str(payload.get("sub", "")),
            email=str(payload.get("email", "")),
            name=str(payload.get("name", "")),
            roles=roles,
            tenant_id=str(payload.get("tenant_id", "")),
            exp=int(payload.get("exp", 0)),
        )

    def _extract_roles(
        self, payload: dict[str, object]
    ) -> list[str]:
        """Extract roles from realm_access.roles in the JWT."""
        realm_access = payload.get("realm_access", {})
        if isinstance(realm_access, dict):
            roles = realm_access.get("roles", [])
            if isinstance(roles, list):
                return [str(r) for r in roles]
        return []

    def get_user_context(self, token_payload: TokenPayload) -> UserContext:
        """Convert a TokenPayload into a UserContext."""
        # Default tenant for now — will be resolved from tenant registry
        default_tenant = "a0000000-0000-0000-0000-000000000001"
        tenant_id = token_payload.tenant_id or default_tenant
        try:
            tid = uuid.UUID(tenant_id)
        except ValueError:
            tid = uuid.UUID(default_tenant)

        return UserContext(
            user_id=uuid.UUID(token_payload.sub),
            email=token_payload.email,
            name=token_payload.name,
            roles=token_payload.roles,
            tenant_id=tid,
        )
