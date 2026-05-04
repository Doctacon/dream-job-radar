"""Apply motherduck/bootstrap_iceberg.sql once against MotherDuck.

Creates / refreshes the persistent S3 secret MotherDuck-server-side
needs to read R2 Iceberg parquet + manifest files. Idempotent;
re-run whenever the R2 access key rotates.

Manual invocation:
    uv run python scripts/bootstrap_motherduck_iceberg.py
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv

BOOTSTRAP_SQL = (
    Path(__file__).resolve().parent.parent / "motherduck" / "bootstrap_iceberg.sql"
)


def main() -> None:
    load_dotenv()
    sql = BOOTSTRAP_SQL.read_text().format(
        KEY=os.environ["R2_ACCESS_KEY_ID"],
        SECRET=os.environ["R2_SECRET_ACCESS_KEY"],
        ACCOUNT_ID=os.environ["R2_ACCOUNT_ID"],
        BUCKET=os.environ["R2_BUCKET"],
    )

    con = duckdb.connect(f"md:?motherduck_token={os.environ['MOTHERDUCK_TOKEN']}")
    try:
        con.execute(sql)
        rows = con.execute(
            "SELECT name, type, scope, persistent FROM duckdb_secrets() "
            "WHERE name = 'r2_pipelines_s3';"
        ).fetchall()
    finally:
        con.close()
    print(f"bootstrapped: {rows}")


if __name__ == "__main__":
    main()
