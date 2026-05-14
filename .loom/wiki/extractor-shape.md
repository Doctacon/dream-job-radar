---
id: wiki:extractor-shape
kind: wiki
page_type: concept
status: active
created_at: 2026-04-30T00:22:47Z
updated_at: 2026-05-02T16:32:00Z
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
| Rippling        | `rippling`   |
| Polymer         | `polymer`    |
| RemoteOK        | `remoteok`   |
| Tech Jobs for Good | `techjobsforgood` |
| GIS Jobs Clearinghouse | `gjc` |
| Green Jobs Board | `greenjobsboard` |

The dlt filesystem destination uses
`bucket_url = s3://<R2_BUCKET>/raw` (no source-kind segment) and the
hive-partitioned layout
`{table_name}/year={YYYY}/month={MM}/day={DD}/{load_id}.{file_id}.{ext}`
(see "R2 layout: hive-partitioned" section). Because dlt
unconditionally prefixes `<dataset_name>/` under `bucket_url`, the
observable R2 layout is:

```
s3://<R2_BUCKET>/raw/<source_kind>/<table_name>/year=YYYY/month=MM/day=DD/<load_id>.<file_id>.parquet
```

For each pipeline, every "company" / board slug / tracked surface gets
its own table name. Each slug → one resource → one table directory,
then one date-partition directory per cron firing.

That makes `r2://<bucket>/raw/<source_kind>/<ats_slug>/year=*/month=*/day=*/`
the path contract the view depends on.

## What lives next to the data

dlt writes auxiliary load metadata under
`raw/<source_kind>/_dlt_loads/`,
`raw/<source_kind>/_dlt_pipeline_state/`,
`raw/<source_kind>/_dlt_version/`, plus an empty `init` marker. These
live as siblings of the table directories. Today they are JSONL or
extensionless, so the view glob (`raw/*/*/**/*.parquet`) does not match
them, but the view also defends against future format changes with an
explicit `WHERE filename NOT LIKE '%/_dlt_%'` filter.

## R2 layout: hive-partitioned

Set 2026-05-02 (`initiative:partition-r2-layout`). New parquet files
land at:

```
raw/<source_kind>/<ats_slug>/year=YYYY/month=MM/day=DD/<load_id>.<file_id>.parquet
```

`year=`, `month=`, `day=` are Hive-standard `key=value` segments —
DuckDB's `read_parquet(..., hive_partitioning=true)` recognizes them
and exposes the date components as queryable columns for partition
pruning.

### dlt config

`pipelines/_r2.py` configures `r2_destination()` with:

```python
layout="{table_name}/year={YYYY}/month={MM}/day={DD}/{load_id}.{file_id}.{ext}"
```

`{YYYY}`, `{MM}`, `{DD}` are dlt's built-in datetime placeholders.
They resolve from the load-package timestamp (the time the cron
run fired). All six source-kind pipelines inherit the layout from
this single shared factory.

### View read

`motherduck/views.sql` reads the zone with:

```sql
read_parquet(
  'r2://<bucket>/raw/*/*/**/*.parquet',
  filename = true,
  union_by_name = true,
  hive_partitioning = true
)
```

The recursive `**` glob matches the six-segment hive layout. The
three-deep `*/*/*.parquet` glob from before the cutover would miss
the new layout entirely.

### Type-awareness

DuckDB auto-types the partition columns:

| column  | type    | notes                          |
|---------|---------|--------------------------------|
| `year`  | INTEGER | parsed from `year=2026`        |
| `month` | VARCHAR | zero-padded; parsed from `month=05` |
| `day`   | VARCHAR | zero-padded; parsed from `day=02` |

WHERE clauses must respect this:

```sql
WHERE year = 2026 AND month = '05' AND day = '02'   -- correct
WHERE year = '2026' AND month = 5                   -- type mismatch
```

### Mixed layouts not allowed under one glob

DuckDB's `hive_partitioning=true` is **strict**: every file matched
by the glob must share the same partition shape. Mixing flat
(3-segment) and hive (6-segment) paths raises:

```
Binder Error: Hive partition mismatch between file ...
```

When the layout changed in `ticket:f4p9p2g3`, all 89 historical flat
parquets were migrated in-place via `s3.copy_object` + `delete`
(server-side; no data rewritten). The migration job inferred the
correct year/month/day per file from the `load_id` epoch embedded
in each filename.

If a future layout change happens again, plan for a similar
in-place migration. Cheap at this scale (KB-MB); becomes a
one-shot job at GB+ scale.

### Public view stays canonical

