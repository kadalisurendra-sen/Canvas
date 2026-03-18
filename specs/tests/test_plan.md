# Helio Canvas Admin Panel — Test Plan

**Status**: draft
**Last Updated**: 2026-03-17
**Coverage Target**: >= 80% overall, >= 90% on critical paths

---

## 1. Unit Tests (per layer)

### 1.1 Types Layer (`src/types/`)

| ID | Test Name | Description | Priority |
|----|-----------|-------------|----------|
| T-001 | `test_tenant_model_valid` | Create Tenant model with all required fields — should succeed | High |
| T-002 | `test_tenant_model_missing_name` | Omit `name` — should raise ValidationError | High |
| T-003 | `test_tenant_model_slug_format` | Slug with spaces/special chars — should reject | High |
| T-004 | `test_tenant_model_default_values` | Verify defaults: `timezone='UTC'`, `default_language='en'`, `primary_color='#5F2CFF'`, `font_family='Montserrat'`, `is_active=True` | Medium |
| T-005 | `test_tenant_model_hex_color_validation` | Invalid hex color (e.g., `'purple'`) — should reject | Medium |
| T-006 | `test_template_model_valid` | Create Template with name, category, status — should succeed | High |
| T-007 | `test_template_model_invalid_category` | Category not in allowed set — should reject | High |
| T-008 | `test_template_model_description_max_length` | Description over 500 chars — should reject | Medium |
| T-009 | `test_template_status_enum` | Validate enum values: `draft`, `published`, `archived` | High |
| T-010 | `test_template_status_invalid` | Invalid status string — should reject | Medium |
| T-011 | `test_template_stage_model_valid` | Create TemplateStage with required fields — should succeed | High |
| T-012 | `test_template_stage_weight_range` | `weight_pct` outside 0-100 — should reject | Medium |
| T-013 | `test_template_stage_fail_action_enum` | Validate: `warn`, `block`, `allow` | High |
| T-014 | `test_template_section_model_valid` | Create TemplateSection — should succeed | Medium |
| T-015 | `test_template_field_model_valid` | Create TemplateField with all field types — should succeed | High |
| T-016 | `test_template_field_type_enum` | Validate: `text_short`, `text_long`, `single_select`, `multi_select`, `number`, `date` | High |
| T-017 | `test_field_option_model_valid` | Create FieldOption with label, value, score — should succeed | Medium |
| T-018 | `test_field_option_score_decimal` | Score as decimal (e.g., `3.50`) — should succeed | Low |
| T-019 | `test_master_data_category_model_valid` | Create MasterDataCategory — should succeed | Medium |
| T-020 | `test_master_data_value_model_valid` | Create MasterDataValue — should succeed | Medium |
| T-021 | `test_master_data_value_severity_enum` | Validate: `high`, `medium`, `low` or None | Medium |
| T-022 | `test_audit_log_model_valid` | Create AuditLog — should succeed | Medium |
| T-023 | `test_audit_log_event_type_enum` | Validate: `MANAGEMENT`, `SYSTEM`, `SECURITY` | High |
| T-024 | `test_user_role_enum` | Validate: `System Admin`, `Admin`, `Contributor`, `Viewer` | High |
| T-025 | `test_user_status_enum` | Validate: `Active`, `Invited`, `Deactivated` | High |
| T-026 | `test_tenant_plan_model_valid` | Create TenantPlan with plan_name, max_users, max_templates — should succeed | Medium |
| T-027 | `test_tenant_plan_name_enum` | Validate: `free`, `pro`, `enterprise` | Medium |
| T-028 | `test_template_tag_model_valid` | Create TemplateTag with template_id and tag string — should succeed | Low |

### 1.2 Config Layer (`src/config/`)

