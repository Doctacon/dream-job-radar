"""Rippling public job-board extractor.

Yields keyword-filtered open roles per board slug. One dlt resource
per slug so the filesystem destination lays files out under
`<bucket>/raw/rippling/<slug>/`.

Rippling's response is a flat JSON list with stable `uuid` per role.
No `posted_at` is exposed at the list endpoint, so the canonical
row stores `posted_at = ""` (the view's TRY_CAST converts to NULL).
There is no `isListed`-equivalent flag — presence in the response
is the published signal (mirrors sitemap-monitor posture).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Iterator

import dlt
import requests

RIPPLING_API = "https://api.rippling.com/platform/api/ats/v1/board/{slug}/jobs"
USER_AGENT = "dream-job-radar/0.1"
TITLE_KEYWORDS = ("data", "engineer", "gis", "geospatial")
DEFAULT_BOARDS: tuple[str, ...] = ("kalkomey",)


def _title_matches(title: str) -> bool:
    lowered = title.lower()
    return any(kw in lowered for kw in TITLE_KEYWORDS)


def _normalize(job: dict, slug: str, fetched_at: str) -> dict:
    work_location = job.get("workLocation") or {}
    location = work_location.get("label") if isinstance(work_location, dict) else None
    return {
        "company": slug,
        "source_kind": "rippling",
        "ats_slug": slug,
        "role_id": str(job["uuid"]),
        "title": job.get("name", ""),
        "url": job.get("url", ""),
        "location": location,
        "posted_at": "",
        "fetched_at": fetched_at,
        "raw_json": json.dumps(job, sort_keys=True),
    }


def _fetch_jobs(slug: str) -> list[dict]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    resp = requests.get(RIPPLING_API.format(slug=slug), headers=headers, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    if not isinstance(payload, list):
        raise ValueError(f"unexpected Rippling payload for {slug}: not a list")
    return payload


def board_resource(slug: str):
    """Return a dlt resource named `<slug>` that yields filtered roles."""

    @dlt.resource(name=slug, write_disposition="append")
    def _resource() -> Iterator[dict]:
        fetched_at = datetime.now(UTC).isoformat()
        jobs = _fetch_jobs(slug)
        print(f"[rippling:{slug}] fetched {len(jobs)} role(s) from board")
        for job in jobs:
            title = job.get("name", "")
            matched = _title_matches(title)
            print(
                f"[rippling:{slug}] {'MATCH' if matched else 'skip '} {title!r}"
            )
            if not matched:
                continue
            yield _normalize(job, slug, fetched_at)

    return _resource


def board_resources(boards: tuple[str, ...] = DEFAULT_BOARDS):
    return [board_resource(slug)() for slug in boards]
