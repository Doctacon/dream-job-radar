---
id: plan:bound-view-window
kind: plan
status: closed
created_at: 2026-05-02T16:26:48Z
updated_at: 2026-05-02T16:32:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:bound-view-window
  constitution: constitution:main
---

# Purpose

Sequence the execution of `initiative:bound-view-window`: edit
`motherduck/views.sql` to filter parquet partitions inside the
CTE, re-materialize, verify.

# Strategy

One ticket, one edit, observation-first verification. Same shape
as `ticket:f4p9p2g3` (the hive-layout ticket) without the
backfill complication.

# Workstreams

## View

Add a date predicate inside the CTE:

```sql
AND make_date(year, CAST(month AS INT), CAST(day AS INT))
    >= current_date - INTERVAL 30 DAY
```

Partition columns come from `hive_partitioning=true` (year is
INT, month/day are zero-padded VARCHAR). The cast keeps DuckDB's
planner happy and lets the predicate prune partitions outside
the window.

## Verification

- Capture pre-change view row counts.
- Apply view DDL via `scripts/apply_views.py`.
- Capture post-change view row counts → expect identical.
- Dispatch the cron workflow once (or just re-render the Dive in
  the browser) → confirm no regression.
- Optional: `EXPLAIN` the view query to confirm partition
  filtering shows up in the plan.

## Documentation

`wiki:extractor-shape` gets a small subsection during the retro:
"How the view bounds scans".

# Milestones

## PM1 — Bounded view shipped

One ticket. Single edit + verify.

## PM2 — Retrospective + wiki

`wiki:extractor-shape` updated. Initiative closes.

# Sequencing

PM1 first. PM2 follows immediately after verification.

# Execution Waves

## Wave 1 — View edit + verify

Sequential, single ticket.

- `ticket:oy4kaq5n` — Edit `motherduck/views.sql` CTE to filter
  on partition columns, re-materialize, verify counts. Status:
  `closed` (2026-05-02). Pre/post row counts identical;
  `EXPLAIN` confirms partition pushdown (~465 rows scanned vs
  ~2094 pre-change, ~4× scan reduction).

# Risks

(Mirrored from initiative.) Net low; the change is a single
WHERE clause; verification is row-count parity.

# Evidence Strategy

Observation-first.

- Pre-change view row counts (per `(source_kind, ats_slug)`).
- Post-change view row counts: identical.
- Optional `EXPLAIN` showing partition pruning in the plan.

Critique disposition: optional. Single SQL clause; no new code
paths; immediately reversible (revert the `apply_views.py` run
with the prior DDL).

# Plan Readiness Review

Spec / acceptance coverage:

- No spec exists; ticket-local acceptance.

Placeholder scan:

- Ticket ID `oy4kaq5n` already chosen.

Ticket-sized slices:

- One ticket. One file edit. One re-materialize.

Likely write scopes:

- `motherduck/views.sql`
- `.loom/wiki/extractor-shape.md` (during retro)

Likely verification posture: observation-first.

Stop / loopback conditions:

- If post-change row counts differ from pre-change in normal
  operation, back out the change and investigate.
- If `make_date` cast errors out (unexpected partition column
  types), escalate to research re-probe.

# Exit Criteria

- View CTE filters partitions before dedupe.
- Pre/post row counts identical.
- Dive renders unchanged.
- `wiki:extractor-shape` documents the view bound.
- Initiative milestones M1–M2 closed.