| ID | Test Name | Description | Priority |
|----|-----------|-------------|----------|
| T-029 | `test_settings_loads_from_env` | Set env vars and verify Settings fields match | High |
| T-030 | `test_settings_default_values` | No env vars set — defaults applied (DB port 5432, host localhost) | High |
| T-031 | `test_database_url_construction` | Verify `postgresql+asyncpg://user:pass@host:port/db` format | High |
| T-032 | `test_platform_db_url` | Platform DB URL points to `db_platform` | High |
| T-033 | `test_tenant_db_url_format` | Tenant DB URL constructed from tenant slug: `db_tenant_{slug}` | High |
| T-034 | `test_keycloak_base_url_config` | Keycloak URL loaded from env | Medium |
| T-035 | `test_redis_url_config` | Redis URL loaded from env | Medium |
| T-036 | `test_cors_origins_config` | CORS allowed origins loaded as list | Medium |
| T-037 | `test_jwt_algorithm_config` | JWT algorithm defaults to RS256 | Low |
| T-038 | `test_missing_required_env_var` | Omit required env var — should raise or use sensible default | High |

### 1.3 Repo Layer (`src/repo/`)

| ID | Test Name | Description | Priority |
|----|-----------|-------------|----------|
| T-039 | `test_tenant_repo_create` | Insert tenant record — returns Tenant with generated UUID | High |
| T-040 | `test_tenant_repo_get_by_id` | Retrieve tenant by UUID — should match inserted data | High |
| T-041 | `test_tenant_repo_get_by_slug` | Retrieve tenant by slug — should match | High |
| T-042 | `test_tenant_repo_list_all` | List tenants — returns all active tenants | Medium |
| T-043 | `test_tenant_repo_update` | Update tenant name — should persist change | High |
| T-044 | `test_tenant_repo_deactivate` | Set `is_active=False` — should soft-delete | High |
| T-045 | `test_template_repo_create` | Insert template — returns Template with UUID | High |
| T-046 | `test_template_repo_get_by_id` | Retrieve template with nested stages/sections/fields | High |
| T-047 | `test_template_repo_list_with_filters` | Filter by category, status — returns matching subset | High |
| T-048 | `test_template_repo_list_pagination` | Paginate results with offset/limit — correct page returned | Medium |
| T-049 | `test_template_repo_update` | Update template metadata — persists | High |
| T-050 | `test_template_repo_delete` | Delete template — cascades to stages/sections/fields | High |
| T-051 | `test_template_stage_repo_bulk_upsert` | Insert/update multiple stages for a template | High |
| T-052 | `test_template_stage_repo_reorder` | Update sort_order for stages — order persisted | Medium |
| T-053 | `test_template_section_repo_create` | Insert section under a stage | Medium |
| T-054 | `test_template_field_repo_create` | Insert field under a section | Medium |
| T-055 | `test_template_field_repo_with_options` | Insert field with associated options — cascade reads work | High |
| T-056 | `test_field_option_repo_create` | Insert option under a field with score | Medium |
| T-057 | `test_master_data_category_repo_list` | List all categories with item counts | Medium |
| T-058 | `test_master_data_category_repo_create` | Insert category — returns with UUID | Medium |
| T-059 | `test_master_data_value_repo_list_by_category` | List values filtered by category_id | High |
| T-060 | `test_master_data_value_repo_create` | Insert value — returns with UUID | Medium |
| T-061 | `test_master_data_value_repo_update` | Update value label/severity — persists | Medium |
| T-062 | `test_master_data_value_repo_delete` | Delete value by ID | Medium |
| T-063 | `test_master_data_value_repo_reorder` | Bulk update sort_order — order persisted | Medium |
| T-064 | `test_master_data_value_repo_search` | Search values by label within category | Medium |
| T-065 | `test_master_data_value_repo_pagination` | Paginate values — correct page returned | Low |
| T-066 | `test_audit_log_repo_create` | Insert audit log entry | High |
| T-067 | `test_audit_log_repo_list_with_filters` | Filter by user_id, event_type, date range | High |
| T-068 | `test_audit_log_repo_pagination` | Paginate audit logs — ordered by created_at DESC | Medium |
| T-069 | `test_tenant_isolation_templates` | Query templates on DB A — should not return data from DB B | Critical |
| T-070 | `test_tenant_isolation_master_data` | Query master data on DB A — should not return data from DB B | Critical |
| T-071 | `test_tenant_isolation_audit_logs` | Query audit logs on DB A — should not return data from DB B | Critical |

### 1.4 Service Layer (`src/service/`)

