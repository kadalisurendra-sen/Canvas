# Helio Canvas 2.0 — Admin Panel

Multi-tenant evaluation template management platform for capturing, evaluating, and prioritizing business opportunities across domains (RPA, AI/ML, Agentic, Digital Transformation).

## Architecture

```
Frontend (React + TypeScript + Tailwind)
    │
    ├── Vite Dev Server (:5173/5174)
    │   └── Proxy /api/* → Backend
    │
Backend (FastAPI + SQLAlchemy)
    │
    ├── Uvicorn (:8000)
    ├── Schema-per-Tenant PostgreSQL
    │   ├── public schema (platform: tenants, tenant_plans, platform_audit_logs)
    │   ├── tenant_acme schema (templates, master_data, audit_logs, ...)
    │   ├── tenant_globex schema
    │   └── tenant_initech schema
    │
    └── Keycloak (:8080)
        ├── helio realm (super admin)
        ├── realm-acme (Acme Corporation)
        ├── realm-globex (Globex Industries)
        └── realm-initech (Initech Solutions)
```

### Multi-Tenancy

- **Schema-per-tenant**: Single PostgreSQL database, one schema per tenant
- **Tenant routing**: `X-Tenant-ID` header on every API request
- **Auth isolation**: Separate Keycloak realm per tenant
- **Session scoping**: `SET search_path TO tenant_<slug>` per DB session

### Authentication Flow

1. User opens `/login?tenant=acme`
2. Frontend stores tenant slug in `localStorage`, sends as `X-Tenant-ID` header
3. Backend looks up tenant → finds `keycloak_realm: realm-acme`
4. Authenticates via Keycloak password grant → returns JWT as HTTP-only cookie
5. JWT validated on every request using tenant's Keycloak JWKS
6. Access token: 15 min, Refresh token: 8 hours (silent refresh)

## Prerequisites

- **Python** 3.11+ (3.12 recommended)
- **Node.js** 18+ with npm
- **PostgreSQL** 16+
- **Keycloak** 24+ (requires JDK 17-21)
- **Redis** 7+ (optional, for caching)

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/kadalisurendra-sen/Canvas.git
cd Canvas

# Backend
pip install -e ".[dev]"
pip install python-jose[cryptography] pydantic[email] asyncpg psycopg2-binary

# Frontend
cd frontend && npm ci && cd ..
```

### 2. Start PostgreSQL and Keycloak

**PostgreSQL** — ensure it's running on port 5432 with user `postgres` / password `postgres`.

**Keycloak** — requires JDK 17:
```bash
set JAVA_HOME=C:\path\to\jdk-17
cd path\to\keycloak-24.0.5\bin
kc.bat start-dev
```
Keycloak runs on http://localhost:8080 (admin login: `admin` / `admin`).

### 3. Setup database and Keycloak realms

```bash
# Create database, schemas, and seed data
python scripts/setup_db.py

# Create Keycloak realms, clients, roles, and test users
python scripts/setup_keycloak.py
```

This creates:

| Tenant | Slug | Schema | Keycloak Realm |
|--------|------|--------|----------------|
| Platform Admin | `platform` | `public` | `helio` |
| Acme Corporation | `acme` | `tenant_acme` | `realm-acme` |
| Globex Industries | `globex` | `tenant_globex` | `realm-globex` |
| Initech Solutions | `initech` | `tenant_initech` | `realm-initech` |

### 4. Start the application

```bash
# Terminal 1: Backend
uvicorn src.runtime.app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173 (or 5174 if 5173 is in use)
- **API Docs**: http://localhost:8000/api/docs

## Login URLs

| Role | URL | Username | Password |
|------|-----|----------|----------|
| Super Admin | `/login?tenant=platform` | `admin` | `admin123` |
| Acme Admin | `/login?tenant=acme` | `admin` | `admin123` |
| Acme Viewer | `/login?tenant=acme` | `viewer` | `viewer123` |
| Globex Admin | `/login?tenant=globex` | `admin` | `admin123` |

## Role-Based Access

| Feature | system_admin | admin | contributor | viewer |
|---------|:---:|:---:|:---:|:---:|
| Template Management | Full | Full | View only | Under Construction |
| Template Wizard | Full | Full | - | - |
| User Management | Full | Full | - | - |
| Tenant Settings | All tenants | Own tenant | - | - |
| Analytics & Audit | Platform-wide | Tenant-scoped | - | - |
| Master Data | Full | Full | - | - |
| Delete Tenants | Yes | - | - | - |

## API Endpoints

### Public (No Auth Required)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/auth/login` | Login with username/password |
| `POST` | `/api/v1/auth/refresh` | Silent token refresh |
| `POST` | `/api/v1/auth/register` | Register new user |
| `POST` | `/api/v1/auth/logout` | Logout and revoke tokens |
| `GET` | `/api/v1/auth/me` | Get current user profile |
| `GET` | `/api/v1/tenants/list` | List active tenants |
| `GET` | `/api/v1/tenants/resolve?slug=` | Resolve tenant by slug |

### Templates

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/templates` | List templates (filter, search, paginate) | Any |
| `POST` | `/api/v1/templates` | Create template (draft) | Any |
| `GET` | `/api/v1/templates/{id}` | Get template with stages/fields/options | Any |
| `PUT` | `/api/v1/templates/{id}` | Update template metadata | Any |
| `DELETE` | `/api/v1/templates/{id}` | Delete template | Any |
| `POST` | `/api/v1/templates/{id}/clone` | Clone a template | Any |

### Template Wizard

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `PUT` | `/api/v1/templates/{id}/stages` | Save evaluation stages | Any |
| `PUT` | `/api/v1/templates/{id}/fields` | Save sections, fields, options | Any |
| `PUT` | `/api/v1/templates/{id}/scoring` | Save scoring weights and thresholds | Any |
| `POST` | `/api/v1/templates/{id}/publish` | Publish template | Any |

### Users

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/users` | List users (search, filter, paginate) | Any |
| `POST` | `/api/v1/users/invite` | Invite user via email | Admin |
| `PUT` | `/api/v1/users/{id}` | Update user role/status | Admin |
| `DELETE` | `/api/v1/users/{id}` | Deactivate user | Admin |

