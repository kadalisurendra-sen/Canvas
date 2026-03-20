"""Setup Keycloak with multiple tenant realms, clients, roles, and test users."""
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
CLIENT_ID = "helio-admin"

MAX_RETRIES = 30
RETRY_DELAY = 3

# Realm definitions: (realm_name, display_name)
REALMS = [
    ("realm-acme", "Acme Corporation"),
    ("realm-globex", "Globex Industries"),
    ("realm-initech", "Initech Solutions"),
]

# Test users per realm: (username, email, first, last, password, role)
TEST_USERS = [
    ("admin", "admin@{realm}.local", "Alex", "Rivera", "admin123", "admin"),
    ("viewer", "viewer@{realm}.local", "Sarah", "Connor", "viewer123", "viewer"),
]


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
    logger.error("Keycloak did not become ready.")
    sys.exit(1)


def get_admin_token(client: httpx.Client) -> str:
    """Obtain an admin access token from the master realm."""
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
    return resp.json()["access_token"]


def create_realm(client: httpx.Client, token: str, realm_name: str, display: str) -> None:
    """Create a realm if it does not exist."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get(f"{KEYCLOAK_URL}/admin/realms/{realm_name}", headers=headers)
    if resp.status_code == 200:
        logger.info("Realm '%s' already exists.", realm_name)
        return

    resp = client.post(
        f"{KEYCLOAK_URL}/admin/realms",
        headers=headers,
        json={
            "realm": realm_name,
            "displayName": display,
            "enabled": True,
            "registrationAllowed": True,
            "loginWithEmailAllowed": True,
        },
    )
    resp.raise_for_status()
    logger.info("Realm '%s' created.", realm_name)


def create_client(client: httpx.Client, token: str, realm_name: str) -> None:
    """Create the helio-admin client in a realm."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get(
        f"{KEYCLOAK_URL}/admin/realms/{realm_name}/clients",
        headers=headers,
        params={"clientId": CLIENT_ID},
    )
    resp.raise_for_status()
    if resp.json():
        logger.info("Client '%s' already exists in '%s'.", CLIENT_ID, realm_name)
        return

    resp = client.post(
        f"{KEYCLOAK_URL}/admin/realms/{realm_name}/clients",
        headers=headers,
        json={
            "clientId": CLIENT_ID,
            "publicClient": True,
            "directAccessGrantsEnabled": True,
            "redirectUris": ["http://localhost:5173/*", "http://localhost:5174/*", "http://localhost:8000/*"],
            "webOrigins": ["http://localhost:5173", "http://localhost:5174", "http://localhost:8000"],
            "standardFlowEnabled": True,
            "rootUrl": "http://localhost:5173",
        },
    )
    resp.raise_for_status()
    logger.info("Client '%s' created in '%s'.", CLIENT_ID, realm_name)


def create_realm_roles(client: httpx.Client, token: str, realm_name: str) -> None:
    """Create realm roles: admin, contributor, viewer."""
    headers = {"Authorization": f"Bearer {token}"}
    for role_name in ["admin", "contributor", "viewer"]:
        resp = client.post(
            f"{KEYCLOAK_URL}/admin/realms/{realm_name}/roles",
            headers=headers,
            json={"name": role_name},
        )
        if resp.status_code == 409:
            logger.info("Role '%s' already exists in '%s'.", role_name, realm_name)
        else:
            resp.raise_for_status()
            logger.info("Role '%s' created in '%s'.", role_name, realm_name)


def create_user(
    client: httpx.Client, token: str, realm_name: str,
    username: str, email: str, first_name: str, last_name: str,
    password: str, role_name: str,
) -> None:
    """Create a user and assign a role in a realm."""
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get(
        f"{KEYCLOAK_URL}/admin/realms/{realm_name}/users",
        headers=headers,
        params={"username": username, "exact": "true"},
    )
    resp.raise_for_status()
    existing = resp.json()

    if existing:
        user_id = existing[0]["id"]
        logger.info("User '%s' already exists in '%s'.", username, realm_name)
    else:
        resp = client.post(
            f"{KEYCLOAK_URL}/admin/realms/{realm_name}/users",
            headers=headers,
            json={
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": True,
                "emailVerified": True,
                "credentials": [{"type": "password", "value": password, "temporary": False}],
            },
        )
        resp.raise_for_status()
        logger.info("User '%s' created in '%s'.", username, realm_name)

        resp = client.get(
            f"{KEYCLOAK_URL}/admin/realms/{realm_name}/users",
            headers=headers,
            params={"username": username, "exact": "true"},
        )
        resp.raise_for_status()
        user_id = resp.json()[0]["id"]

    # Assign role
    resp = client.get(
        f"{KEYCLOAK_URL}/admin/realms/{realm_name}/roles/{role_name}",
        headers=headers,
    )
    resp.raise_for_status()
    role_repr = resp.json()

    client.post(
        f"{KEYCLOAK_URL}/admin/realms/{realm_name}/users/{user_id}/role-mappings/realm",
        headers=headers,
        json=[role_repr],
    )
    logger.info("Role '%s' assigned to '%s' in '%s'.", role_name, username, realm_name)


def main() -> None:
    """Run the full Keycloak setup for all tenant realms."""
    logger.info("=== Keycloak Multi-Tenant Setup ===")
    with httpx.Client(timeout=30) as http:
        wait_for_keycloak(http)
        token = get_admin_token(http)

        for realm_name, display_name in REALMS:
            logger.info("--- Setting up realm: %s ---", realm_name)
            create_realm(http, token, realm_name, display_name)
            create_client(http, token, realm_name)
            create_realm_roles(http, token, realm_name)

            for username, email_tpl, first, last, pwd, role in TEST_USERS:
                email = email_tpl.replace("{realm}", realm_name)
                create_user(http, token, realm_name, username, email, first, last, pwd, role)

    logger.info("=== Keycloak Setup Complete ===")
    logger.info("Realms created: %s", [r[0] for r in REALMS])
    logger.info("Test users: admin/admin123, viewer/viewer123 (in each realm)")


if __name__ == "__main__":
    main()