| ID | Test Name | Description | Priority |
|----|-----------|-------------|----------|
| T-072 | `test_template_wizard_create_step1` | Create template with general info — returns draft template | High |
| T-073 | `test_template_wizard_update_stages` | Update stages for existing template — stages saved with sort_order | High |
| T-074 | `test_template_wizard_update_fields` | Update fields/sections for template — nested hierarchy saved | High |
| T-075 | `test_template_wizard_update_scoring` | Set stage weights, thresholds, fail actions — saved correctly | High |
| T-076 | `test_template_wizard_weights_must_sum_100` | Stage weights not summing to 100 — should reject | High |
| T-077 | `test_template_wizard_publish` | Publish draft template — status changes to `published`, version increments | High |
| T-078 | `test_template_wizard_publish_incomplete` | Publish template missing required stages — should reject | High |
| T-079 | `test_template_wizard_save_draft` | Save as draft — status remains `draft` | Medium |
| T-080 | `test_user_invite_service` | Invite user with email and role — creates Keycloak user, returns invitation | High |
| T-081 | `test_user_invite_duplicate_email` | Invite already-existing email — should reject with error | High |
| T-082 | `test_user_update_role` | Change user role — updates in Keycloak realm | Medium |
| T-083 | `test_user_deactivate` | Deactivate user — disables in Keycloak, updates status | Medium |
| T-084 | `test_tenant_provisioning_creates_db` | Provision tenant — creates new PostgreSQL database | Critical |
| T-085 | `test_tenant_provisioning_creates_realm` | Provision tenant — creates Keycloak realm | Critical |
| T-086 | `test_tenant_provisioning_rollback_on_failure` | DB created but Keycloak fails — rolls back DB creation | High |
| T-087 | `test_master_data_csv_import_valid` | Import valid CSV — creates values in correct category | High |
| T-088 | `test_master_data_csv_import_invalid_headers` | CSV missing required columns — returns validation error | High |
| T-089 | `test_master_data_csv_import_partial_failure` | Some rows invalid — returns error details, no partial commit | Medium |
| T-090 | `test_master_data_csv_import_empty_file` | Empty CSV — returns error | Low |
| T-091 | `test_analytics_dashboard_metrics` | Aggregate metrics — returns correct totals for projects, use cases, evaluations, ROI | High |
| T-092 | `test_analytics_use_cases_by_stage` | Chart data — correct counts per stage | Medium |
| T-093 | `test_analytics_template_usage_distribution` | Chart data — correct distribution percentages | Medium |
| T-094 | `test_analytics_evaluations_over_time` | Monthly trend data — correct month-by-month counts | Medium |
| T-095 | `test_analytics_top_users` | Top users — ordered by evaluation count descending | Medium |
| T-096 | `test_analytics_date_range_filter` | Apply date range — only includes data within range | High |
| T-097 | `test_audit_log_create_on_login` | Login event — creates SECURITY audit log entry | High |
| T-098 | `test_audit_log_create_on_config_change` | Config change — creates MANAGEMENT audit log entry | Medium |
| T-099 | `test_audit_log_create_on_data_export` | Data export — creates SYSTEM audit log entry | Medium |
| T-100 | `test_tenant_settings_update` | Update tenant general settings — persists all fields | Medium |
| T-101 | `test_tenant_branding_update` | Update branding (color, favicon, font) — persists | Medium |
| T-102 | `test_tenant_settings_reset_defaults` | Reset to defaults — reverts to original values | Low |

### 1.5 Runtime Layer (`src/runtime/`)