### Tenants

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/tenants/all` | List all tenants (detailed) | Any |
| `GET` | `/api/v1/tenants/{id}` | Get tenant settings | Any |
| `PUT` | `/api/v1/tenants/{id}` | Update general settings | Admin |
| `PUT` | `/api/v1/tenants/{id}/branding` | Update branding | Admin |
| `PUT` | `/api/v1/tenants/{id}/defaults` | Update defaults | Admin |
| `DELETE` | `/api/v1/tenants/delete/{id}` | Delete tenant | System Admin |

### Master Data

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/master-data/categories` | List categories | Any |
| `GET` | `/api/v1/master-data/categories/{id}/values` | List values (paginated) | Any |
| `POST` | `/api/v1/master-data/categories/{id}/values` | Create value | Any |
| `PUT` | `/api/v1/master-data/values/{id}` | Update value | Any |
| `DELETE` | `/api/v1/master-data/values/{id}` | Delete value | Any |
| `PUT` | `/api/v1/master-data/categories/{id}/reorder` | Reorder values | Any |
| `POST` | `/api/v1/master-data/categories/{id}/import` | Import CSV | Any |

### Analytics & Audit

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/analytics/dashboard` | Dashboard metrics (platform-wide for super admin) | Any |
| `GET` | `/api/v1/analytics/top-users` | Top users by activity | Any |
| `GET` | `/api/v1/analytics/audit-logs` | Audit logs (platform logs for super admin) | Any |
| `GET` | `/api/v1/analytics/export` | Export dashboard as CSV | Any |
| `GET` | `/api/v1/analytics/audit-logs/export` | Export audit logs as CSV | Any |

## Project Structure

```
canvas_v1/
├── src/
│   ├── config/          # Settings (env vars, Pydantic)
│   ├── types/           # Pydantic schemas & enums
│   ├── repo/            # Database models & repositories
│   ├── service/         # Business logic
│   ├── runtime/
│   │   ├── app.py       # FastAPI app factory
│   │   ├── middleware/   # Tenant resolver middleware
│   │   ├── dependencies/ # Auth & DB session dependencies
│   │   └── routes/      # API route handlers
│   └── ui/              # (reserved for future)
├── frontend/
│   ├── src/
│   │   ├── pages/       # Page components (Login, Templates, Users, etc.)
│   │   ├── components/  # Reusable UI components
│   │   ├── services/    # API client functions
│   │   ├── context/     # React contexts (Auth, Wizard)
│   │   ├── types/       # TypeScript interfaces
│   │   └── router.tsx   # Route definitions
│   ├── vite.config.ts   # Vite config with API proxy
│   └── tailwind.config.js
├── scripts/
│   ├── setup_db.py      # Database & schema setup
│   ├── setup_keycloak.py # Keycloak realm setup
│   └── setup_all.py     # Full setup orchestrator
├── alembic/             # Database migrations
├── tests/               # Test suite
├── specs/               # Feature specs & stories
└── canvas_docs/         # Business requirements & tech spec
```

## Database Schema

### Platform (public schema)

- `tenants` — Tenant registry (name, slug, schema_name, keycloak_realm, branding)
- `tenant_plans` — Subscription plans
- `platform_audit_logs` — Super admin audit trail
- `alembic_version` — Migration tracking

### Per-Tenant Schema (tenant_acme, tenant_globex, etc.)

- `templates` — Evaluation templates (name, category, status, version)
- `template_tags` — Search tags
- `template_stages` — Evaluation stages (Desirable, Feasible, Viable)
- `template_sections` — Sections within stages
- `template_fields` — Fields within sections (text, select, number, date)
- `field_options` — Predefined options for select fields (with scores)
- `master_data_categories` — Organization-wide data categories
- `master_data_values` — Values within categories
- `audit_logs` — Tenant-scoped audit trail

## Environment Variables

Copy `.env.example` to `.env` and adjust:

```env
APP_NAME=Helio Canvas
APP_ENV=development
DEBUG=true
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/db_platform
DB_USER=postgres
DB_PASSWORD=postgres
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=helio
KEYCLOAK_CLIENT_ID=helio-admin
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=["http://localhost:5173"]
AUTH_MODE=keycloak
```

## Key Features

- **Template Wizard** — 5-step wizard (metadata, stages, fields/options, scoring, preview/publish)
- **Import from Master Data** — Pull predefined options from master data into template fields
- **Multi-Tenant Isolation** — Schema-per-tenant with Keycloak realm-per-tenant
- **Role-Based Access** — system_admin, admin, contributor, viewer with sidebar/route protection
- **Silent Token Refresh** — 15-min access token with automatic background refresh
- **Audit Logging** — All user/template/tenant actions logged per tenant + platform level
- **Real Analytics** — Dashboard metrics from actual DB data, not mock data
- **Super Admin Panel** — Tenant list, manage/delete tenants, platform-wide analytics

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Tailwind CSS, Vite |
| Backend | Python 3.12, FastAPI, SQLAlchemy (async), Pydantic v2 |
| Database | PostgreSQL 17 (schema-per-tenant) |
| Auth | Keycloak 24 (OIDC, JWT, per-tenant realms) |
| Migrations | Alembic |

## License

Confidential — Virtusa Helio Platform. For internal use and authorized partners only.
