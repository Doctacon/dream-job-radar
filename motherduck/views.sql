-- current_open_roles: stable shape over R2 raw zone.
-- Globs all source-kind / ATS-slug subdirectories under raw/ so Wave 2
-- extractor kinds plug in without a view rewrite.
--
-- Run once via:
--   uv run python -c "import os, duckdb; from dotenv import load_dotenv; \
--     load_dotenv(); \
--     sql = open('motherduck/views.sql').read().replace('${R2_BUCKET}', os.environ['R2_BUCKET']); \
--     duckdb.connect(f\"md:?motherduck_token={os.environ['MOTHERDUCK_TOKEN']}\").execute(sql)"
--
-- The view assumes a MotherDuck-side R2 secret already exists.

CREATE OR REPLACE VIEW current_open_roles AS
WITH raw AS (
    SELECT
        company,
        source_kind,
        ats_slug,
        role_id,
        title,
        url,
        location,
        posted_at,
        fetched_at
    FROM read_parquet(
        'r2://${R2_BUCKET}/raw/*/*/*.parquet',
        filename = true,
        union_by_name = true
    )
    WHERE filename NOT LIKE '%/_dlt_%'
)
SELECT
    company,
    source_kind,
    ats_slug,
    role_id,
    title,
    url,
    location,
    posted_at,
    fetched_at,
    MIN(fetched_at) OVER (
        PARTITION BY source_kind, ats_slug, role_id
    ) AS first_seen_at,
    MAX(fetched_at) OVER (
        PARTITION BY source_kind, ats_slug, role_id
    ) AS last_seen_at
FROM raw
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY source_kind, ats_slug, role_id
    ORDER BY fetched_at DESC
) = 1;
