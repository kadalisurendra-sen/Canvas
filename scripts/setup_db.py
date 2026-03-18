"""Setup PostgreSQL databases, run migrations, and seed data."""
import logging
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

PG_HOST = "localhost"
PG_PORT = "5432"
PG_USER = "postgres"
PG_PASS = "postgres"
PLATFORM_DB = "db_platform"
TENANT_DB = "db_tenant_acme"

MAX_RETRIES = 20
RETRY_DELAY = 2


def _psql(
    sql: str,
    dbname: str = "postgres",
) -> subprocess.CompletedProcess[str]:
    """Execute SQL via docker exec into the postgres container."""
    cmd = [
        "docker", "exec", "-e", f"PGPASSWORD={PG_PASS}",
        "canvas_v1-postgres-1",
        "psql", "-h", "localhost", "-U", PG_USER, "-d", dbname,
        "-c", sql,
    ]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _psql_check(
    sql: str,
    dbname: str = "postgres",
) -> str:
    """Execute SQL and return stdout, raising on failure."""
    result = _psql(sql, dbname)
    if result.returncode != 0:
        logger.error("psql error: %s", result.stderr.strip())
        raise RuntimeError(f"psql failed: {result.stderr.strip()}")
    return result.stdout


def wait_for_postgres() -> None:
    """Wait until PostgreSQL accepts connections."""
    logger.info("Waiting for PostgreSQL to be ready...")
    for attempt in range(1, MAX_RETRIES + 1):
        result = _psql("SELECT 1;")
        if result.returncode == 0:
            logger.info("PostgreSQL is ready.")
            return
        logger.info(
            "  Attempt %d/%d - not ready, retrying in %ds...",
            attempt, MAX_RETRIES, RETRY_DELAY,
        )
        time.sleep(RETRY_DELAY)
    logger.error("PostgreSQL did not become ready.")
    sys.exit(1)


def create_databases() -> None:
    """Create platform and tenant databases if they don't exist."""
    for db_name in [PLATFORM_DB, TENANT_DB]:
        logger.info("Checking database '%s'...", db_name)
        result = _psql(
            f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';",
        )
        if db_name in result.stdout or "1" not in result.stdout:
            # More reliable check
            check_result = _psql(
                f"SELECT count(*) FROM pg_database "
                f"WHERE datname = '{db_name}';",
            )
            count_line = check_result.stdout.strip().split("\n")
            # Parse count from psql output
            found = False
            for line in count_line:
                stripped = line.strip()
                if stripped.isdigit() and int(stripped) > 0:
                    found = True
                    break
            if found:
                logger.info(
                    "Database '%s' already exists, skipping.", db_name,
                )
                continue

        logger.info("Creating database '%s'...", db_name)
        _psql(f"CREATE DATABASE {db_name};")
        logger.info("Database '%s' created.", db_name)