`current_open_roles` does not expose `year` / `month` / `day` as
columns. Partition pruning via the view is opaque to consumers —
the partition columns are useful only for ad-hoc `read_parquet`
queries that bypass the view. If a future Dive iteration wants
date-partition access, add a sibling view or a parametrized
table function.

### How the view bounds scans

Set 2026-05-02 (`initiative:bound-view-window`). The view's CTE
filters parquet partitions on a 30-day window before the dedupe
window function runs:

```sql
AND make_date(year, CAST(month AS INTEGER), CAST(day AS INTEGER))
    >= current_date - INTERVAL 30 DAY
```

Net effect:

- DuckDB pushes the predicate to the parquet read layer; only
  partitions inside the 30-day window are scanned.
- The dedupe `ROW_NUMBER() OVER (PARTITION BY source_kind,
  ats_slug, role_id ORDER BY fetched_at DESC) = 1` operates on
  the bounded set.
- Scan size stays roughly constant as history accumulates.
  Without the bound, a year of daily cron would feed 365 ×
  per-day rows into the window function.

The 30-day window is intentionally generous:

- Cron health-check already fails fast on per-slug staleness
  > 36 hours.
- Manual one-off pipeline outages of a week or two are
  recoverable without losing slugs from the view.
- The Dive layers a tighter 7-day filter on top of the view
  output, so the view's wider window is invisible to public
  consumers.

If cron stalls for a slug for > 30 days the view will silently
forget that slug until cron resumes. That is an acceptable
trade-off: a slug not observed in a month is operationally
stale, and the health-check would have already alerted long
before.

The choice of `make_date(year, CAST(month AS INTEGER),
CAST(day AS INTEGER))` is deliberate: `year` arrives as INT,
`month` and `day` arrive as zero-padded VARCHAR (per
`hive_partitioning=true` type inference). The cast makes the
predicate partition-comparable so DuckDB's planner prunes
correctly. If a future DuckDB version regresses partition
pushdown for `make_date`, fall back to a lexicographic
comparison against a string-formatted cutoff
(`year || '-' || month || '-' || day >= '2026-04-02'`).
Verify via `EXPLAIN` after any planner change.

### What this enables

- **Partition pruning** when querying R2 directly with a WHERE
  on year/month/day.
- **Industry-standard hive layout** that other tools
  (Athena, Trino, Spark) recognize natively if the project ever
  needs interop.
- **Resume-credible "I built a hive-partitioned data lake on
  Cloudflare R2"** as a project narrative.

### What this defers

- **Iceberg, DuckLake, Polaris catalog.** Managed table formats
  add a metadata + transaction layer beyond what hive
  partitioning provides. Cost: real complexity (catalog service,
  versioning state, write coordination). Benefit: ACID, time
  travel, schema evolution. Not worth it at v3 scale; revisit if
  the project either outgrows plain Parquet's pain points or the
  user wants explicit Iceberg-on-resume work.

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

Per-source-kind posture:

| source_kind | posture                                                                  |
|-------------|--------------------------------------------------------------------------|
| greenhouse  | API-implicit — `/jobs` only returns published roles; no extra check     |
| ashby       | flag-based — `if not job.get("isListed", True): continue`               |
| sitemap     | presence-based — sitemap `<loc>` is the published signal                |
| page        | presence-based — being on the careers page IS the signal                |
| rippling    | presence-based — list response excludes unpublished by upstream contract|
| polymer     | presence-based — index URL on parent careers page IS the signal         |

Three distinct postures across six source kinds. The rule for new
source kinds:

1. Check the upstream docs for a `published` / `isLive` /
   `status == "open"` flag.
2. If present, gate before the keyword filter (Ashby pattern).
3. If absent, accept presence-as-signal and document the choice
   in this table.

## Polite-fetch UA boundary

Default User-Agent is `dream-job-radar/0.1`. Polymer's extractor
includes a polite→browser UA fallback: if the polite UA returns
403 or 503, retry once with a real browser UA. This is the v1
ceiling on UA tactics. Anything beyond that — cookies, JS
execution, headless browsers, login flows — requires a research
loopback and explicit constitutional discussion (per
`constitution:main` "no anti-bot evasion" posture).

In v1 + v2, the fallback is exercised by neither Polymer
(Upstream Tech) nor any other source — all surfaces returned 200
to the polite UA. The fallback exists pre-emptively for sites
that Cloudflare-front their careers pages; if a future site
becomes unreachable even with browser UA, that company is
dropped, not escalated to harder evasion.

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

## Sitemap-monitor sources (CMS-driven, no ATS)

