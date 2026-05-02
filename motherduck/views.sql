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
        -- posted_at is heterogeneous across source kinds:
        --   greenhouse / ashby / sitemap → ISO timestamp string parsed as
        --     TIMESTAMP WITH TIME ZONE in their native parquet
        --   page → empty string (page-monitor sources have no upstream
        --     posting date)
        -- union_by_name across these widens the column to VARCHAR. Cast
        -- back to TIMESTAMP WITH TIME ZONE here so consumers (Dive,
        -- ad-hoc SQL) can use strftime / extract directly. Empty strings
        -- become NULL; honest evidence that page-monitor rows lack a
        -- posted_at signal.
        TRY_CAST(posted_at AS TIMESTAMP WITH TIME ZONE) AS posted_at,
        fetched_at
    FROM read_parquet(
        -- Recursive ** glob spans both old flat layout
        -- (raw/<source_kind>/<ats_slug>/<file>.parquet) and the
        -- new hive-partitioned layout
        -- (raw/<source_kind>/<ats_slug>/year=YYYY/month=MM/day=DD/<file>.parquet).
        -- hive_partitioning=true exposes year/month/day as queryable
        -- columns when present in the path (NULL for old flat files).
        'r2://${R2_BUCKET}/raw/*/*/**/*.parquet',
        filename = true,
        union_by_name = true,
        hive_partitioning = true
    )
    WHERE filename NOT LIKE '%/_dlt_%'
      AND source_kind IS NOT NULL
      AND ats_slug IS NOT NULL
      AND role_id IS NOT NULL
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
