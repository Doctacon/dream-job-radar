"""Run all dream-job-radar slices.

Runs the Greenhouse pipeline followed by every other source kind
(currently Ashby). Each source kind is its own dlt pipeline with
`dataset_name = <source_kind>` so the observable R2 layout is
`raw/<source_kind>/<ats_slug>/...` per `wiki:extractor-shape`.

Per-source entry points (cleaner per-source error isolation when
Wave 3 wires GitHub Actions cron):

    uv run python -m dream_job_radar.pipelines.ashby

Run all sources sequentially:

    uv run python -m dream_job_radar.pipelines.radar
"""

from __future__ import annotations

import dlt
from dotenv import load_dotenv

from dream_job_radar.extractors.greenhouse import (
    DEFAULT_BOARDS as GREENHOUSE_BOARDS,
    board_resources as greenhouse_resources,
)
from dream_job_radar.pipelines import ashby as ashby_pipeline
from dream_job_radar.pipelines._r2 import r2_destination

PIPELINE_NAME = "dream_job_radar"
GREENHOUSE_DATASET = "greenhouse"


def run_greenhouse(boards: tuple[str, ...] = GREENHOUSE_BOARDS) -> None:
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=r2_destination(),
        dataset_name=GREENHOUSE_DATASET,
        progress="log",
    )
    info = pipeline.run(greenhouse_resources(boards), loader_file_format="parquet")
    print(info)


def run_all() -> None:
    print("=" * 72)
    print("[radar] running greenhouse pipeline")
    print("=" * 72)
    run_greenhouse()
    print("=" * 72)
    print("[radar] running ashby pipeline")
    print("=" * 72)
    ashby_pipeline.run()


def main() -> None:
    load_dotenv()
    run_all()


if __name__ == "__main__":
    main()
