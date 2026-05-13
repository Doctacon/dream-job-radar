"""RemoteOK public job-board extractor.

Yields strictly filtered technical roles from RemoteOK. RemoteOK is a
broad discovery source, so filtering is intentionally narrower than
curated company boards before rows enter raw inventory.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Iterator

import dlt
import requests

REMOTEOK_API = "https://remoteok.com/api"
USER_AGENT = "dream-job-radar/0.1"
ATS_SLUG = "remoteok"

INCLUDE_PHRASES = (
    "analytics engineer",
    "ai engineer",
    "backend engineer",
    "cloud engineer",
    "cloud enablement engineer",
    "data analyst",
    "data architect",
    "data engineer",
    "data scientist",
    "database engineer",
    "devops engineer",
    "engineering manager",
    "frontend engineer",
    "gis",
    "geospatial",
    "infrastructure architect",
    "infrastructure engineer",
    "machine learning engineer",
    "ml engineer",
    "platform engineer",
    "platform engineering",
    "principal engineer",
    "reliability engineer",
    "security engineer",
    "site reliability",
    "software architect",
    "software developer",
    "software development engineer",
    "software engineer",
    "staff engineer",
    "technical architect",
)

EXCLUDE_PHRASES = (
    "account executive",
    "assistant",
    "attorney",
    "content",
    "copywriter",
    "customer success",
    "customer support",
    "developer advocate",
    "director",
    "executive",
    "founder",
    "freelance writer",
    "head of",
    "intern",
    "junior",
    "marketing",
    "office",
    "operations",
    "president",
    "recruiter",
    "sales",
    "seo",
    "support advisor",
    "support engineer",
    "support specialist",
    "technical support",
    "vice president",
    "vp ",
    "writer",
)


def _title_matches(title: str) -> bool:
    lowered = " ".join(title.lower().split())
    if any(phrase in lowered for phrase in EXCLUDE_PHRASES):
        return False
    return any(phrase in lowered for phrase in INCLUDE_PHRASES)


def _posted_at(job: dict) -> str:
    for key in ("date", "epoch", "publication_date"):
        value = job.get(key)
        if value:
            return str(value)
    return ""


def _normalize(job: dict, fetched_at: str) -> dict:
    return {
        "company": job.get("company", ""),
        "source_kind": "remoteok",
        "ats_slug": ATS_SLUG,
        "role_id": str(job["id"]),
        "title": job.get("position", ""),
        "url": job.get("url", ""),
        "location": job.get("location", ""),
        "posted_at": _posted_at(job),
        "fetched_at": fetched_at,
        "raw_json": json.dumps(job, sort_keys=True),
    }


def _fetch_jobs() -> list[dict]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    resp = requests.get(REMOTEOK_API, headers=headers, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    if not isinstance(payload, list):
        raise ValueError("unexpected RemoteOK payload: not a list")
    return [job for job in payload if isinstance(job, dict) and "position" in job]


@dlt.resource(name=ATS_SLUG, write_disposition="append")
def remoteok_resource() -> Iterator[dict]:
    fetched_at = datetime.now(UTC).isoformat()
    jobs = _fetch_jobs()
    matched = 0
    skipped = 0
    print(f"[remoteok:{ATS_SLUG}] fetched {len(jobs)} role(s)")
    for job in jobs:
        title = job.get("position", "")
        if not _title_matches(title):
            skipped += 1
            print(f"[remoteok:{ATS_SLUG}] skip  {title!r}")
            continue
        matched += 1
        print(f"[remoteok:{ATS_SLUG}] MATCH {title!r}")
        yield _normalize(job, fetched_at)
    print(f"[remoteok:{ATS_SLUG}] matched {matched}; skipped {skipped}")
