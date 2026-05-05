---
id: ticket:q67za0wk
kind: ticket
status: closed
change_class: code-behavior
risk_class: medium
created_at: 2026-05-04T03:40:00Z
updated_at: 2026-05-04T04:00:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:lakehouse-iceberg
  plan: plan:lakehouse-iceberg
  research:
    - research:lakehouse-iceberg-spike
  predecessor:
    - ticket:9gbi98mx
  constitution: constitution:main
external_refs: {}
---

# Summary

P1.2 of `initiative:lakehouse-iceberg`. Build the
`mart.job_postings_daily_snapshot` writer end-to-end as a
local-only entrypoint: read today's `current_open_roles`
snapshot from MotherDuck, append to the Iceberg table on R2
Data Catalog, refresh the MotherDuck materialized copy via
`CREATE OR REPLACE TABLE … AS SELECT * FROM iceberg_scan(…)`.
Idempotent on same-day rerun.

# Goal

After running `uv run python -m
dream_job_radar.pipelines.iceberg_mart` (or equivalent
entrypoint), Dive can read `mart.job_postings_daily_snapshot`
as a native MotherDuck table and see today's snapshot. Re-runs
on the same day do not double-write.

# In Scope

- `src/dream_job_radar/pipelines/iceberg_mart.py` containing:
  1. Catalog handle via `_iceberg.iceberg_catalog()`.
  2. MotherDuck connection.
  3. Read `current_open_roles` snapshot with `snapshot_date =
     current_date` injected as a column. Hardcode the column
     list (don't `SELECT *`) so view drift fails closed
     instead of silently extending the Iceberg schema.
  4. Ensure namespace `mart` exists (cheap idempotent check).
  5. Try `catalog.load_table('mart.job_postings_daily_snapshot')`;
     on `NoSuchTableError`, `create_table()` from the arrow
     schema.
  6. Idempotency probe: count rows in the live Iceberg table
     `WHERE snapshot_date = current_date` via
     `iceberg_scan(metadata_location)`. If > 0, skip append.
  7. Otherwise `tbl.append(arrow)` and `tbl.refresh()`.
  8. Always refresh the materialization:
     `CREATE OR REPLACE TABLE mart.job_postings_daily_snapshot
     AS SELECT * FROM iceberg_scan('<latest_metadata_location>')`.
  9. `SET unsafe_enable_version_guessing = true;` per session.
- An entrypoint shim or a `__main__` block so the script can be
  run with `uv run python -m dream_job_radar.pipelines.iceberg_mart`.
- Two end-to-end runs verified: first run creates table +
  appends; second run on same day skips append, still refreshes
  materialization.
- Manual verification from a separate MotherDuck session:
  `SELECT count(*) FROM mart.job_postings_daily_snapshot`
  matches expected row count, `SELECT DISTINCT snapshot_date`
  shows today.

# Out Of Scope

- Cron / GitHub Actions wire-up (P1.3).
- Dive panel (P1.4).
- Wiki / retro (P1.5).
- Schema evolution. View shape change post-deploy must fail
  closed, not auto-extend.
- UPDATE / DELETE / MERGE flows on the Iceberg table.
- Cleanup of Phase 0 spike artifacts (`spike` namespace,
  `spike.trivial`).
- Touching `pipelines/_r2.py`, `motherduck/views.sql`,
  `_iceberg.py`, `bootstrap_iceberg.sql`, or radar source
  pipelines.

# Acceptance Criteria

- AC1: `pipelines/iceberg_mart.py` exists, runs to completion
  via `uv run python -m dream_job_radar.pipelines.iceberg_mart`.
  No tracebacks on first run (fresh table) or second run
  (idempotent skip).
- AC2: After first run, R2 Data Catalog contains
  `mart.job_postings_daily_snapshot` with N rows where N =
  `SELECT count(*) FROM current_open_roles` at run time, all
  with `snapshot_date = current_date`.
- AC3: After same-day second run, Iceberg table row count
  unchanged. Materialization still refreshed (proves the
  refresh path runs every invocation).
- AC4: From a fresh MotherDuck connection,
  `SELECT count(*), count(DISTINCT snapshot_date) FROM
  mart.job_postings_daily_snapshot;` returns `(N, 1)` where N
  matches AC2.
- AC5: Hardcoded column list in writer matches view; if a future
  view change adds a column, the writer fails noisily instead
  of silently extending Iceberg schema.
- AC6: Stdout log captures: rows-read, append-or-skip decision,
  Iceberg snapshot id post-write, materialization confirmed.
- AC7: No changes to forbidden files (see Out Of Scope).

# Verification Posture

`observation-first`. Behavior is "it ran and the data flowed
correctly". Evidence:

- Save stdout of first + second run under
  `.loom/evidence/lakehouse-iceberg-spike/p1_2_*.log` (gitignored
  per repo policy; the scripts and the log layout are
  committed).
- One ad-hoc MotherDuck SQL probe captured to log too:
  `SELECT count(*), count(DISTINCT snapshot_date), max(snapshot_date)`.

# Notes For Implementer

- Iceberg create_table needs a schema. Easiest: build the arrow
  table first, pass `schema=arrow.schema`. Idempotent path:
  `try load_table; except NoSuchTableError: create_table`.
- `tbl.refresh()` after append ensures `tbl.metadata_location`
  points at the new snapshot before composing the
  materialization SQL.
- MotherDuck refresh DDL: `CREATE OR REPLACE TABLE
  mart.job_postings_daily_snapshot AS SELECT * FROM
  iceberg_scan('<location>')`. The materialization lives in
  whichever MotherDuck DB the session is attached to (default:
  the user's primary). Use a fully-qualified name
  (`<dbname>.mart.<table>`) only if defaulting causes
  confusion.
- Hardcode the SELECT projection. Suggested column order
  (matches the view body):
  `company, source_kind, ats_slug, role_id, title, url,
  location, posted_at, fetched_at, first_seen_at,
  last_seen_at, current_date AS snapshot_date`.
- The MotherDuck mart database/schema must exist. If it does
  not, create it with `CREATE SCHEMA IF NOT EXISTS mart;` once
  inside the entrypoint.
- Entry shape mirrors `radar.py` if it's a runnable module —
  reuse `if __name__ == "__main__":` pattern.
- DO NOT cast types defensively here — the view already does
  the heavy casts (e.g. `posted_at` to TIMESTAMP WITH TIME
  ZONE). PyArrow will inherit those types from
  `con.execute(...).arrow()`.
- pyiceberg's `tbl.append(arrow)` requires the arrow schema to
  match the iceberg schema. Type widening (e.g. NULL columns
  vs typed) can mismatch. If the first run succeeds and the
  second run fails on append, that's a schema-bind problem to
  diagnose, not a graceful migration.

# Status Summary

Drafted 2026-05-04 immediately after `ticket:9gbi98mx` (P1.1
bootstrap) closed. Executed same session.

## Outcome 2026-05-04: closed

All ACs met:

- AC1: `pipelines/iceberg_mart.py` runs to completion via
  `uv run python -m dream_job_radar.pipelines.iceberg_mart`.
- AC2: First run created table + appended 120 rows
  (snapshot_id=4681652724995565945).
- AC3: Second-same-day run loaded existing table, skipped
  append, refreshed materialization. Idempotency confirmed.
- AC4: Fresh MotherDuck session reports `(120, 1,
  date(2026,05,05))` for `count(*), count(DISTINCT
  snapshot_date), max(snapshot_date)`. Sample rows surface
  cleanly. (Date 05-05 not 05-04 because session is UTC-pinned;
  see notes below.)
- AC5: Hardcoded SELECT projection in `iceberg_mart.py` matches
  current_open_roles. View drift fails closed.
- AC6: Stdout logs (`p1_2_run1.log`, `p1_2_run2.log`,
  `p1_2_md_verify.log`) capture rows-read, append-or-skip,
  snapshot_id, materialization confirmation, and verify probe.
- AC7: No changes to forbidden files. Verified via
  `git status --short`.

## Implementation gotchas

1. DuckDB `.arrow()` returns a streaming `RecordBatchReader`;
   need `.to_arrow_table()` for a materialized `pa.Table`.
2. PyIceberg only accepts arrow `timestamp[us, tz=UTC]` (or
   naive). DuckDB session TZ defaults to local
   (`America/Phoenix`); arrow conversion preserves it. Fix:
   `SET TimeZone = 'UTC';` on the connection before fetching.
3. R2 Data Catalog returns 404 with body
   `"Table not found or action can_get_metadata forbidden for
   Anonymous"` for non-existent tables. PyIceberg maps this to
   `NoSuchTableError`; create_table flow runs as designed. Not
   an auth problem.
4. UTC pinning means `current_date` is UTC-relative, so the
   first run on 2026-05-04 evening Phoenix time produced rows
   tagged `snapshot_date=2026-05-05`. This is the intended
   behavior for a globally-consistent daily snapshot.

Next: P1.3 (cron wire-up). Will be opened as a fresh ticket.
