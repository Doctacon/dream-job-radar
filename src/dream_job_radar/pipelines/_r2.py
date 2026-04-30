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
        layout="{table_name}/{load_id}.{file_id}.{ext}",
    )
