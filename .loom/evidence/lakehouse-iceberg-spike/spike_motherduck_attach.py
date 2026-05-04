"""Phase 0 spike: MotherDuck attach R2 Data Catalog.

Critical unknown: MotherDuck Iceberg docs list REST catalog reads as
"limited to S3, S3 Tables, GCS". This probes whether attaching the
R2 Data Catalog REST endpoint actually works.

Run: `uv run python .loom/evidence/lakehouse-iceberg-spike/spike_motherduck_attach.py`
"""

from __future__ import annotations

import os
import duckdb
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
BUCKET = os.environ["R2_BUCKET"]
TOKEN = os.environ["R2_TOKEN_VALUE"]
MD_TOKEN = os.environ["MOTHERDUCK_TOKEN"]

WAREHOUSE = f"{ACCOUNT_ID}_{BUCKET}"
URI = f"https://catalog.cloudflarestorage.com/{ACCOUNT_ID}/{BUCKET}"


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
    print(f"[probe] warehouse={WAREHOUSE}")
    print(f"[probe] uri={URI}")

    conn = duckdb.connect(f"md:?motherduck_token={MD_TOKEN}")
    print(f"[probe] connected to MotherDuck")

    print(f"[probe] duckdb={duckdb.__version__}")
    print(conn.execute("SELECT version()").fetchone())

    step("install + load iceberg extension", lambda: conn.execute(
        "INSTALL iceberg; LOAD iceberg;"
    ))

    step("enable version guessing", lambda: conn.execute(
        "SET unsafe_enable_version_guessing = true;"
    ))

    step("create r2 s3 secret for data files", lambda: conn.execute(
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

    step("drop existing secret if any", lambda: conn.execute(
        "DROP SECRET IF EXISTS r2_iceberg_secret;"
    ))

    step("create iceberg secret", lambda: conn.execute(
        f"""
        CREATE SECRET r2_iceberg_secret (
            TYPE ICEBERG,
            TOKEN '{TOKEN}'
        );
        """
    ))

    step("detach existing if any", lambda: conn.execute(
        "DETACH DATABASE IF EXISTS r2_lake;"
    ))

    step("attach R2 catalog", lambda: conn.execute(
        f"""
        ATTACH '{WAREHOUSE}' AS r2_lake (
            TYPE iceberg,
            SECRET r2_iceberg_secret,
            ENDPOINT '{URI}'
        );
        """
    ))

    step("show databases", lambda: print(
        conn.execute("SHOW DATABASES;").fetchall()
    ))

    step("show schemas in r2_lake", lambda: print(
        conn.execute(
            "SELECT schema_name FROM information_schema.schemata "
            "WHERE catalog_name='r2_lake';"
        ).fetchall()
    ))

    step("list tables in r2_lake.spike", lambda: print(
        conn.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_catalog='r2_lake';"
        ).fetchall()
    ))

    step("SELECT * FROM r2_lake.spike.trivial", lambda:
        conn.execute("SELECT * FROM r2_lake.spike.trivial ORDER BY id;").fetchall()
    )

    step("count rows", lambda:
        conn.execute("SELECT count(*) FROM r2_lake.spike.trivial;").fetchone()
    )


if __name__ == "__main__":
    main()
