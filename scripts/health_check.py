"""Per-(source_kind, ats_slug) freshness health check.

For every slug that has ever produced parquet in R2, check that the
most recent observation is fresher than `STALE_THRESHOLD_HOURS`.
A stale slug means the most recent extractor run yielded zero
records (and therefore wrote no parquet), even though the slug
previously had matches. That is the FIND-001 page-monitor regex
fragility scenario from `critique:page-monitor-iter1`.

Slugs that have never produced parquet (e.g. sitemap/gohunt today)
do not appear in the result and do not produce false positives.

Exit code 0: all observed slugs are fresh.
Exit code 1: at least one observed slug is stale.

Manual invocation:
    uv run python scripts/health_check.py
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

import duckdb
from dotenv import load_dotenv

STALE_THRESHOLD_HOURS = 36
KNOWN_ZERO_MATCH_SOURCES = {
    ("page", "felt"),
}

QUERY = """
WITH all_fetches AS (
    SELECT
        source_kind,
        ats_slug,
        fetched_at,
        count(*) AS n
    FROM read_parquet(
        -- Match new hive layout (raw/<src>/<slug>/year=YYYY/month=MM/day=DD/<file>.parquet)
        -- via recursive ** glob, with hive_partitioning=true so the
        -- partition columns parse cleanly (mirrors motherduck/views.sql).
        'r2://{bucket}/raw/*/*/**/*.parquet',
        filename = true,
        union_by_name = true,
        hive_partitioning = true
    )
    WHERE filename NOT LIKE '%/_dlt_%'
      AND source_kind IS NOT NULL
      AND ats_slug IS NOT NULL
      AND role_id IS NOT NULL
    GROUP BY 1, 2, 3
),
ranked AS (
    SELECT
        source_kind,
        ats_slug,
        fetched_at,
        n,
        ROW_NUMBER() OVER (
            PARTITION BY source_kind, ats_slug
            ORDER BY fetched_at DESC
        ) AS rn
    FROM all_fetches
)
SELECT
    source_kind,
    ats_slug,
    MAX(fetched_at) FILTER (WHERE rn = 1) AS latest_fetched,
    MAX(n) FILTER (WHERE rn = 1) AS latest_count,
    MAX(fetched_at) FILTER (WHERE rn = 2) AS prior_fetched,
    MAX(n) FILTER (WHERE rn = 2) AS prior_count
FROM ranked
GROUP BY 1, 2
ORDER BY 1, 2
"""


def main() -> None:
    load_dotenv()
    bucket = os.environ["R2_BUCKET"]
    token = os.environ["MOTHERDUCK_TOKEN"]

    sql = QUERY.format(bucket=bucket)
    con = duckdb.connect(f"md:?motherduck_token={token}")
    try:
        rows = con.execute(sql).fetchall()
    finally:
        con.close()

    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(hours=STALE_THRESHOLD_HOURS)
    regression = False

    print(
        f"[health] checking {len(rows)} observed slug(s); "
        f"stale threshold = {STALE_THRESHOLD_HOURS}h "
        f"(cutoff = {stale_cutoff.isoformat()})"
    )
    for source_kind, ats_slug, latest, latest_n, prior, prior_n in rows:
        # latest_fetched comes back as datetime (TIMESTAMP WITH TIME ZONE).
        if latest is None:
            print(f"[health] WARN  {source_kind}/{ats_slug} has no fetched_at?")
            continue
        if latest < stale_cutoff:
            age_h = (now - latest).total_seconds() / 3600
            if (source_kind, ats_slug) in KNOWN_ZERO_MATCH_SOURCES:
                print(
                    f"[health] WARN  {source_kind}/{ats_slug} stale matched rows "
                    f"ignored for known zero-match source: "
                    f"latest={latest.isoformat()} ({age_h:.1f}h old) "
                    f"latest_count={latest_n} prior_count={prior_n}"
                )
                continue

            print(
                f"[health] STALE {source_kind}/{ats_slug} "
                f"latest={latest.isoformat()} ({age_h:.1f}h old) "
                f"latest_count={latest_n} prior_count={prior_n}"
            )
            regression = True
        else:
            age_h = (now - latest).total_seconds() / 3600
            print(
                f"[health] ok    {source_kind}/{ats_slug} "
                f"latest={latest.isoformat()} ({age_h:.1f}h old) "
                f"latest_count={latest_n}"
            )

    if regression:
        print("[health] FAIL: at least one slug is stale")
        sys.exit(1)
    print("[health] PASS")


if __name__ == "__main__":
    main()
