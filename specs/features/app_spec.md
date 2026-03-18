# App Spec: Helio Canvas Admin Panel

**Status**: draft

## Overview

Helio Canvas is a multi-tenant admin panel for managing evaluation templates, users, tenants, master data, and analytics. Platform admins create configurable evaluation templates (with stages, fields, scoring formulas) that tenant users employ to assess AI/ML projects, RPA solutions, and other digital initiatives. The system enforces DB-per-tenant isolation with Keycloak-based OIDC authentication.

## Technology Stack

### Frontend
- **Framework**: React.js with Vite
- **Styling**: Tailwind CSS with custom design tokens (primary purple #5F2CFF, accent green #02F576, dark nav #1E2345)
- **State management**: React hooks + Context API (+ React Query for server state)
- **Routing**: React Router v6
- **Auth**: next-auth (Auth.js) with Keycloak OIDC provider (authorization code flow + PKCE)
- **Font**: Montserrat

### Backend
- **Runtime**: Python 3.11+ / FastAPI
- **ORM**: SQLAlchemy 2.0 (async with asyncpg)
- **Database**: PostgreSQL (localhost) — DB-per-tenant pattern
- **Migrations**: Alembic (per-tenant execution)
- **API style**: REST (JSON)
- **Authentication**: Keycloak JWT validation via JWKS endpoint
- **Caching**: Redis (tenant DB connection string cache)

### External Services
- **Keycloak** — OIDC identity provider (localhost), one realm per tenant
- **Redis** — Connection string caching, session store

### Infrastructure
- **Hosting**: Docker Compose (local dev), production TBD
- **CI/CD**: GitHub Actions
- **Containerization**: Docker
- **Database hosting**: PostgreSQL localhost
- **Secrets management**: Environment variables via src/config/
- **Deployment strategy**:
  - Environments: dev (local Docker Compose)
  - Triggers: manual
  - Zero-downtime: N/A for initial release

## Core Features

### Feature Group 1: Authentication & Authorization
- Sign in page with username/password form
- "Remember me" checkbox persists session
- "Forgot Password" link triggers Keycloak password reset flow
- "Register" link redirects to Keycloak self-registration
- JWT stored in httpOnly cookie, Bearer token on API calls
- Role-based access control (System Admin, Admin, Contributor, Viewer)
- FastAPI dependency injection validates JWT against Keycloak JWKS

### Feature Group 2: User Management
- List users with table (Name, Email, Role, Status, Last Login, Actions)
- Invite user via email (sends Keycloak realm invitation)
- Inline role assignment via dropdown (Admin, Contributor, Viewer)
- Status management (Active, Invited, Deactivated)
- Edit and delete user actions
- Search users by name/email
- Filter by role and status dropdowns
- Pagination (showing X of Y users)

### Feature Group 3: Template Management
- List all evaluation templates with grid/table view
- Create New Template via 5-step wizard:
  - **Step 1 — General Info**: Template name, category/domain dropdown (AI/ML Solutions, RPA Automation, Cloud Migration, FinOps Optimization), description (500 char max), icon picker, theme color picker, search tags
  - **Step 2 — Stage Config**: Add/remove/reorder evaluation stages via drag-and-drop (e.g., Desirable, Feasible, Viable)
  - **Step 3 — Fields & Sections**: Hierarchical section tree per stage, field configuration (field key, label, help text, mandatory toggle, scoring toggle), field types (text_short, single_select, etc.), option management with scores, live preview panel
  - **Step 4 — Scoring & Formulas**: Stage weight percentages with distribution chart, qualification thresholds per stage (min score to pass), action on fail (Warn/Block/Allow)
  - **Step 5 — Preview & Publish**: Desktop preview of template, summary stats (stages configured, total fields, scoring model, status), Save as Draft / Publish actions
- Edit existing template (reopens wizard)
- Delete template
- Template versioning (draft vs published status)

### Feature Group 4: Tenant Settings
- **General tab**: Organization name, logo upload (PNG/SVG max 2MB), timezone dropdown (Eastern/Pacific/London), default language (English/Spanish/French), default template selection
- **Branding tab**: Primary brand color picker, favicon upload (SVG/PNG/ICO max 512x512), font family selection (Montserrat/Inter/Roboto/Open Sans), email signature text area
- **Defaults tab**: Default configuration values
- "Back to All Tenants" navigation for super admins
- Discard / Save Changes actions
- Reset to Defaults option

### Feature Group 5: Master Data Management
- Left sidebar category picker:
  - Organizational Taxonomy (128 items)
  - KPIs (42 items)
  - Solution Types
  - Digital Platforms
  - ML Models
  - Risk Categories (14 items)
- Data table per category with columns: Value, Label, Severity, Description, Status
- Drag-to-reorder rows
- Add Value action
- Import from CSV
- Inline edit with toggle active/inactive
- Search within category
- Pagination

### Feature Group 6: Analytics & Audit Logs
- **Dashboard tab**:
  - Date range filter (Last 30 Days default)
  - Export Report button
  - KPI metric cards: Total Projects, Total Use Cases, Active Evaluations, Completed Evaluations, Average ROI
  - Bar chart: Use Cases by Stage (Desirable, Feasible, Viable, Prioritized, Not Started)
  - Pie/donut chart: Template Usage Distribution (AI/ML, RPA, Agentic AI, Data Science, Custom)
  - Line chart: Evaluations Over Time (monthly trend)
  - Top Users Activity table (user, evaluations count, last active)
- **Audit Log tab**:
  - Filter by User, Action Type (Login/Logout, Configuration Change, Data Export), Date
  - Apply Filters / Clear buttons
  - Log table: Date/Time, Actor, Event category (MANAGEMENT, SYSTEM, SECURITY), Details
  - Pagination (showing X of Y results)
  - Export Log button

### Feature Group 7: Sidebar Navigation (Shared Layout)
- Collapsible sidebar with icons + labels
- Navigation items: Template Management, User Management, Tenant Settings, Analytics & Audit Logs, Master Data Management
- Active state highlighting
- App branding: "Helio Canvas 2.0"
- User profile section: avatar, name, role badge

## Database Schema

### Platform Database (db_platform)

#### tenants
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | `PRIMARY KEY` | |
| `name` | `VARCHAR(255)` | `NOT NULL UNIQUE` | Organization name |
| `slug` | `VARCHAR(100)` | `NOT NULL UNIQUE` | URL-safe identifier |
| `keycloak_realm` | `VARCHAR(100)` | `NOT NULL UNIQUE` | Keycloak realm name |
| `db_name` | `VARCHAR(100)` | `NOT NULL UNIQUE` | Tenant database name |
| `db_host` | `VARCHAR(255)` | `NOT NULL DEFAULT 'localhost'` | |
| `db_port` | `INTEGER` | `NOT NULL DEFAULT 5432` | |
| `logo_url` | `TEXT` | | |
| `timezone` | `VARCHAR(50)` | `NOT NULL DEFAULT 'UTC'` | |
| `default_language` | `VARCHAR(10)` | `NOT NULL DEFAULT 'en'` | |
| `primary_color` | `VARCHAR(7)` | `DEFAULT '#5F2CFF'` | Hex color |
| `favicon_url` | `TEXT` | | |
| `font_family` | `VARCHAR(50)` | `DEFAULT 'Montserrat'` | |
| `email_signature` | `TEXT` | | |
| `is_active` | `BOOLEAN` | `NOT NULL DEFAULT TRUE` | |
| `created_at` | `TIMESTAMP` | `NOT NULL DEFAULT NOW()` | |
| `updated_at` | `TIMESTAMP` | `NOT NULL DEFAULT NOW()` | |

#### tenant_plans
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | `PRIMARY KEY` | |
| `tenant_id` | `UUID` | `FK -> tenants.id` | |
| `plan_name` | `VARCHAR(50)` | `NOT NULL` | free, pro, enterprise |
| `max_users` | `INTEGER` | `NOT NULL` | |
| `max_templates` | `INTEGER` | `NOT NULL` | |
| `valid_from` | `TIMESTAMP` | `NOT NULL` | |
| `valid_to` | `TIMESTAMP` | | |

### Tenant Database (db_tenant_{slug}) — repeated per tenant

#### templates
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | `PRIMARY KEY` | |
| `name` | `VARCHAR(255)` | `NOT NULL` | |
| `category` | `VARCHAR(100)` | `NOT NULL` | AI/ML, RPA, Cloud, FinOps |
| `description` | `TEXT` | | Max 500 chars enforced in app |
| `icon` | `VARCHAR(50)` | | Material icon name |
| `theme_color` | `VARCHAR(7)` | | Hex color |
| `status` | `VARCHAR(20)` | `NOT NULL DEFAULT 'draft'` | draft, published, archived |
| `version` | `INTEGER` | `NOT NULL DEFAULT 1` | |
| `created_by` | `UUID` | `NOT NULL` | Keycloak user ID |
| `created_at` | `TIMESTAMP` | `NOT NULL DEFAULT NOW()` | |
| `updated_at` | `TIMESTAMP` | `NOT NULL DEFAULT NOW()` | |

#### template_tags
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | `PRIMARY KEY` | |
| `template_id` | `UUID` | `FK -> templates.id ON DELETE CASCADE` | |
| `tag` | `VARCHAR(50)` | `NOT NULL` | |

#### template_stages
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | `PRIMARY KEY` | |
| `template_id` | `UUID` | `FK -> templates.id ON DELETE CASCADE` | |
| `name` | `VARCHAR(100)` | `NOT NULL` | e.g., Desirable, Feasible, Viable |
| `sort_order` | `INTEGER` | `NOT NULL` | |
| `weight_pct` | `DECIMAL(5,2)` | `DEFAULT 0` | Stage weight for scoring |
| `min_pass_score` | `DECIMAL(5,2)` | | Qualification threshold |
| `fail_action` | `VARCHAR(10)` | `DEFAULT 'warn'` | warn, block, allow |

#### template_sections
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | `PRIMARY KEY` | |
| `stage_id` | `UUID` | `FK -> template_stages.id ON DELETE CASCADE` | |
| `name` | `VARCHAR(200)` | `NOT NULL` | e.g., Business Opportunity |
| `sort_order` | `INTEGER` | `NOT NULL` | |

#### template_fields
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | `PRIMARY KEY` | |
| `section_id` | `UUID` | `FK -> template_sections.id ON DELETE CASCADE` | |
| `field_key` | `VARCHAR(100)` | `NOT NULL` | Machine-readable key |
| `label` | `VARCHAR(200)` | `NOT NULL` | Display label |
| `field_type` | `VARCHAR(30)` | `NOT NULL` | text_short, text_long, single_select, multi_select, number, date |
| `help_text` | `TEXT` | | |
| `is_mandatory` | `BOOLEAN` | `NOT NULL DEFAULT FALSE` | |
| `is_scoring` | `BOOLEAN` | `NOT NULL DEFAULT FALSE` | |
| `sort_order` | `INTEGER` | `NOT NULL` | |

#### field_options
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | `PRIMARY KEY` | |
| `field_id` | `UUID` | `FK -> template_fields.id ON DELETE CASCADE` | |
| `label` | `VARCHAR(200)` | `NOT NULL` | |
| `value` | `VARCHAR(200)` | `NOT NULL` | |
| `score` | `DECIMAL(5,2)` | `DEFAULT 0` | Points for this option |
| `sort_order` | `INTEGER` | `NOT NULL` | |

#### master_data_categories
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | `PRIMARY KEY` | |
| `name` | `VARCHAR(100)` | `NOT NULL UNIQUE` | e.g., risk_categories |
| `display_name` | `VARCHAR(200)` | `NOT NULL` | e.g., Risk Categories |
| `icon` | `VARCHAR(50)` | | Material icon name |
| `sort_order` | `INTEGER` | `NOT NULL` | |

#### master_data_values
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | `PRIMARY KEY` | |
| `category_id` | `UUID` | `FK -> master_data_categories.id ON DELETE CASCADE` | |
| `value` | `VARCHAR(200)` | `NOT NULL` | Machine key |
| `label` | `VARCHAR(200)` | `NOT NULL` | Display label |
| `severity` | `VARCHAR(20)` | | high, medium, low |
| `description` | `TEXT` | | |
| `is_active` | `BOOLEAN` | `NOT NULL DEFAULT TRUE` | |
| `sort_order` | `INTEGER` | `NOT NULL` | |

#### audit_logs
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `UUID` | `PRIMARY KEY` | |
| `user_id` | `UUID` | | Keycloak user ID, null for system events |
| `user_name` | `VARCHAR(200)` | | Denormalized for display |
| `event_type` | `VARCHAR(30)` | `NOT NULL` | MANAGEMENT, SYSTEM, SECURITY |
| `action` | `VARCHAR(100)` | `NOT NULL` | e.g., login, config_change, data_export |
| `details` | `TEXT` | | JSON details string |
| `ip_address` | `VARCHAR(45)` | | |
| `created_at` | `TIMESTAMP` | `NOT NULL DEFAULT NOW()` | |

**Index**: `idx_audit_logs_created_at` on `created_at DESC`
**Index**: `idx_audit_logs_user_id` on `user_id`

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/auth/login` | Redirect to Keycloak OIDC login |
| `POST` | `/api/v1/auth/callback` | Handle OIDC callback, issue session |
| `POST` | `/api/v1/auth/logout` | Revoke token, clear session |
| `GET` | `/api/v1/auth/me` | Get current user profile from JWT |

### Tenants (Platform Admin)
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/tenants` | List all tenants |
| `POST` | `/api/v1/tenants` | Create tenant (+ DB + Keycloak realm) |
| `GET` | `/api/v1/tenants/{tenant_id}` | Get tenant details |
| `PUT` | `/api/v1/tenants/{tenant_id}` | Update tenant settings |
| `DELETE` | `/api/v1/tenants/{tenant_id}` | Deactivate tenant |
| `PUT` | `/api/v1/tenants/{tenant_id}/branding` | Update branding settings |

### Users (Tenant-scoped)
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/users` | List users (with search, role/status filters, pagination) |
| `POST` | `/api/v1/users/invite` | Invite user via email |
| `GET` | `/api/v1/users/{user_id}` | Get user details |
| `PUT` | `/api/v1/users/{user_id}` | Update user (role, status) |
| `DELETE` | `/api/v1/users/{user_id}` | Deactivate user |

### Templates (Tenant-scoped)
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/templates` | List templates (with filters) |
| `POST` | `/api/v1/templates` | Create template (Step 1 data) |
| `GET` | `/api/v1/templates/{template_id}` | Get full template with stages/fields |
| `PUT` | `/api/v1/templates/{template_id}` | Update template metadata |
| `DELETE` | `/api/v1/templates/{template_id}` | Delete template |
| `PUT` | `/api/v1/templates/{template_id}/stages` | Update stages config (Step 2) |
| `PUT` | `/api/v1/templates/{template_id}/fields` | Update fields & sections (Step 3) |
| `PUT` | `/api/v1/templates/{template_id}/scoring` | Update scoring config (Step 4) |
| `POST` | `/api/v1/templates/{template_id}/publish` | Publish template (Step 5) |

### Master Data (Tenant-scoped)
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/master-data/categories` | List all categories with item counts |
| `GET` | `/api/v1/master-data/categories/{cat_id}/values` | List values for a category |
| `POST` | `/api/v1/master-data/categories/{cat_id}/values` | Add value |
| `PUT` | `/api/v1/master-data/values/{value_id}` | Update value |
| `DELETE` | `/api/v1/master-data/values/{value_id}` | Delete value |
| `PUT` | `/api/v1/master-data/categories/{cat_id}/reorder` | Reorder values |
| `POST` | `/api/v1/master-data/categories/{cat_id}/import` | Import from CSV |

### Analytics (Tenant-scoped)
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/analytics/dashboard` | Get dashboard metrics and chart data |
| `GET` | `/api/v1/analytics/top-users` | Get top users activity |
| `GET` | `/api/v1/analytics/audit-logs` | List audit logs (with filters, pagination) |
| `GET` | `/api/v1/analytics/export` | Export analytics report |

## UI Layout

### Main Structure
Fixed left sidebar (240px collapsed to 64px) + top header bar + scrollable main content area. Dark navy sidebar (#1E2345) with light content area.

### Sidebar
- App logo + "Helio Canvas 2.0" text (collapses to just logo)
- Navigation links with Material icons: Template Management, User Management, Tenant Settings, Analytics & Audit Logs, Master Data Management
- Active item highlighted with accent color left border + background tint
- Bottom: user avatar + name + role badge

### Top Header Bar
- Breadcrumb / page title
- Notification bell icon
- User avatar dropdown (profile, logout)

### Content Area
- Page title + description text
- Action buttons (top right aligned)
- Filter/search bar
- Data tables or form content
- Pagination controls at bottom

### Key Modals / Overlays
- **Invite User Modal** — triggered by "Invite User" button, email + role fields
- **Delete Confirmation Modal** — triggered by delete actions, confirm/cancel
- **CSV Import Modal** — triggered by "Import from CSV", file upload + preview

## Design System

### Colors
- **Primary**: #5F2CFF (purple — buttons, active states, links)
- **Accent**: #02F576 (neon green — success indicators, highlights)
- **Sidebar bg**: #1E2345 (dark navy)
- **Sidebar text**: #A0AEC0 (muted gray), white when active
- **Content bg**: #F7F8FC (light gray)
- **Card bg**: #FFFFFF
- **Text primary**: #1A202C
- **Text secondary**: #718096
- **Error**: #E53E3E
- **Warning**: #DD6B20
- **Success**: #38A169

### Typography
- **Font family**: Montserrat, system-ui fallback
- **Headings**: 600-700 weight
- **Body text**: 14px, 400 weight, 1.5 line-height
- **Small text**: 12px (table cells, captions)

### Component Patterns
- **Buttons**: Primary (purple bg, white text, rounded-lg), Secondary (outline), Icon buttons (ghost)
- **Inputs**: border-gray-300, rounded-lg, focus:ring-purple-500, 40px height
- **Cards**: white bg, rounded-xl, shadow-sm, p-6
- **Tables**: striped rows, sticky headers, hover highlight
- **Badges**: rounded-full, small text, colored bg (green=active, yellow=invited, red=deactivated)

## Key Interaction Flows

### Flow 1: Sign In
1. User navigates to login page
2. Enters username and password
3. Frontend redirects to Keycloak OIDC authorization endpoint
4. Keycloak authenticates and redirects back with auth code
5. Backend exchanges code for tokens, validates JWT
6. Frontend stores JWT in httpOnly cookie, redirects to dashboard

### Flow 2: Create Evaluation Template
1. Admin clicks "Create New Template" on Template Management page
2. Step 1: Fills general info (name, category, description, icon, color, tags) → Next
3. Step 2: Adds/reorders evaluation stages (Desirable, Feasible, Viable) → Next
4. Step 3: Builds field structure per stage — adds sections, adds fields to sections, configures field types and scoring options → Next
5. Step 4: Sets stage weight percentages, qualification thresholds, fail actions → Next
6. Step 5: Reviews preview, checks summary stats → Publish or Save as Draft
7. System validates all steps, sets status to published

### Flow 3: Manage Master Data
1. Admin navigates to Master Data Management
2. Selects category from left sidebar (e.g., Risk Categories)
3. Views data table with existing values
4. Can: Add Value (inline form), Edit (click edit icon), Toggle active/inactive, Reorder (drag), Import CSV
5. Changes save immediately with optimistic UI updates

### Flow 4: Manage Tenant Settings
1. Super admin navigates to Tenant Settings
2. Selects tab (General / Branding / Defaults)
3. Modifies form fields
4. Clicks "Save Changes" to persist or "Discard" to revert

## Implementation Phases

### Phase 1: Foundation & Auth
- Project scaffolding (FastAPI + React + Docker Compose)
- PostgreSQL platform database setup with tenants table
- Keycloak integration (realm creation, OIDC flow)
- JWT validation middleware in FastAPI
- Tenant resolution from JWT claims
- Dynamic DB session routing per tenant
- Login/logout UI
- **Milestone**: User can sign in via Keycloak and be routed to correct tenant

### Phase 2: Core Admin — Users & Tenant Settings
- User management CRUD API + UI (list, invite, edit role, deactivate)
- Tenant settings API + UI (general, branding, defaults tabs)
- Sidebar navigation layout with all routes
- **Milestone**: Admin can manage users and configure tenant settings

### Phase 3: Template Management
- Template CRUD API
- 5-step wizard UI (General Info, Stage Config, Fields & Sections, Scoring, Preview & Publish)
- Template listing page with status badges
- **Milestone**: Admin can create, edit, and publish evaluation templates

### Phase 4: Master Data & Analytics
- Master data categories + values CRUD API + UI
- CSV import endpoint
- Analytics dashboard API (aggregated metrics, chart data)
- Analytics dashboard UI (metric cards, charts)
- Audit log API + UI (filterable, paginated)
- **Milestone**: Full admin panel feature-complete

## Success Criteria

### Functional
- [ ] User can sign in via Keycloak OIDC and access tenant-specific data
- [ ] CRUD operations work for users, templates, master data, tenant settings
- [ ] Template wizard creates valid templates with stages, fields, and scoring
- [ ] Analytics dashboard shows accurate aggregated metrics
- [ ] Audit log captures all admin actions

### User Experience
- [ ] Desktop responsive layout (1280px+ viewport)
- [ ] Consistent design system (colors, typography, spacing)
- [ ] Navigation between all sections works seamlessly
- [ ] Form validation with clear error messages

### Technical
- [ ] Clean 6-layer architecture maintained
- [ ] Test coverage >= 80%
- [ ] All linters pass
- [ ] No hardcoded secrets
- [ ] Tenant isolation enforced — no cross-tenant data leaks

## Non-Functional Requirements

- **Performance**: API response < 500ms, page transitions < 1s
- **Security**: JWT validation on all endpoints, CORS configured, input sanitization, tenant isolation in DB queries
- **Scalability**: Pagination on all list endpoints, DB connection pooling
- **Accessibility**: Keyboard navigation for forms, ARIA labels on interactive elements
