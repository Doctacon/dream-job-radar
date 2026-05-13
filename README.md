# dream-job-radar

Pipeline that extracts open roles from a curated set of public job
boards, filters to data/engineering/GIS/geospatial titles, writes
Parquet to Cloudflare R2, and exposes stable MotherDuck views for full
inventory and personally relevant roles.

Source kinds and ATS slugs covered today:

| source_kind  | slug         | upstream                                                              |
|--------------|--------------|-----------------------------------------------------------------------|
| `greenhouse` | `onxmaps`    | https://boards-api.greenhouse.io/v1/boards/onxmaps/jobs               |
| `greenhouse` | `planetlabs` | https://boards-api.greenhouse.io/v1/boards/planetlabs/jobs            |
| `greenhouse` | `floodbase`  | https://boards-api.greenhouse.io/v1/boards/floodbase/jobs             |
| `greenhouse` | `blastpoint` | https://boards-api.greenhouse.io/v1/boards/blastpoint/jobs            |
| `greenhouse` | `overstory`  | https://boards-api.greenhouse.io/v1/boards/overstory/jobs             |
| `ashby`      | `Mapbox`     | https://api.ashbyhq.com/posting-api/job-board/Mapbox (case-sensitive) |
| `ashby`      | `pano-ai`    | https://api.ashbyhq.com/posting-api/job-board/pano-ai (case-sensitive)|
| `sitemap`    | `gohunt`     | https://www.gohunt.com/sitemap.xml + per-URL JSON-LD scrape           |
| `page`       | `regrid`     | https://jobs.gusto.com/boards/regrid-... (Gusto-hosted board)         |
| `page`       | `felt`       | https://felt.com/careers (Webflow page; apply via mailto)             |
| `page`       | `wherobots`  | https://wherobots.com/careers/ (WordPress; `<li class="job-item">`)   |
| `rippling`   | `kalkomey`   | https://api.rippling.com/platform/api/ats/v1/board/kalkomey/jobs      |
| `polymer`    | `upstream-tech` | https://www.upstream.tech/careers (index) → https://jobs.upstream.tech/{id} (per-role JSON-LD) |
| `remoteok`   | `remoteok`   | https://remoteok.com/api (broad discovery, company-domain gated)         |

## Run the pipeline

Prerequisites:

- W0 acceptance state: R2 bucket reachable, MotherDuck-side R2 secret
  in place (proven via `scripts/smoke_r2.py` and
  `scripts/smoke_motherduck.py`).
- `.env` populated with `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`,
  `R2_ACCOUNT_ID`, `R2_BUCKET`, `MOTHERDUCK_TOKEN`.

Run a single source kind:

```bash
# Greenhouse slice (onx + planetlabs) → s3://$R2_BUCKET/raw/greenhouse/<slug>/
uv run python -m dream_job_radar.pipelines.greenhouse

# Ashby slice → s3://$R2_BUCKET/raw/ashby/<slug>/
uv run python -m dream_job_radar.pipelines.ashby

# Sitemap-monitor slice → s3://$R2_BUCKET/raw/sitemap/<slug>/
# (0-row outcomes are honest; the resource yields only roles whose
# titles match the v1 keyword filter.)
uv run python -m dream_job_radar.pipelines.sitemap

# Page-monitor slice → s3://$R2_BUCKET/raw/page/<slug>/
# Per-site HTML parsing for sources without an API.
uv run python -m dream_job_radar.pipelines.page

# Rippling slice → s3://$R2_BUCKET/raw/rippling/<slug>/
# Public Rippling job-board API (flat JSON list).
uv run python -m dream_job_radar.pipelines.rippling

# Polymer slice → s3://$R2_BUCKET/raw/polymer/<slug>/
# Parent careers page enumerates role IDs; per-role JSON-LD on
# jobs.<company>.<tld> subdomain.
uv run python -m dream_job_radar.pipelines.polymer

# RemoteOK discovery slice → s3://$R2_BUCKET/raw/remoteok/remoteok/
# Public RemoteOK API; strict technical title/seniority filter before raw write.
# User-facing visibility is gated by company-domain review/rules in relevant_open_roles.
uv run python -m dream_job_radar.pipelines.remoteok
```

