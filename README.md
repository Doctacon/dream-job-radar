# dream-job-radar

Pipeline that extracts open roles from a curated set of public job
boards, filters to data/engineering/GIS/geospatial titles, writes
Parquet to Cloudflare R2, and exposes a stable `current_open_roles`
view in MotherDuck.

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
```

Run all sources sequentially (Greenhouse → Ashby → sitemap → page → rippling → polymer):

```bash
uv run python -m dream_job_radar.pipelines.radar
```

Materialize the MotherDuck view (idempotent — `CREATE OR REPLACE`):

```bash
uv run python scripts/apply_views.py
```

Health check (per-(source_kind, ats_slug) freshness; non-zero exit
when a previously-observed slug went stale):

```bash
uv run python scripts/health_check.py
```

Then in MotherDuck:

```sql
SELECT source_kind, ats_slug, count(*) FROM current_open_roles
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
