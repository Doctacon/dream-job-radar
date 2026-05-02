---
id: research:r2-hive-partitioning
kind: research
status: closed
created_at: 2026-05-02T15:31:33Z
updated_at: 2026-05-02T15:31:33Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:partition-r2-layout
  constitution: constitution:main
  predecessor:
    - initiative:close-the-loop
    - initiative:expand-radar
external_refs: {}
---

# Question

Can we move the R2 raw-zone layout from
`raw/<source_kind>/<ats_slug>/<load_id>.<file_id>.parquet` to a
hive-partitioned shape
`raw/<source_kind>/<ats_slug>/year=YYYY/month=MM/day=DD/<load_id>.<file_id>.parquet`
without breaking dlt writes or MotherDuck reads, and what does the
view need to know about it?

# Why This Matters

The current layout produces one Parquet file per pipeline run per
(source_kind, ats_slug). After ~10 daily cron firings the project
has ~110 files; on the order of months / years it grows
unbounded. Hive-partitioned paths are the industry-standard
solution and let DuckDB partition-prune on date-bound queries.
The win at v2 scale (KB-MB) is negligible; the win is
future-proofing plus resume-relevant signal.

User raised the question after a domain conversation about
positioning as a data engineer in outdoor-tech. Iceberg /
DuckLake / catalog services were also discussed and explicitly
deferred — partitioning is the cheapest first step.

# Scope

In scope:

- Verify dlt's filesystem destination supports the date
  placeholders in `layout` and resolves them per-run.
- Verify DuckDB / MotherDuck `read_parquet(...,
  hive_partitioning=true)` correctly exposes the partition
  columns and prunes when a WHERE clause references them.
- Confirm migration posture: do existing flat files break under
  the new view glob?

Out of scope:

- Iceberg / DuckLake / Polaris catalog services. Explicitly
  deferred per user direction; revisit when the project
  outgrows plain Parquet.
- Backfill (rewriting historical files into the new path).
  Address as a separate decision; not required to start
  partitioning new writes.

# Method

Probed dlt's `path_utils.create_path` to confirm placeholder
resolution, then probed MotherDuck against synthetic R2 objects
written into hive-style paths.

# Sources

- `dlt.destinations.path_utils.create_path` — public API for
  resolving filesystem destination layouts.
- `dlt.destinations.path_utils.STANDARD_PLACEHOLDERS` —
  enumerates supported placeholders.
- DuckDB `read_parquet` with `hive_partitioning` parameter
  (verified against MotherDuck against R2 directly).

# Evidence

## dlt placeholder support

`STANDARD_PLACEHOLDERS` includes `YYYY`, `YY`, `MM`, `MMM`,
`MMMM`, `DD`, `dd`, `D`, `Q`, `HH`, `mm`, `ss`, etc. (full
datetime grammar). All resolve from a `current_datetime` value
that defaults to the load-package timestamp.

`create_path` test:

```python
layout = "{table_name}/year={YYYY}/month={MM}/day={DD}/{load_id}.{file_id}.{ext}"
create_path(
    layout=layout,
    file_name="mapbox.abc123.0.parquet",
    schema_name="ashby",
    load_id="1777728522.0",
    load_package_timestamp=pendulum.parse("2026-05-02T14:30:00Z"),
    current_datetime=pendulum.parse("2026-05-02T14:30:00Z"),
)
# → 'mapbox/year=2026/month=05/day=02/1777728522.0.abc123.parquet'
```

`MM` and `DD` produce zero-padded values; `YYYY` produces 4-digit
year. No additional `extra_placeholders` needed.

## DuckDB hive_partitioning behavior

Wrote two synthetic Parquet objects into R2 directly:

```
hive_probe/year=2026/month=05/day=01/file.parquet  (val=1)
hive_probe/year=2026/month=05/day=02/file.parquet  (val=2)
```

Then queried:

```sql
SELECT year, month, day, val
FROM read_parquet(
  'r2://<bucket>/hive_probe/**/*.parquet',
  hive_partitioning = true
)
ORDER BY year, month, day
```

Result:

```
[(2026, '05', '01', 1), (2026, '05', '02', 2)]
```

Note the auto-typing: `year` returned as INT, `month` and `day`
returned as VARCHAR with zero-padding preserved. WHERE clauses
must respect this:

```sql
WHERE year = 2026 AND month = '05' AND day = '02'   -- correct
WHERE year = '2026' AND month = 5 AND day = 2       -- type mismatch
```

Filtered query reduced result set correctly:

```sql
WHERE year = 2026 AND month = '05' AND day = '02'
-- → [(2026, '05', '02', 2)]
```

Probe parquets cleaned up after the test.

## Migration posture