| ID | Test Name | Description | Priority |
|----|-----------|-------------|----------|
| **Auth Endpoints** | | | |
| T-103 | `test_auth_login_redirect` | `POST /api/v1/auth/login` — returns Keycloak OIDC redirect URL | High |
| T-104 | `test_auth_callback_valid_code` | `POST /api/v1/auth/callback` with valid auth code — sets JWT cookie, returns user | High |
| T-105 | `test_auth_callback_invalid_code` | `POST /api/v1/auth/callback` with invalid code — returns 401 | High |
| T-106 | `test_auth_logout` | `POST /api/v1/auth/logout` — clears session, revokes token | High |
| T-107 | `test_auth_me_valid_token` | `GET /api/v1/auth/me` with valid JWT — returns user profile | High |
| T-108 | `test_auth_me_no_token` | `GET /api/v1/auth/me` without JWT — returns 401 | High |
| **JWT Middleware** | | | |
| T-109 | `test_jwt_valid_token` | Valid JWT with correct claims — request proceeds | Critical |
| T-110 | `test_jwt_expired_token` | Expired JWT — returns 401 | Critical |
| T-111 | `test_jwt_wrong_signature` | JWT signed with wrong key — returns 401 | Critical |
| T-112 | `test_jwt_missing_tenant_claim` | JWT without tenant claim — returns 403 | High |
| T-113 | `test_jwt_wrong_tenant` | JWT for tenant A accessing tenant B data — returns 403 | Critical |
| **Tenant Resolution Middleware** | | | |
| T-114 | `test_tenant_resolution_from_jwt` | Extract tenant slug from JWT claims — resolves to correct DB | Critical |
| T-115 | `test_tenant_resolution_inactive_tenant` | Tenant is deactivated — returns 403 | High |
| T-116 | `test_tenant_resolution_unknown_tenant` | Unknown tenant slug — returns 404 | High |
| **RBAC** | | | |
| T-117 | `test_rbac_system_admin_full_access` | System Admin can access all endpoints | High |
| T-118 | `test_rbac_admin_manage_users` | Admin can invite/edit/deactivate users | High |
| T-119 | `test_rbac_contributor_edit_templates` | Contributor can create/edit templates | High |
| T-120 | `test_rbac_viewer_read_only` | Viewer cannot create/edit/delete — returns 403 | High |
| T-121 | `test_rbac_viewer_can_list` | Viewer can list templates, users, master data | Medium |
| **Tenant Endpoints** | | | |
| T-122 | `test_tenants_list` | `GET /api/v1/tenants` — returns tenant list (platform admin only) | High |
| T-123 | `test_tenants_create` | `POST /api/v1/tenants` — creates tenant with DB + realm | High |
| T-124 | `test_tenants_get_by_id` | `GET /api/v1/tenants/{id}` — returns tenant details | Medium |
| T-125 | `test_tenants_update` | `PUT /api/v1/tenants/{id}` — updates settings | Medium |
| T-126 | `test_tenants_delete` | `DELETE /api/v1/tenants/{id}` — deactivates tenant | Medium |
| T-127 | `test_tenants_update_branding` | `PUT /api/v1/tenants/{id}/branding` — updates branding | Medium |
| T-128 | `test_tenants_non_admin_forbidden` | Non-platform-admin accessing tenants — returns 403 | High |
| **User Endpoints** | | | |
| T-129 | `test_users_list` | `GET /api/v1/users` — returns user list with pagination | High |
| T-130 | `test_users_list_search` | `GET /api/v1/users?search=john` — filters by name/email | Medium |
| T-131 | `test_users_list_filter_role` | `GET /api/v1/users?role=Admin` — filters by role | Medium |
| T-132 | `test_users_list_filter_status` | `GET /api/v1/users?status=Active` — filters by status | Medium |
| T-133 | `test_users_invite` | `POST /api/v1/users/invite` — sends invitation | High |
| T-134 | `test_users_invite_invalid_email` | Invite with malformed email — returns 422 | Medium |
| T-135 | `test_users_get_by_id` | `GET /api/v1/users/{id}` — returns user details | Medium |
| T-136 | `test_users_update` | `PUT /api/v1/users/{id}` — updates role/status | Medium |
| T-137 | `test_users_delete` | `DELETE /api/v1/users/{id}` — deactivates user | Medium |
| **Template Endpoints** | | | |
| T-138 | `test_templates_list` | `GET /api/v1/templates` — returns template list | High |
| T-139 | `test_templates_list_filter_category` | Filter by category — returns matching templates | Medium |
| T-140 | `test_templates_list_filter_status` | Filter by status — returns matching templates | Medium |
| T-141 | `test_templates_create` | `POST /api/v1/templates` — creates draft template (step 1) | High |
| T-142 | `test_templates_create_missing_name` | Create without name — returns 422 | Medium |
| T-143 | `test_templates_get_by_id` | `GET /api/v1/templates/{id}` — returns full template with stages/fields | High |
| T-144 | `test_templates_get_not_found` | Get non-existent ID — returns 404 | Medium |
| T-145 | `test_templates_update` | `PUT /api/v1/templates/{id}` — updates metadata | Medium |
| T-146 | `test_templates_delete` | `DELETE /api/v1/templates/{id}` — removes template | Medium |
| T-147 | `test_templates_update_stages` | `PUT /api/v1/templates/{id}/stages` — updates stage config | High |
| T-148 | `test_templates_update_fields` | `PUT /api/v1/templates/{id}/fields` — updates fields/sections | High |
| T-149 | `test_templates_update_scoring` | `PUT /api/v1/templates/{id}/scoring` — updates scoring | High |
| T-150 | `test_templates_publish` | `POST /api/v1/templates/{id}/publish` — publishes template | High |
| T-151 | `test_templates_publish_already_published` | Publish already-published template — returns 409 or idempotent success | Medium |
| **Master Data Endpoints** | | | |
| T-152 | `test_master_data_list_categories` | `GET /api/v1/master-data/categories` — returns categories with counts | High |
| T-153 | `test_master_data_list_values` | `GET /api/v1/master-data/categories/{id}/values` — returns values | High |
| T-154 | `test_master_data_create_value` | `POST /api/v1/master-data/categories/{id}/values` — adds value | High |
| T-155 | `test_master_data_create_value_invalid` | Missing required fields — returns 422 | Medium |
| T-156 | `test_master_data_update_value` | `PUT /api/v1/master-data/values/{id}` — updates value | Medium |
| T-157 | `test_master_data_delete_value` | `DELETE /api/v1/master-data/values/{id}` — removes value | Medium |
| T-158 | `test_master_data_reorder` | `PUT /api/v1/master-data/categories/{id}/reorder` — updates order | Medium |
| T-159 | `test_master_data_import_csv` | `POST /api/v1/master-data/categories/{id}/import` — imports CSV | High |
| T-160 | `test_master_data_import_csv_bad_format` | Upload non-CSV file — returns 422 | Medium |
| **Analytics Endpoints** | | | |
| T-161 | `test_analytics_dashboard` | `GET /api/v1/analytics/dashboard` — returns metrics + chart data | High |
| T-162 | `test_analytics_dashboard_date_filter` | `GET /api/v1/analytics/dashboard?from=...&to=...` — filtered results | Medium |
| T-163 | `test_analytics_top_users` | `GET /api/v1/analytics/top-users` — returns ranked user list | Medium |
| T-164 | `test_analytics_audit_logs` | `GET /api/v1/analytics/audit-logs` — returns paginated logs | High |
| T-165 | `test_analytics_audit_logs_filter_user` | Filter logs by user — returns matching entries | Medium |
| T-166 | `test_analytics_audit_logs_filter_action` | Filter logs by action type — returns matching entries | Medium |
| T-167 | `test_analytics_audit_logs_filter_date` | Filter logs by date range — returns matching entries | Medium |
| T-168 | `test_analytics_export` | `GET /api/v1/analytics/export` — returns downloadable report | Medium |
| **Request Validation** | | | |
| T-169 | `test_request_missing_required_body` | POST with empty body — returns 422 | Medium |
| T-170 | `test_request_invalid_uuid_param` | Path param with invalid UUID — returns 422 | Medium |
| T-171 | `test_request_invalid_query_param_type` | Query param wrong type (e.g., `page=abc`) — returns 422 | Low |

