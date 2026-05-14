"""Run all dream-job-radar slices.

Runs the Greenhouse pipeline followed by every other source kind.
Each source kind is its own dlt
pipeline with `dataset_name = <source_kind>` so the observable R2
layout is `raw/<source_kind>/<ats_slug>/...` per
`wiki:extractor-shape`.

Per-source entry points (cleaner per-source error isolation when
Wave 3 wires GitHub Actions cron):

    uv run python -m dream_job_radar.pipelines.greenhouse
    uv run python -m dream_job_radar.pipelines.eightythousandhours
    uv run python -m dream_job_radar.pipelines.gjc
    uv run python -m dream_job_radar.pipelines.greenjobsboard
    uv run python -m dream_job_radar.pipelines.ashby
    uv run python -m dream_job_radar.pipelines.sitemap
    uv run python -m dream_job_radar.pipelines.page
    uv run python -m dream_job_radar.pipelines.rippling
    uv run python -m dream_job_radar.pipelines.polymer
    uv run python -m dream_job_radar.pipelines.remoteok
    uv run python -m dream_job_radar.pipelines.techjobsforgood

Run all sources sequentially:

    uv run python -m dream_job_radar.pipelines.radar
"""

from __future__ import annotations

from dotenv import load_dotenv

from dream_job_radar.pipelines import ashby as ashby_pipeline
from dream_job_radar.pipelines import eightythousandhours as eightythousandhours_pipeline
from dream_job_radar.pipelines import gjc as gjc_pipeline
from dream_job_radar.pipelines import greenjobsboard as greenjobsboard_pipeline
from dream_job_radar.pipelines import greenhouse as greenhouse_pipeline
from dream_job_radar.pipelines import page as page_pipeline
from dream_job_radar.pipelines import polymer as polymer_pipeline
from dream_job_radar.pipelines import remoteok as remoteok_pipeline
from dream_job_radar.pipelines import rippling as rippling_pipeline
from dream_job_radar.pipelines import sitemap as sitemap_pipeline
from dream_job_radar.pipelines import techjobsforgood as techjobsforgood_pipeline


def run_all() -> None:
    print("=" * 72)
    print("[radar] running greenhouse pipeline")
    print("=" * 72)
    greenhouse_pipeline.run()
    print("=" * 72)
    print("[radar] running ashby pipeline")
    print("=" * 72)
    ashby_pipeline.run()
    print("=" * 72)
    print("[radar] running sitemap pipeline")
    print("=" * 72)
    sitemap_pipeline.run()
    print("=" * 72)
    print("[radar] running page pipeline")
    print("=" * 72)
    page_pipeline.run()
    print("=" * 72)
    print("[radar] running rippling pipeline")
    print("=" * 72)
    rippling_pipeline.run()
    print("=" * 72)
    print("[radar] running polymer pipeline")
    print("=" * 72)
    polymer_pipeline.run()
    print("=" * 72)
    print("[radar] running remoteok pipeline")
    print("=" * 72)
    try:
        remoteok_pipeline.run()
    except Exception as exc:
        print(f"[radar] remoteok pipeline failed; continuing: {exc}")
    print("=" * 72)
    print("[radar] running eightythousandhours pipeline")
    print("=" * 72)
    try:
        eightythousandhours_pipeline.run()
    except Exception as exc:
        print(f"[radar] eightythousandhours pipeline failed; continuing: {exc}")
    print("=" * 72)
    print("[radar] running gjc pipeline")
    print("=" * 72)
    try:
        gjc_pipeline.run()
    except Exception as exc:
        print(f"[radar] gjc pipeline failed; continuing: {exc}")
    print("=" * 72)
    print("[radar] running greenjobsboard pipeline")
    print("=" * 72)
    try:
        greenjobsboard_pipeline.run()
    except Exception as exc:
        print(f"[radar] greenjobsboard pipeline failed; continuing: {exc}")
    print("=" * 72)
    print("[radar] running techjobsforgood pipeline")
    print("=" * 72)
    try:
        techjobsforgood_pipeline.run()
    except Exception as exc:
        print(f"[radar] techjobsforgood pipeline failed; continuing: {exc}")


def main() -> None:
    load_dotenv()
    run_all()


if __name__ == "__main__":
    main()
