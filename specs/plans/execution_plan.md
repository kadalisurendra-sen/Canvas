# Execution Plan: Helio Canvas Admin Panel

**Generated**: 2026-03-17
**Total Stories**: 25
**Parallel Groups**: 4

## Story Dependency Graph

```
US-001 (Scaffolding)
  └─> US-002 (Keycloak + JWT)
       └─> US-025 (Sidebar/Layout/Routing)
            ├─> US-003 (Login UI)
            ├─> US-004 (List Users)
            │    ├─> US-005 (Invite User)
            │    └─> US-006 (Edit/Deactivate User)
            ├─> US-007 (List Templates)
            │    └─> US-008 (Wizard Step 1)
            │         └─> US-009 (Wizard Step 2)
            │              └─> US-010 (Wizard Step 3)
            │                   └─> US-011 (Wizard Step 4)
            │                        └─> US-012 (Wizard Step 5)
            │                             └─> US-013 (Delete Template)
            ├─> US-014 (Tenant General)
            │    ├─> US-015 (Tenant Branding)
            │    └─> US-016 (Tenant Defaults)
            ├─> US-017 (Master Data Categories)
            │    └─> US-018 (CRUD Values)
            │         ├─> US-019 (Reorder Values)
            │         └─> US-020 (CSV Import)
            └─> US-021 (Dashboard Metrics)
                 ├─> US-022 (Dashboard Charts)
                 ├─> US-023 (Audit Log)
                 │    └─> US-024 (Export)
                 └─> US-024 (Export)
```

## Execution Phases

### Phase 1: Foundation (Sequential — must be first)
| Order | Story | Description | Est. Complexity |
|-------|-------|-------------|-----------------|
| 1 | US-001 | Project scaffolding, Docker Compose, platform DB | High |
| 2 | US-002 | Keycloak integration, JWT middleware, tenant resolution | High |
| 3 | US-025 | Sidebar navigation, header, routing, auth guards | Medium |
| 4 | US-003 | Login UI page | Low |

**Gate**: User can sign in via Keycloak and see the admin layout with sidebar navigation.

### Phase 2: Parallel Group A — User Management + Tenant Settings
*Can run in parallel after Phase 1*

| Stream | Story | Description | Est. Complexity |
|--------|-------|-------------|-----------------|
| A1 | US-004 | List users with search/filter/pagination | Medium |
| A1 | US-005 | Invite user modal + Keycloak integration | Medium |
| A1 | US-006 | Edit role, deactivate user | Low |
| A2 | US-014 | Tenant settings — General tab | Medium |
| A2 | US-015 | Tenant settings — Branding tab | Low |
| A2 | US-016 | Tenant settings — Defaults tab | Low |

**Gate**: Admin can manage users and configure tenant settings.

### Phase 3: Parallel Group B — Template Wizard + Master Data
*Can run in parallel after Phase 1*

| Stream | Story | Description | Est. Complexity |
|--------|-------|-------------|-----------------|
| B1 | US-007 | List templates | Medium |
| B1 | US-008 | Wizard Step 1 — General Info | Medium |
| B1 | US-009 | Wizard Step 2 — Stage Config | Medium |
| B1 | US-010 | Wizard Step 3 — Fields & Sections | High |
| B1 | US-011 | Wizard Step 4 — Scoring & Formulas | Medium |
| B1 | US-012 | Wizard Step 5 — Preview & Publish | Medium |
| B1 | US-013 | Delete template | Low |
| B2 | US-017 | Master data categories listing | Low |
| B2 | US-018 | CRUD values | Medium |
| B2 | US-019 | Reorder values (drag-and-drop) | Low |
| B2 | US-020 | CSV import | Medium |

**Gate**: Admin can create full templates and manage master data.

### Phase 4: Parallel Group C — Analytics & Audit
*Can run after Phase 1 (or after Phase 2/3 for realistic data)*

| Stream | Story | Description | Est. Complexity |
|--------|-------|-------------|-----------------|
| C1 | US-021 | Dashboard metric cards | Medium |
| C1 | US-022 | Dashboard charts | Medium |
| C2 | US-023 | Audit log with filters | Medium |
| C2 | US-024 | Export (analytics + audit) | Low |

**Gate**: Full admin panel feature-complete.

## Parallel Execution Strategy

```
Timeline:
─────────────────────────────────────────────────────────
Phase 1:  [US-001 → US-002 → US-025 → US-003]  (sequential)
─────────────────────────────────────────────────────────
Phase 2:  [Stream A1: US-004→005→006]  ║  [Stream A2: US-014→015→016]
Phase 3:  [Stream B1: US-007→...→013]  ║  [Stream B2: US-017→018→019→020]
Phase 4:  [Stream C1: US-021→022]      ║  [Stream C2: US-023→024]
─────────────────────────────────────────────────────────
```

Phases 2, 3, and 4 can run concurrently since they share no data dependencies (only the foundation from Phase 1).

Within each phase, the two streams (A1/A2, B1/B2, C1/C2) can run in parallel.

## Implementation Team Plan

Given 25 stories with 4 parallel groups, implementation will use **multiple implementer agents**:

| Agent | Streams | Stories |
|-------|---------|---------|
| Implementer 1 | Phase 1 (all) + Stream B1 | US-001, 002, 025, 003, 007-013 |
| Implementer 2 | Stream A1 + A2 | US-004-006, 014-016 |
| Implementer 3 | Stream B2 + C1 + C2 | US-017-024 |

## Quality Gates Per Story

After each story:
1. `python3 .claude/linters/lint_all.py` — layer deps + file size
2. `pytest tests/ --cov=src --cov-fail-under=80` — tests pass with coverage
3. Manual smoke test of the feature in browser

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Keycloak integration complexity | US-002 is high priority; if blocked, stub with mock JWT for other stories |
| Template wizard complexity (Step 3) | US-010 is the most complex story; allocate extra time, split if needed |
| Multi-tenant DB routing | Test early in US-001/002; use testcontainers for integration tests |
| Redis dependency | Optional for dev; fall back to in-memory cache if Redis unavailable |
