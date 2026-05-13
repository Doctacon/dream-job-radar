"""Run the Tech Jobs for Good discovery slice of dream-job-radar.

Loads public visible mission-fit jobs into Cloudflare R2 as Parquet
under `s3://<bucket>/raw/techjobsforgood/jobs/`.

Manual invocation:
    uv run python -m dream_job_radar.pipelines.techjobsforgood
"""

from __future__ import annotations

import dlt
from dotenv import load_dotenv

from dream_job_radar.extractors.techjobsforgood import techjobsforgood_resource
from dream_job_radar.pipelines._r2 import r2_destination

PIPELINE_NAME = "dream_job_radar"
SOURCE_KIND = "techjobsforgood"
DATASET_NAME = SOURCE_KIND


def run() -> None:
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=r2_destination(),
        dataset_name=DATASET_NAME,
        progress="log",
    )
    info = pipeline.run(techjobsforgood_resource(), loader_file_format="parquet")
    print(info)


def main() -> None:
    load_dotenv()
    run()


if __name__ == "__main__":
    main()