Some companies don't use any ATS. Their job posts ship as CMS
articles, indexed in `sitemap.xml`. GoHunt is the v1 example.

The pattern:

1. Fetch the company's public `sitemap.xml`.
2. Filter `<loc>` entries by a substring heuristic
   (e.g. `"job-opportunity"` for GoHunt).
3. For each matching URL, fetch the role page (one HTTP GET each;
   sleep ~0.5s between fetches to be polite).
4. Extract the first `<script type="application/ld+json">` block
   whose `@type` is `"Article"` (JSON-LD is the cleanest source of
   structured metadata on CMS pages).
5. Pull `headline`, `datePublished`, `url` from the Article block.
6. Apply the v1 title-keyword filter to `headline`.
7. Yield matched roles via `_normalize`.

### `role_id` derivation

For sitemap-monitor sources, the upstream has no UUID — the URL
slug IS the de-facto identity. Today's implementation derives
`role_id = urlsplit(article_url).path.rstrip("/").split("/")[-1]`.

**Constraint:** if the upstream renames a slug (typo fix, SEO
change, title rewording), the next pipeline run sees a "new" role
with a fresh `first_seen_at`, and the old observation drops out of
the view (no fresh `fetched_at` to win the dedup partition). The
old parquet is still in R2 but invisible to the public view.

For v1 this is acceptable. If slug renames become a real problem,
consider hashing `headline + canonical_url_host` as a secondary
identity. Defer until a real rename event surfaces.

### JSON-LD parsing tradeoff

`extractors/sitemap.py` extracts JSON-LD via regex
(`<script type="application/ld+json">...</script>`) rather than
`BeautifulSoup` or `lxml`. The regex is fragile in theory (a literal
`</script>` inside a JSON string would prematurely end the match),
but the JSON spec forbids unescaped `</script>` literals — the only
way one would appear is `"<\/script>"`, which the regex does not
trigger on.

If a future source kind embeds odd content that breaks the regex,
switch to `lxml.html` (already a transitive dep) or add
`beautifulsoup4`. Do not pre-emptively swap.

### Sitemap-index escalation

`_fetch_sitemap_urls` checks the root tag and raises `ValueError`
if it sees `<sitemapindex>`. v1 does not recurse into sub-sitemaps.
If a host shards their sitemap, the failure is loud (raises) rather
than silent (wrong data).

When a sharded sitemap is the only path forward, decide explicitly:
either (a) implement single-level recursion, or (b) point at the
specific sub-sitemap that contains role pages directly.

## Page-monitor sources (HTML scraping, no API)

Some sources have no ATS and no JSON-LD — open roles are
hand-maintained in HTML on a careers page or job board. v1 covers
two: Regrid (hosted on a Gusto job board) and Felt (Webflow
careers page).

The pattern:

1. Fetch the careers / board page.
2. Apply a per-site parser strategy (regex against
   site-specific class names) to extract role records.
3. Apply v1 keyword filter to titles.
4. Yield matched roles via `_normalize`.

### Per-site parser dispatch

Each site spec carries a `parser_kind` string. The extractor
dispatches to the matching parser (`_parse_gusto_board`,
`_parse_felt_careers`, etc.). Adding a new page-monitor site means:

- add a new `_parse_<shape>(html, spec)` function
- add a new `parser_kind` literal recognized by `_parse(...)`
- add a `SiteSpec` to `DEFAULT_SITES`

Parsers can also share strategies (multiple sites can use the same
Gusto-board pattern if Gusto-hosted).

### Regex fragility — the fundamental constraint

Page-monitor parsers depend on exact upstream class names:

- Felt: `<div class="h4 careers">TITLE</div>`
- Gusto: `<a class="block hover:bg-gray-50" href="...">` +
  `<h3 class="text-lg">TITLE</h3>`

Webflow regenerations or Tailwind class re-shuffling on either
host can silently produce 0 matches even when humans see roles on
the page. The MATCH/skip log is the only run-time signal.

Operator convention: each `site_resource` prints
`[page:<slug>] parsed N role(s) from page` followed by per-role
MATCH/skip lines. Wave 3 (scheduling) should treat a transition
from N>0 to 0 as a loud failure, not a silent count change.

### Felt is special: no per-role URL, apply via mailto

Felt's careers page does not link each role to a per-role page;
applying is via `mailto:hello@felt.com`. The Felt parser uses the
careers page URL itself as `url` for every Felt row. Multiple Felt
rows therefore share the same `url`. If a future Dive iteration
wants to surface a structured apply-action, capture mailto in a
new column then; do not extend the canonical row pre-emptively.

### Vibrant Planet deferral

