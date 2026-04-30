"""Materialize MotherDuck views from motherduck/views.sql.

Idempotent (DDL uses CREATE OR REPLACE). Safe to re-run on every
scheduled refresh. Replaces the brittle README one-liner.

Manual invocation:
    uv run python scripts/apply_views.py
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv

VIEWS_SQL = Path(__file__).resolve().parent.parent / "motherduck" / "views.sql"


def main() -> None:
    load_dotenv()
    bucket = os.environ["R2_BUCKET"]
    token = os.environ["MOTHERDUCK_TOKEN"]

    sql = VIEWS_SQL.read_text().replace("${R2_BUCKET}", bucket)

    con = duckdb.connect(f"md:?motherduck_token={token}")
    try:
        con.execute(sql)
    finally:
        con.close()
    print("view materialized")


if __name__ == "__main__":
    main()
