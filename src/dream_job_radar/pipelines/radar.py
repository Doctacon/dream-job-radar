"""Run the dream-job-radar walking-skeleton pipeline.

Loads Greenhouse board roles into Cloudflare R2 as Parquet under
`s3://<bucket>/raw/greenhouse/<slug>/`.

Manual invocation:
    uv run python -m dream_job_radar.pipelines.radar
"""

from __future__ import annotations

import os

import dlt
from dlt.destinations import filesystem
from dotenv import load_dotenv

from dream_job_radar.extractors.greenhouse import DEFAULT_BOARDS, board_resources

PIPELINE_NAME = "dream_job_radar"
SOURCE_KIND = "greenhouse"
# dataset_name doubles as the source_kind path component. dlt's filesystem
# destination always prefixes <dataset_name>/ under bucket_url, so the
# observable layout is raw/<dataset_name>/<table_name>/... and the view
# globs raw/*/*/*.parquet. Wave 2 source kinds run as their own datasets.
DATASET_NAME = SOURCE_KIND


def _r2_destination() -> "filesystem":
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


def run(boards: tuple[str, ...] = DEFAULT_BOARDS) -> None:
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=_r2_destination(),
        dataset_name=DATASET_NAME,
        progress="log",
    )
    info = pipeline.run(board_resources(boards), loader_file_format="parquet")
    print(info)


def main() -> None:
    load_dotenv()
    run()


if __name__ == "__main__":
    main()
