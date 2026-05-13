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
      -- Bound the scan to the last 30 days of partitions
      -- (initiative:bound-view-window). Hive partition columns
      -- arrive as year=INT, month/day=zero-padded VARCHAR.
      -- DuckDB's planner prunes parquet outside this window, so
      -- the dedupe window function below operates on a bounded
      -- input regardless of how many years of history live in R2.
      -- 30 days is a generous superset of the cron's 36h
      -- staleness check; the Dive layers a tighter 7-day filter
      -- on top of the view output.
      AND make_date(year, CAST(month AS INTEGER), CAST(day AS INTEGER))
          >= current_date - INTERVAL 30 DAY
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

-- relevant_open_roles: personalized high-precision role surface.
-- Keeps current_open_roles as full inventory while normal user-facing
-- displays can hide roles outside the operator's location constraints.
CREATE OR REPLACE VIEW relevant_open_roles AS
WITH classified AS (
    SELECT
        *,
        lower(coalesce(location, '')) AS location_lc
    FROM current_open_roles
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
    first_seen_at,
    last_seen_at
FROM classified
WHERE
    (
        -- Explicit remote US/worldwide only. Vague "Remote" stays out.
        location_lc LIKE '%remote%'
        AND (
            location_lc LIKE '%united states%'
            OR regexp_matches(location_lc, '(^|[^a-z0-9])u\.?s\.?([^a-z0-9]|$)')
            OR regexp_matches(location_lc, '(^|[^a-z0-9])u\.?s\.?a\.?([^a-z0-9]|$)')
            OR location_lc LIKE '%worldwide%'
            OR location_lc LIKE '%global%'
        )
    )
    OR (
        -- Explicit Arizona-local roles.
        location_lc LIKE '%arizona%'
        OR regexp_matches(location_lc, '(^|[^a-z0-9])az([^a-z0-9]|$)')
        OR location_lc LIKE '%phoenix%'
        OR location_lc LIKE '%tucson%'
        OR location_lc LIKE '%tempe%'
        OR location_lc LIKE '%scottsdale%'
        OR location_lc LIKE '%mesa%'
        OR location_lc LIKE '%chandler%'
        OR location_lc LIKE '%gilbert%'
        OR location_lc LIKE '%glendale%'
        OR location_lc LIKE '%peoria%'
        OR location_lc LIKE '%flagstaff%'
    );
