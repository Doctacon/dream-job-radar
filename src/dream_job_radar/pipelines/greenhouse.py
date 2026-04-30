"""Run the Greenhouse slice of dream-job-radar.

Loads Greenhouse board roles into Cloudflare R2 as Parquet under
`s3://<bucket>/raw/greenhouse/<slug>/`.

Manual invocation:
    uv run python -m dream_job_radar.pipelines.greenhouse
"""

from __future__ import annotations

import dlt
from dotenv import load_dotenv

from dream_job_radar.extractors.greenhouse import (
    DEFAULT_BOARDS,
    board_resources,
)
from dream_job_radar.pipelines._r2 import r2_destination

PIPELINE_NAME = "dream_job_radar"
SOURCE_KIND = "greenhouse"
DATASET_NAME = SOURCE_KIND


def run(boards: tuple[str, ...] = DEFAULT_BOARDS) -> None:
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=r2_destination(),
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
