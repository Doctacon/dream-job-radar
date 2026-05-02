"""Run the Polymer slice of dream-job-radar.

Loads roles from Polymer-hosted job boards (parent careers index +
per-role JSON-LD on a custom `jobs.<company>.<tld>` subdomain) into
Cloudflare R2 as Parquet under `s3://<bucket>/raw/polymer/<slug>/`.

Manual invocation:
    uv run python -m dream_job_radar.pipelines.polymer
"""

from __future__ import annotations

import dlt
from dotenv import load_dotenv

from dream_job_radar.extractors.polymer import DEFAULT_SITES, SiteSpec, site_resources
from dream_job_radar.pipelines._r2 import r2_destination

PIPELINE_NAME = "dream_job_radar"
SOURCE_KIND = "polymer"
DATASET_NAME = SOURCE_KIND


def run(specs: tuple[SiteSpec, ...] = DEFAULT_SITES) -> None:
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=r2_destination(),
        dataset_name=DATASET_NAME,
        progress="log",
    )
    info = pipeline.run(site_resources(specs), loader_file_format="parquet")
    print(info)


def main() -> None:
    load_dotenv()
    run()


if __name__ == "__main__":
    main()
