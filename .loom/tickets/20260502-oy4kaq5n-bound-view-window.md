---
id: ticket:oy4kaq5n
kind: ticket
status: closed
change_class: code-behavior
risk_class: low
created_at: 2026-05-02T16:26:48Z
updated_at: 2026-05-02T16:32:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:bound-view-window
  plan: plan:bound-view-window
  constitution: constitution:main
  wiki: wiki:extractor-shape
  predecessor: ticket:f4p9p2g3
external_refs: {}
depends_on: []
---

# Summary

Wave 1 / PM1 of `plan:bound-view-window`: filter parquet
partitions in the `current_open_roles` CTE so the view scans only
the last 30 days of data before deduping. One file edit;
observation-first verification.

# Context

`initiative:partition-r2-layout` shipped hive partitioning, but
the view doesn't currently exploit it for read pruning. Today's
view does:

```sql
WITH raw AS (
  SELECT ...
  FROM read_parquet('r2://${R2_BUCKET}/raw/*/*/**/*.parquet',
                    filename = true,
                    union_by_name = true,
                    hive_partitioning = true)
  WHERE filename NOT LIKE '%/_dlt_%'
    AND source_kind IS NOT NULL
    AND ats_slug IS NOT NULL
    AND role_id IS NOT NULL
)
SELECT ...
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY source_kind, ats_slug, role_id
  ORDER BY fetched_at DESC
) = 1
FROM raw
```

After a year of daily cron, the input set to the window function
is ~365 × 11 slugs × N_roles rows. Bounded scan to 30 days keeps
cost flat regardless of historical depth.

# Why Now

Cheapest before historical data accumulates. Single SQL clause.

# Scope

Edit `motherduck/views.sql`. Inside the `raw` CTE add:

```sql
AND make_date(year, CAST(month AS INT), CAST(day AS INT))
    >= current_date - INTERVAL 30 DAY
```

`year` is INT, `month` and `day` are zero-padded VARCHAR (per
`research:r2-hive-partitioning`).

Re-materialize via `scripts/apply_views.py`. Confirm row counts
unchanged from pre-change snapshot.

# Non-goals

- No incremental dlt ingest. Deferred per
  `initiative:bound-view-window` scope.
- No view shape changes (column projection unchanged).
- No Dive changes. The Dive's existing 7-day filter on
  `coalesce(posted_at, first_seen_at)` narrows further on top.
- No tighter window than 30 days at the view layer. Conservative
  buffer against cron stalls; Dive applies the strict 7-day
  presentation filter on top.

# Acceptance Criteria

1. Edit applied to `motherduck/views.sql`. View
   re-materialized successfully via `apply_views.py`.
2. Per-`(source_kind, ats_slug)` row counts in
   `current_open_roles` unchanged from pre-change snapshot.
3. Dive renders unchanged (open the Dive URL; KPI numbers and
   role list match pre-change).
4. Optional: `EXPLAIN SELECT * FROM current_open_roles LIMIT 1`
   shows partition filtering in the plan (look for
   `Filters: ((make_date(...))) >= ...` near the parquet scan).
5. No cron failures on the next scheduled or manual workflow
   run.

# Coverage

Ticket-local. `wiki:extractor-shape` will gain a "How the view
bounds scans" subsection during PM2 retro.

# Claim Matrix

None.

# Execution Notes

- The 30-day window is generous on purpose. Cron's
  health-check already fails fast on per-slug staleness > 36h,
  so 30 days is well past any realistic pipeline outage. If
  cron stalls for a slug > 30 days the view forgets that slug
  until cron resumes — acceptable trade-off.
- Partition-pruning effectiveness depends on DuckDB's planner.
  The `make_date(year, ...)` cast must remain partition-
  comparable. If `EXPLAIN` shows full scan despite the
  predicate, fall back to a simpler shape (e.g. compose a date
  string and lexicographic compare against a cutoff string).
  Today's research-probe evidence suggests the planner handles
  it; verify post-change.
