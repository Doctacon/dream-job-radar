"""Green Jobs Board public listing extractor."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from html import unescape
from typing import Iterator

import dlt
import requests

BASE_URL = "https://www.greenjobsboard.us"
LISTING_URL = f"{BASE_URL}/jobboard/explore-jobs"
USER_AGENT = "dream-job-radar/0.1"
ATS_SLUG = "jobs"

INCLUDE_PHRASES = (
    "analytics engineer",
    "backend engineer",
    "cloud engineer",
    "data analyst",
    "data architect",
    "data engineer",
    "data scientist",
    "database engineer",
    "devops engineer",
    "gis",
    "geospatial",
    "infrastructure engineer",
    "machine learning",
    "ml engineer",
    "platform engineer",
    "security engineer",
    "site reliability",
    "software developer",
    "software engineer",
    "technical analyst",
)

EXCLUDE_PHRASES = (
    "campaign",
    "communications",
    "coordinator",
    "development associate",
    "development coordinator",
    "director",
    "executive director",
    "field organizer",
    "fundraising",
    "human resources",
    "internship",
    "legal",
    "marketing",
    "operations",
    "policy",
    "program manager",
    "sales",
    "storytelling",
    "technician",
)


def _clean(value: str | None) -> str:
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", value)
    return " ".join(unescape(text).split())


def _match(pattern: str, text: str) -> str:
    found = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
    return _clean(found.group(1)) if found else ""


def _fetch(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


def _title_matches(title: str) -> bool:
    lowered = " ".join(title.lower().split())
    if any(phrase in lowered for phrase in EXCLUDE_PHRASES):
        return False
    return any(phrase in lowered for phrase in INCLUDE_PHRASES)


def _card_blocks(html: str) -> list[str]:
    blocks = re.findall(
        r'<a\b[^>]*href="/jobs/[^"]+"[^>]*class="main-job-card w-inline-block".*?</a>',
        html,
        flags=re.DOTALL,
    )
    return blocks


def _parse_card(block: str) -> dict | None:
    href = _match(r'href="(/jobs/[^"]+)"', block)
    if not href:
        return None
    title = _match(r'<div class="filter-title">(.*?)</div>', block)
    return {
        "role_id": href.rstrip("/").rsplit("/", 1)[-1],
        "url": f"{BASE_URL}{href}",
        "title": title,
        "company": _match(r'<div class="filter-company">(.*?)</div>', block),
        "location": _match(r'<div class="job-meta-tag">(.*?)</div>', block),
        "pathway": _match(r'<div class="filter-industry">(.*?)</div>', block),
        "position_type": _match(r'<div class="filter-job-role">(.*?)</div>', block),
        "experience": _match(r'<div class="filter-experience">(.*?)</div>', block),
        "workplace": _match(r'<div class="filter-onsite-remote">(.*?)</div>', block),
    }


def _property(label: str, html: str) -> str:
    pattern = (
        rf'<div class="job-tag [^"]*"><div class="job-properties-text">{re.escape(label)}</div></div>'
        r'(.*?)</div>'
    )
    section = _match(pattern, html)
    return section


def _parse_detail(card: dict) -> dict:
    html = _fetch(card["url"])
    location_parts = re.findall(
        r'<h[13] class="job-properties-text location-text">(.*?)</h[13]>',
        html,
        flags=re.DOTALL,
    )
    location = ", ".join(_clean(part) for part in location_parts if _clean(part))
    detail = {
        "compensation": _property("Compensation", html),
        "apply_before": _property("Apply Before", html),
        "workplace": _property("Workplace", html) or card.get("workplace", ""),
        "experience": _property("Experience", html) or card.get("experience", ""),
        "apply_url": _match(r'href="(https?://[^"]+)"[^>]*class="btn-primary-1 w-button">Apply Now</a>', html),
        "description": _match(r'<div class="job-description-text w-richtext">(.*?)</div>\s*</div>', html),
    }
    if location:
        detail["location"] = location
    return {**card, **detail}


def _fetch_jobs() -> list[dict]:
    html = _fetch(LISTING_URL)
    cards = [_parse_card(block) for block in _card_blocks(html)]
    parsed = [card for card in cards if card and _title_matches(card.get("title", ""))]
    print(f"[greenjobsboard:{ATS_SLUG}] parsed {len(cards)} card(s); matched {len(parsed)}")
    return [_parse_detail(card) for card in parsed]


def _normalize(job: dict, fetched_at: str) -> dict:
    raw = dict(job)
    return {
        "company": job.get("company", ""),
        "source_kind": "greenjobsboard",
        "ats_slug": ATS_SLUG,
        "role_id": job.get("role_id", ""),
        "title": job.get("title", ""),
        "url": job.get("url", ""),
        "location": job.get("location", ""),
        "posted_at": "",
        "fetched_at": fetched_at,
        "gjb_pathway": job.get("pathway", ""),
        "gjb_workplace": job.get("workplace", ""),
        "gjb_experience": job.get("experience", ""),
        "gjb_position_type": job.get("position_type", ""),
        "gjb_compensation": job.get("compensation", ""),
        "gjb_apply_before": job.get("apply_before", ""),
        "gjb_apply_url": job.get("apply_url", ""),
        "gjb_description": job.get("description", ""),
        "raw_json": json.dumps(raw, sort_keys=True),
    }


@dlt.resource(name=ATS_SLUG, write_disposition="append")
def greenjobsboard_resource() -> Iterator[dict]:
    fetched_at = datetime.now(UTC).isoformat()
    jobs = _fetch_jobs()
    for job in jobs:
        print(
            f"[greenjobsboard:{ATS_SLUG}] MATCH "
            f"{job.get('title')!r} at {job.get('company')!r}"
        )
        yield _normalize(job, fetched_at)
