# Stitch UI Reference — Helio Canvas Admin Panel

**CRITICAL**: All UI implementation MUST match the Stitch designs exactly. Use the HTML source files below as the ground truth for layout, styling, component structure, and visual design.

## Screen Index

| # | Screen | Title | HTML Source |
|---|--------|-------|-------------|
| 1 | Sign In | Helio Canvas Sign In Page | `sign_in.html` |
| 2 | User Management | Helio Canvas Admin User Management | `user_management.html` |
| 3 | Master Data - Risk Categories | Helio Canvas Master Data Management | `master_data.html` |
| 4 | Template Management | Helio Canvas Admin Template Management | `template_management.html` |
| 5 | Analytics Dashboard | Helio Canvas Admin Analytics Dashboard | `analytics_dashboard.html` |
| 6 | Analytics - Extended | Helio Canvas Admin Analytics Dashboard (full) | `analytics_dashboard_full.html` |
| 7 | Audit Log | Analytics & Audit Logs | `audit_log.html` |
| 8 | Tenant Settings - General | Helio Canvas Admin Tenant Settings | `tenant_general.html` |
| 9 | Tenant Settings - Branding | Helio Canvas Admin Tenant Settings | `tenant_branding.html` |
| 10 | Tenant Settings - Advanced | Helio Canvas Admin Tenant Settings | `tenant_advanced.html` |
| 11 | Wizard Step 1 | Admin Template Creation Wizard - Step 1 | `wizard_step1.html` |
| 12 | Wizard Step 2 | Admin Template Wizard - Stage Configuration | `wizard_step2.html` |
| 13 | Wizard Step 3 | Admin Template Wizard - Field Editor | `wizard_step3.html` |
| 14 | Wizard Step 4 | Admin Template Wizard - Scoring & Formulas | `wizard_step4.html` |
| 15 | Wizard Step 5 | Admin Template Wizard - Preview & Publish | `wizard_step5.html` |
| 16 | Template List (alt) | Helio Canvas Admin Template Management | `template_list_alt.html` |
| 17 | Master Data - alt views | Various master data screens | `master_data_*.html` |

## Design Tokens (extracted from Stitch HTML)

### Colors
- Sidebar background: `#1E2345` (dark navy)
- Sidebar text: `#A0AEC0` (muted), `#FFFFFF` (active)
- Primary accent: `#5F2CFF` (purple)
- Secondary accent: `#02F576` (neon green)
- Content background: `#F7F8FC`
- Card background: `#FFFFFF`
- Text primary: `#1A202C`
- Text secondary: `#718096`

### Typography
- Font: Montserrat (Google Fonts)
- Headings: 600-700 weight
- Body: 14px, 400 weight

### Layout
- Sidebar width: 240px (collapsed: 64px)
- Content max-width: fluid
- Card border-radius: 12px (rounded-xl)
- Input border-radius: 8px (rounded-lg)

### Icons
- Material Symbols Outlined (Google Fonts)
- Used throughout: dashboard_customize, group, settings, analytics, database, layers, etc.

## Implementation Notes

- All screens use Tailwind CSS utility classes
- Google Material Symbols for all icons (not Material Icons legacy)
- Login page has gradient left panel with abstract SVG curves
- Sidebar uses fixed positioning with scrollable content area
- Tables use alternating row colors with hover effects
- Wizard uses step indicator with checkmarks for completed steps
- Drag-and-drop uses visual grab handles (drag_indicator icon)
