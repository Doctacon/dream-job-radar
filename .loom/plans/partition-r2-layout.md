---
id: plan:partition-r2-layout
kind: plan
status: active
created_at: 2026-05-02T15:31:33Z
updated_at: 2026-05-02T15:31:33Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:partition-r2-layout
  constitution: constitution:main
  research:
    - research:r2-hive-partitioning
  predecessor:
    - plan:expand-radar
---

# Purpose

Sequence the execution of `initiative:partition-r2-layout`:
re-layout the R2 raw zone to hive partitions and update the view
to read both flat and hive paths.

# Strategy

One ticket, one local edit, no Ralph packet. The change is two
file edits + one re-materialize + one cron-side verification.
Total expected scope: ~30 minutes of work.

The shared `r2_destination()` factory in `pipelines/_r2.py` is the
single point of change for ALL six source kinds — extractors do
not need individual edits. The view DDL gets two changes (glob
recursive + `hive_partitioning=true`).

# Workstreams

## Layout

Update `pipelines/_r2.py` `layout` argument:

```python
layout = "{table_name}/year={YYYY}/month={MM}/day={DD}/{load_id}.{file_id}.{ext}"
```

All 6 source-kind pipelines inherit this automatically.

## View

Update `motherduck/views.sql`:

- glob `raw/*/*/*.parquet` → `raw/*/*/**/*.parquet`
- add `hive_partitioning = true` to the `read_parquet(...)` call

The CTE keeps existing column projections; partition columns
(year, month, day) are not exposed in the public view — they stay
implicit. If a future ad-hoc query wants to prune by date,
querying the parquet glob directly with `hive_partitioning=true`
gives access to those columns.

## Verification

- Run `pipelines.radar` locally; confirm new files appear at hive
  paths.
- Run `apply_views.py` to re-materialize the view.
- Confirm view row counts are unchanged from pre-change state.
- Sample a partition-pruned probe query against MotherDuck (with
  `hive_partitioning=true` directly on the glob, not via the
  view) to confirm pruning works.
- Dispatch the cron workflow once; confirm it runs end-to-end.

## Documentation

`wiki:extractor-shape` gets a new "R2 layout: hive-partitioned"
section during retrospective.

# Milestones

## PM1 — Layout shipped + cron green

One ticket lands the dlt + view changes and verifies via local
run + cron dispatch.

## PM2 — Retrospective + wiki

`wiki:extractor-shape` updated. Initiative closes.

# Sequencing

PM1 first (only one ticket). PM2 happens immediately after PM1
verification.

# Execution Waves

## Wave 1 — Layout + view

Sequential, single ticket.

- `ticket:<TBD>` — Edit `pipelines/_r2.py` layout, edit
  `motherduck/views.sql` glob + hive_partitioning, run + verify.
  Same shape as `ticket:vejd8gon` (v2 Wave 1 trivial-config-add)
  in scope and risk profile. Critique optional.

# Risks

(Mirrored from initiative.) Net low; the change is local, the
research confirmed both ends of the pipeline behave correctly,
and the migration posture leaves historical files untouched.

# Evidence Strategy

Observation-first.

- Pre-change snapshot: per-`(source_kind, ats_slug)` row counts.
- Post-change snapshot: same query, same counts.
- New parquet at hive path: `boto3 list_objects_v2` after a
  pipeline run.
- Partition-pruning probe: ad-hoc SQL with WHERE on year/month/day.

Critique disposition: optional. The shared `_r2.py` factory was
already critiqued during `critique:ashby-mapbox-iter1` (FIND-004
resolved by inspection); this change is a layout-string update.
View DDL change is small and verifiable.

# Plan Readiness Review

Spec / acceptance coverage:

- No spec exists. Acceptance is ticket-local.

Placeholder scan:

- Ticket ID `<TBD>`; filled when ticket is created.

Ticket-sized slices:

- One ticket. Two file edits + verification.

Likely write scopes:

- `src/dream_job_radar/pipelines/_r2.py`
- `motherduck/views.sql`
- `.loom/wiki/extractor-shape.md` (during retro)

Likely verification posture: observation-first.

Stop / loopback conditions:

- If the view glob change misses files (row counts drop), back
  out and investigate.
- If dlt does not actually substitute the placeholders as
  expected at runtime, escalate to research re-probe.
- If MotherDuck's `hive_partitioning=true` produces unexpected
  column types beyond what the research probe covered, escalate.

# Exit Criteria

- New parquet files land at hive paths.
- View reads both old and new files; row counts unchanged.
- Cron run green on the new layout.
- `wiki:extractor-shape` documents the layout.
- Initiative milestones M1–M2 closed.
