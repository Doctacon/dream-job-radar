"""Prove MotherDuck reads the R2 placeholder via the R2 secret.

Acceptance criterion 4. Run after smoke_r2.py has uploaded the placeholder.

Pre-req: in MotherDuck (UI or SQL), create an R2 secret:
    CREATE SECRET IN MOTHERDUCK (
        TYPE R2,
        KEY_ID '<R2_ACCESS_KEY_ID>',
        SECRET '<R2_SECRET_ACCESS_KEY>',
        ACCOUNT_ID '<R2_ACCOUNT_ID>'
    );
"""

import os

import duckdb
from dotenv import load_dotenv

load_dotenv()

BUCKET = os.environ["R2_BUCKET"]
TOKEN = os.environ["MOTHERDUCK_TOKEN"]
PLACEHOLDER_URI = f"r2://{BUCKET}/smoke/placeholder.parquet"


def main() -> None:
    con = duckdb.connect(f"md:?motherduck_token={TOKEN}")
    rows = con.execute(
        f"SELECT id, note FROM read_parquet('{PLACEHOLDER_URI}')"
    ).fetchall()
    print(f"OK read {PLACEHOLDER_URI}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