Run all sources sequentially (Greenhouse → Ashby → sitemap → page → rippling → polymer → RemoteOK locally):

```bash
uv run python -m dream_job_radar.pipelines.radar
```

Materialize the MotherDuck view (idempotent — `CREATE OR REPLACE`):

```bash
uv run python scripts/apply_company_domain_review.py
uv run python scripts/apply_views.py
```

Broad-discovery company review decisions live in
`motherduck/company_domain_review.sql`. Update that SQL seed for manual
`approved`, `rejected`, or `pending` company decisions, then re-run the seed and
view scripts above.

Health check (per-(source_kind, ats_slug) freshness; non-zero exit
when a previously-observed slug went stale):

```bash
uv run python scripts/health_check.py
```

## Dream Job Radar Dive

The public Dive is a relevance-first radar over
`"acorn-granary"."main"."relevant_open_roles"`.

- `current_open_roles` remains the full matching open-role inventory for recovery,
  debugging, and snapshot history.
- `relevant_open_roles` is the normal user-facing surface. It includes explicit
  remote US/worldwide roles and explicit Arizona-local roles, and excludes vague
  remote, non-US remote, and non-Arizona onsite/hybrid roles.
- Broad-discovery sources such as RemoteOK must also pass company/domain review
  or deterministic mission-fit rules before they appear in `relevant_open_roles`.
  Unknown, pending, or rejected broad-discovery companies remain available in
  `current_open_roles` for review/debugging but are hidden from the Dive.
- Primary KPIs count current relevant open roles, companies, and locations.
- Daily snapshot history comes from
  `"acorn-granary"."mart"."job_postings_daily_snapshot"` and tracks the full
  current matching open-role inventory once per UTC day.
- The recent lens is separate: it counts and lists roles whose `posted_at`, or
  fallback `first_seen_at`, is within the last 7 days and pass the relevance view.

Do not describe the whole Dive as "last 7 days" unless the query is scoped to the
recent lens. Also do not describe `current_open_roles` as personalized; it is full
inventory, while `relevant_open_roles` is the location-relevant surface.

Then in MotherDuck:

```sql
SELECT source_kind, ats_slug, count(*) FROM current_open_roles
GROUP BY 1, 2 ORDER BY 1, 2;

SELECT source_kind, ats_slug, count(*) FROM relevant_open_roles
GROUP BY 1, 2 ORDER BY 1, 2;

SELECT title, location FROM current_open_roles
WHERE source_kind = 'ashby' AND ats_slug = 'Mapbox'
LIMIT 10;
```

## Scheduled refresh

`.github/workflows/refresh.yml` runs the pipeline on cron:

- **schedule:** daily at `0 12 * * *` (12:00 UTC = 5am Pacific /
  8am Eastern)
- **manual:** `gh workflow run refresh.yml` or the GitHub UI's
  "Run workflow" button

Workflow shape:

1. Checkout, install `uv`, `uv sync`.
2. Run each source kind in its own step with
   `continue-on-error: true` (one source failing does not block
   others).
3. `scripts/apply_views.py` runs with `if: always()` so the view
   DDL is reapplied even if a source step failed.
4. `scripts/health_check.py` runs as a required step. Failure
   here fails the workflow and triggers GitHub's email-on-failure.

The five required secrets (`R2_ACCESS_KEY_ID`,
`R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`, `R2_BUCKET`,
`MOTHERDUCK_TOKEN`) are configured at the repo level per Wave 0
acceptance.

`concurrency: { group: refresh, cancel-in-progress: false }` keeps
two runs from racing on `_dlt_pipeline_state` writes.