---

## 2. Integration Tests

| ID | Test Name | Description | Priority |
|----|-----------|-------------|----------|
| T-172 | `test_integ_db_template_crud` | Create, read, update, delete template against real PostgreSQL — full round-trip | High |
| T-173 | `test_integ_db_template_cascade_delete` | Delete template — verify stages, sections, fields, options all removed | High |
| T-174 | `test_integ_db_master_data_crud` | Create category, add values, update, delete against real DB | High |
| T-175 | `test_integ_db_audit_log_write_read` | Write audit log entries, query with filters — correct results | Medium |
| T-176 | `test_integ_db_tenant_crud` | Create, update, deactivate tenant in platform DB | High |
| T-177 | `test_integ_keycloak_token_validation` | Obtain real JWT from Keycloak, validate with JWKS endpoint | Critical |
| T-178 | `test_integ_keycloak_user_creation` | Create user in Keycloak realm, verify user exists | High |
| T-179 | `test_integ_multi_tenant_db_routing` | Create two tenants, write data to each, verify isolation when querying | Critical |
| T-180 | `test_integ_multi_tenant_connection_pool` | Connect to tenant A, then tenant B, then tenant A again — connection reuse | Medium |
| T-181 | `test_integ_redis_tenant_cache` | Cache tenant DB connection string in Redis, retrieve it, verify TTL | Medium |
| T-182 | `test_integ_template_wizard_e2e` | Step 1 through Step 5 (create -> stages -> fields -> scoring -> publish) against real DB | Critical |
| T-183 | `test_integ_csv_import_real_file` | Upload actual CSV file to master data import endpoint — values persisted | High |
| T-184 | `test_integ_csv_import_large_file` | Import CSV with 1000+ rows — completes within timeout, all rows persisted | Medium |
| T-185 | `test_integ_alembic_migration` | Run Alembic migrations on fresh tenant DB — schema matches expected | High |
| T-186 | `test_integ_tenant_provisioning_full` | Provision tenant end-to-end: platform DB record + tenant DB + Keycloak realm | Critical |

