"""Greenhouse public board extractor.

Yields keyword-filtered open roles per board slug. One dlt resource per slug
so the filesystem destination lays files out under
`<bucket>/raw/greenhouse/<slug>/`.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Iterator

import dlt
import requests

GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
USER_AGENT = "dream-job-radar/0.1"
TITLE_KEYWORDS = ("data", "engineer", "gis", "geospatial")
DEFAULT_BOARDS = ("onxmaps", "planetlabs")


def _title_matches(title: str) -> bool:
    lowered = title.lower()
    return any(kw in lowered for kw in TITLE_KEYWORDS)


def _normalize(job: dict, slug: str, fetched_at: str) -> dict:
    location = (job.get("location") or {}).get("name")
    departments = [d.get("name") for d in (job.get("departments") or []) if d.get("name")]
    return {
        "company": slug,
        "source_kind": "greenhouse",
        "ats_slug": slug,
        "role_id": str(job["id"]),
        "title": job.get("title", ""),
        "url": job.get("absolute_url", ""),
        "location": location,
        "departments": departments,
        "posted_at": job.get("updated_at", ""),
        "fetched_at": fetched_at,
        "raw_json": json.dumps(job, sort_keys=True),
    }


def _fetch_jobs(slug: str) -> list[dict]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    resp = requests.get(GREENHOUSE_API.format(slug=slug), headers=headers, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    jobs = payload.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError(f"unexpected Greenhouse payload for {slug}: missing 'jobs' list")
    return jobs


def board_resource(slug: str):
    """Return a dlt resource named `<slug>` that yields filtered roles."""

    @dlt.resource(name=slug, write_disposition="append")
    def _resource() -> Iterator[dict]:
        fetched_at = datetime.now(UTC).isoformat()
        for job in _fetch_jobs(slug):
            if not _title_matches(job.get("title", "")):
                continue
            yield _normalize(job, slug, fetched_at)

    return _resource


def board_resources(boards: tuple[str, ...] = DEFAULT_BOARDS):
    return [board_resource(slug)() for slug in boards]
