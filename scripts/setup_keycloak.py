"""Setup Keycloak realm, client, roles, and test users via Admin REST API."""
import logging
import sys
import time

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

KEYCLOAK_URL = "http://localhost:8080"
ADMIN_USER = "admin"
ADMIN_PASS = "admin"
REALM_NAME = "helio"
CLIENT_ID = "helio-admin"

MAX_RETRIES = 30
RETRY_DELAY = 3


def wait_for_keycloak(client: httpx.Client) -> None:
    """Poll Keycloak until it responds."""
    logger.info("Waiting for Keycloak to be ready...")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.get(
                f"{KEYCLOAK_URL}/realms/master/.well-known/openid-configuration"
            )
            if resp.status_code == 200:
                logger.info("Keycloak is ready.")
                return
        except httpx.ConnectError:
            pass
        except httpx.HTTPError:
            pass
        logger.info(
            "  Attempt %d/%d - not ready yet, retrying in %ds...",
            attempt, MAX_RETRIES, RETRY_DELAY,
        )
        time.sleep(RETRY_DELAY)
    logger.error("Keycloak did not become ready after %d attempts.", MAX_RETRIES)
    sys.exit(1)


def get_admin_token(client: httpx.Client) -> str:
    """Obtain an admin access token from the master realm."""
    logger.info("Obtaining admin token...")
    resp = client.post(
        f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token",
        data={
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": ADMIN_USER,
            "password": ADMIN_PASS,
        },
    )
    resp.raise_for_status()
    token = resp.json()["access_token"]
    logger.info("Admin token obtained.")
    return token


def create_realm(client: httpx.Client, token: str) -> None:
    """Create the helio realm if it does not exist."""
    logger.info("Creating realm '%s'...", REALM_NAME)
    headers = {"Authorization": f"Bearer {token}"}

    # Check if realm exists
    resp = client.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}",
        headers=headers,
    )
    if resp.status_code == 200:
        logger.info("Realm '%s' already exists, skipping.", REALM_NAME)
        return

    resp = client.post(
        f"{KEYCLOAK_URL}/admin/realms",
        headers=headers,
        json={
            "realm": REALM_NAME,
            "enabled": True,
            "registrationAllowed": True,
            "loginWithEmailAllowed": True,
        },
    )
    resp.raise_for_status()
    logger.info("Realm '%s' created.", REALM_NAME)


def create_client(client: httpx.Client, token: str) -> None:
    """Create the helio-admin client in the helio realm."""
    logger.info("Creating client '%s'...", CLIENT_ID)
    headers = {"Authorization": f"Bearer {token}"}

    # Check if client already exists
    resp = client.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients",
        headers=headers,
        params={"clientId": CLIENT_ID},
    )
    resp.raise_for_status()
    existing = resp.json()
    if existing:
        logger.info("Client '%s' already exists, skipping.", CLIENT_ID)
        return

    resp = client.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients",
        headers=headers,
        json={
            "clientId": CLIENT_ID,
            "publicClient": True,
            "directAccessGrantsEnabled": True,
            "redirectUris": [
                "http://localhost:5173/*",
                "http://localhost:8000/*",
            ],
            "webOrigins": [
                "http://localhost:5173",
                "http://localhost:8000",
            ],
            "standardFlowEnabled": True,
            "rootUrl": "http://localhost:5173",
        },
    )
    resp.raise_for_status()
    logger.info("Client '%s' created.", CLIENT_ID)


def create_realm_roles(
    client: httpx.Client, token: str,
) -> None:
    """Create realm roles: admin, contributor, viewer."""
    headers = {"Authorization": f"Bearer {token}"}
    roles = ["admin", "contributor", "viewer"]
    for role_name in roles:
        logger.info("Creating realm role '%s'...", role_name)
        resp = client.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/roles",
            headers=headers,
            json={"name": role_name},
        )
        if resp.status_code == 409:
            logger.info("Role '%s' already exists, skipping.", role_name)
        else:
            resp.raise_for_status()
            logger.info("Role '%s' created.", role_name)


def create_user(
    client: httpx.Client,
    token: str,
    username: str,
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    role_name: str,
) -> None:
    """Create a user and assign a realm role."""
    headers = {"Authorization": f"Bearer {token}"}
    logger.info("Creating user '%s' (%s)...", username, email)

    # Check if user exists
    resp = client.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
        headers=headers,
        params={"username": username, "exact": "true"},
    )
    resp.raise_for_status()
    existing = resp.json()
    if existing:
        logger.info("User '%s' already exists, skipping.", username)
        user_id = existing[0]["id"]
    else:
        resp = client.post(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
            headers=headers,
            json={
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": True,
                "credentials": [
                    {
                        "type": "password",
                        "value": password,
                        "temporary": False,
                    }
                ],
            },
        )
        resp.raise_for_status()
        logger.info("User '%s' created.", username)

        # Fetch user id
        resp = client.get(
            f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users",
            headers=headers,
            params={"username": username, "exact": "true"},
        )
        resp.raise_for_status()
        user_id = resp.json()[0]["id"]

    # Get role representation
    resp = client.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/roles/{role_name}",
        headers=headers,
    )
    resp.raise_for_status()
    role_repr = resp.json()

    # Assign role
    resp = client.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}"
        f"/role-mappings/realm",
        headers=headers,
        json=[role_repr],
    )
    if resp.status_code == 204:
        logger.info("Role '%s' assigned to user '%s'.", role_name, username)
    else:
        resp.raise_for_status()
        logger.info("Role '%s' assigned to user '%s'.", role_name, username)


def main() -> None:
    """Run the full Keycloak setup."""
    logger.info("=== Keycloak Setup ===")
    with httpx.Client(timeout=30) as http:
        wait_for_keycloak(http)
        token = get_admin_token(http)
        create_realm(http, token)
        create_client(http, token)
        create_realm_roles(http, token)
        create_user(
            http, token,
            username="admin",
            email="admin@helio.local",
            first_name="Alex",
            last_name="Rivera",
            password="admin123",
            role_name="admin",
        )
        create_user(
            http, token,
            username="viewer",
            email="viewer@helio.local",
            first_name="Sarah",
            last_name="Connor",
            password="viewer123",
            role_name="viewer",
        )
    logger.info("=== Keycloak Setup Complete ===")


if __name__ == "__main__":
    main()
