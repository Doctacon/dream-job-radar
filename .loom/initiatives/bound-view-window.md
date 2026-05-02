---
id: initiative:bound-view-window
kind: initiative
status: closed
created_at: 2026-05-02T16:26:48Z
updated_at: 2026-05-02T16:32:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  constitution: constitution:main
  predecessor:
    - initiative:partition-r2-layout
external_refs: {}
---

# Summary

Make the `current_open_roles` view scan only recent date
partitions before deduping. Today the view reads ALL parquet
across all years/months/days and runs a window function over the
full set. After a year of daily cron, that's ~365 × 11 slugs ×
N_roles rows in the input set — real query cost.

# Objective

Bound the view's parquet read at the partition layer (`year`,
`month`, `day` from hive paths) so scan size stays constant
regardless of how many years of history accumulate in R2. Window
dedup operates on a bounded recent window, not the full history.

# Why Now

`initiative:partition-r2-layout` shipped hive partitioning. The
read-time win is unrealized because the view doesn't filter on
partition columns. User asked specifically for the view-side
bound after a Dive-perf walking conversation. Now is the
cheapest time — before historical data accumulates and the cost
becomes operationally annoying.

Important context from the same conversation:
incremental dlt ingest was floated as a path to faster Dive but
**was correctly identified as a separate optimization**. The
Dive perf win comes from the read layer, not the write layer.
Incremental ingest is deferred.

# In Scope

- Edit `motherduck/views.sql` so the CTE filters parquet by a
  date predicate built from the hive partition columns BEFORE
  the dedupe window function. Lookback window: 30 days.
- Re-materialize the view via `scripts/apply_views.py`.
- Confirm `current_open_roles` row counts unchanged in normal
  operation (the 30-day window comfortably covers active cron
  state).
- Confirm Dive renders identically (Dive's existing
  posted_at-based 7-day filter narrows further on top of the
  view's 30-day bound).

# Out Of Scope

- Incremental dlt ingest. Deferred per user direction.
  Re-evaluate when (a) ~50+ companies, (b) upstream rate
  limits, or (c) resume goal demands it.
- Materialized table in MotherDuck (CTAS refreshed by cron).
  Would beat any view-time filter at scale but requires another
  pipeline step. Defer until 30-day-bounded view is itself slow.
- Dive-side filter changes. The Dive's existing 7-day
  `coalesce(posted_at, first_seen_at)` filter stays as-is.

# Success Metrics

- View row counts unchanged from pre-change snapshot in normal
  operation.
- Partition-pruning probe against the view's underlying glob +
  date predicate confirms DuckDB skips partitions outside the
  30-day window.
- Dive render unchanged.

# Milestones

## M1 — Bounded view shipped

`motherduck/views.sql` filters partitions in the CTE; view
re-materialized; counts unchanged; Dive verified.

## M2 — Wiki + retrospective

`wiki:extractor-shape` "R2 layout: hive-partitioned" section
extended with a "How the view bounds scans" subsection.
Initiative closes.

# Dependencies

Hard prerequisites:

- `initiative:partition-r2-layout` (closed) — provides the hive
  layout this change exploits.
- `wiki:extractor-shape` "R2 layout: hive-partitioned" section.

Soft references:

- `decision:0001-storage-backend-r2` — unchanged.

# Risks

- **Roles last observed > 30 days ago drop from the view.** This
  is by design: the view's purpose is "currently open roles",
  and a role we haven't fetched in a month is stale anyway. If
  cron ever silently stops for a slug for > 30 days, the view
  forgets that slug entirely until cron resumes. Mitigation:
  cron's existing health-check fails on per-slug staleness
  > 36h, well before the view bound bites.
- **`make_date(year, month, day)` type cast.** Partition columns
  arrive as INT (year) and VARCHAR (month/day). Build the date
  carefully: `make_date(year, CAST(month AS INT), CAST(day AS INT))`.
- **Partition-pruning is opportunistic.** DuckDB's planner may
  or may not push the predicate through depending on whether the
  date arithmetic stays partition-comparable. Verify via EXPLAIN
  if perf doesn't materialize.

# Linked Work

Plan: `plan:bound-view-window`.

# Status Summary

Drafted 2026-05-02. Single-ticket plan, single-edit ticket.
Should land in one short pass.

## Close-out 2026-05-02

Status → `closed`. Outcome by milestone:

- **M1 — Bounded view shipped:** done. `ticket:oy4kaq5n`
  closed. View CTE filters partitions to last 30 days; row
  counts unchanged pre/post; `EXPLAIN` confirms partition
  pushdown. ~4× scan reduction today (465 vs 2094 raw rows
  feeding the dedupe window); bound stays constant as history
  grows.
- **M2 — Wiki + retrospective:** done. `wiki:extractor-shape`
  "How the view bounds scans" subsection captures the predicate
  shape, type-awareness, the 30-day-window rationale, and a
  fallback if the planner ever regresses partition pushdown for
  `make_date`.

State at close-out:

- View scans ~465 rows today; would have grown unbounded
  without this change.
- Dive renders identical (Dive's 7-day filter on
  `coalesce(posted_at, first_seen_at)` narrows further on top
  of the view's 30-day bound).
- No code touches outside `motherduck/views.sql`.
- Reversible by re-running `apply_views.py` against any prior
  DDL.

Carryover (still deferred):

- Incremental dlt ingest. Re-evaluate when ~50+ companies,
  upstream rate-limits, or resume goal demands it.
- Materialized table in MotherDuck (CTAS refreshed by cron)
  if/when the bounded-view scan itself becomes slow at scale.
