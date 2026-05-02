---
id: initiative:partition-r2-layout
kind: initiative
status: closed
created_at: 2026-05-02T15:31:33Z
updated_at: 2026-05-02T15:55:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  constitution: constitution:main
  research:
    - research:r2-hive-partitioning
  predecessor:
    - initiative:close-the-loop
    - initiative:expand-radar
external_refs: {}
---

# Summary

Move the R2 raw-zone layout from
`raw/<source_kind>/<ats_slug>/<file>.parquet` to a
hive-partitioned shape
`raw/<source_kind>/<ats_slug>/year=YYYY/month=MM/day=DD/<file>.parquet`.
Update the MotherDuck view to read hive partitions. Keep
historical flat files in place (no backfill). Defer Iceberg /
DuckLake / catalog services.

# Objective

The radar's R2 layout matches industry-standard hive partitioning
so that future date-bound queries can partition-prune, and the
project surfaces a more resume-credible data-engineering shape
without the complexity cost of managed table formats.

# Why Now

`initiative:expand-radar` just closed (2026-05-02). Pipeline runs
have been writing flat parquets for ~10 days; volume is still
small (~110 files, MB-scale). Re-laying-out the dlt destination
is mechanical and cheap right now; same change against years of
data later would imply a backfill job.

User raised the change after a conversation about resume signal
in outdoor-tech data-engineering roles. Iceberg specifically
came up; this initiative addresses the partitioning piece without
committing to a managed table format. Iceberg / DuckLake / catalog
services explicitly defer to a future initiative.

# In Scope

One change with three edits and one verification:

1. `pipelines/_r2.py` — change `layout` from
   `'{table_name}/{load_id}.{file_id}.{ext}'` to
   `'{table_name}/year={YYYY}/month={MM}/day={DD}/{load_id}.{file_id}.{ext}'`.
2. `motherduck/views.sql` — change the glob from
   `raw/*/*/*.parquet` to `raw/*/*/**/*.parquet` and add
   `hive_partitioning = true` to the `read_parquet` call.
3. Run the pipelines once locally and via the cron workflow to
   confirm new files land at hive paths AND that the view returns
   the same row counts as before (existing flat files remain
   readable; new files add their partition columns when reading).

# Out Of Scope

- **Backfill.** Historical flat files stay where they are. They
  remain readable through the view but cannot partition-prune.
  As they roll out of the daily-cron-relevant window the pruning
  gain materializes naturally for new data.
- **Iceberg, DuckLake, Polaris catalog.** Deferred per user
  direction.
  - Iceberg = open table-format spec adding metadata + transaction
    layer atop object storage. Useful when v3+ needs versioning,
    time travel, ACID, or interop with Snowflake/Trino/etc.
  - DuckLake = DuckDB-native table format. Similar idea, smaller
    ecosystem.
  - Polaris = a catalog service that manages Iceberg metadata.
  None of these are strictly required to add partitioning.
  Revisit when (a) pipeline outgrows plain Parquet's pain points,
  or (b) user wants explicit "I built Iceberg" resume work.
- **"Last 5 days" Dive filter.** Decide separately; depends on
  whether the user wants `fetched_at`-based or `posted_at`-based
  recency. Not required to land partitioning.
- **R2 layout for the raw zone's `_dlt_*` system tables.** Those
  remain at their existing positions; dlt manages them.

# Success Metrics

- After the change, all new parquet files land under
  `raw/<source_kind>/<ats_slug>/year=YYYY/month=MM/day=DD/...`.
- `current_open_roles` row counts unchanged immediately after the
  change (same view shape, same roles).
- A WHERE-on-partition probe query against MotherDuck returns the
  expected pruned subset (e.g. `WHERE year=2026 AND month='05'
  AND day='02'`).
- `wiki:extractor-shape` documents the layout in its "What lives
  next to the data" / new "R2 layout" section.

# Milestones

## M1 — Layout shipped

dlt writes new files to hive paths; view reads both new and old
files cleanly; cron run green.

