---
id: plan:lakehouse-iceberg
kind: plan
status: closed
created_at: 2026-05-04T02:49:06Z
updated_at: 2026-05-13T18:33:15Z
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

## Phase 1 — One mart table, shape A'

Reader path is degraded per Phase 0 follow-up: MotherDuck
catalog ATTACH `SELECT` SIGSEGVs on R2 Iceberg, but
`iceberg_scan(<metadata_location>)` works. Phase 1 carries the
materialization step explicitly: writer resolves the fresh
metadata pointer via PyIceberg, then `CREATE OR REPLACE TABLE`
in MotherDuck against `iceberg_scan(<ptr>)`. Dive panels read
the native MotherDuck table.

Mart table:

- Name: `mart.job_postings_daily_snapshot`
- Shape: all columns from `current_open_roles` plus
  `snapshot_date DATE`
- Append-only, unpartitioned (small scale; keeps DuckDB Iceberg
  write API simple)

Sub-steps. Each is its own ticket when ready; only the next one
is pre-opened to avoid stale work.

- **P1.1 (`ticket:9gbi98mx`, ready)** — bootstrap. Persistent
  MotherDuck secrets (`r2_pipelines_s3` already created in
  Phase 0; confirm + document; iceberg session secret pattern
  too). New `src/dream_job_radar/pipelines/_iceberg.py` catalog
  factory mirroring `_r2.py`. Smoke-create `mart` namespace.
  No mart table writes yet.
- **P1.2** — writer. New `pipelines/iceberg_mart.py` end-to-end:
  read `current_open_roles` snapshot, append into
  `mart.job_postings_daily_snapshot` (creating on first run),
  resolve fresh metadata pointer, refresh MotherDuck mart copy
  via `CREATE OR REPLACE TABLE`. Idempotent on same-day rerun
  (skip append if `snapshot_date = current_date` rows already
  present). Local-only execution.
- **P1.3** — cron wire. Add Iceberg mart step to
  `.github/workflows/cron.yml` after the existing radar
  pipelines. Secret env shape, `unsafe_enable_version_guessing`
  posture, error containment (mart failure must not break raw
  ingest).
- **P1.4** — Dive panel. One panel reading
  `mart.job_postings_daily_snapshot` (e.g. open-roles-per-day
  line chart). Verify Dive sees the table after a refresh
  cycle.
- **P1.5** — critique + wiki + retro. Promote the degraded-
  reader pattern into wiki (`extractor-shape` extension or new
  `wiki:lakehouse-iceberg` page), close initiative.

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

## 2026-05-04 — Re-scope to shape A' → plan active

User chose shape A' after follow-up diagnostic confirmed:
auth ruled out (persistent MotherDuck S3 secret didn't fix
SIGSEGV); degraded reader workflow (PyIceberg resolves
metadata pointer → MotherDuck `iceberg_scan` reads, including
freshly-appended rows; `CREATE OR REPLACE TABLE … AS SELECT
* FROM iceberg_scan(…)` materializes into native MotherDuck
table cleanly).

Phase 0 ticket → ready to close. Phase 1 substeps populated
above; first ticket `ticket:9gbi98mx` (P1.1 bootstrap) opened.
Plan status → `active`.

## 2026-05-13 - Closed as stale

Operator requested stale Loom work be closed out. This plan is no
longer active execution state. Closure is administrative and does
not claim the Iceberg roadmap, Phase 1 sequence, or remaining
follow-up work was accepted or still intended.