- Today's Dive filter is `coalesce(posted_at, first_seen_at)
  >= current_date - INTERVAL 6 DAY`. The view's 30-day bound is
  a strict superset; Dive output unchanged.

# Blockers

None.

# Next Move / Next Route

Local edit, no Ralph packet. Single SQL clause + verify.

# Ralph Readiness

N/A — local edit.

Write boundary if it ever needs Ralph:

- `motherduck/views.sql`

Verification posture: `observation-first`.

# Evidence

Expected on completion:

- pre-change `(source_kind, ats_slug, count(*))` snapshot
- post-change snapshot — identical
- view re-materialize confirmation
- (optional) EXPLAIN excerpt showing pruning

Captured 2026-05-02T16:32Z:

Pre-change snapshot:
```
ashby/Mapbox=61, ashby/pano-ai=4,
greenhouse/blastpoint=2, greenhouse/onxmaps=8,
greenhouse/overstory=7, greenhouse/planetlabs=37,
page/felt=1
```

Edit applied: added the partition-bound clause to the CTE:
```sql
AND make_date(year, CAST(month AS INTEGER), CAST(day AS INTEGER))
    >= current_date - INTERVAL 30 DAY
```

`scripts/apply_views.py` re-materialized the view.

Post-change snapshot — IDENTICAL:
```
ashby/Mapbox=61, ashby/pano-ai=4,
greenhouse/blastpoint=2, greenhouse/onxmaps=8,
greenhouse/overstory=7, greenhouse/planetlabs=37,
page/felt=1
```

`EXPLAIN SELECT count(*) FROM current_open_roles` shows the
READ_PARQUET node with `~465 rows` feeding the WINDOW dedupe
(and `~93` rows surviving the dedupe filter). Pre-change the
same probe scanned 2094 raw rows. **~4× scan reduction today**;
the gap widens linearly as the historical R2 zone grows.

Dive renders unchanged (verified by reload — KPI numbers and
role list match).

# Critique Disposition

Risk class: low

Critique policy: optional

Policy rationale: single SQL clause; no new code paths;
reversible by re-running `apply_views.py` against the prior DDL.

Findings: None — no critique scheduled.

Disposition status: not_required

Deferral / not-required rationale: low risk, ticket-local
acceptance, immediately reversible.

# Wiki Disposition

`wiki:extractor-shape` "R2 layout: hive-partitioned" section
gains a "How the view bounds scans" subsection during PM2 retro.

# Acceptance Decision

Accepted by: Connor
Accepted at: 2026-05-02T16:32:00Z
Basis: AC1–AC4 satisfied with observation-first evidence (see
Evidence section). Pre/post row counts identical; EXPLAIN
confirms partition pruning; Dive unchanged. AC5 (cron green on
new view) deferred to next scheduled firing — view is reversible
via `apply_views.py` if anything regresses.
Residual risks:
- 30-day window will silently drop slugs whose cron has stalled
  > 30 days. Cron's existing 36h health-check fires well before
  this; mitigation in place.
- DuckDB planner could regress the partition predicate in a
  future version. Mitigation: ticket Execution Notes describe a
  fallback (lexicographic string comparison) if EXPLAIN ever
  shows full scan despite the predicate.

# Dependencies

Hard prerequisites:

- `initiative:partition-r2-layout` (closed) — provides hive
  partitions this change exploits.
- `ticket:f4p9p2g3` (closed) — established the partition layout.

Soft references:

- `wiki:extractor-shape` — canonical pattern.
- `research:r2-hive-partitioning` — type-awareness for partition
  columns.

# Journal

- 2026-05-02 — ticket created from `plan:bound-view-window`.
  Risk classified `low`; critique optional. Single-edit local
  change. Next route: inline implementation.
- 2026-05-02 — Edit applied + view re-materialized. Row counts
  identical pre/post. EXPLAIN confirms READ_PARQUET node sees
  ~465 rows (down from ~2094). ~4× scan reduction today;
  bound stays constant as history grows. Status → `closed`.
