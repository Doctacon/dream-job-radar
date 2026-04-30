"""Run the sitemap-monitor slice of dream-job-radar.

Loads sitemap-derived roles into Cloudflare R2 as Parquet under
`s3://<bucket>/raw/sitemap/<slug>/`. A 0-row outcome is acceptable —
the canonical view returns an honest empty count for the source kind.

Manual invocation:
    uv run python -m dream_job_radar.pipelines.sitemap
"""

from __future__ import annotations

import dlt
from dotenv import load_dotenv

from dream_job_radar.extractors.sitemap import DEFAULT_SITES, SiteSpec, site_resources
from dream_job_radar.pipelines._r2 import r2_destination

PIPELINE_NAME = "dream_job_radar"
SOURCE_KIND = "sitemap"
DATASET_NAME = SOURCE_KIND


def run(sites: tuple[SiteSpec, ...] = DEFAULT_SITES) -> None:
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=r2_destination(),
        dataset_name=DATASET_NAME,
        progress="log",
    )
    info = pipeline.run(site_resources(sites), loader_file_format="parquet")
    print(info)


def main() -> None:
    load_dotenv()
    run()


if __name__ == "__main__":
    main()