---

## 3. E2E Tests

| ID | Test Name | Description | Priority |
|----|-----------|-------------|----------|
| **Authentication Flow** | | | |
| T-187 | `test_e2e_login_flow` | Navigate to login, enter credentials, Keycloak redirect, callback, land on dashboard | Critical |
| T-188 | `test_e2e_login_invalid_credentials` | Enter wrong password — error message displayed | High |
| T-189 | `test_e2e_login_remember_me` | Check "Remember me", login, close browser, reopen — still authenticated | Medium |
| T-190 | `test_e2e_logout` | Click logout — session cleared, redirected to login page | High |
| T-191 | `test_e2e_forgot_password` | Click "Forgot Password" — redirects to Keycloak reset flow | Medium |
| **User Management CRUD** | | | |
| T-192 | `test_e2e_users_list_page` | Navigate to User Management — table loads with users | High |
| T-193 | `test_e2e_users_search` | Type in search box — table filters by name/email | Medium |
| T-194 | `test_e2e_users_filter_role` | Select role from dropdown — table filters | Medium |
| T-195 | `test_e2e_users_filter_status` | Select status from dropdown — table filters | Medium |
| T-196 | `test_e2e_users_invite` | Click "Invite User", fill email + role, submit — user appears in table as Invited | High |
| T-197 | `test_e2e_users_edit_role` | Click edit on user, change role via dropdown — role updated | Medium |
| T-198 | `test_e2e_users_deactivate` | Click delete on user, confirm — status changes to Deactivated | Medium |
| T-199 | `test_e2e_users_pagination` | Navigate through pages — correct users displayed per page | Low |
| **Template Creation Wizard** | | | |
| T-200 | `test_e2e_template_wizard_step1` | Fill general info (name, category, description, icon, color, tags) — proceed to step 2 | High |
| T-201 | `test_e2e_template_wizard_step2` | Add stages, reorder via drag-drop — proceed to step 3 | High |
| T-202 | `test_e2e_template_wizard_step3` | Add sections, add fields, configure types and options — proceed to step 4 | High |
| T-203 | `test_e2e_template_wizard_step4` | Set stage weights (summing to 100%), thresholds, fail actions — proceed to step 5 | High |
| T-204 | `test_e2e_template_wizard_step5_publish` | Review preview, click Publish — template status becomes published | High |
| T-205 | `test_e2e_template_wizard_step5_save_draft` | Review preview, click Save as Draft — template saved with draft status | Medium |
| T-206 | `test_e2e_template_wizard_back_navigation` | Navigate back between steps — data preserved | Medium |
| T-207 | `test_e2e_template_edit` | Click edit on existing template — wizard opens with pre-filled data | Medium |
| T-208 | `test_e2e_template_delete` | Click delete, confirm — template removed from list | Medium |
| T-209 | `test_e2e_template_list_views` | Toggle between grid and table view — both render correctly | Low |
| **Master Data Management** | | | |
| T-210 | `test_e2e_master_data_browse_categories` | Navigate to Master Data — sidebar shows categories with item counts | High |
| T-211 | `test_e2e_master_data_select_category` | Click category in sidebar — table loads with values | High |
| T-212 | `test_e2e_master_data_add_value` | Click "Add Value", fill fields, save — value appears in table | High |
| T-213 | `test_e2e_master_data_edit_value` | Click edit icon on value, modify fields — changes saved | Medium |
| T-214 | `test_e2e_master_data_toggle_active` | Toggle active/inactive — status updates | Medium |
| T-215 | `test_e2e_master_data_reorder` | Drag row to new position — sort order persisted | Medium |
| T-216 | `test_e2e_master_data_import_csv` | Click "Import from CSV", upload file, preview — values imported | High |
| T-217 | `test_e2e_master_data_search` | Type in search box — table filters within category | Medium |
| **Analytics Dashboard** | | | |
| T-218 | `test_e2e_analytics_dashboard_loads` | Navigate to Analytics — metric cards and charts render | High |
| T-219 | `test_e2e_analytics_date_filter` | Change date range — charts and metrics update | Medium |
| T-220 | `test_e2e_analytics_export` | Click "Export Report" — file downloads | Medium |
| T-221 | `test_e2e_analytics_top_users_table` | Top users table renders with correct columns | Low |
| **Audit Log** | | | |
| T-222 | `test_e2e_audit_log_list` | Navigate to Audit Log tab — log table loads | High |
| T-223 | `test_e2e_audit_log_filter_user` | Filter by user — table filters | Medium |
| T-224 | `test_e2e_audit_log_filter_action` | Filter by action type — table filters | Medium |
| T-225 | `test_e2e_audit_log_filter_date` | Filter by date range — table filters | Medium |
| T-226 | `test_e2e_audit_log_clear_filters` | Click "Clear" — filters reset, full list shown | Low |
| T-227 | `test_e2e_audit_log_pagination` | Navigate through pages — correct entries displayed | Low |
| T-228 | `test_e2e_audit_log_export` | Click "Export Log" — file downloads | Medium |
| **Tenant Settings** | | | |
| T-229 | `test_e2e_tenant_settings_general` | Navigate to Tenant Settings > General — form loads with current values | Medium |
| T-230 | `test_e2e_tenant_settings_branding` | Switch to Branding tab — color picker, font selector visible | Medium |
| T-231 | `test_e2e_tenant_settings_save` | Modify fields, click "Save Changes" — changes persisted | Medium |
| T-232 | `test_e2e_tenant_settings_discard` | Modify fields, click "Discard" — reverts to saved values | Medium |
| T-233 | `test_e2e_tenant_settings_reset_defaults` | Click "Reset to Defaults" — all fields revert | Low |
| **Navigation** | | | |
| T-234 | `test_e2e_sidebar_navigation` | Click each nav item — correct page loads | Medium |
| T-235 | `test_e2e_sidebar_collapse` | Collapse sidebar — icons visible, labels hidden | Low |
| T-236 | `test_e2e_sidebar_active_state` | Navigate to page — correct nav item highlighted | Low |