`vibrantplanet.net/about/team-and-careers` returns 200 but their
careers section currently shows the literal placeholder `"No open
roles at the moment. Check back soon!"`. There is no role-list
HTML to validate a parser against. Vibrant Planet is intentionally
absent from `extractors/page.py` `DEFAULT_SITES` until they post
roles. A `vibrant_planet_careers` parser can be added once the
populated HTML structure is observable. The module docstring
documents this so future agents do not blindly add a guess parser.

## Rippling sources (public board API)

Rippling is a flat JSON-list public API:

`GET https://api.rippling.com/platform/api/ats/v1/board/<slug>/jobs`
→ HTTP 200, list of records with shape:

```json
{
  "uuid": "86cb9df0-2d01-4994-8e75-06e21ce17534",
  "name": "Content Editor (Contractor)",
  "department": {"id": "Marketing", "label": "Marketing"},
  "url": "https://ats.rippling.com/<slug>/jobs/<uuid>",
  "workLocation": {"label": "Remote (United States)", "id": "..."}
}
```

The pattern:

1. Fetch list endpoint.
2. For each record, apply title-keyword filter on `name`.
3. Yield matched roles via `_normalize`.

### `role_id` derivation

`role_id = str(job["uuid"])`. Server-generated, opaque, does not
change with title rewrites. Same identity quality as Greenhouse
integer ids and Ashby UUIDs.

### `workLocation` and `department` flattening

Both fields are dicts with `id` + `label`. The canonical row
exposes only `location = workLocation.label` (string).
`department` lives only in `raw_json` per the no-list / no-nested-
struct rule (FIND-001 of Ashby/Mapbox critique).

### `posted_at` is empty

Rippling's list endpoint exposes no posting timestamp. The
extractor sets `posted_at = ""`; the view's TRY_CAST converts to
NULL. Use `first_seen_at` for recency.

## Polymer sources (parent-page index + per-role JSON-LD)

Polymer is a hybrid pattern: index from a parent careers URL
(e.g. `upstream.tech/careers`), role data from per-role pages on a
custom `jobs.<company>.<tld>` subdomain.

The pattern:

1. Fetch the parent careers page.
2. Apply a per-site regex (`SiteSpec.id_pattern`) to extract role
   IDs.
3. For each ID, GET `SiteSpec.role_url_template.format(id=id)`.
4. Extract the first `<script type="application/ld+json">` block
   whose `@type == "JobPosting"`.
5. Parse `title`, `datePosted`, `url`, `jobLocation` (defensive
   for list-typed multi-location postings).
6. Apply title-keyword filter, yield matched roles.

### SiteSpec parameterization

Each Polymer-hosted company is a `SiteSpec` with `slug`,
`index_url`, `id_pattern` (regex), `role_url_template`. Adding a
new Polymer site = one tuple entry plus verification that the
regex extracts IDs and the role pages carry JSON-LD JobPosting.

### `role_id` derivation

`role_id` = the numeric upstream ID extracted from the index page.
Server-generated; persists across title rewrites. Same identity
quality as Rippling UUIDs.

### `datePosted` reformatting

Polymer's `datePosted` is non-ISO: `'YYYY-MM-DD HH:MM:SS UTC'`.
The extractor reformats to ISO via `datetime.strptime` +
`isoformat()` before storage so the view's TRY_CAST handles it
cleanly. Unparseable values → `""` → NULL via TRY_CAST.

### Index regex fragility

Same risk class as page-monitor parsers. A parent careers page
re-skin can move role-ID links into JS-rendered content,
silently producing 0 IDs. The
`[polymer:<slug>] index discovered N role(s)` log line is the
operator-visibility signal; Wave 3 cron has no automated alert
for N→0 transitions on index discovery (only on parquet
freshness).

### Index discovery is parent-page only

`jobs.<company>.<tld>` does NOT typically expose a sitemap or
JSON list endpoint (verified for Upstream Tech: `/sitemap.xml`,
`/jobs.json`, `/api/jobs` all 404 / 500). Always derive role IDs
from the parent careers page; do not try to enumerate role IDs
by guessing.

## role_id strategies across source kinds

Different source kinds use different identity strategies. Each is
correct for its source.