## M2 — Wiki + retrospective

`wiki:extractor-shape` updated. Carryover: confirm all 6 source
kinds emit hive paths consistently; flag any that don't (none
expected — all share the same `r2_destination()` factory).

# Dependencies

Hard prerequisites:

- `research:r2-hive-partitioning` (closed) — confirms dlt
  placeholder support and DuckDB hive_partitioning behavior.
- `initiative:close-the-loop` + `initiative:expand-radar` closed
  — provides the 6-source-kind, 11-slug pipeline + cron + view +
  Dive that this initiative modifies in-place.

Soft references:

- `decision:0001-storage-backend-r2` — unchanged.
- `wiki:extractor-shape` — gains a new section during the retro.

# Risks

- **Type-mismatch on partition WHERE clauses.** DuckDB types
  `year` as INT, `month`/`day` as VARCHAR with zero-padding.
  Mitigation: ticket execution notes spell this out and any view
  WHERE clause matches the inferred types.
- **Glob change might miss old or new files.** Mitigation: the
  glob `raw/*/*/**/*.parquet` matches both 3-segment (flat) and
  6-segment (hive) paths. Verify post-change row counts equal
  pre-change row counts.
- **Cron mid-cutover.** A cron firing during the cutover would
  produce a mix of paths. Acceptable; both paths are readable.
- **dlt internal directory layout.** dlt also writes
  `_dlt_loads/`, `_dlt_pipeline_state/`, `_dlt_version/`, `init`
  files into `raw/<source_kind>/`. The view's
  `WHERE filename NOT LIKE '%/_dlt_%'` filter already excludes
  them. Confirmed unaffected by layout change.

# Linked Work

Plan: `plan:partition-r2-layout`.

# Status Summary

Initiative drafted 2026-05-02 immediately after
`initiative:expand-radar` closed. Research probe
(`research:r2-hive-partitioning`) confirmed dlt placeholder
support and DuckDB `hive_partitioning=true` behavior on R2.
Ready to route into a single-ticket plan.

## Close-out 2026-05-02

Status → `closed`. Outcome by milestone:

- **M1 — Layout shipped:** done. `ticket:f4p9p2g3` (closed).
  Edits to `pipelines/_r2.py` and `motherduck/views.sql`. 89
  historical flat parquets backfilled into hive paths in-place
  (DuckDB `hive_partitioning=true` is strict; mixing layouts is
  rejected, not gracefully NULLed). View row counts unchanged
  pre/post. Manual cron dispatch run 25255565860 green
  end-to-end (after a one-line follow-up fix to
  `scripts/health_check.py` whose old glob matched zero files
  post-backfill, run 25255532404 caught it).
- **M2 — Wiki + retrospective:** done.
  `wiki:extractor-shape` extended with new "R2 layout:
  hive-partitioned" section covering dlt placeholders, DuckDB
  `hive_partitioning=true` behavior, type-awareness for
  partition columns, mixed-layout prohibition + migration
  recipe, and explicit Iceberg / DuckLake / catalog deferral.
  Old glob references in the wiki updated to the recursive
  form. dataset_name table grew to include Rippling + Polymer
  rows from prior initiative.

State at close-out:

- All R2 parquet under hive layout
  `raw/<source_kind>/<ats_slug>/year=YYYY/month=MM/day=DD/...`.
- View reads cleanly; row counts unchanged from pre-cutover.
- Cron green on the new layout.
- No data was rewritten — backfill used `s3.copy_object` +
  `delete` (server-side).
- Iceberg / DuckLake / catalog deferred. Revisit when v3+
  scale or a "build Iceberg" resume goal forces the question.

Carried forward as deferred follow-ups (not promoted to tickets
today):

- Same FIND set inherited from prior critiques: tighten
  `STALE_THRESHOLD_HOURS`; per-step `env:` for secret
  minimization; N→0 silent breakage detection for HTML / index
  regex parsers.
- Vibrant Planet parser when they post roles (carryover from
  v2).
- Iceberg integration if/when scale or resume goals demand it.
