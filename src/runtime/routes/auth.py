"""Authentication routes — login, callback, logout, me, register."""
import logging

from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel

from src.config.settings import get_settings
from src.service.keycloak_client import KeycloakClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Login request with username and password."""

    username: str
    password: str


class RegisterRequest(BaseModel):
    """Registration request."""

    email: str
    username: str
    password: str
    first_name: str = ""
    last_name: str = ""


@router.post("/login")
async def login(
    body: LoginRequest,
    response: Response,
) -> dict[str, str]:
    """Authenticate user via Keycloak direct access grant."""
    settings = get_settings()
    kc = KeycloakClient()

    try:
        tokens = await kc.password_grant(body.username, body.password)
    except Exception as exc:
        logger.warning("Login failed for %s: %s", body.username, exc)
        raise HTTPException(
            status_code=401, detail="Invalid username or password"
        ) from exc

    access_token = tokens.get("access_token", "")
    is_secure = settings.APP_ENV != "development"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=3600,
    )

    return {"message": "Login successful", "redirect": "/templates"}


@router.post("/register")
async def register(body: RegisterRequest) -> dict[str, str]:
    """Register via Keycloak Admin API."""
    settings = get_settings()
    kc_url = settings.KEYCLOAK_URL.rstrip("/")
    realm = settings.KEYCLOAK_REALM

    import httpx

    async with httpx.AsyncClient() as client:
        # Get admin token
        token_resp = await client.post(
            f"{kc_url}/realms/master/protocol/openid-connect/token",
            data={
                "grant_type": "client_credentials",
                "client_id": "admin-cli",
                "client_secret": "",
                "username": "admin",
                "password": "admin",
                "grant_type": "password",
            },
            timeout=10.0,
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=500, detail="Registration service unavailable"
            )

        admin_token = token_resp.json()["access_token"]

        # Create user
        user_resp = await client.post(
            f"{kc_url}/admin/realms/{realm}/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "username": body.username,
                "email": body.email,
                "firstName": body.first_name,
                "lastName": body.last_name,
                "enabled": True,
                "credentials": [
                    {
                        "type": "password",
                        "value": body.password,
                        "temporary": False,
                    }
                ],
            },
            timeout=10.0,
        )

        if user_resp.status_code == 409:
            raise HTTPException(
                status_code=409, detail="Username or email already exists"
            )
        if user_resp.status_code != 201:
            logger.error("Registration failed: %s", user_resp.text)
            raise HTTPException(
                status_code=500, detail="Registration failed"
            )

    return {"message": "Registration successful. You can now sign in."}


@router.post("/logout")
async def logout(
    response: Response,
    access_token: str = Cookie(default=""),
) -> dict[str, str]:
    """Clear session cookie and revoke token."""
    if access_token:
        try:
            kc = KeycloakClient()
            await kc.revoke_token(access_token)
        except Exception as exc:
            logger.warning("Token revocation failed: %s", exc)

    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_profile(
    access_token: str = Cookie(default=""),
) -> dict[str, str | list[str]]:
    """Return current user profile from JWT."""
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Decode JWT using Keycloak JWKS
    import httpx
    from jose import jwt as jose_jwt, JWTError

    kc = KeycloakClient()
    try:
        async with httpx.AsyncClient() as client:
            jwks_resp = await client.get(kc.jwks_url, timeout=10.0)
            jwks_data = jwks_resp.json()

        # Decode without audience verification (Keycloak uses 'account')
        header = jose_jwt.get_unverified_header(access_token)
        kid = header.get("kid")

        signing_key = None
        for key in jwks_data.get("keys", []):
            if key.get("kid") == kid:
                signing_key = key
                break

        if not signing_key:
            raise HTTPException(status_code=401, detail="Invalid token signing key")

        payload = jose_jwt.decode(
            access_token,
            signing_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except JWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc

    # Extract roles from realm_access
    realm_access = payload.get("realm_access", {})
    roles = realm_access.get("roles", []) if isinstance(realm_access, dict) else []
    # Filter to only app roles
    app_roles = [r for r in roles if r in ("admin", "contributor", "viewer")]

    return {
        "id": payload.get("sub", ""),
        "email": payload.get("email", ""),
        "name": payload.get("name", ""),
        "roles": app_roles,
    }