def run_migrations() -> None:
    """Run Alembic migrations on the platform database."""
    logger.info("Running Alembic migrations on '%s'...", PLATFORM_DB)
    result = subprocess.run(
        ["py", "-m", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd="C:/Users/kadalisurendra/Desktop/canvas_v1",
    )
    if result.returncode != 0:
        logger.warning(
            "Alembic migration returned non-zero: %s",
            result.stderr.strip(),
        )
        logger.warning(
            "This may be OK if migrations haven't been generated yet.",
        )
    else:
        logger.info("Alembic migrations complete.")


def seed_platform_db() -> None:
    """Seed the platform database with the Acme tenant."""
    logger.info("Seeding platform database...")
    tenant_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    sql = f"""
    INSERT INTO tenants (
        id, name, slug, keycloak_realm, db_name,
        db_host, db_port, is_active, created_at, updated_at
    ) VALUES (
        '{tenant_id}', 'Acme Corporation', 'acme', 'helio',
        '{TENANT_DB}', 'localhost', 5432, true,
        '{now}', '{now}'
    ) ON CONFLICT (slug) DO NOTHING;
    """
    _psql_check(sql, PLATFORM_DB)
    logger.info("Platform DB seeded with Acme Corporation tenant.")


def _create_tenant_tables() -> None:
    """Create tenant tables directly via SQL in the tenant database."""
    logger.info("Creating tenant tables in '%s'...", TENANT_DB)

    ddl = """
    CREATE TABLE IF NOT EXISTS master_data_categories (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(100) NOT NULL UNIQUE,
        display_name VARCHAR(200) NOT NULL,
        icon VARCHAR(50),
        sort_order INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS master_data_values (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        category_id UUID NOT NULL
            REFERENCES master_data_categories(id) ON DELETE CASCADE,
        value VARCHAR(200) NOT NULL,
        label VARCHAR(200) NOT NULL,
        severity VARCHAR(20),
        description TEXT,
        is_active BOOLEAN NOT NULL DEFAULT true,
        sort_order INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS templates (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(255) NOT NULL,
        category VARCHAR(100) NOT NULL,
        description TEXT,
        icon VARCHAR(50),
        theme_color VARCHAR(7),
        status VARCHAR(20) NOT NULL DEFAULT 'draft',
        version INTEGER NOT NULL DEFAULT 1,
        created_by UUID NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT now(),
        updated_at TIMESTAMP NOT NULL DEFAULT now()
    );

    CREATE TABLE IF NOT EXISTS template_tags (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        template_id UUID NOT NULL
            REFERENCES templates(id) ON DELETE CASCADE,
        tag VARCHAR(50) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS template_stages (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        template_id UUID NOT NULL
            REFERENCES templates(id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL,
        sort_order INTEGER NOT NULL,
        weight_pct NUMERIC(5,2) DEFAULT 0,
        min_pass_score NUMERIC(5,2),
        fail_action VARCHAR(10) DEFAULT 'warn'
    );

    CREATE TABLE IF NOT EXISTS template_sections (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        stage_id UUID NOT NULL
            REFERENCES template_stages(id) ON DELETE CASCADE,
        name VARCHAR(200) NOT NULL,
        sort_order INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS template_fields (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        section_id UUID NOT NULL
            REFERENCES template_sections(id) ON DELETE CASCADE,
        field_key VARCHAR(100) NOT NULL,
        label VARCHAR(200) NOT NULL,
        field_type VARCHAR(30) NOT NULL,
        help_text TEXT,
        is_mandatory BOOLEAN NOT NULL DEFAULT false,
        is_scoring BOOLEAN NOT NULL DEFAULT false,
        sort_order INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS field_options (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        field_id UUID NOT NULL
            REFERENCES template_fields(id) ON DELETE CASCADE,
        label VARCHAR(200) NOT NULL,
        value VARCHAR(200) NOT NULL,
        score NUMERIC(5,2) DEFAULT 0,
        sort_order INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID,
        user_name VARCHAR(200),
        event_type VARCHAR(30) NOT NULL,
        action VARCHAR(100) NOT NULL,
        details TEXT,
        ip_address VARCHAR(45),
        created_at TIMESTAMP NOT NULL DEFAULT now()
    );
    """
    _psql_check(ddl, TENANT_DB)
    logger.info("Tenant tables created.")


def seed_tenant_db() -> None:
    """Seed the tenant database with master data and a sample template."""
    logger.info("Seeding tenant database '%s'...", TENANT_DB)

    # Create tables first (in case Alembic hasn't run on tenant DB)
    _create_tenant_tables()

    # Master data categories
    categories = [
        ("organizational_taxonomy", "Organizational Taxonomy",
         "sitemap", 1),
        ("kpis", "KPIs", "target", 2),
        ("solution_types", "Solution Types", "lightbulb", 3),
        ("digital_platforms", "Digital Platforms", "monitor", 4),
        ("ml_models", "ML Models", "cpu", 5),
        ("risk_categories", "Risk Categories", "shield-alert", 6),
    ]

    for name, display, icon, order in categories:
        sql = f"""
        INSERT INTO master_data_categories
            (name, display_name, icon, sort_order)
        VALUES ('{name}', '{display}', '{icon}', {order})
        ON CONFLICT (name) DO NOTHING;
        """
        _psql_check(sql, TENANT_DB)
    logger.info("Master data categories seeded.")

    # Get risk_categories id
    result = _psql_check(
        "SELECT id FROM master_data_categories "
        "WHERE name = 'risk_categories';",
        TENANT_DB,
    )
    # Parse UUID from psql output
    risk_cat_id = None
    for line in result.strip().split("\n"):
        stripped = line.strip()
        if len(stripped) == 36 and "-" in stripped:
            risk_cat_id = stripped
            break

    if not risk_cat_id:
        logger.error("Could not find risk_categories ID.")
        sys.exit(1)

    # Risk category values
    risk_values = [
        ("data_privacy", "Data Privacy", "High",
         "Risk of exposing sensitive data", 1),
        ("implementation", "Implementation", "Medium",
         "Risk of failed implementation", 2),
        ("operational", "Operational", "Low",
         "Day-to-day operational risks", 3),
        ("biased_data", "Biased Data", "High",
         "Risk of biased training data affecting outcomes", 4),
    ]

    for value, label, severity, desc, order in risk_values:
        sql = f"""
        INSERT INTO master_data_values
            (category_id, value, label, severity, description,
             is_active, sort_order)
        SELECT '{risk_cat_id}', '{value}', '{label}', '{severity}',
               '{desc}', true, {order}
        WHERE NOT EXISTS (
            SELECT 1 FROM master_data_values
            WHERE category_id = '{risk_cat_id}' AND value = '{value}'
        );
        """
        _psql_check(sql, TENANT_DB)
    logger.info("Risk category values seeded.")

    # Sample template
    template_id = str(uuid.uuid4())
    created_by = str(uuid.uuid4())
    sql = f"""
    INSERT INTO templates
        (id, name, category, description, icon, theme_color,
         status, version, created_by)
    SELECT
        '{template_id}', 'AI/ML Evaluation Framework', 'AI/ML',
        'Comprehensive evaluation framework for AI and ML initiatives '
        'covering desirability, feasibility, and viability.',
        'brain', '#8B5CF6', 'published', 1, '{created_by}'
    WHERE NOT EXISTS (
        SELECT 1 FROM templates
        WHERE name = 'AI/ML Evaluation Framework'
    );
    """
    _psql_check(sql, TENANT_DB)

    # Get the actual template id (might have existed already)
    result = _psql_check(
        "SELECT id FROM templates "
        "WHERE name = 'AI/ML Evaluation Framework';",
        TENANT_DB,
    )
    actual_template_id = None
    for line in result.strip().split("\n"):
        stripped = line.strip()
        if len(stripped) == 36 and "-" in stripped:
            actual_template_id = stripped
            break

    if not actual_template_id:
        logger.warning("Could not find template ID, skipping stages.")
        return

    # Template stages
    stages = [
        ("Desirable", 1, 33.33),
        ("Feasible", 2, 33.33),
        ("Viable", 3, 33.34),
    ]
    for stage_name, order, weight in stages:
        sql = f"""
        INSERT INTO template_stages
            (template_id, name, sort_order, weight_pct)
        SELECT '{actual_template_id}', '{stage_name}', {order}, {weight}
        WHERE NOT EXISTS (
            SELECT 1 FROM template_stages
            WHERE template_id = '{actual_template_id}'
              AND name = '{stage_name}'
        );
        """
        _psql_check(sql, TENANT_DB)
    logger.info("Sample template 'AI/ML Evaluation Framework' seeded.")


def main() -> None:
    """Run the full database setup."""
    logger.info("=== Database Setup ===")
    wait_for_postgres()
    create_databases()
    run_migrations()
    seed_platform_db()
    seed_tenant_db()
    logger.info("=== Database Setup Complete ===")


if __name__ == "__main__":
    main()
