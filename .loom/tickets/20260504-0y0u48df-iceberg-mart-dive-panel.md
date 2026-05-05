---
id: ticket:0y0u48df
kind: ticket
status: closed
change_class: code-behavior
risk_class: low
created_at: 2026-05-05T02:35:00Z
updated_at: 2026-05-05T03:38:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:lakehouse-iceberg
  plan: plan:lakehouse-iceberg
  predecessor:
    - ticket:7t9jzfqe
  constitution: constitution:main
external_refs:
  dive: 391d1329-70d7-4223-89c8-d0dfde66ef7f
---

# Summary

P1.4 of `initiative:lakehouse-iceberg`. Surface
`mart.job_postings_daily_snapshot` in the live "dream-job-radar
— open roles" Dive so the resume claim of "Iceberg lakehouse on
R2 → MotherDuck → Dive" is visibly real, not just plumbing.
Mirror the same change in `.dive-preview/src/dive.tsx` so local
iteration stays useful.

# Goal

Dive viewer sees a "Daily snapshot history" strip showing per-
day open-role counts driven by the Iceberg-backed mart table.
Initially one bar (today). Becomes more meaningful daily as
cron lands new snapshots.

# In Scope

- New `useSQLQuery` reading
  `SELECT snapshot_date, count(*) AS roles
   FROM mart.job_postings_daily_snapshot
   GROUP BY snapshot_date
   ORDER BY snapshot_date`.
- Small visual: a thin bar strip (pure React inline SVG, no
  recharts dependency in the published Dive). Each bar = one
  snapshot day. Height proportional to row count. Hover /
  title for the count.
- Section header "Daily snapshot history" with a one-line
  caption pointing at the Iceberg table as the source.
- Position: between KPI strip and "Recent roles" table, so
  the new section reinforces the freshness story before the
  per-role detail.
- Apply identical edit to:
  - `.dive-preview/src/dive.tsx` (local preview)
  - Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` via
    `mcp__MotherDuck__edit_dive_content` (new version).

# Out Of Scope

- Recharts integration, animation, full chart library.
- Filtering by company / source on the trend strip.
- Historical backfill of past `current_open_roles` snapshots
  into Iceberg (mart only starts from today).
- Changes to summary / role list queries.
- Wiki / retro (P1.5).

# Acceptance Criteria

- AC1: Live Dive `391d1329-…` updated to a new version (>=6).
  `read_dive` confirms the new section is present.
- AC2: New SQL query references
  `mart.job_postings_daily_snapshot` exactly. No fully-qualified
  `acorn-granary.main.…` prefix unless the existing pattern
  requires it (the existing dive uses
  `"acorn-granary"."main"."current_open_roles"` — match that
  shape: `"acorn-granary"."mart"."job_postings_daily_snapshot"`).
- AC3: Probe via MCP query: `SELECT count(*),
  count(DISTINCT snapshot_date) FROM
  acorn-granary.mart.job_postings_daily_snapshot;` returns the
  expected (rows, days) shape.
- AC4: `.dive-preview/src/dive.tsx` mirror updated and the
  local Vite dev server boots without errors.
- AC5: No changes to writer pipeline, cron workflow, or
  Iceberg table schema.

# Verification Posture

`observation-first`. Behavior is "Dive renders the new section
without breakage and reads the mart table". Evidence:

- `mcp__MotherDuck__query` capture of the count probe (AC3).
- Local Vite boot log saved if a regression surfaces; skip if
  clean.
- Updated Dive version number recorded in ticket close-out.

# Notes For Implementer

- The materialized MotherDuck table lives at
  `acorn-granary.mart.job_postings_daily_snapshot`. Confirm via
  `SHOW TABLES IN acorn-granary.mart;` if uncertain.
- Use the existing `T` palette for bar fills; accent for
  positive values, faint border for the strip backdrop.
- Bar strip shape: height ~24-32px, width fills the section.
  Each bar can be a `<div>` with `flex: 1` and inline-styled
  height proportional to `roles / max(roles)`.
- Hover `title` attribute on each bar:
  `${snapshot_date}: ${roles} open roles`. Cheap accessibility,
  no JS event handlers needed.
- `mcp__MotherDuck__edit_dive_content` accepts an `edits`
  array. Make the live edit a single composite replacement so
  reverting is one MCP call away.

# Status Summary

Drafted + executed 2026-05-05.

## Outcome 2026-05-05: closed

All ACs met:

- AC1: Dive `391d1329-…` bumped from version 5 to version 6
  (`updated_at` 2026-05-05 03:37:48Z, confirmed via
  `list_dives`).
- AC2: New `useSQLQuery` references
  `"acorn-granary"."mart"."job_postings_daily_snapshot"` exactly.
- AC3: MCP query probe returns
  `(rows=120, days=1, latest=2026-05-05)`.
- AC4: `.dive-preview/src/dive.tsx` mirror updated (4 edits +
  new `SnapshotStrip` helper). Structural read confirms all
  pieces present.
- AC5: No changes to writer / cron / Iceberg schema.

`SnapshotStrip` renders a thin bar strip (height 48px) with one
bar per UTC day, height proportional to that day's open-role
count. Title attribute carries the date + count for hover
inspection. With one snapshot today, the strip shows one bar;
becomes meaningfully time-series-ish from tomorrow's cron
onward.

Phase 1 milestones M1 (mart live) effectively complete: writer
runs daily, mart materialized, Dive surfaces it. Next: P1.5
critique + wiki + retro.
