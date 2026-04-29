# dream-job-radar

Walking-skeleton pipeline that extracts open roles from a public Greenhouse
board (onX), filters to data/engineer/GIS/geospatial titles, writes Parquet
to Cloudflare R2, and exposes a stable `current_open_roles` view in
MotherDuck.

## Run the pipeline

Prerequisites:

- W0 acceptance state: R2 bucket reachable, MotherDuck-side R2 secret in
  place (proven via `scripts/smoke_r2.py` and `scripts/smoke_motherduck.py`).
- `.env` populated with `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`,
  `R2_ACCOUNT_ID`, `R2_BUCKET`, `MOTHERDUCK_TOKEN`.

Extract + load (Greenhouse `onxmaps` → R2 Parquet under
`s3://$R2_BUCKET/raw/greenhouse/onxmaps/`):

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
SELECT count(*) FROM current_open_roles;
SELECT title, location FROM current_open_roles
WHERE source_kind = 'greenhouse' AND ats_slug = 'onxmaps'
LIMIT 10;
```
