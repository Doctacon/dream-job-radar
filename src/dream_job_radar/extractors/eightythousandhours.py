"""80,000 Hours public Algolia job-board extractor.

Uses only the public browser search endpoint and stores minimal metadata.
Full job descriptions are intentionally out of scope.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from html import unescape
from typing import Iterator
from urllib.parse import urlencode

import dlt
import requests

ALGOLIA_APP_ID = "W6KM1UDIB3"
ALGOLIA_SEARCH_KEY = "d1d7f2c8696e7b36837d5ed337c4a319"
ALGOLIA_INDEX = "jobs_prod_super_ranked"
ALGOLIA_URL = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{ALGOLIA_INDEX}/query"
USER_AGENT = "dream-job-radar/0.1"
ATS_SLUG = "jobs"
HITS_PER_PAGE = 200
MAX_PAGES = 5

ATTRIBUTES_TO_RETRIEVE = (
    "objectID",
    "post_pk",
    "title",
    "company_name",
    "company_id",
    "url_external",
    "card_locations",
    "tags_location_80k",
    "tags_location_type",
    "tags_country",
    "tags_city",
    "tags_area",
    "tags_role_type",
    "tags_skill",
    "tags_generic",
    "salary",
    "posted_at",
    "closes_at",
    "description_short",
)

INCLUDE_PHRASES = (
    "ai engineer",
    "analytics engineer",
    "backend engineer",
    "cloud engineer",
    "data analyst",
    "data architect",
    "data engineer",
    "data scientist",
    "database engineer",
    "devops engineer",
    "engineering manager",
    "frontend engineer",
    "geospatial",
    "infrastructure engineer",
    "machine learning engineer",
    "ml engineer",
    "platform engineer",
    "research engineer",
    "security engineer",
    "site reliability",
    "software architect",
    "software developer",
    "software engineer",
    "technical analyst",
    "technical architect",
)

EXCLUDE_PHRASES = (
    "account executive",
    "campaign",
    "biologist",
    "communications",
    "coordinator",
    "customer success",
    "customer support",
    "director",
    "executive director",
    "externship",
    "funding",
    "fundraising",
    "graduate",
    "head of",
    "human resources",
    "intern",
    "junior",
    "legal",
    "marketing",
    "operations",
    "policy",
    "program manager",
    "sales",
    "strategist",
    "support engineer",
    "technical support",
    "volunteer",
    "vice president",
    "vp ",
)


def _clean(value: object) -> str:
    if value is None:
        return ""
    text = re.sub(r"<[^>]+>", " ", str(value))
    return " ".join(unescape(text).split())


def _list(value: object) -> list[str]:
    if isinstance(value, list):
        return [_clean(item) for item in value if _clean(item)]
    cleaned = _clean(value)
    return [cleaned] if cleaned else []


def _title_matches(title: str) -> bool:
    lowered = " ".join(title.lower().split())
    if any(phrase in lowered for phrase in EXCLUDE_PHRASES):
        return False
    if re.search(r"(^|[^a-z0-9])gis([^a-z0-9]|$)", lowered):
        return True
    return any(phrase in lowered for phrase in INCLUDE_PHRASES)


def _timestamp(value: object) -> str:
    if value in (None, ""):
        return ""
    try:
        return datetime.fromtimestamp(int(value), UTC).isoformat()
    except (TypeError, ValueError, OSError):
        return str(value)


def _location(job: dict) -> str:
    for key in ("card_locations", "tags_location_80k", "tags_city", "tags_country"):
        values = _list(job.get(key))
        if values:
            return ", ".join(values)
    return ""


def _minimal_raw(job: dict) -> dict:
    return {
        "objectID": job.get("objectID"),
        "post_pk": job.get("post_pk"),
        "title": job.get("title"),
        "company_name": job.get("company_name"),
        "company_id": job.get("company_id"),
        "url_external": job.get("url_external"),
        "card_locations": _list(job.get("card_locations")),
        "tags_location_80k": _list(job.get("tags_location_80k")),
        "tags_location_type": _list(job.get("tags_location_type")),
        "tags_country": _list(job.get("tags_country")),
        "tags_city": _list(job.get("tags_city")),
        "tags_area": _list(job.get("tags_area")),
        "tags_role_type": _list(job.get("tags_role_type")),
        "tags_skill": _list(job.get("tags_skill")),
        "tags_generic": _list(job.get("tags_generic")),
        "salary": job.get("salary"),
        "posted_at": job.get("posted_at"),
        "closes_at": job.get("closes_at"),
        "description_short": _clean(job.get("description_short")),
    }


def _normalize(job: dict, fetched_at: str) -> dict:
    raw = _minimal_raw(job)
    role_id = job.get("post_pk") or job.get("objectID")
    return {
        "company": _clean(job.get("company_name")),
        "source_kind": "eightythousandhours",
        "ats_slug": ATS_SLUG,
        "role_id": str(role_id),
        "title": _clean(job.get("title")),
        "url": _clean(job.get("url_external")),
        "location": _location(job),
        "posted_at": _timestamp(job.get("posted_at")),
        "fetched_at": fetched_at,
        "eighty_k_company_id": str(job.get("company_id") or ""),
        "eighty_k_salary": _clean(job.get("salary")),
        "eighty_k_closes_at": _timestamp(job.get("closes_at")),
        "eighty_k_tags_area": json.dumps(raw["tags_area"], sort_keys=True),
        "eighty_k_tags_skill": json.dumps(raw["tags_skill"], sort_keys=True),
        "eighty_k_tags_role_type": json.dumps(raw["tags_role_type"], sort_keys=True),
        "eighty_k_description_short": raw["description_short"],
        "raw_json": json.dumps(raw, sort_keys=True),
    }


def _fetch_page(page: int) -> dict:
    params = urlencode(
        [
            ("query", ""),
            ("page", str(page)),
            ("hitsPerPage", str(HITS_PER_PAGE)),
            ("attributesToRetrieve", ",".join(ATTRIBUTES_TO_RETRIEVE)),
        ]
    )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "X-Algolia-API-Key": ALGOLIA_SEARCH_KEY,
        "X-Algolia-Application-Id": ALGOLIA_APP_ID,
    }
    resp = requests.post(ALGOLIA_URL, headers=headers, json={"params": params}, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("hits"), list):
        raise ValueError("unexpected 80,000 Hours Algolia payload")
    return payload


def _fetch_jobs() -> list[dict]:
    jobs: dict[str, dict] = {}
    for page in range(MAX_PAGES):
        payload = _fetch_page(page)
        hits = [hit for hit in payload["hits"] if isinstance(hit, dict)]
        print(
            f"[eightythousandhours:{ATS_SLUG}] page {page + 1} "
            f"has {len(hits)} hit(s) of {payload.get('nbHits', '?')}"
        )
        for hit in hits:
            role_id = str(hit.get("post_pk") or hit.get("objectID") or "")
            if role_id:
                jobs[role_id] = hit
        if len(hits) < HITS_PER_PAGE:
            break
    return list(jobs.values())


@dlt.resource(name=ATS_SLUG, write_disposition="append")
def eightythousandhours_resource() -> Iterator[dict]:
    fetched_at = datetime.now(UTC).isoformat()
    jobs = _fetch_jobs()
    matched = 0
    skipped = 0
    for job in jobs:
        title = _clean(job.get("title"))
        if not _title_matches(title):
            skipped += 1
            continue
        matched += 1
        print(
            f"[eightythousandhours:{ATS_SLUG}] MATCH "
            f"{title!r} at {_clean(job.get('company_name'))!r}"
        )
        yield _normalize(job, fetched_at)
    print(f"[eightythousandhours:{ATS_SLUG}] matched {matched}; skipped {skipped}")
