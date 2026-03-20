"""Setup PostgreSQL database with schema-per-tenant architecture."""
import logging
import sys
import time
import uuid
from datetime import datetime, timezone

import psycopg2

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

MAX_RETRIES = 20
RETRY_DELAY = 2

# Tenant definitions: (name, slug, schema_name, keycloak_realm)
TENANTS = [
    ("Acme Corporation", "acme", "tenant_acme", "realm-acme"),
    ("Globex Industries", "globex", "tenant_globex", "realm-globex"),
    ("Initech Solutions", "initech", "tenant_initech", "realm-initech"),
]


def _get_conn(dbname: str = "postgres"):
    """Get a psycopg2 connection."""
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT,
        user=PG_USER, password=PG_PASS,
        dbname=dbname,
    )


def wait_for_postgres() -> None:
    """Wait until PostgreSQL accepts connections."""
    logger.info("Waiting for PostgreSQL to be ready...")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            conn = _get_conn()
            conn.close()
            logger.info("PostgreSQL is ready.")
            return
        except Exception:
            pass
        logger.info(
            "  Attempt %d/%d - not ready, retrying in %ds...",
            attempt, MAX_RETRIES, RETRY_DELAY,
        )
        time.sleep(RETRY_DELAY)
    logger.error("PostgreSQL did not become ready.")
    sys.exit(1)


def create_database() -> None:
    """Create the platform database if it doesn't exist."""
    conn = _get_conn()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s", (PLATFORM_DB,)
    )
    if cur.fetchone():
        logger.info("Database '%s' already exists.", PLATFORM_DB)
    else:
        cur.execute(f"CREATE DATABASE {PLATFORM_DB}")
        logger.info("Database '%s' created.", PLATFORM_DB)
    cur.close()
    conn.close()


def run_migrations() -> None:
    """Run Alembic migrations on the platform database."""
    import subprocess
    logger.info("Running Alembic migrations...")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        capture_output=True, text=True, timeout=60,
        cwd="C:/Users/kadalisurendra/Desktop/canvas_v1",
    )
    if result.returncode != 0:
        logger.warning("Alembic: %s", result.stderr.strip())
    else:
        logger.info("Alembic migrations complete.")


TENANT_TABLES_DDL = """
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


def create_tenant_schema(conn, schema_name: str) -> None:
    """Create a tenant schema and its tables."""
    cur = conn.cursor()
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
    cur.execute(f"SET search_path TO {schema_name}")
    cur.execute(TENANT_TABLES_DDL)
    cur.execute("SET search_path TO public")
    conn.commit()
    cur.close()
    logger.info("Schema '%s' created with tables.", schema_name)


def seed_tenant_schema(conn, schema_name: str) -> None:
    """Seed a tenant schema with master data and sample template."""
    cur = conn.cursor()
    cur.execute(f"SET search_path TO {schema_name}")

    # Master data categories
    categories = [
        ("organizational_taxonomy", "Organizational Taxonomy", "account_tree", 1),
        ("kpis", "KPIs", "trending_up", 2),
        ("solution_types", "Solution Types", "lightbulb", 3),
        ("digital_platforms", "Digital Platforms", "monitor", 4),
        ("ml_models", "ML Models", "cpu", 5),
        ("risk_categories", "Risk Categories", "shield", 6),
    ]
    for name, display, icon, order in categories:
        cur.execute(
            "INSERT INTO master_data_categories (name, display_name, icon, sort_order) "
            "VALUES (%s, %s, %s, %s) ON CONFLICT (name) DO NOTHING",
            (name, display, icon, order),
        )

    # Risk category values
    cur.execute("SELECT id FROM master_data_categories WHERE name = 'risk_categories'")
    row = cur.fetchone()
    if row:
        risk_cat_id = row[0]
        risk_values = [
            ("data_privacy", "Data Privacy", "High", "Risk of exposing sensitive data", 1),
            ("implementation", "Implementation", "Medium", "Risk of failed implementation", 2),
            ("operational", "Operational", "Low", "Day-to-day operational risks", 3),
            ("biased_data", "Biased Data", "High", "Risk of biased training data", 4),
        ]
        for value, label, severity, desc, order in risk_values:
            cur.execute(
                "INSERT INTO master_data_values "
                "(category_id, value, label, severity, description, is_active, sort_order) "
                "SELECT %s, %s, %s, %s, %s, true, %s "
                "WHERE NOT EXISTS (SELECT 1 FROM master_data_values WHERE category_id = %s AND value = %s)",
                (risk_cat_id, value, label, severity, desc, order, risk_cat_id, value),
            )

    # Sample template
    template_id = str(uuid.uuid4())
    created_by = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO templates (id, name, category, description, icon, theme_color, status, version, created_by) "
        "SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s "
        "WHERE NOT EXISTS (SELECT 1 FROM templates WHERE name = %s)",
        (template_id, "AI/ML Evaluation Framework", "AI/ML",
         "Comprehensive evaluation framework for AI and ML initiatives.",
         "brain", "#8B5CF6", "published", 1, created_by,
         "AI/ML Evaluation Framework"),
    )

    # Template stages
    cur.execute("SELECT id FROM templates WHERE name = 'AI/ML Evaluation Framework'")
    trow = cur.fetchone()
    if trow:
        tid = trow[0]
        stages = [("Desirable", 1, 33.33), ("Feasible", 2, 33.33), ("Viable", 3, 33.34)]
        for name, order, weight in stages:
            cur.execute(
                "INSERT INTO template_stages (template_id, name, sort_order, weight_pct) "
                "SELECT %s, %s, %s, %s "
                "WHERE NOT EXISTS (SELECT 1 FROM template_stages WHERE template_id = %s AND name = %s)",
                (tid, name, order, weight, tid, name),
            )

    cur.execute("SET search_path TO public")
    conn.commit()
    cur.close()
    logger.info("Schema '%s' seeded.", schema_name)


def seed_platform_tenants(conn) -> None:
    """Seed the tenants table with all configured tenants."""
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    for name, slug, schema_name, realm in TENANTS:
        tenant_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO tenants (id, name, slug, schema_name, keycloak_realm, is_active, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, true, %s, %s) "
            "ON CONFLICT (slug) DO UPDATE SET schema_name = EXCLUDED.schema_name, keycloak_realm = EXCLUDED.keycloak_realm",
            (tenant_id, name, slug, schema_name, realm, now, now),
        )
    conn.commit()
    cur.close()
    logger.info("Platform tenants seeded: %s", [t[1] for t in TENANTS])


def main() -> None:
    """Run the full database setup."""
    logger.info("=== Database Setup (Schema-per-Tenant) ===")
    wait_for_postgres()
    create_database()
    run_migrations()

    conn = _get_conn(PLATFORM_DB)

    # Seed tenant records
    seed_platform_tenants(conn)

    # Create schemas and seed each tenant
    for name, slug, schema_name, realm in TENANTS:
        logger.info("Setting up tenant: %s (%s)", name, schema_name)
        create_tenant_schema(conn, schema_name)
        seed_tenant_schema(conn, schema_name)

    conn.close()
    logger.info("=== Database Setup Complete ===")
    logger.info("Tenants: %s", [t[1] for t in TENANTS])
    logger.info("Schemas: %s", [t[2] for t in TENANTS])
    logger.info("Keycloak realms: %s", [t[3] for t in TENANTS])


if __name__ == "__main__":
    main()
