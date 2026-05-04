"""Phase 0 spike diagnostic: local DuckDB read of R2 Iceberg table.

Isolates whether the MotherDuck SIGSEGV is MotherDuck-specific or
also reproduces in a local DuckDB process. Tries both:
  (a) full ATTACH against R2 Data Catalog REST endpoint
  (b) direct iceberg_scan against the metadata path
"""

from __future__ import annotations

import os
import duckdb
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
BUCKET = os.environ["R2_BUCKET"]
TOKEN = os.environ["R2_TOKEN_VALUE"]

WAREHOUSE = f"{ACCOUNT_ID}_{BUCKET}"
URI = f"https://catalog.cloudflarestorage.com/{ACCOUNT_ID}/{BUCKET}"
METADATA = (
    f"s3://{BUCKET}/__r2_data_catalog/"
    "019df0ea-14be-7080-885c-7d01165fec42/"
    "019df0ea-174e-7921-8878-4ac7334bcece/metadata/"
    "00002-019df0ea-75ba-7f63-b04a-1a88438388fc.gz.metadata.json"
)


def step(label: str, fn):
    import sys
    print(f"\n[step] {label}", flush=True)
    try:
        result = fn()
        print(f"[step] OK -> {result!r}", flush=True)
        return result
    except BaseException as e:
        print(f"[step] FAIL: {type(e).__name__}: {e}", flush=True)
        sys.stdout.flush()
        return e


def main() -> None:
    conn = duckdb.connect()
    print(f"[probe] duckdb={duckdb.__version__}")

    step("install + load iceberg + httpfs", lambda: conn.execute(
        "INSTALL iceberg; LOAD iceberg; INSTALL httpfs; LOAD httpfs;"
    ))

    step("install + load aws", lambda: conn.execute(
        "INSTALL aws; LOAD aws;"
    ))

    step("set version guessing", lambda: conn.execute(
        "SET unsafe_enable_version_guessing = true;"
    ))

    step("create r2 s3 secret", lambda: conn.execute(
        f"""
        CREATE OR REPLACE SECRET r2_s3_secret (
            TYPE S3,
            KEY_ID '{os.environ["R2_ACCESS_KEY_ID"]}',
            SECRET '{os.environ["R2_SECRET_ACCESS_KEY"]}',
            ENDPOINT '{ACCOUNT_ID}.r2.cloudflarestorage.com',
            REGION 'auto',
            URL_STYLE 'path',
            SCOPE 's3://{BUCKET}'
        );
        """
    ))

    step("create iceberg rest secret", lambda: conn.execute(
        f"""
        CREATE OR REPLACE SECRET r2_iceberg_secret (
            TYPE ICEBERG,
            TOKEN '{TOKEN}'
        );
        """
    ))

    step("attach R2 catalog (local duckdb)", lambda: conn.execute(
        f"""
        ATTACH '{WAREHOUSE}' AS r2_lake (
            TYPE iceberg,
            SECRET r2_iceberg_secret,
            ENDPOINT '{URI}'
        );
        """
    ))

    step("SELECT via attached", lambda:
        conn.execute("SELECT * FROM r2_lake.spike.trivial ORDER BY id;").fetchall()
    )

    step("iceberg_scan direct metadata", lambda:
        conn.execute(f"SELECT * FROM iceberg_scan('{METADATA}');").fetchall()
    )


if __name__ == "__main__":
    main()
