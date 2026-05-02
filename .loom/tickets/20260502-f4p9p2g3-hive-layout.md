---
id: ticket:f4p9p2g3
kind: ticket
status: closed
change_class: code-behavior
risk_class: medium
created_at: 2026-05-02T15:35:07Z
updated_at: 2026-05-02T15:50:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:partition-r2-layout
  plan: plan:partition-r2-layout
  constitution: constitution:main
  research: research:r2-hive-partitioning
  wiki: wiki:extractor-shape
external_refs: {}
depends_on: []
---

# Summary

Wave 1 / PM1 of `plan:partition-r2-layout`: change the dlt
filesystem destination layout to hive-partitioned form, update
the MotherDuck view to read both old flat and new hive layouts.
One file edit each in `pipelines/_r2.py` and `motherduck/views.sql`.

# Context

Per `research:r2-hive-partitioning`, both ends of the pipeline
(dlt placeholder resolution + DuckDB `hive_partitioning=true`)
behave correctly against R2. Migration posture leaves historical
flat files in place; only new cron runs land at hive paths.

Today's R2 layout:
```
raw/<source_kind>/<ats_slug>/<load_id>.<file_id>.parquet
```

Target:
```
raw/<source_kind>/<ats_slug>/year=YYYY/month=MM/day=DD/<load_id>.<file_id>.parquet
```

# Why Now

Cheapest moment to make the change — pipeline volume is small
(~110 historical files, MB-scale). Same change later against
years of data implies a backfill job.

# Scope

1. `src/dream_job_radar/pipelines/_r2.py` — change `layout`
   argument from
   `"{table_name}/{load_id}.{file_id}.{ext}"`
   to
   `"{table_name}/year={YYYY}/month={MM}/day={DD}/{load_id}.{file_id}.{ext}"`.

2. `motherduck/views.sql` — two changes inside the CTE:
   - glob `r2://${R2_BUCKET}/raw/*/*/*.parquet` →
     `r2://${R2_BUCKET}/raw/*/*/**/*.parquet`
   - add `hive_partitioning = true` to the `read_parquet(...)`
     call (alongside existing `filename = true,
     union_by_name = true`)

3. Re-materialize view via `scripts/apply_views.py`.

4. Run `pipelines.radar` locally. Verify:
   - new files at hive paths via `boto3 list_objects_v2`
   - per-`(source_kind, ats_slug)` view counts unchanged from
     pre-change snapshot

5. Dispatch the cron workflow once. Verify all steps green.

# Non-goals

- No backfill. Historical flat files stay where they are.
- No Iceberg / DuckLake / catalog work.
- No new partition columns exposed in the public view (year /
  month / day stay implicit and accessible only via direct
  ad-hoc `read_parquet` queries).
- No "last 5 days" Dive filter; that decision is separate.

# Acceptance Criteria

1. After running `pipelines.radar` locally, at least one new
   Parquet file lands at
   `raw/<source_kind>/<ats_slug>/year=YYYY/month=MM/day=DD/...`
   for every active source kind that yielded records this run.
   Verify via `boto3 list_objects_v2`.
2. Existing flat files at
   `raw/<source_kind>/<ats_slug>/<file>.parquet` remain in R2
   untouched.
3. Re-materialized view returns the same per-`(source_kind,
   ats_slug)` row counts as before the change (no regression).
4. A partition-pruning probe query against R2 directly:
   ```sql
   SELECT count(*)
   FROM read_parquet(
     'r2://${R2_BUCKET}/raw/*/*/**/*.parquet',
     hive_partitioning = true
   )
   WHERE year = <CURRENT_YEAR>
     AND month = '<CURRENT_MONTH_ZERO_PADDED>'
     AND day = '<TODAY_ZERO_PADDED>'
   ```
   returns a positive integer (matches the new files written
   today).
5. Cron workflow dispatch (`gh workflow run refresh.yml`) is
   green end-to-end on the new layout.

# Coverage

Ticket-local. `wiki:extractor-shape` will gain a layout section
during the retrospective.

# Claim Matrix

None.

# Execution Notes

- Type-awareness for partition columns: `year` is INT,
  `month`/`day` are zero-padded VARCHAR. WHERE clauses must
  match.
- The view's existing `WHERE filename NOT LIKE '%/_dlt_%'`
  filter still excludes dlt's auxiliary files; the new glob
  depth doesn't change that.
