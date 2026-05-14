"""Tech Jobs for Good public listing extractor.

Parses only public visible listing cards. Premium, locked, and login-only
results are intentionally out of scope.
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

BASE_URL = "https://www.techjobsforgood.com"
JOBS_URL = f"{BASE_URL}/jobs/"
USER_AGENT = "dream-job-radar/0.1"
ATS_SLUG = "jobs"
MAX_PAGES = 3

ALLOWED_JOB_FUNCTIONS = {"Software Engineering", "Data + Analytics"}
ALLOWED_IMPACT_AREAS = {
    "Climate Change",
    "Environment",
    "Clean Energy",
    "Public Infrastructure",
    "Public Service & Civic Engagement",
    "Partners & Advocates",
}

EXCLUDED_TITLE_PATTERNS = re.compile(
    r"(^|[^a-z0-9])(junior|jr\.?|entry[- ]?level|intern|internship|graduate|"
    r"director|executive|vp|vice president|chief)([^a-z0-9]|$)",
    re.IGNORECASE,
)


def _strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    return " ".join(unescape(text).split())


def _match(pattern: str, text: str) -> str:
    found = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
    return _strip_html(found.group(1)) if found else ""


def _listing_url(page: int) -> str:
    params = [
        ("job_function", "Software Engineering"),
        ("job_function", "Data + Analytics"),
        ("location", "Remote (US)"),
        ("sort_by", "date"),
    ]
    if page > 1:
        params.append(("page", str(page)))
    return f"{JOBS_URL}?{urlencode(params)}#q"


def _fetch_page(page: int) -> str:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html"}
    resp = requests.get(_listing_url(page), headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def _card_blocks(html: str) -> list[str]:
    parts = html.split('class="ui raised fluid card job-card"')
    return parts[1:]


def _parse_card(block: str) -> dict | None:
    href = _match(r'href="(/jobs/(\d+)/[^"#]*)', block)
    job_id = _match(r'href="/jobs/(\d+)/', block)
    if not href or not job_id:
        return None

    labels = [
        _strip_html(label)
        for label in re.findall(r'<div class="ui [^"]*label"[^>]*>(.*?)</div>', block, re.DOTALL)
    ]
    job_function = labels[0] if labels else ""
    impact_areas = labels[1:]
    allowed_impacts = [area for area in impact_areas if area in ALLOWED_IMPACT_AREAS]
    if job_function not in ALLOWED_JOB_FUNCTIONS or not allowed_impacts:
        return None

    title = _match(r'class="header job-title"[^>]*title="([^"]+)"', block)
    if EXCLUDED_TITLE_PATTERNS.search(title):
        return None

    return {
        "role_id": job_id,
        "url": f"{BASE_URL}{href}",
        "title": title,
        "company": _match(r'class="meta company-name"[^>]*title="([^"]+)"', block),
        "location": _match(r'<span class="location"[^>]*title="([^"]*)"', block),
        "salary": _match(r'<span class="salary"[^>]*title="([^"]*)"', block),
        "job_function": job_function,
        "impact_areas": impact_areas,
        "company_blurb": _match(r'class="content job-snippet"[^>]*>(.*?)</div>', block),
        "posted_text": _match(r'<span class="date-posted">(.*?)</span>', block),
    }


def _fetch_jobs() -> list[dict]:
    jobs: dict[str, dict] = {}
    for page in range(1, MAX_PAGES + 1):
        html = _fetch_page(page)
        cards = _card_blocks(html)
        print(f"[techjobsforgood:{ATS_SLUG}] page {page} has {len(cards)} card(s)")
        if not cards:
            break
        for block in cards:
            parsed = _parse_card(block)
            if parsed:
                jobs[parsed["role_id"]] = parsed
        if f"page={page + 1}" not in html:
            break
    return list(jobs.values())


def _normalize(job: dict, fetched_at: str) -> dict:
    return {
        "company": job.get("company", ""),
        "source_kind": "techjobsforgood",
        "ats_slug": ATS_SLUG,
        "role_id": str(job["role_id"]),
        "title": job.get("title", ""),
        "url": job.get("url", ""),
        "location": job.get("location", ""),
        "posted_at": "",
        "fetched_at": fetched_at,
        "tjfg_job_function": job.get("job_function", ""),
        "tjfg_impact_areas": json.dumps(job.get("impact_areas") or []),
        "tjfg_company_blurb": job.get("company_blurb", ""),
        "tjfg_salary": job.get("salary", ""),
        "tjfg_posted_text": job.get("posted_text", ""),
        "raw_json": json.dumps(job, sort_keys=True),
    }


@dlt.resource(name=ATS_SLUG, write_disposition="append")
def techjobsforgood_resource() -> Iterator[dict]:
    fetched_at = datetime.now(UTC).isoformat()
    jobs = _fetch_jobs()
    print(f"[techjobsforgood:{ATS_SLUG}] matched {len(jobs)} public visible role(s)")
    for job in jobs:
        print(
            f"[techjobsforgood:{ATS_SLUG}] MATCH "
            f"{job.get('title')!r} at {job.get('company')!r}"
        )
        yield _normalize(job, fetched_at)
