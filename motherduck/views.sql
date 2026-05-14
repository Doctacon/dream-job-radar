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
-- displays require location relevance and, for broad-discovery sources,
-- company/domain relevance.
CREATE OR REPLACE VIEW relevant_open_roles AS
WITH broad_context AS (
    SELECT
        source_kind,
        ats_slug,
        role_id,
        lower(concat_ws(
            ' ',
            coalesce(json_extract_string(raw_json, '$.description'), ''),
            coalesce(CAST(json_extract(raw_json, '$.tags') AS VARCHAR), ''),
            coalesce(json_extract_string(raw_json, '$.company_blurb'), ''),
            coalesce(CAST(json_extract(raw_json, '$.impact_areas') AS VARCHAR), ''),
            coalesce(json_extract_string(raw_json, '$.job_function'), ''),
            coalesce(json_extract_string(raw_json, '$.pathway'), ''),
            coalesce(json_extract_string(raw_json, '$.position_type'), ''),
            coalesce(json_extract_string(raw_json, '$.workplace'), '')
        )) AS source_domain_text_lc
    FROM read_parquet(
        'r2://${R2_BUCKET}/raw/*/*/**/*.parquet',
        filename = true,
        union_by_name = true,
        hive_partitioning = true
    )
    WHERE filename NOT LIKE '%/_dlt_%'
      AND source_kind IN ('remoteok', 'techjobsforgood', 'gjc', 'greenjobsboard')
      AND ats_slug IS NOT NULL
      AND role_id IS NOT NULL
      AND make_date(year, CAST(month AS INTEGER), CAST(day AS INTEGER))
          >= current_date - INTERVAL 30 DAY
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY source_kind, ats_slug, role_id
        ORDER BY fetched_at DESC
    ) = 1
),
classified AS (
    SELECT
        c.*,
        lower(coalesce(c.location, '')) AS location_lc,
        r.decision AS company_domain_decision,
        lower(concat_ws(
            ' ',
            coalesce(c.company, ''),
            coalesce(c.title, ''),
            coalesce(b.source_domain_text_lc, '')
        )) AS domain_text_lc
    FROM current_open_roles c
    LEFT JOIN broad_context b
      ON c.source_kind = b.source_kind
     AND c.ats_slug = b.ats_slug
     AND c.role_id = b.role_id
    LEFT JOIN company_domain_review r
      ON c.source_kind = r.source_kind
     AND lower(c.company) = lower(r.company)
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
        (
            -- Remote is eligible by default, but explicit non-US/non-worldwide
            -- remote regions stay out unless the same string also names US or
            -- worldwide/global eligibility.
            location_lc LIKE '%remote%'
            AND (
                location_lc LIKE '%united states%'
                OR regexp_matches(location_lc, '(^|[^a-z0-9])u\.?s\.?([^a-z0-9]|$)')
                OR regexp_matches(location_lc, '(^|[^a-z0-9])u\.?s\.?a\.?([^a-z0-9]|$)')
                OR location_lc LIKE '%worldwide%'
                OR location_lc LIKE '%global%'
                OR NOT (
                    location_lc LIKE '%canada%'
                    OR location_lc LIKE '%ontario%'
                    OR location_lc LIKE '%british columbia%'
                    OR regexp_matches(location_lc, '(^|[^a-z0-9])uk([^a-z0-9]|$)')
                    OR location_lc LIKE '%united kingdom%'
                    OR location_lc LIKE '%europe%'
                    OR location_lc LIKE '%emea%'
                    OR location_lc LIKE '%apac%'
                    OR location_lc LIKE '%asia%'
                    OR location_lc LIKE '%australia%'
                    OR location_lc LIKE '%austria%'
                    OR location_lc LIKE '%belgium%'
                    OR location_lc LIKE '%germany%'
                    OR location_lc LIKE '%slovenia%'
                    OR location_lc LIKE '%france%'
                    OR location_lc LIKE '%netherlands%'
                    OR location_lc LIKE '%denmark%'
                    OR location_lc LIKE '%estonia%'
                    OR location_lc LIKE '%ireland%'
                    OR location_lc LIKE '%portugal%'
                    OR location_lc LIKE '%sweden%'
                    OR location_lc LIKE '%switzerland%'
                    OR location_lc LIKE '%india%'
                    OR location_lc LIKE '%mexico%'
                    OR location_lc LIKE '%brazil%'
                    OR location_lc LIKE '%latin america%'
                )
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
        )
    )
    AND (
        -- Curated company-board sources are already operator-approved.
        source_kind NOT IN ('remoteok', 'techjobsforgood', 'gjc', 'greenjobsboard')
        OR company_domain_decision = 'approved'
        OR (
            company_domain_decision IS NULL
            AND (
                domain_text_lc LIKE '%outdoor%'
                OR domain_text_lc LIKE '%recreation%'
                OR domain_text_lc LIKE '%geospatial%'
                OR domain_text_lc LIKE '% gis %'
                OR domain_text_lc LIKE '% map%'
                OR domain_text_lc LIKE '%mapping%'
                OR domain_text_lc LIKE '%climate%'
                OR domain_text_lc LIKE '%environment%'
                OR domain_text_lc LIKE '%conservation%'
                OR domain_text_lc LIKE '%earth observation%'
                OR domain_text_lc LIKE '%satellite%'
                OR domain_text_lc LIKE '%remote sensing%'
                OR domain_text_lc LIKE '%wildfire%'
                OR domain_text_lc LIKE '%public infrastructure%'
                OR domain_text_lc LIKE '%civic%'
                OR domain_text_lc LIKE '%democracy%'
                OR domain_text_lc LIKE '%voter%'
                OR domain_text_lc LIKE '%public benefit%'
                OR domain_text_lc LIKE '%transit%'
                OR domain_text_lc LIKE '%mobility%'
            )
            AND NOT (
                domain_text_lc LIKE '%healthcare%'
                OR domain_text_lc LIKE '%biotech%'
                OR domain_text_lc LIKE '%genetic%'
                OR domain_text_lc LIKE '%insurance%'
                OR domain_text_lc LIKE '%mortgage%'
                OR domain_text_lc LIKE '%fintech%'
                OR domain_text_lc LIKE '%payment%'
                OR domain_text_lc LIKE '%sales%'
                OR domain_text_lc LIKE '%marketing%'
                OR domain_text_lc LIKE '%customer success%'
                OR domain_text_lc LIKE '%recruiting%'
            )
        )
    );