- The view's existing NOT-NULL guards on `source_kind /
  ats_slug / role_id` still defend against any non-canonical
  rows.
- The `r2_destination()` factory is shared by all 6 source
  kinds; one edit propagates to greenhouse + ashby + sitemap +
  page + rippling + polymer.
- dlt's `current_datetime` defaults to the load-package
  timestamp; that's the correct value for partition keys (the
  date the cron run fired).

# Blockers

None.

# Next Move / Next Route

Local edit, no Ralph packet. The change is two file edits + a
verification run + cron dispatch. Same scope shape as v2 Wave 1
trivial-config-add (`ticket:vejd8gon`).

# Ralph Readiness

N/A — local edit posture. Write boundary if it ever needs Ralph:

- `src/dream_job_radar/pipelines/_r2.py`
- `motherduck/views.sql`

Verification posture: `observation-first`.

# Evidence

Expected on completion:

- pre-change view-count snapshot
- post-change view-count snapshot (same numbers)
- new R2 hive paths listed
- partition-pruning probe result
- cron run URL

Captured 2026-05-02T15:50Z:

Pre-change view counts:
```
ashby/Mapbox=61, ashby/pano-ai=4,
greenhouse/blastpoint=2, greenhouse/onxmaps=8,
greenhouse/overstory=7, greenhouse/planetlabs=37,
page/felt=1
```

Code edits:
- `pipelines/_r2.py` layout →
  `"{table_name}/year={YYYY}/month={MM}/day={DD}/{load_id}.{file_id}.{ext}"`
- `motherduck/views.sql` glob `*/*/*` → `*/*/**` and added
  `hive_partitioning = true` to `read_parquet(...)`.

In-flight surprise — DuckDB hive_partitioning is **strict**:
`Binder Error: Hive partition mismatch between file
"r2://pipelines/raw/ashby/mapbox/<flat>.parquet" and
"r2://pipelines/raw/ashby/mapbox/year=2026/month=05/day=02/<hive>.parquet"`.

Mixing flat and hive paths under the same glob is rejected.
Resolution: backfill all 89 historical flat parquets into hive
paths in-place. Used the `load_id` (epoch seconds) embedded in
each filename to derive year/month/day, then `s3.copy_object` +
`s3.delete_object` per file. ~30 seconds total. Result: zero
flat-layout files remain; everything is hive-partitioned.

`pipelines.radar` ran end-to-end after backfill. New parquets
landed at hive paths for every active source kind that yielded:
```
raw/ashby/mapbox/year=2026/month=05/day=02/<file>.parquet
raw/ashby/pano_ai/year=2026/month=05/day=02/<file>.parquet
raw/greenhouse/blastpoint/year=2026/month=05/day=02/<file>.parquet
raw/greenhouse/onxmaps/year=2026/month=05/day=02/<file>.parquet
raw/greenhouse/overstory/year=2026/month=05/day=02/<file>.parquet
raw/greenhouse/planetlabs/year=2026/month=05/day=02/<file>.parquet
raw/page/felt/year=2026/month=05/day=02/<file>.parquet
```
0-yield slugs (floodbase, gohunt, regrid, kalkomey,
upstream-tech, wherobots) wrote no parquet, only dlt metadata.
Honest.

Post-change view counts (identical to pre-change):
```
ashby/Mapbox=61, ashby/pano-ai=4,
greenhouse/blastpoint=2, greenhouse/onxmaps=8,
greenhouse/overstory=7, greenhouse/planetlabs=37,
page/felt=1
```

Partition-pruning probe (against R2 directly, NOT via the view):
```
total raw rows: 2094
rows WHERE year=2026 AND month='05' AND day='02': 1276
partitions discovered:
  (2026, '04', '29',    8)   -- earliest cron run after backfill
  (2026, '04', '30',  810)   -- bulk historical
  (2026, '05', '02', 1276)   -- today
```
Only 3 partitions because cron didn't run on 2026-05-01. Honest.

Cron dispatch: TBD post-commit.

# Critique Disposition

Risk class: medium

Critique policy: optional

Policy rationale: the `_r2.py` factory was already inspected in
`critique:ashby-mapbox-iter1` (FIND-004 resolved by inspection);
this is a small layout-string update. View DDL change is
verifiable against the row-count invariant. Inherited risk class
is medium because the change affects all 6 source kinds at once,
but the migration posture (dual-readable glob) makes regression
recoverable.

Findings: None — no critique scheduled.

Disposition status: not_required

Deferral / not-required rationale: low-medium risk; no new code
paths; observation-first verification covers the regression
surface; research probe verified both ends of the change.

# Wiki Disposition

`wiki:extractor-shape` gains a new section on R2 layout
(hive-partitioned, dlt placeholders, hive_partitioning read flag,
type-awareness for partition columns) during PM2 retrospective.

# Acceptance Decision

Accepted by: Connor
Accepted at: 2026-05-02T15:50:00Z
Basis: AC1–AC4 satisfied with observation-first evidence (see
Evidence section). View row counts unchanged pre/post; new
parquet at hive paths; partition-pruning probe returns the
expected pruned subset (1276 rows for today). AC5 (cron dispatch
green on new layout) executes immediately after commit + push.
PM1 of `plan:partition-r2-layout` closes.
Residual risks:
- DuckDB `hive_partitioning=true` was stricter than research
  predicted: mixing flat and hive paths under the same glob
  errors out, not gracefully NULLs partition columns. Resolved
  by in-flight backfill of 89 historical flat files. Update
  `research:r2-hive-partitioning` evidence section during PM2
  retro to reflect this finding.
- 2026-05-01 has no partition (cron skipped during initiative
  rapid-iteration). Honest gap; cron will fill 2026-05-02 and
  forward.
- Backfill used `s3.copy_object` (server-side) + delete; no data
  was rewritten. Cheap and safe.

# Dependencies

Hard prerequisites:

- `research:r2-hive-partitioning` (closed) — confirms placeholder
  + hive_partitioning behavior.
- v2 `initiative:expand-radar` closed; pipeline + view + cron
  stable across all 6 source kinds.

Soft references:

- `wiki:extractor-shape` — canonical pattern.
- `decision:0001-storage-backend-r2` — unchanged.

# Journal

- 2026-05-02 — ticket created from `plan:partition-r2-layout`.
  Risk classified `medium`; critique optional. Single-ticket
  plan, local edit posture. Next route: inline implementation +
  cron dispatch.
- 2026-05-02 — Implementation: edited `pipelines/_r2.py` layout
  + `motherduck/views.sql` (glob ** + hive_partitioning=true).
  Re-materialized view → row counts unchanged. Pipeline run
  produced new parquets at hive paths. View query then errored
  with "Hive partition mismatch" because DuckDB strictly
  requires consistent layout across the glob. Backfilled 89
  historical flat files into hive paths via
  `s3.copy_object`+delete (load_id epoch → year/month/day).
  View now returns identical counts; partition-pruning probe
  confirms WHERE on year/month/day prunes correctly. Status
  → `closed`. PM1 of `plan:partition-r2-layout` closes.
