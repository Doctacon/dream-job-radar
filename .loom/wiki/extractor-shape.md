---
id: wiki:extractor-shape
kind: wiki
page_type: concept
status: active
created_at: 2026-04-30T00:22:47Z
updated_at: 2026-04-30T01:18:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:close-the-loop
  plan: plan:v1-radar
  ticket: ticket:gjkpkpum
  critique: critique:walking-skeleton-iter1
  decision: decision:0001-storage-backend-r2
---

# Summary

How a single dream-job-radar extractor is shaped end-to-end: how the dlt
pipeline writes Parquet under R2, how the MotherDuck `current_open_roles`
view reads that layout, what each output column means, and which
constraints make this shape load-bearing for Wave 2.

# Why This Concept Exists

Wave 1 (`ticket:gjkpkpum`) shipped one extractor (Greenhouse → onX). Wave 2
will copy the pattern four times (Greenhouse → Planet Labs, Ashby → Mapbox,
page monitor → Regrid + Felt, sitemap monitor → GoHunt). The shape was
chosen by trial: the first attempt failed because dlt's filesystem
destination always prefixes `<dataset_name>/` under `bucket_url`, which
collided with the path contract the view expected. Without this page,
Wave 2 will rediscover the same surprise four times.

# Core Idea

## One pipeline per source kind

Each extractor kind (Greenhouse, Ashby, page monitor, sitemap monitor)
is its own dlt pipeline. The pipeline-name is `dream_job_radar` for all
of them; the differentiator is `dataset_name`, which is set to the
source kind:

| source kind     | dataset_name |
|-----------------|--------------|
| Greenhouse      | `greenhouse` |
| Ashby           | `ashby`      |
| page monitor    | `page`       |
| sitemap monitor | `sitemap`    |

The dlt filesystem destination uses
`bucket_url = s3://<R2_BUCKET>/raw` (no source-kind segment) and the
default layout `{table_name}/{load_id}.{file_id}.{ext}`. Because dlt
unconditionally prefixes `<dataset_name>/` under `bucket_url`, the
observable R2 layout becomes:

```
s3://<R2_BUCKET>/raw/<source_kind>/<table_name>/<load_id>.<file_id>.parquet
```

For each pipeline, every "company" / board slug / tracked surface gets
its own table name. Each slug → one resource → one table directory.

That makes `r2://<bucket>/raw/<source_kind>/<ats_slug>/` the path
contract the view depends on.

## What lives next to the data

dlt writes auxiliary load metadata under
`raw/<source_kind>/_dlt_loads/`,
`raw/<source_kind>/_dlt_pipeline_state/`,
`raw/<source_kind>/_dlt_version/`, plus an empty `init` marker. These
live as siblings of the table directories. Today they are JSONL or
extensionless, so the view glob (`raw/*/*/*.parquet`) does not match
them, but the view also defends against future format changes with an
explicit `WHERE filename NOT LIKE '%/_dlt_%'` filter.

## What columns the view exposes

`current_open_roles` returns one row per
`(source_kind, ats_slug, role_id)` with the latest `fetched_at` row
winning. The columns are:

```
company        VARCHAR  -- friendly company name (today: same as ats_slug)
source_kind    VARCHAR  -- 'greenhouse' | 'ashby' | 'page' | 'sitemap'
ats_slug       VARCHAR  -- board slug or page key for this source
role_id        VARCHAR  -- stringified upstream id; stable per source
title          VARCHAR  -- role title (passes the v1 keyword filter)
url            VARCHAR  -- canonical role URL on the upstream surface
location       VARCHAR  -- single location string when known
posted_at      TIMESTAMP-- upstream "updated_at" today (see below)
fetched_at     TIMESTAMP-- when the dlt run that wrote this row started
first_seen_at  TIMESTAMP-- min(fetched_at) over (source_kind, ats_slug, role_id)
last_seen_at   TIMESTAMP-- max(fetched_at) over (source_kind, ats_slug, role_id)
```

The view does NOT expose `raw_json` (which the extractor still writes
to Parquet). That keeps the public surface thin; a sibling
`raw_open_roles` view can expose `raw_json` later if needed without
disturbing the public view.

## Canonical row must not contain Python list values

The Ashby Wave 2 #2 iteration learned this the painful way. dlt's
filesystem destination normalizes any non-empty list field into a
nested child table — Ashby's non-empty `[department]` produced
`raw/ashby/mapbox__departments/...parquet`, which the view's
`read_parquet(..., union_by_name=true)` slurped, polluting
`current_open_roles` with a `(null, null, null)` row that survived
dedup.

Rule for v1: **the canonical row that the extractor yields must not
contain Python list values.** Multi-valued source fields (departments,
secondary locations, tags) stay only in `raw_json`. Future consumers
who need them can parse `raw_json` directly or build a sibling view.

(The Greenhouse extractor never tripped this even though it had a
`departments` field, because the `/jobs` endpoint omits departments
entirely — `_normalize` always produced `[]` and dlt dropped the
empty column. So the bug was hidden until a source kind with
non-empty list values arrived.)

## Title-keyword filter is applied at extract time

The v1 filter is a simple lowercase substring match on `title` against
`('data', 'engineer', 'gis', 'geospatial')`. Filtering happens inside
the dlt resource (before yield), not in SQL, so unfiltered Parquet
never lands in R2. This is intentional: it keeps R2 small and means
re-running with a wider filter requires a new ingest run, not just a
new view.

