"""Master setup script: starts Docker services and runs all setup steps."""
import logging
import subprocess
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_DIR = "C:/Users/kadalisurendra/Desktop/canvas_v1"
MAX_RETRIES = 30
RETRY_DELAY = 3


def check_docker() -> None:
    """Verify Docker is running."""
    logger.info("Checking Docker is running...")
    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        logger.error(
            "Docker is not running. Please start Docker Desktop and retry.",
        )
        sys.exit(1)
    logger.info("Docker is running.")


def start_services() -> None:
    """Start postgres, redis, keycloak via docker-compose."""
    logger.info("Starting Docker services (postgres, redis, keycloak)...")
    result = subprocess.run(
        ["docker", "compose", "up", "-d", "postgres", "redis", "keycloak"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=PROJECT_DIR,
    )
    if result.returncode != 0:
        logger.error("docker compose up failed: %s", result.stderr.strip())
        sys.exit(1)
    logger.info("Docker services started.")


def wait_for_service_healthy(
    service: str,
    check_cmd: list[str],
    max_retries: int = MAX_RETRIES,
) -> None:
    """Wait for a Docker service to become healthy."""
    logger.info("Waiting for %s to be healthy...", service)
    for attempt in range(1, max_retries + 1):
        result = subprocess.run(
            check_cmd,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            logger.info("%s is healthy.", service)
            return
        logger.info(
            "  Attempt %d/%d - %s not ready, retrying in %ds...",
            attempt, max_retries, service, RETRY_DELAY,
        )
        time.sleep(RETRY_DELAY)
    logger.error("%s did not become healthy.", service)
    sys.exit(1)


def run_script(script_name: str) -> None:
    """Run a Python setup script."""
    logger.info("Running %s...", script_name)
    result = subprocess.run(
        ["py", f"scripts/{script_name}"],
        text=True,
        timeout=300,
        cwd=PROJECT_DIR,
    )
    if result.returncode != 0:
        logger.error("%s failed with exit code %d.", script_name, result.returncode)
        sys.exit(1)
    logger.info("%s completed successfully.", script_name)


def print_summary() -> None:
    """Print setup summary with URLs and credentials."""
    summary = """
============================================================
  Helio Canvas - Setup Complete
============================================================

  Services:
    App (backend):     http://localhost:8000
    Frontend:          http://localhost:5173
    Keycloak Admin:    http://localhost:8080
                       Username: admin / Password: admin

  Test Users (Keycloak helio realm):
    Admin user:        admin / admin123
                       Email: admin@helio.local
    Viewer user:       viewer / viewer123
                       Email: viewer@helio.local

  Databases:
    Platform DB:       db_platform (postgres://localhost:5432)
    Tenant DB:         db_tenant_acme (postgres://localhost:5432)

  Next steps:
    1. Start the backend:   make run
    2. Start the frontend:  make frontend-dev
    3. Open http://localhost:5173 and log in

============================================================
"""
    print(summary)


def main() -> None:
    """Run the full setup pipeline."""
    logger.info("=== Helio Canvas Full Setup ===")

    check_docker()
    start_services()

    # Wait for PostgreSQL
    wait_for_service_healthy(
        "PostgreSQL",
        [
            "docker", "exec", "canvas_v1-postgres-1",
            "pg_isready", "-U", "postgres",
        ],
    )

    # Run database setup
    run_script("setup_db.py")

    # Wait for Keycloak (just check HTTP, detailed wait is in the script)
    logger.info(
        "Giving Keycloak a few seconds to initialize before setup...",
    )
    time.sleep(5)

    # Run Keycloak setup
    run_script("setup_keycloak.py")

    print_summary()
    logger.info("=== Full Setup Complete ===")


if __name__ == "__main__":
    main()
