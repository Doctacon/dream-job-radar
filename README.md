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
| `ashby`      | `Mapbox`     | https://api.ashbyhq.com/posting-api/job-board/Mapbox (case-sensitive) |
| `sitemap`    | `gohunt`     | https://www.gohunt.com/sitemap.xml + per-URL JSON-LD scrape           |

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
# Currently invoked via the meta-runner; per-source entry point lands in Wave 3.

# Ashby slice → s3://$R2_BUCKET/raw/ashby/<slug>/
uv run python -m dream_job_radar.pipelines.ashby

# Sitemap-monitor slice → s3://$R2_BUCKET/raw/sitemap/<slug>/
# (0-row outcomes are honest; the resource yields only roles whose
# titles match the v1 keyword filter.)
uv run python -m dream_job_radar.pipelines.sitemap
```

Run all sources sequentially (Greenhouse, then Ashby, then sitemap):

```bash
uv run python -m dream_job_radar.pipelines.radar
```

Materialize the MotherDuck view once (or any time the DDL changes):

```bash
uv run python -c "
import os, duckdb
from dotenv import load_dotenv
load_dotenv()
sql = open('motherduck/views.sql').read().replace('\${R2_BUCKET}', os.environ['R2_BUCKET'])
duckdb.connect(f\"md:?motherduck_token={os.environ['MOTHERDUCK_TOKEN']}\").execute(sql)
print('view materialized')
"
```

Then in MotherDuck:

```sql
SELECT source_kind, ats_slug, count(*) FROM current_open_roles
GROUP BY 1, 2 ORDER BY 1, 2;

SELECT title, location FROM current_open_roles
WHERE source_kind = 'ashby' AND ats_slug = 'Mapbox'
LIMIT 10;
```
