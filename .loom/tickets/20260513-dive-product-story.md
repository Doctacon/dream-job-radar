# Dive Product Story Refresh

ID: ticket:20260513-dive-product-story
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - changes user-facing Dive layout, query mix, and decision hierarchy.
Depends On: ticket:20260513-dive-snapshot-repair

## Summary

Refresh the Dream Job Radar Dive so it feels like an intentional compact radar rather than a crude KPI strip, ambiguous bar strip, and long table. The single closure claim is that the Dive presents a coherent inventory-first story with a separate recent/new lens and a useful company/source breakdown, without redundant visuals or unrelated pipeline changes.

## Related Records

- `plan:20260513-dive-radar-refresh` - parent strategy and visual/story direction.
- `ticket:20260513-dive-metric-contract` - metric semantics this design must preserve.
- `ticket:20260513-dive-snapshot-repair` - prerequisite snapshot section repair this design builds on.
- `.dive-preview/src/dive.tsx` - local component write boundary.
- Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` - target user-facing surface.

## Scope

In scope:

- Local Dive React layout and SQL query selection.
- Inventory KPIs, recent/new role lens, company/source coverage, and recent role detail as compact sections.
- Responsive desktop/mobile behavior inside the existing Dive runtime constraints.
- Progressive loading and error/empty states for each section changed.

Out of scope:

- Source extractor changes.
- `current_open_roles` view changes unless a query cannot be written against the existing view and the ticket returns to plan shaping.
- Iceberg mart writer/schema changes.
- Export/download controls unless separately requested.
- Adding a chart library solely for polish if native layout or existing allowed libraries are enough.

Stop and return to shaping if the desired story requires a new product decision, such as ranking roles by a subjective fit score or adding user-specific preferences.

## Acceptance

- ACC-001: The Dive's above-the-fold story is inventory-first and distinguishes recent/new roles as a separate lens.
  - Evidence: Source inspection and, when feasible, local preview screenshot or visual inspection notes.
  - Audit: Closure review should challenge whether the hierarchy matches the approved metric contract.

- ACC-002: The Dive avoids redundant chart/table content and keeps the page compact enough for the constrained Dive viewport.
  - Evidence: Source inspection names each section and why it exists; local preview/build evidence if available.
  - Audit: Review should challenge whether any visual repeats the same data without adding a distinct decision use.

- ACC-003: Changed queries are SQL-heavy, fully qualified, and handle numeric/date rendering safely.
  - Evidence: Source inspection plus read-only MotherDuck probes for any new aggregate query shapes.
  - Audit: Review should challenge BigInt/date rendering risk and live Dive runtime compatibility.

- ACC-004: Mobile behavior remains usable for KPI, trend, breakdown, and role detail sections.
  - Evidence: Local preview responsive inspection when feasible, or source-level class/layout inspection if preview is unavailable.
  - Audit: Separate audit should focus on layout breakage risk and information hierarchy.

## Current State

Closed. `.dive-preview/src/dive.tsx` now presents a compact inventory-first story: header and KPIs for current open-role inventory, a daily UTC inventory trend, company coverage with inventory and recent counts, source mix, and a separate recent roles table limited to last-7-day roles. The implementation stayed inside the local Dive React/SQL write boundary and did not change extractors, `current_open_roles`, the Iceberg mart writer, schema, or cron.

Changed queries are SQL-heavy and fully qualified through `TABLE` and `MART_TABLE`; dates are formatted in SQL, and numeric render paths use `N(...)`. Progressive loading and empty states are per section. Desktop/mobile behavior is source-inspected through responsive Tailwind classes: KPI grid is 2 columns on mobile and 4 on larger screens, coverage stacks before using `lg:grid-cols-5`, and role location is hidden in the table but repeated under the title on mobile.

Evidence: read-only MotherDuck probes validated the aggregate shapes for inventory, recent roles, snapshot trend, company coverage, source coverage, and role detail; `.dive-preview` `npm exec vite build` passed with only Vite's large-chunk warning. Audit `audit:20260513-dive-radar-refresh-closure` found the local Dive supports the intended contract; `FIND-001` record follow-through is resolved here.

## Journal

- 2026-05-13: Created ticket with Status `open` as the product/design slice of the Dive refresh plan.
- 2026-05-13: Implemented the inventory-first compact Dive story in `.dive-preview/src/dive.tsx`, validated query shapes and local build, and closed after audit follow-through.
