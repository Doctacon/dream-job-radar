"""Shared R2 filesystem destination factory.

The R2 destination configuration is identical across source kinds —
only `dataset_name` differs, and dataset_name lives on the pipeline,
not on the destination.
"""

from __future__ import annotations

import os

from dlt.destinations import filesystem


def r2_destination():
    bucket = os.environ["R2_BUCKET"]
    account_id = os.environ["R2_ACCOUNT_ID"]
    endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
    return filesystem(
        bucket_url=f"s3://{bucket}/raw",
        credentials={
            "aws_access_key_id": os.environ["R2_ACCESS_KEY_ID"],
            "aws_secret_access_key": os.environ["R2_SECRET_ACCESS_KEY"],
            "endpoint_url": endpoint,
            "region_name": "auto",
        },
        # Hive-partitioned layout per initiative:partition-r2-layout.
        # dlt resolves YYYY/MM/DD from the load-package timestamp.
        # DuckDB read_parquet with hive_partitioning=true exposes
        # year (INT) / month (VARCHAR, zero-padded) / day (VARCHAR,
        # zero-padded) as queryable columns for date-bound queries.
        layout="{table_name}/year={YYYY}/month={MM}/day={DD}/{load_id}.{file_id}.{ext}",
    )