---

## 4. Coverage Targets

| Scope | Target | Rationale |
|-------|--------|-----------|
| **Overall** | >= 80% | Project quality gate (enforced by `pytest --cov-fail-under=80`) |
| **Auth flow** (`src/runtime/` auth middleware + endpoints) | >= 90% | Security-critical: JWT validation, token handling |
| **Tenant isolation** (`src/repo/` tenant-scoped queries, `src/runtime/` tenant middleware) | >= 90% | Data safety: must prevent cross-tenant leaks |
| **Template wizard** (`src/service/` orchestration, `src/runtime/` wizard endpoints) | >= 90% | Core business logic: multi-step workflow with validation |
| **Types layer** (`src/types/`) | >= 95% | Foundational: all models should be fully validated |
| **Config layer** (`src/config/`) | >= 85% | Important but simpler surface area |
| **Master data** (`src/service/` + `src/repo/` + `src/runtime/`) | >= 80% | Standard CRUD, import logic needs coverage |
| **Analytics** (`src/service/` + `src/runtime/`) | >= 75% | Aggregation logic important, but lower risk |

---

## 5. Test Infrastructure

### Fixtures and Helpers

| Fixture | Scope | Description |
|---------|-------|-------------|
| `db_session` | function | Async SQLAlchemy session with transaction rollback per test |
| `platform_db` | session | Platform database connection (testcontainers or test DB) |
| `tenant_db` | function | Isolated tenant database per test |
| `test_client` | function | FastAPI `AsyncClient` (httpx) with overridden dependencies |
| `mock_keycloak` | function | Mocked Keycloak client (unit tests) |
| `keycloak_client` | session | Real Keycloak client (integration tests) |
| `valid_jwt` | function | Factory for generating valid JWT tokens with configurable claims |
| `expired_jwt` | function | Factory for expired JWT tokens |
| `sample_template` | function | Pre-built template with stages, sections, fields, options |
| `sample_csv_file` | function | Temporary CSV file with valid master data |
| `redis_client` | session | Redis client (testcontainers or test instance) |

