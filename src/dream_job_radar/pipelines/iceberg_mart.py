"""Daily Iceberg mart writer for current_open_roles.

Snapshots `current_open_roles` once per day into the Iceberg
table `mart.job_postings_daily_snapshot` on R2 Data Catalog,
then refreshes a same-named MotherDuck table from the freshly
resolved Iceberg metadata pointer so Dive panels read native
MotherDuck.

Idempotent on same-day rerun: skips append if rows for
`current_date` already exist in the Iceberg table.

Run:
    uv run python -m dream_job_radar.pipelines.iceberg_mart
"""

from __future__ import annotations

import os

import duckdb
from dotenv import load_dotenv
from pyiceberg.exceptions import NoSuchTableError

from dream_job_radar.pipelines._iceberg import iceberg_catalog

NAMESPACE = "mart"
TABLE = "job_postings_daily_snapshot"
FQN = f"{NAMESPACE}.{TABLE}"

# Hardcoded projection: matches motherduck/views.sql current_open_roles
# body. Fail-closed on view drift (a new column will not silently
# extend the Iceberg schema; a removed column will raise here).
SNAPSHOT_SQL = """
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
    last_seen_at,
    current_date AS snapshot_date
FROM current_open_roles
"""


def run() -> None:
    load_dotenv()

    cat = iceberg_catalog()
    md = duckdb.connect(f"md:?motherduck_token={os.environ['MOTHERDUCK_TOKEN']}")
    md.execute("INSTALL iceberg; LOAD iceberg;")
    md.execute("SET unsafe_enable_version_guessing = true;")
    # PyIceberg only accepts arrow timestamp tz=UTC. Pin the session
    # so TIMESTAMPTZ columns surface as tz=UTC instead of local.
    md.execute("SET TimeZone = 'UTC';")

    arrow = md.execute(SNAPSHOT_SQL).to_arrow_table()
    print(f"[iceberg_mart] snapshot rows: {arrow.num_rows}")

    if (NAMESPACE,) not in cat.list_namespaces():
        cat.create_namespace(NAMESPACE)
        print(f"[iceberg_mart] created namespace {NAMESPACE}")

    try:
        tbl = cat.load_table(FQN)
        print(f"[iceberg_mart] loaded existing {FQN}")
    except NoSuchTableError:
        tbl = cat.create_table(FQN, schema=arrow.schema)
        print(f"[iceberg_mart] created table {FQN}")

    today_count = md.execute(
        f"SELECT count(*) FROM iceberg_scan('{tbl.metadata_location}') "
        "WHERE snapshot_date = current_date"
    ).fetchone()[0]

    if today_count > 0:
        print(
            f"[iceberg_mart] skip append: {today_count} rows already "
            "snapshotted today"
        )
    else:
        tbl.append(arrow)
        tbl.refresh()
        snap = tbl.current_snapshot()
        print(
            f"[iceberg_mart] appended {arrow.num_rows} rows "
            f"snapshot_id={snap.snapshot_id if snap else 'NA'}"
        )

    md.execute("CREATE SCHEMA IF NOT EXISTS mart;")
    md.execute(
        f"CREATE OR REPLACE TABLE {FQN} AS "
        f"SELECT * FROM iceberg_scan('{tbl.metadata_location}')"
    )
    print(f"[iceberg_mart] refreshed materialization {FQN}")


if __name__ == "__main__":
    run()