The current view glob is `raw/*/*/*.parquet` — a fixed three-deep
glob that matches the existing flat layout
`raw/<source_kind>/<ats_slug>/<file>.parquet`.

A new layout
`raw/<source_kind>/<ats_slug>/year=YYYY/month=MM/day=DD/<file>.parquet`
is six segments deep. The fixed glob does not match it; new
files would silently disappear from the view.

Switch to `raw/*/*/**/*.parquet` (with `**`) so the glob spans
arbitrary depth. DuckDB recognizes `**` as a recursive segment.
This matches both the old flat layout AND the new hive layout.

Add `hive_partitioning = true` to the `read_parquet` call so
DuckDB exposes the year/month/day columns when present in the
path. For old flat files, the partition columns will be NULL —
acceptable for backward read.

WHERE clauses for partition pruning will only apply to files that
have the key=value segments. Old flat files cannot prune; they
are still read in full. As they roll off the active window, the
pruning gain materializes naturally.

# Rejected Options

- **Re-layout existing files (backfill).** Possible via a one-shot
  Python job: list R2, infer date from `fetched_at` inside each
  parquet, rewrite under hive path, delete old. Defer — the
  current dataset is small (~110 files, MB-scale), and historical
  files will age out of the daily-cron-relevant window quickly.
  Revisit if a future query pattern needs deep historical
  coverage with pruning.

- **Numeric-only path segments (no `key=value`).** Cleaner ls
  output, but DuckDB does not auto-recognize plain `2026/05/02/`
  as partition columns. Would need explicit casting in every
  query. The `key=value` Hive-standard form is the only one that
  enables auto-pruning via `hive_partitioning=true`.

- **Iceberg / DuckLake / Polaris catalog now.** Explicitly
  deferred per user direction. Adding a managed table format
  has a real complexity cost and is not warranted at v2 scale.
  When the project either grows past plain Parquet's pain points
  or the user needs a "I built an Iceberg pipeline" resume entry,
  open a fresh initiative.

# Null Results

None. Both probes succeeded.

# Conclusions

Yes — partitioning is mechanical and safe.

1. dlt accepts the new layout via its built-in placeholders. No
   custom callbacks needed.
2. MotherDuck / DuckDB reads hive-partitioned R2 paths cleanly
   and exposes year/month/day as queryable columns when
   `hive_partitioning=true`.
3. The view glob change from `raw/*/*/*.parquet` to
   `raw/*/*/**/*.parquet` is backward-compatible: old flat
   files keep working, new hive files appear with partition
   columns populated.
4. Type-awareness is the only real gotcha: `year` is INT,
   `month`/`day` are zero-padded VARCHAR. The view + any future
   ad-hoc queries must match types.

The change touches:

- `pipelines/_r2.py` — update `r2_destination(...)` `layout` arg
- `motherduck/views.sql` — change glob, add
  `hive_partitioning = true`
- existing flat files: leave alone; they remain readable

# Recommendations

- Promote findings into `initiative:partition-r2-layout` (this
  research is its evidentiary base).
- Plan that sequences the initiative should treat the work as
  one ticket: change the dlt layout in `_r2.py`, update the view
  DDL, run + verify the cron picks up new files at hive paths,
  re-materialize the view, sample a partition-pruned query.
- "Last 5 days" Dive filter is a separate decision (see Open
  Questions) and not strictly required to land partitioning.
- Defer Iceberg / DuckLake / catalog services. Re-evaluate when
  the project either grows past plain-Parquet pain points or the
  user wants resume-credible Iceberg work.

# Open Questions

- **What does "last 5 days" mean for the Dive?** Two distinct
  semantics:
  - (a) `WHERE fetched_at >= now() - INTERVAL 5 DAY` — restricts
    to roles the cron has observed in the last 5 days. Loses
    roles whose last fetch is older (cron stalled, pipeline
    failed, etc.). Matches partition-pruning naturally.
  - (b) `WHERE posted_at >= now() - INTERVAL 5 DAY` — restricts
    to roles posted upstream in the last 5 days. More useful
    semantically but `posted_at` is data, not path → no pruning.
  Decide before adding any Dive-side date filter. May be
  resolved cleanly by leaving the view unbounded (current
  behavior) and only adding a Dive UI control if the user
  wants it.

- **Backfill historical files.** Skipped today; revisit if a
  future query pattern needs deep historical coverage with
  pruning.

# Linked Work

- `initiative:partition-r2-layout` — primary consumer of this
  research.
- `wiki:extractor-shape` — gains an "R2 layout: hive-partitioned"
  section during the initiative retro.
- `decision:0001-storage-backend-r2` — unchanged; R2 is still the
  store of record.