### Test Organization

```
tests/
  conftest.py                    # Shared fixtures
  unit/
    types/
      test_tenant_models.py      # T-001 through T-005
      test_template_models.py    # T-006 through T-018
      test_master_data_models.py # T-019 through T-021
      test_audit_models.py       # T-022 through T-023
      test_enums.py              # T-024 through T-028
    config/
      test_settings.py           # T-029 through T-038
    repo/
      test_tenant_repo.py        # T-039 through T-044
      test_template_repo.py      # T-045 through T-056
      test_master_data_repo.py   # T-057 through T-065
      test_audit_log_repo.py     # T-066 through T-068
      test_tenant_isolation.py   # T-069 through T-071
    service/
      test_template_wizard.py    # T-072 through T-079
      test_user_service.py       # T-080 through T-083
      test_tenant_service.py     # T-084 through T-086
      test_csv_import.py         # T-087 through T-090
      test_analytics_service.py  # T-091 through T-096
      test_audit_service.py      # T-097 through T-099
      test_tenant_settings.py    # T-100 through T-102
    runtime/
      test_auth_endpoints.py     # T-103 through T-108
      test_jwt_middleware.py      # T-109 through T-113
      test_tenant_middleware.py   # T-114 through T-116
      test_rbac.py               # T-117 through T-121
      test_tenant_endpoints.py   # T-122 through T-128
      test_user_endpoints.py     # T-129 through T-137
      test_template_endpoints.py # T-138 through T-151
      test_master_data_endpoints.py # T-152 through T-160
      test_analytics_endpoints.py   # T-161 through T-168
      test_request_validation.py # T-169 through T-171
  integration/
    test_db_operations.py        # T-172 through T-176
    test_keycloak.py             # T-177 through T-178
    test_multi_tenant.py         # T-179 through T-180
    test_redis_cache.py          # T-181
    test_template_wizard.py      # T-182
    test_csv_import.py           # T-183 through T-184
    test_alembic.py              # T-185
    test_tenant_provisioning.py  # T-186
  e2e/
    test_auth_flow.py            # T-187 through T-191
    test_user_management.py      # T-192 through T-199
    test_template_wizard.py      # T-200 through T-209
    test_master_data.py          # T-210 through T-217
    test_analytics.py            # T-218 through T-221
    test_audit_log.py            # T-222 through T-228
    test_tenant_settings.py      # T-229 through T-233
    test_navigation.py           # T-234 through T-236
```

### Running Tests

```bash
# All unit tests
pytest tests/unit/ -v

# All integration tests (requires Docker services)
pytest tests/integration/ -v --timeout=60

# All E2E tests (requires full stack running)
pytest tests/e2e/ -v --timeout=120

# Full suite with coverage
pytest tests/ --cov=src --cov-fail-under=80 --cov-report=html

# Critical path tests only
pytest tests/ -m "critical" -v
```

### Pytest Markers

```python
# conftest.py
pytest.mark.unit       # Fast, no external deps
pytest.mark.integration # Requires DB, Keycloak, Redis
pytest.mark.e2e        # Requires full stack
pytest.mark.critical   # Critical path tests (auth, tenant isolation, wizard)
```

---

## 6. Test ID Summary

| Range | Layer / Category | Count |
|-------|-----------------|-------|
| T-001 to T-028 | Types (unit) | 28 |
| T-029 to T-038 | Config (unit) | 10 |
| T-039 to T-071 | Repo (unit) | 33 |
| T-072 to T-102 | Service (unit) | 31 |
| T-103 to T-171 | Runtime (unit) | 69 |
| T-172 to T-186 | Integration | 15 |
| T-187 to T-236 | E2E | 50 |
| **Total** | | **236** |