| source_kind | site             | role_id derivation                                       | rename-stable? |
|-------------|------------------|----------------------------------------------------------|----------------|
| greenhouse  | onxmaps          | `str(job["id"])` — Greenhouse integer                   | yes            |
| greenhouse  | planetlabs       | `str(job["id"])` — Greenhouse integer                   | yes            |
| greenhouse  | floodbase        | `str(job["id"])` — Greenhouse integer                   | yes            |
| greenhouse  | blastpoint       | `str(job["id"])` — Greenhouse integer                   | yes            |
| greenhouse  | overstory        | `str(job["id"])` — Greenhouse integer                   | yes            |
| ashby       | Mapbox           | `str(job["id"])` — Ashby UUID                           | yes            |
| ashby       | pano-ai          | `str(job["id"])` — Ashby UUID                           | yes            |
| sitemap     | gohunt           | last URL path segment                                   | NO — slug rename creates new role |
| page        | regrid           | trailing UUID of Gusto posting slug                     | yes            |
| page        | felt             | sha1(`slug + ":" + title`)[:16]                         | NO — title rename creates new role |
| page        | wherobots        | trailing path segment of apply URL (URL slug)           | NO — slug rename creates new role |
| rippling    | kalkomey         | `str(job["uuid"])` — Rippling UUID                      | yes            |
| polymer     | upstream-tech    | numeric upstream ID from index page                     | yes            |

Rule for new source kinds: **if the upstream provides a stable
machine-id, use it; otherwise hash a stable content-derived key
and accept that renames break identity continuity.** Document the
choice when adding a new site.

## `posted_at` semantic

`posted_at` carries different upstream semantics by source kind:

| source_kind | site                       | upstream field                                |
|-------------|----------------------------|-----------------------------------------------|
| greenhouse  | (all)                      | `updated_at` ("last modified at source")     |
| ashby       | (all)                      | `publishedAt` (true publication timestamp)   |
| sitemap     | gohunt                     | JSON-LD `datePublished` (fallback `dateModified`) |
| page        | regrid + felt + wherobots  | `""` (no upstream signal exists)             |
| rippling    | kalkomey                   | `""` (Rippling list endpoint exposes none)   |
| polymer     | upstream-tech              | JSON-LD `datePosted` reformatted to ISO inside the extractor (Polymer ships `'YYYY-MM-DD HH:MM:SS UTC'`, not ISO) |

Consumers that want a unified "recency" signal should use the
view-derived `first_seen_at` instead — it is the same shape across
every source kind: when the pipeline first observed the role.

The view's `TRY_CAST(posted_at AS TIMESTAMP)` (added 2026-05-01)
turns empty / unparseable strings into NULL. Extractors that emit
non-ISO formats (Polymer's case) **must** reformat to ISO before
storage so downstream consumers and the view dedup-window order
correctly.

If the upstream-semantic divergence becomes meaningful, split the
column into `posted_at` (true creation when known) and
`last_modified_at` during a future spec pass.

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
- 2026-04-30 — extended after `ticket:xwfvoj4o` (sitemap →
  GoHunt) retrospective. Added: full sitemap-monitor section
  (the pattern, role_id derivation, JSON-LD regex tradeoff,
  sitemap-index escalation). Defensive-checks section extended
  with the sitemap-presence-is-the-signal note.
- 2026-04-30 — extended after `ticket:k0ftbmsi` (page-monitor →
  Regrid + Felt) retrospective and Wave 2 close-out. Added: full
  page-monitor section (per-site parser dispatch, regex
  fragility, MATCH/skip log convention, Felt-as-careers-page
  note); role_id strategies comparison table across all 4 source
  kinds; `posted_at` semantic table replacing the
  Greenhouse-only paragraph.
- 2026-05-02 — extended after `plan:expand-radar` PM5
  retrospective. Added Rippling and Polymer sections (each with
  pattern overview + role_id, posted_at, and identity-fragility
  notes); polite-fetch UA boundary section; defensive
  listed/published per-source-kind table; Vibrant Planet
  deferral note inside page-monitor section. role_id strategies
  table grew from 6 to 13 rows (one per ATS slug); posted_at
  semantic table grew from 4 to 6 rows.
- 2026-05-02 — extended after `plan:partition-r2-layout` PM2
  retrospective. New "R2 layout: hive-partitioned" section
  captures the dlt layout, read flag, type-awareness rules,
  mixed-layout prohibition + in-place migration recipe, and the
  explicit Iceberg / DuckLake / catalog deferral. "What lives
  next to the data" glob updated from `raw/*/*/*.parquet` to
  `raw/*/*/**/*.parquet`. dataset_name table grew to include
  Rippling + Polymer rows.
- 2026-05-02 — extended after `plan:bound-view-window` PM2
  retrospective. Added "How the view bounds scans" subsection:
  view filters partitions to last 30 days at the CTE before
  dedupe runs; bound stays constant as history accumulates;
  fallback path documented for future planner-pushdown
  regressions.
