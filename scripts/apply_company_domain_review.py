"""Apply repo-owned broad-discovery company review seed to MotherDuck.

Manual invocation:
    uv run python scripts/apply_company_domain_review.py
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv

REVIEW_SQL = (
    Path(__file__).resolve().parent.parent
    / "motherduck"
    / "company_domain_review.sql"
)


def main() -> None:
    load_dotenv()
    token = os.environ["MOTHERDUCK_TOKEN"]
    sql = REVIEW_SQL.read_text()

    con = duckdb.connect(f"md:?motherduck_token={token}")
    try:
        con.execute(sql)
    finally:
        con.close()
    print("company domain review seed applied")


if __name__ == "__main__":
    main()