Known tradeoff: substring matching means `data` matches "Database
Administrator", `gis` matches "logistics", etc. Wave 1 had no false
positives in the onX corpus. Re-evaluate during the Wave 2
retrospective.

## Slug-case policy

Some source kinds use mixed-case slugs (Ashby's `Mapbox`, where
lowercase 404s); some use lowercase only (Greenhouse's `onxmaps`).
The policy across all source kinds:

- The extractor uses the slug **verbatim** for the upstream API call
  (case-sensitive when the source requires it).
- The extractor stores the slug **verbatim** in the `ats_slug` data
  column.
- The dlt resource is named after the slug; dlt's default
  `snake_case` naming convention then **lowercases** the
  table-directory in the R2 path.

Net result: the R2 path may be lowercased even when `ats_slug` keeps
the source casing. The view groups by `ats_slug` (data column), so
`SELECT ats_slug, count(*) FROM current_open_roles` returns
`Mapbox`, not `mapbox`. R2 listings show `raw/ashby/mapbox/...`.

Do not switch dlt to `naming_convention = "direct"` to "fix" this;
that decision affects every source kind and could surface unrelated
weirdness on character classes the snake_case normalizer was
quietly handling. Accept the lowercased path.

## Defensive listed/published checks

Sources often expose unlisted drafts in the same response shape as
public listings. Before applying the title-keyword filter, check for
the source-specific "is this actually live?" flag and skip drafts.

Examples:

- Ashby: `if not job.get("isListed", True): continue`
- Greenhouse: no equivalent flag in the public `/jobs` endpoint;
  the API only returns published roles, so no extra check needed.
- Future source kinds: check the upstream docs for a
  `published`, `isLive`, `status == "open"`, or similar flag and
  apply it defensively even if today's data does not appear to need
  it.

## Duplicates by title are upstream behavior

Both Ashby (Mapbox) and Greenhouse (Planet Labs) publish the same
role title under multiple region-specific listings, each with a
distinct upstream id. The view's `(source_kind, ats_slug, role_id)`
dedup preserves all of them — that is intentional, since each
region has its own canonical URL and own apply flow.

Do not dedup-by-title in the extractor or the view. If the Dive
ever needs a "deduplicated by title" surface, build it as a
sibling view at the Dive layer; the canonical view stays
role_id-keyed.

## `posted_at` semantic

For Greenhouse, `posted_at` comes from the upstream `updated_at`. So
it is "last-modified at the source", not strictly "first-posted at the
source". Other source kinds may expose a true creation timestamp; if
the divergence becomes meaningful, rename the column to
`source_updated_at` or split into `posted_at` and `last_modified_at`
during a Wave 2 spec pass. Until then, `posted_at` carries the
"updated" interpretation across all source kinds.

## Project packaging

The `pyproject.toml` declares a hatchling build target with
`packages = ["src/dream_job_radar"]`. This is required so that
`uv run python -m dream_job_radar.pipelines.<entry>` resolves the
package; without it, `uv sync` does not install the project as a
distribution and `python -m` fails with `ModuleNotFoundError`.
Future extractor entry points should reuse the
`src/dream_job_radar/pipelines/<source_kind>.py` shape.

# Important Boundaries

- This page does not own pipeline scheduling. Wave 3 (GitHub Actions
  cron) handles that.
- This page does not own Dive presentation. Dive layout is captured in
  the Dive itself; this page only describes the read surface
  (`current_open_roles`) the Dive consumes.
- This page does not own the constitutional choice of R2 over other
  backends. That lives in `decision:0001-storage-backend-r2`.
- This page is not a how-to-run guide. The repo `README.md` owns the
  manual run command for Wave 1; Wave 3 will own the scheduled-run
  story.

# How It Connects

- `decision:0001-storage-backend-r2` — R2 is the system of record.
  This page describes the R2 prefix contract that decision implies.
- `plan:v1-radar` — Wave 2 sequencing inherits this pattern; the plan
  cites this page so future extractor tickets do not re-derive it.
- `critique:walking-skeleton-iter1` — FIND-005 (`posted_at` semantic),
  FIND-006 (one pipeline per source_kind), and FIND-007 (no tests yet)
  are the lessons that produced this page.
- `initiative:close-the-loop` — The v1 keyword filter and the six
  confirmed companies live there. This page describes how each one
  becomes an extractor.

# Sources

- `ticket:gjkpkpum` — Wave 1 acceptance evidence.
- `critique:walking-skeleton-iter1` — adversarial review of the
  shape.
- `src/dream_job_radar/extractors/greenhouse.py` — reference
  implementation of the resource-per-slug factory.
- `src/dream_job_radar/pipelines/radar.py` — reference implementation
  of the pipeline configuration.
- `motherduck/views.sql` — reference implementation of the view.

# Related Pages

None yet. When Wave 2 introduces the page-monitor and sitemap-monitor
extractor kinds, those will likely deserve their own troubleshooting
or workflow pages (HTML brittleness, sitemap pagination), and this
page should link forward to them.

# Change Notes

- 2026-04-30 — initial promotion from `ticket:gjkpkpum` retrospective.
  Captures the dataset_name = source_kind pattern, the view shape, the
  raw-zone layout, and the v1 keyword-filter / `posted_at` semantics.
- 2026-04-30 — extended after `ticket:oy172mt9` (Ashby → Mapbox)
  retrospective. Added: "canonical row must not contain Python list
  values" rule (FIND-001), slug-case policy (FIND-002),
  duplicate-by-title note (FIND-006), defensive listed/published
  checks (FIND-007). `departments` removed from canonical column
  table.
