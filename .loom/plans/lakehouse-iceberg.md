---
id: plan:lakehouse-iceberg
kind: plan
status: blocked
created_at: 2026-05-04T02:49:06Z
updated_at: 2026-05-04T03:05:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:lakehouse-iceberg
  constitution: constitution:main
  research:
    - research:lakehouse-iceberg-spike
external_refs: {}
---

# Summary

Sequence the lakehouse-iceberg initiative as a halt-gated spike
followed by one mart table. Phase 0 is a single research-spike
ticket. Phase 1 only happens if Phase 0 returns green. Phase 2
is wiki + retro.

# Sequence

## Phase 0 — Spike (halt gate)

Single ticket: `ticket:mka30wgd` (Phase 0 R2 Data Catalog ↔
MotherDuck spike).

- Provision R2 Data Catalog.
- Write trivial Iceberg table via PyIceberg (preferred for
  minimum surface area).
- Attach + read from MotherDuck.
- Document outcome in `research:lakehouse-iceberg-spike`.
- Decision point at end: green → Phase 1; red → halt.

**Halt gate is hard.** If Phase 0 returns red, this plan does
not silently route to Phase 1. The initiative goes back through
outer-loop framing (constitution / research / new initiative)
before any further implementation work.

## Phase 1 — One mart table (only if Phase 0 green)

Sub-steps (each its own ticket when Phase 1 opens; not pre-
populated to avoid stale tickets):

- Pick the mart table shape (likely
  `mart_job_postings_daily_snapshot`: append-only daily
  snapshot of `current_open_roles` rows).
- Build the writer (PyIceberg-driven Python script under
  `pipelines/`, or a dlt iceberg destination pipeline,
  decided after Phase 0 informs ergonomics).
- Wire the writer into the existing GitHub Actions cron
  (separate workflow or extra step, decided in the ticket).
- Land MotherDuck reader path: ATTACH catalog, expose the table
  via a view or directly to a Dive panel.
- Smoke test: row counts, catalog metadata visible, repeated
  runs append correctly.

## Phase 2 — Wiki + retro

- Promote learning into `wiki:extractor-shape` (new section) or
  a sibling page `wiki:lakehouse-iceberg`.
- Update memory pointers; mark
  `project_partition_r2_closed.md`'s "Iceberg deferred" note as
  superseded.
- Run retrospective. Close initiative.

# Halt-Gate Discipline

If `ticket:mka30wgd` (Phase 0 spike) returns:

- **green** → continue to Phase 1; open Phase 1 tickets.
- **partial** (e.g. PyIceberg writes work but MotherDuck attach
  fails; `iceberg_scan` direct read works) → halt, document in
  research, decide explicitly whether to proceed with a degraded
  reader path or re-scope.
- **red** → halt, document failure, mark initiative paused or
  cancelled, return control to outer loop. Do not auto-pivot to
  Lakekeeper / Polaris / Glue.

The halt is not optional. It is the contract with the user for
this initiative.

# Risks

- **Spike scope creep.** Tempting to pre-build the full mart
  during Phase 0. Resist; the trivial-table probe is the entire
  Phase 0 goal.
- **Stack churn during spike.** R2 Data Catalog is in beta;
  Iceberg writes in DuckDB are <6 months old. Pin versions in
  the spike notes.
- **Auth foot-guns.** R2 token scoping, MotherDuck secret
  surfaces, and PyIceberg's credential resolution can all
  conflict. Document each layer separately so a re-scope can
  reuse the diagnostics.

# Status Summary

Drafted alongside `initiative:lakehouse-iceberg`.

## 2026-05-04 — Phase 0 partial → plan blocked

Phase 0 ticket `ticket:mka30wgd` executed and parked
`complete_pending_acceptance`. Outcome was partial per the
halt-gate definition (PyIceberg writes work, local DuckDB
reads work, MotherDuck catalog-mediated `SELECT` SIGSEGVs).
Phase 1 not opened. Plan status → `blocked` until user
explicitly reroutes via initiative update. See
`research:lakehouse-iceberg-spike` Decision section for
re-scope options A-F.
