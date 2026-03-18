# Helio Canvas Admin Panel - Design Document

**Version**: 1.0
**Date**: 2026-03-17
**Status**: Draft
**Source**: [App Spec](../features/app_spec.md)

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [6-Layer Architecture Mapping](#2-6-layer-architecture-mapping)
3. [Multi-Tenancy Design](#3-multi-tenancy-design)
4. [Authentication Flow](#4-authentication-flow)
5. [Key Design Decisions](#5-key-design-decisions)
6. [Data Flow Diagrams](#6-data-flow-diagrams)
7. [Security Considerations](#7-security-considerations)

---

## 1. System Architecture

### High-Level System Diagram

```
+------------------------------------------------------------------+
|                        CLIENT (Browser)                          |
|                                                                  |
|  +-----------------------------------------------------------+  |
|  |              React SPA (Vite + Tailwind CSS)               |  |
|  |  - React Router v6       - React Query (server state)      |  |
|  |  - Auth.js (Keycloak)    - Context API (local state)       |  |
|  +----------------------------+------------------------------+  |
+-------------------------------|----------------------------------+
                                | HTTPS (REST/JSON)
                                v
+------------------------------------------------------------------+
|                     FASTAPI BACKEND (Python 3.11+)               |
|                                                                  |
|  +-----------------------------------------------------------+  |
|  |                  Runtime Layer (src/runtime/)              |  |
|  |  - FastAPI App          - CORS Middleware                  |  |
|  |  - API Routers          - Tenant Resolution Middleware     |  |
|  |  - JWT Auth Dependency  - Request Logging                  |  |
|  +----------------------------+------------------------------+  |
|  |                  Service Layer (src/service/)              |  |
|  |  - Template Wizard Orchestration                          |  |
|  |  - User Management       - Tenant Provisioning            |  |
|  |  - Master Data Mgmt      - Analytics Aggregation          |  |
|  |  - Audit Logger                                           |  |
|  +----------------------------+------------------------------+  |
|  |                  Repo Layer (src/repo/)                    |  |
|  |  - SQLAlchemy 2.0 Models (async)                          |  |
|  |  - Repository classes     - Dynamic Session Factory        |  |
|  |  - Alembic Migrations                                     |  |
|  +----------------------------+------------------------------+  |
|  |                  Config Layer (src/config/)                |  |
|  |  - Settings (env vars)    - DB connection config           |  |
|  |  - Keycloak config        - Redis config                   |  |
|  +----------------------------+------------------------------+  |
|  |                  Types Layer (src/types/)                  |  |
|  |  - Pydantic models        - Enums                         |  |
|  |  - Shared type defs       - API schemas                   |  |
|  +-----------------------------------------------------------+  |
+------------------------------------------------------------------+
         |                    |                    |
         v                    v                    v
+----------------+  +-------------------+  +----------------+
|   Keycloak     |  |   PostgreSQL      |  |    Redis       |
|                |  |                   |  |                |
| - OIDC/OAuth2  |  | +---------------+ |  | - Tenant DB    |
| - Realm/tenant |  | | db_platform   | |  |   conn cache   |
| - User store   |  | | (tenants,     | |  | - Session      |
| - JWKS endpoint|  | |  tenant_plans) | |  |   store        |
| - Password     |  | +---------------+ |  +----------------+
|   reset flow   |  | +---------------+ |
| - Self-reg     |  | | db_tenant_foo | |
+----------------+  | +---------------+ |
                    | +---------------+ |
                    | | db_tenant_bar | |
                    | +---------------+ |
                    | +---------------+ |
                    | | db_tenant_... | |
                    | +---------------+ |
                    +-------------------+
```

### Component Responsibilities

| Component | Technology | Responsibility |
|-----------|-----------|----------------|
| React SPA | React + Vite + Tailwind | All UI rendering, client-side routing, form state |
| FastAPI Backend | Python 3.11+ / FastAPI | REST API, business logic, auth enforcement |
| Keycloak | Keycloak (Docker) | Identity provider, OIDC, user federation, password reset |
| PostgreSQL | PostgreSQL (localhost) | Platform metadata + per-tenant data storage |
| Redis | Redis (Docker) | Tenant DB connection string caching, session store |

### Network Topology (Local Dev)

```
Docker Compose Network
+--------------------------------------------------+
|                                                  |
|  react-app:5173  ---->  fastapi:8000             |
|                           |    |    |            |
|                           v    v    v            |
|                    postgres:5432                  |
|                    keycloak:8080                  |
|                    redis:6379                     |
+--------------------------------------------------+
```

---

## 2. 6-Layer Architecture Mapping

### Layer Dependency Rule

```
Types(0) --> Config(1) --> Repo(2) --> Service(3) --> Runtime(4) --> UI(5)
```

Each layer may only import from layers with a **lower** number. Backward imports are forbidden.

### Layer 0: Types (`src/types/`)

Shared Pydantic models, enums, and type definitions used across all layers.

```
src/types/
  __init__.py
  tenant.py          # TenantCreate, TenantUpdate, TenantResponse, TenantBranding
  user.py             # UserInvite, UserUpdate, UserResponse, UserRole (enum), UserStatus (enum)
  template.py         # TemplateCreate, TemplateUpdate, TemplateResponse, TemplateStatus (enum)
  template_stage.py   # StageCreate, StageUpdate, StageResponse, FailAction (enum)
  template_field.py   # FieldCreate, FieldResponse, FieldType (enum), FieldOptionCreate
  template_section.py # SectionCreate, SectionResponse
  master_data.py      # CategoryResponse, MasterDataValueCreate, MasterDataValueUpdate
  analytics.py        # DashboardMetrics, ChartData, AuditLogEntry, AuditEventType (enum)
  auth.py             # TokenPayload, CurrentUser, JWTClaims
  common.py           # PaginatedResponse[T], SortOrder (enum), UUIDModel base
```

**Key Enums:**
- `UserRole`: SYSTEM_ADMIN, ADMIN, CONTRIBUTOR, VIEWER
- `UserStatus`: ACTIVE, INVITED, DEACTIVATED
- `TemplateStatus`: DRAFT, PUBLISHED, ARCHIVED
- `FieldType`: TEXT_SHORT, TEXT_LONG, SINGLE_SELECT, MULTI_SELECT, NUMBER, DATE
- `FailAction`: WARN, BLOCK, ALLOW
- `AuditEventType`: MANAGEMENT, SYSTEM, SECURITY

### Layer 1: Config (`src/config/`)

Application settings loaded from environment variables. No business logic.

```
src/config/
  __init__.py
  settings.py         # AppSettings (Pydantic BaseSettings): APP_NAME, DEBUG, LOG_LEVEL
  database.py         # DatabaseConfig: PLATFORM_DB_URL, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
  keycloak.py         # KeycloakConfig: KEYCLOAK_URL, KEYCLOAK_ADMIN_USER, KEYCLOAK_ADMIN_PASSWORD
  redis.py            # RedisConfig: REDIS_URL, CACHE_TTL
  cors.py             # CORSConfig: ALLOWED_ORIGINS, ALLOWED_METHODS
```

**Config loading strategy**: All configuration is read from environment variables via `pydantic-settings`. No `.env` files are read directly in production; Docker Compose maps env vars. The `src/config/` module is the single source of truth for all external configuration.

### Layer 2: Repo (`src/repo/`)

SQLAlchemy ORM models, repository classes (data access), and database session management.

```
src/repo/
  __init__.py
  models/
    __init__.py
    platform.py       # TenantModel, TenantPlanModel (platform DB)
    tenant.py          # TemplateModel, TemplateStageModel, TemplateSectionModel,
                       # TemplateFieldModel, FieldOptionModel, TemplateTagModel
    master_data.py     # MasterDataCategoryModel, MasterDataValueModel
    audit.py           # AuditLogModel
  repositories/
    __init__.py
    tenant_repo.py     # TenantRepository: CRUD on platform.tenants
    template_repo.py   # TemplateRepository: full template tree CRUD
    user_repo.py       # UserRepository: Keycloak user operations wrapper
    master_data_repo.py # MasterDataRepository: categories + values CRUD
    audit_repo.py      # AuditLogRepository: insert + query with filters
    analytics_repo.py  # AnalyticsRepository: aggregation queries
  session.py           # Platform session factory, tenant session factory (dynamic)
  migrations/          # Alembic configuration
    env.py
    versions/          # Migration scripts (applied per-tenant)
```

**Repository pattern**: Each repository class accepts an `AsyncSession` and exposes typed methods. No raw SQL outside repo layer. All queries are scoped to the session's database, ensuring tenant isolation by construction.

### Layer 3: Service (`src/service/`)

Business logic orchestration. Services call repositories and enforce business rules.

```
src/service/
  __init__.py
  tenant_service.py       # Tenant provisioning: create DB + Keycloak realm + seed data
  user_service.py         # Invite user (Keycloak API), role changes, deactivation
  template_service.py     # Template wizard orchestration (validate steps, publish)
  master_data_service.py  # Master data CRUD orchestration, CSV import parsing
  analytics_service.py    # Dashboard metric aggregation, chart data assembly
  audit_service.py        # Audit log recording (called by other services)
  keycloak_client.py      # Keycloak Admin API wrapper (realm, user, role operations)
```

**Key service responsibilities:**
- `TenantService.provision_tenant()`: Creates PostgreSQL database, runs Alembic migrations, creates Keycloak realm, seeds default master data, caches connection string in Redis.
- `TemplateService.publish_template()`: Validates all 5 wizard steps are complete, checks stage weight totals equal 100%, transitions status from DRAFT to PUBLISHED.
- `UserService.invite_user()`: Creates user in Keycloak realm, assigns role, sends invitation email via Keycloak, records audit log entry.

### Layer 4: Runtime (`src/runtime/`)

FastAPI application, routers, middleware, and dependency injection.

```
src/runtime/
  __init__.py
  app.py               # FastAPI app factory, lifespan events, middleware registration
  dependencies.py      # Dependency injection: get_current_user, get_tenant_session,
                       # get_platform_session, require_role(...)
  middleware/
    __init__.py
    tenant_resolver.py # Extract tenant from JWT claims, resolve DB connection
    request_logger.py  # Log all requests with tenant context
    error_handler.py   # Global exception handlers, structured error responses
  routers/
    __init__.py
    auth.py            # /api/v1/auth/* endpoints
    tenants.py         # /api/v1/tenants/* endpoints (platform admin)
    users.py           # /api/v1/users/* endpoints (tenant-scoped)
    templates.py       # /api/v1/templates/* endpoints (tenant-scoped)
    master_data.py     # /api/v1/master-data/* endpoints (tenant-scoped)
    analytics.py       # /api/v1/analytics/* endpoints (tenant-scoped)
```

**Dependency injection chain:**
1. `get_current_user`: Validates JWT via Keycloak JWKS, returns `CurrentUser`
2. `get_tenant_session`: Reads tenant slug from `CurrentUser.tenant`, resolves DB connection from Redis cache (or platform DB fallback), returns `AsyncSession` bound to tenant DB
3. `require_role(UserRole.ADMIN)`: Checks `CurrentUser.role` against required role

### Layer 5: UI (`src/ui/`)

React single-page application. Separate build pipeline; communicates with backend exclusively via REST API.

```
src/ui/
  index.html
  package.json
  vite.config.ts
  tailwind.config.ts
  src/
    main.tsx
    App.tsx
    auth/                # Auth.js (next-auth) Keycloak provider setup
    components/
      layout/            # Sidebar, TopHeader, MainContent wrapper
      common/            # Button, Input, Modal, Table, Pagination, Badge
      templates/         # WizardStepper, StageConfig, FieldEditor, ScoringPanel, Preview
      users/             # UserTable, InviteUserModal, RoleDropdown
      tenant-settings/   # GeneralTab, BrandingTab, DefaultsTab
      master-data/       # CategorySidebar, DataTable, CSVImportModal
      analytics/         # MetricCard, BarChart, PieChart, LineChart, AuditLogTable
    hooks/               # useAuth, useTenant, useTemplateWizard, usePagination
    api/                 # Axios/fetch wrappers per resource, React Query config
    pages/               # Route-level page components
    types/               # TypeScript interfaces mirroring backend schemas
    styles/              # Tailwind base + design tokens
```

---

## 3. Multi-Tenancy Design

### DB-Per-Tenant Pattern

```
                        +-------------------+
                        |   db_platform     |
                        |  - tenants        |
                        |  - tenant_plans   |
                        +-------------------+
                                |
                  +-------------+-------------+
                  |             |             |
          +-------v---+  +----v------+  +---v--------+
          | db_tenant_ |  | db_tenant_|  | db_tenant_ |
          | acme       |  | globex    |  | initech    |
          | - templates|  | - templates|  | - templates|
          | - stages   |  | - stages   |  | - stages   |
          | - fields   |  | - fields   |  | - fields   |
          | - master_  |  | - master_  |  | - master_  |
          |   data     |  |   data     |  |   data     |
          | - audit_   |  | - audit_   |  | - audit_   |
          |   logs     |  |   logs     |  |   logs     |
          +-----------+  +-----------+  +------------+
```

### Tenant Resolution Middleware

Every authenticated request passes through the tenant resolution middleware:

```
Request
  |
  v
[1] JWT Validation (Keycloak JWKS)
  |
  v
[2] Extract tenant_slug from JWT custom claim "tenant"
  |
  v
[3] Lookup tenant in Redis cache
  |  (cache miss) --> Query db_platform.tenants --> Cache in Redis (TTL: 5 min)
  |
  v
[4] Verify tenant.is_active == True
  |  (inactive) --> 403 Forbidden
  |
  v
[5] Build async DB connection string: postgresql+asyncpg://{user}:{pass}@{host}:{port}/{db_name}
  |
  v
[6] Create/reuse AsyncSession bound to tenant DB
  |
  v
[7] Inject session into request state (available via get_tenant_session dependency)
```

### Dynamic Session Routing (`src/repo/session.py`)

```python
# Conceptual design (not production code)

class TenantSessionManager:
    """Manages per-tenant async database sessions with connection pooling."""

    def __init__(self, redis_client, platform_session_factory):
        self._engines: dict[str, AsyncEngine] = {}  # slug -> engine
        self._redis = redis_client
        self._platform_sf = platform_session_factory

    async def get_session(self, tenant_slug: str) -> AsyncSession:
        """Return an AsyncSession bound to the tenant's database."""
        engine = self._engines.get(tenant_slug)
        if engine is None:
            conn_str = await self._resolve_connection(tenant_slug)
            engine = create_async_engine(conn_str, pool_size=5, max_overflow=10)
            self._engines[tenant_slug] = engine
        return AsyncSession(engine, expire_on_commit=False)

    async def _resolve_connection(self, tenant_slug: str) -> str:
        """Check Redis cache first, then fall back to platform DB."""
        cached = await self._redis.get(f"tenant:conn:{tenant_slug}")
        if cached:
            return cached
        # Query platform DB for tenant record
        # Build connection string, cache in Redis with TTL
        ...
```

**Connection pool management:**
- Each tenant gets its own `AsyncEngine` with a pool of 5 connections (max overflow 10).
- Engines are lazily created on first request and cached in-memory in the `TenantSessionManager`.
- Connection strings are cached in Redis with a 5-minute TTL to avoid querying the platform DB on every request.
- On tenant deactivation, the engine is disposed and the cache entry is invalidated.

### Alembic Per-Tenant Migrations

```
src/repo/migrations/
  alembic.ini           # Template config (DB URL is injected at runtime)
  env.py                # Custom env.py that accepts a target DB URL
  versions/
    001_initial.py      # Creates all tenant tables
    002_add_audit_idx.py
    ...
```

**Migration execution strategy:**

1. **On tenant creation**: `TenantService.provision_tenant()` creates the PostgreSQL database, then runs all Alembic migrations against it.
2. **On application upgrade**: A management command iterates all active tenants from the platform DB and runs `alembic upgrade head` against each tenant DB sequentially.
3. **Migration safety**: Each migration runs in a transaction. Failed migrations roll back and log an error but do not block other tenants.

```
# Management command (conceptual)
async def migrate_all_tenants():
    tenants = await platform_repo.list_active_tenants()
    for tenant in tenants:
        conn_str = build_connection_string(tenant)
        alembic_cfg = build_alembic_config(conn_str)
        command.upgrade(alembic_cfg, "head")
```

---

## 4. Authentication Flow

### OIDC Authorization Code Flow with PKCE

```
+----------+           +------------+          +-----------+          +----------+
|  React   |           |  FastAPI   |          |  Keycloak |          | Tenant   |
|  SPA     |           |  Backend   |          |  Server   |          | DB       |
+----+-----+           +-----+------+          +-----+-----+          +----+-----+
     |                        |                       |                     |
     | 1. Click "Sign In"     |                       |                     |
     |----------------------->|                       |                     |
     |                        |                       |                     |
     | 2. Redirect to Keycloak auth endpoint          |                     |
     |   (with PKCE code_challenge, state, nonce)     |                     |
     |----------------------------------------------->|                     |
     |                        |                       |                     |
     | 3. User enters credentials                     |                     |
     |   (username + password on Keycloak login page) |                     |
     |<-----------------------------------------------|                     |
     |----------------------------------------------->|                     |
     |                        |                       |                     |
     | 4. Keycloak redirects back with auth code      |                     |
     |<-----------------------------------------------|                     |
     |                        |                       |                     |
     | 5. POST /api/v1/auth/callback (auth code + code_verifier)           |
     |----------------------->|                       |                     |
     |                        |                       |                     |
     |                        | 6. Exchange code for  |                     |
     |                        |    tokens (+ PKCE     |                     |
     |                        |    code_verifier)     |                     |
     |                        |---------------------->|                     |
     |                        |                       |                     |
     |                        | 7. Receive:           |                     |
     |                        |    - access_token     |                     |
     |                        |    - refresh_token    |                     |
     |                        |    - id_token         |                     |
     |                        |<----------------------|                     |
     |                        |                       |                     |
     |                        | 8. Validate JWT       |                     |
     |                        |    signature via JWKS |                     |
     |                        |---------------------->|                     |
     |                        |<----------------------|                     |
     |                        |                       |                     |
     | 9. Set httpOnly cookie |                       |                     |
     |    (JWT) + redirect to |                       |                     |
     |    dashboard           |                       |                     |
     |<-----------------------|                       |                     |
     |                        |                       |                     |
     | 10. Subsequent API calls with Bearer token     |                     |
     |----------------------->|                       |                     |
     |                        | 11. Validate JWT      |                     |
     |                        |     Extract tenant    |                     |
     |                        |     + role claims     |                     |
     |                        |                       |                     |
     |                        | 12. Route to tenant DB|                     |
     |                        |------------------------------------------>|
     |                        |<------------------------------------------|
     | 13. Response            |                       |                     |
     |<-----------------------|                       |                     |
```

### JWT Claims Structure

```json
{
  "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "iss": "http://localhost:8080/realms/tenant-acme",
  "aud": "helio-canvas-api",
  "exp": 1742400000,
  "iat": 1742396400,
  "preferred_username": "john.doe",
  "email": "john.doe@acme.com",
  "given_name": "John",
  "family_name": "Doe",
  "realm_access": {
    "roles": ["admin"]
  },
  "tenant": "acme"
}
```

### Role Mapping

| Keycloak Realm Role | Application Role | Permissions |
|---------------------|-----------------|-------------|
| `system_admin` | SYSTEM_ADMIN | All operations + cross-tenant access + tenant provisioning |
| `admin` | ADMIN | Manage users, templates, master data, settings within own tenant |
| `contributor` | CONTRIBUTOR | Create/edit templates, manage master data |
| `viewer` | VIEWER | Read-only access to all tenant data |

### JWT Validation Dependency

The `get_current_user` FastAPI dependency performs:

1. Extract Bearer token from `Authorization` header (or httpOnly cookie fallback).
2. Fetch Keycloak JWKS keys (cached in-memory with 1-hour TTL).
3. Decode and validate JWT: signature, expiry, issuer, audience.
4. Map `realm_access.roles` to `UserRole` enum.
5. Extract `tenant` custom claim.
6. Return `CurrentUser` typed object.

If any validation step fails, return `401 Unauthorized`.

### Token Refresh Strategy

- Access tokens have a 15-minute expiry.
- Refresh tokens have a 24-hour expiry ("Remember me" extends to 30 days).
- The React SPA uses Auth.js to silently refresh tokens before expiry.
- On refresh failure, the user is redirected to the login page.

---

## 5. Key Design Decisions

### Decision 1: DB-Per-Tenant vs. Schema-Per-Tenant vs. Shared-Table

| Criteria | DB-Per-Tenant (chosen) | Schema-Per-Tenant | Shared Table |
|----------|----------------------|-------------------|--------------|
| **Isolation** | Complete - separate DB files, users, backups | Good - schema-level separation | Weak - row-level filtering only |
| **Tenant data leak risk** | Negligible - wrong DB = connection error | Low - wrong schema = error | High - missing WHERE clause leaks data |
| **Backup/restore** | Per-tenant backup trivial | Possible but complex | Must filter by tenant_id |
| **Performance** | Dedicated connection pool per tenant | Shared pool, SET search_path | Index on tenant_id, shared pool |
| **Migration complexity** | Must iterate all tenant DBs | Must iterate all schemas | Single migration |
| **Connection overhead** | Higher - one pool per tenant | Medium | Lowest |
| **Scalability ceiling** | ~100-500 tenants (connection limits) | ~1000 tenants | Unlimited |

**Decision**: DB-per-tenant. The application targets enterprise customers with a limited number of tenants (tens, not thousands). Complete isolation is the top priority for security and compliance. The connection overhead is manageable with lazy engine creation and pool sizing.

### Decision 2: Keycloak as Identity Provider

**Why Keycloak over custom auth:**
- Standards-based OIDC/OAuth2 implementation out of the box.
- Built-in features: password reset, self-registration, email verification, brute-force protection.
- Per-realm isolation maps naturally to per-tenant identity.
- Admin API enables programmatic realm/user/role management during tenant provisioning.
- Avoids storing password hashes in the application database.
- SSO capability for future integrations.

**Tradeoffs:**
- Added infrastructure component (Docker container).
- Learning curve for Keycloak admin API.
- Realm-per-tenant means Keycloak must scale with tenant count.

### Decision 3: Template Wizard State Management

**Approach**: Server-side draft persistence with optimistic UI updates.

```
Step 1 (General Info)
  |
  POST /api/v1/templates  --> Creates template record (status=draft)
  |                            Returns template_id
  v
Step 2 (Stages)
  |
  PUT /api/v1/templates/{id}/stages  --> Upserts stages
  |
  v
Step 3 (Fields & Sections)
  |
  PUT /api/v1/templates/{id}/fields  --> Upserts sections + fields + options
  |
  v
Step 4 (Scoring)
  |
  PUT /api/v1/templates/{id}/scoring  --> Updates weights + thresholds
  |
  v
Step 5 (Preview & Publish)
  |
  POST /api/v1/templates/{id}/publish  --> Validates all steps, sets status=published
```

**Rationale:**
- Each wizard step persists immediately to the server. The user can close the browser and resume later.
- The template remains in `draft` status until explicitly published.
- Step navigation is unrestricted (user can jump to any completed step).
- Validation is enforced at publish time, not at individual step transitions, to allow partial saves.
- React Query handles server state caching and optimistic updates for the wizard form.

### Decision 4: Redis for Connection String Caching

**Why Redis over in-memory-only caching:**
- If the FastAPI process restarts, connection strings are immediately available from Redis without querying the platform DB.
- In a multi-worker deployment (uvicorn with multiple workers), all workers share the same cache.
- TTL-based expiry ensures tenant configuration changes (e.g., DB host migration) propagate within 5 minutes.
- Redis also serves as the session store for Auth.js, consolidating caching infrastructure.

### Decision 5: Async SQLAlchemy with asyncpg

**Why async:**
- FastAPI is async-native; synchronous DB calls block the event loop.
- `asyncpg` is the fastest PostgreSQL driver for Python.
- Async connection pools handle concurrent tenant requests efficiently.
- Per-tenant engines with small pool sizes (5 + 10 overflow) prevent connection exhaustion.

---

## 6. Data Flow Diagrams

### Flow 1: Template Creation Wizard

```
React SPA                    FastAPI                      Tenant DB
    |                            |                            |
    | POST /templates            |                            |
    | {name, category, desc,     |                            |
    |  icon, theme_color, tags}  |                            |
    |--------------------------->|                            |
    |                            | Validate input             |
    |                            | INSERT templates            |
    |                            | INSERT template_tags        |
    |                            |--------------------------->|
    |                            |<---------------------------|
    |                            | Record audit log           |
    |   201 {template_id}        |--------------------------->|
    |<---------------------------|                            |
    |                            |                            |
    | PUT /templates/{id}/stages |                            |
    | [{name, sort_order}, ...]  |                            |
    |--------------------------->|                            |
    |                            | DELETE old stages          |
    |                            | INSERT new stages          |
    |                            |--------------------------->|
    |   200 {stages}             |<---------------------------|
    |<---------------------------|                            |
    |                            |                            |
    | PUT /templates/{id}/fields |                            |
    | {stages: [{sections:       |                            |
    |   [{fields: [...]}]}]}     |                            |
    |--------------------------->|                            |
    |                            | Upsert sections            |
    |                            | Upsert fields              |
    |                            | Upsert field_options       |
    |                            |--------------------------->|
    |   200 {full_template}      |<---------------------------|
    |<---------------------------|                            |
    |                            |                            |
    | PUT /templates/{id}/scoring|                            |
    | [{stage_id, weight_pct,    |                            |
    |   min_pass_score,          |                            |
    |   fail_action}]            |                            |
    |--------------------------->|                            |
    |                            | Validate weights sum=100%  |
    |                            | UPDATE stages scoring      |
    |                            |--------------------------->|
    |   200 {stages}             |<---------------------------|
    |<---------------------------|                            |
    |                            |                            |
    | POST /templates/{id}/publish                            |
    |--------------------------->|                            |
    |                            | Validate completeness:     |
    |                            |  - Has at least 1 stage    |
    |                            |  - Each stage has fields   |
    |                            |  - Weights sum to 100%     |
    |                            | UPDATE status='published'  |
    |                            | version += 1               |
    |                            |--------------------------->|
    |                            | Record audit log           |
    |   200 {template}           |--------------------------->|
    |<---------------------------|                            |
```

### Flow 2: Tenant Provisioning

```
Platform Admin               FastAPI                 Platform DB    PostgreSQL     Keycloak       Redis
     |                          |                        |              |              |             |
     | POST /tenants            |                        |              |              |             |
     | {name, slug, ...}        |                        |              |              |             |
     |------------------------->|                        |              |              |             |
     |                          |                        |              |              |             |
     |                          | 1. Validate uniqueness |              |              |             |
     |                          |    (name, slug)        |              |              |             |
     |                          |----------------------->|              |              |             |
     |                          |<-----------------------|              |              |             |
     |                          |                        |              |              |             |
     |                          | 2. INSERT tenant       |              |              |             |
     |                          |    record               |              |              |             |
     |                          |----------------------->|              |              |             |
     |                          |<-----------------------|              |              |             |
     |                          |                        |              |              |             |
     |                          | 3. CREATE DATABASE     |              |              |             |
     |                          |    db_tenant_{slug}    |              |              |             |
     |                          |------------------------------------->|              |             |
     |                          |<-------------------------------------|              |             |
     |                          |                        |              |              |             |
     |                          | 4. Run Alembic         |              |              |             |
     |                          |    migrations          |              |              |             |
     |                          |------------------------------------->|              |             |
     |                          |<-------------------------------------|              |             |
     |                          |                        |              |              |             |
     |                          | 5. Seed default        |              |              |             |
     |                          |    master data         |              |              |             |
     |                          |------------------------------------->|              |             |
     |                          |<-------------------------------------|              |             |
     |                          |                        |              |              |             |
     |                          | 6. Create Keycloak     |              |              |             |
     |                          |    realm + client      |              |              |             |
     |                          |---------------------------------------------->|             |
     |                          |<----------------------------------------------|             |
     |                          |                        |              |              |             |
     |                          | 7. Create admin user   |              |              |             |
     |                          |    in Keycloak realm   |              |              |             |
     |                          |---------------------------------------------->|             |
     |                          |<----------------------------------------------|             |
     |                          |                        |              |              |             |
     |                          | 8. Cache connection    |              |              |             |
     |                          |    string in Redis     |              |              |             |
     |                          |---------------------------------------------------------->|
     |                          |<----------------------------------------------------------|
     |                          |                        |              |              |             |
     |  201 {tenant}            |                        |              |              |             |
     |<-------------------------|                        |              |              |             |
```

**Provisioning is transactional**: If any step fails (e.g., Keycloak realm creation), the service rolls back all previous steps: drops the tenant DB, deletes the tenant record from the platform DB, and invalidates the Redis cache entry.

### Flow 3: User Invitation

```
Admin (React)          FastAPI                    Keycloak              Tenant DB
     |                     |                          |                     |
     | POST /users/invite  |                          |                     |
     | {email, role}       |                          |                     |
     |-------------------->|                          |                     |
     |                     |                          |                     |
     |                     | 1. Check tenant plan     |                     |
     |                     |    user limit            |                     |
     |                     |    (platform DB query)   |                     |
     |                     |                          |                     |
     |                     | 2. Create user in        |                     |
     |                     |    Keycloak realm        |                     |
     |                     |    (email, temp password) |                     |
     |                     |------------------------->|                     |
     |                     |<-------------------------|                     |
     |                     |                          |                     |
     |                     | 3. Assign role to user   |                     |
     |                     |    in Keycloak realm     |                     |
     |                     |------------------------->|                     |
     |                     |<-------------------------|                     |
     |                     |                          |                     |
     |                     | 4. Trigger Keycloak      |                     |
     |                     |    "verify email" action  |                     |
     |                     |    (sends invitation)     |                     |
     |                     |------------------------->|                     |
     |                     |<-------------------------|                     |
     |                     |                          |                     |
     |                     | 5. Record audit log      |                     |
     |                     |    (user_invited)         |                     |
     |                     |-------------------------------------------->|
     |                     |<--------------------------------------------|
     |                     |                          |                     |
     |  201 {user}         |                          |                     |
     |  (status: INVITED)  |                          |                     |
     |<--------------------|                          |                     |
     |                     |                          |                     |
     |                     |    --- Later ---          |                     |
     |                     |                          |                     |
     |     Invited user clicks email link             |                     |
     |     Sets password in Keycloak                  |                     |
     |     Logs in via OIDC flow                      |                     |
     |     Status changes to ACTIVE on first login    |                     |
```

---

## 7. Security Considerations

### 7.1 Tenant Isolation

| Layer | Isolation Mechanism |
|-------|-------------------|
| **Database** | Separate PostgreSQL database per tenant. Connection credentials scoped to individual DBs. No shared tables between tenants (except platform DB). |
| **Identity** | Separate Keycloak realm per tenant. Users in one realm cannot authenticate against another. |
| **Application** | Tenant resolution middleware extracts tenant from JWT. All downstream DB sessions are bound to the resolved tenant's database. There is no application-level WHERE clause for tenant filtering -- isolation is structural. |
| **API** | Every tenant-scoped endpoint requires authentication. The `get_tenant_session` dependency ensures queries run against the correct database. Cross-tenant access is only available to SYSTEM_ADMIN role via the platform `/tenants` endpoints. |
| **Cache** | Redis keys are namespaced with tenant slug: `tenant:conn:{slug}`, `tenant:session:{slug}:{session_id}`. |

### 7.2 JWT Validation

- **Signature verification**: Every request validates the JWT signature against Keycloak's JWKS endpoint (keys are cached with 1-hour rotation).
- **Claim validation**: Issuer (`iss`) must match the expected Keycloak realm URL. Audience (`aud`) must match the registered client ID. Expiry (`exp`) must be in the future.
- **Token binding**: The `tenant` custom claim in the JWT is the only source of tenant identity. It cannot be overridden by request headers or query parameters.
- **Refresh tokens**: Never sent to the frontend. Stored server-side (Redis session store) or in httpOnly cookies.

### 7.3 CORS Configuration

```python
# Configured in src/config/cors.py, applied in src/runtime/app.py
ALLOWED_ORIGINS = ["http://localhost:5173"]  # React dev server
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
ALLOWED_HEADERS = ["Authorization", "Content-Type"]
ALLOW_CREDENTIALS = True  # Required for httpOnly cookie auth
```

- No wildcard origins in any environment.
- Credentials mode is enabled to support httpOnly cookie-based JWT transport.
- Production origins will be explicitly listed.

### 7.4 Input Sanitization

| Input Type | Validation |
|-----------|-----------|
| **All request bodies** | Pydantic model validation with strict types. Unknown fields are rejected (`model_config = {"extra": "forbid"}`). |
| **String fields** | Max length enforced (e.g., template description 500 chars). No raw HTML allowed. |
| **UUIDs** | Pydantic `UUID` type validates format. |
| **Pagination params** | `page` min=1, `page_size` min=1 max=100. |
| **File uploads** | Logo: max 2MB, PNG/SVG only. Favicon: max 512KB, SVG/PNG/ICO only. MIME type validated server-side. |
| **CSV import** | Parsed row-by-row with validation. Malformed rows are rejected with line-number error reporting. No formula execution. |
| **SQL injection** | Prevented by SQLAlchemy parameterized queries. No raw SQL string concatenation. |

### 7.5 Rate Limiting and Abuse Prevention

- **Login endpoint**: Rate limited to 10 attempts per minute per IP (Keycloak brute-force protection).
- **Invitation endpoint**: Rate limited to 50 invitations per hour per tenant.
- **CSV import**: Max file size 5MB, max 10,000 rows per import.
- **API general**: 100 requests per minute per authenticated user (enforced via middleware).

### 7.6 Audit Trail

All state-changing operations are recorded in the tenant's `audit_logs` table:

| Event Type | Examples |
|-----------|---------|
| SECURITY | Login, logout, failed login, password reset, role change |
| MANAGEMENT | User invited, user deactivated, template published, settings changed |
| SYSTEM | Tenant provisioned, migration executed, CSV imported |

Audit logs are append-only. No API endpoint exposes delete or update operations on audit records. Logs include: timestamp, actor (user_id + user_name), event type, action, details (JSON), and source IP address.

### 7.7 Secrets Management

- All secrets (DB passwords, Keycloak admin credentials, Redis password) are loaded from environment variables via `src/config/`.
- No secrets are hardcoded in source code or committed to version control.
- `.env` files are listed in `.gitignore` and used only for local development.
- The `src/config/` settings module is the single point of access for all secrets.
- Docker Compose passes secrets via environment variables defined in `.env` (not checked in).

### 7.8 Transport Security

- All inter-service communication uses HTTPS in production (TLS terminated at reverse proxy).
- httpOnly + Secure + SameSite=Lax flags on JWT cookies.
- No sensitive data in URL query parameters (tokens, passwords).

---

## Appendix A: File Size and Complexity Constraints

Per project conventions (CLAUDE.md):
- Maximum **300 lines** per file.
- Maximum **50 lines** per function.
- If a module exceeds these limits, it must be split into sub-modules within the same layer.

This design accounts for these constraints in the file structure proposals above. For example, the `template_repo.py` will likely need to be split into `template_repo.py` (CRUD operations) and `template_tree_repo.py` (nested stage/section/field operations) to stay within limits.

## Appendix B: Error Response Format

All API errors follow a consistent JSON structure:

```json
{
  "detail": {
    "code": "TENANT_NOT_FOUND",
    "message": "Tenant with slug 'acme' does not exist or is inactive.",
    "field": null
  }
}
```

For validation errors (422):

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Appendix C: Environment Variables Summary

| Variable | Layer | Description |
|----------|-------|-------------|
| `APP_NAME` | Config | Application name (default: "Helio Canvas") |
| `DEBUG` | Config | Debug mode flag |
| `LOG_LEVEL` | Config | Logging level (INFO, DEBUG, WARNING) |
| `PLATFORM_DB_URL` | Config | Platform database connection string |
| `DB_HOST` | Config | Default PostgreSQL host for tenant DBs |
| `DB_PORT` | Config | Default PostgreSQL port |
| `DB_USER` | Config | PostgreSQL user |
| `DB_PASSWORD` | Config | PostgreSQL password |
| `KEYCLOAK_URL` | Config | Keycloak base URL |
| `KEYCLOAK_ADMIN_USER` | Config | Keycloak admin username |
| `KEYCLOAK_ADMIN_PASSWORD` | Config | Keycloak admin password |
| `KEYCLOAK_CLIENT_ID` | Config | OIDC client ID |
| `KEYCLOAK_CLIENT_SECRET` | Config | OIDC client secret |
| `REDIS_URL` | Config | Redis connection URL |
| `CACHE_TTL` | Config | Default cache TTL in seconds (default: 300) |
| `CORS_ORIGINS` | Config | Comma-separated allowed origins |
| `JWT_AUDIENCE` | Config | Expected JWT audience claim |
