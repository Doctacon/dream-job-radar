"""Polymer-style extractor.

Hybrid pattern:
- Index page (parent careers URL) enumerates per-role IDs in HTML.
- Per-role page on a custom `jobs.<company>.<tld>` subdomain
  carries a JSON-LD `<script type="application/ld+json">` block
  with `@type="JobPosting"` (Schema.org).

Yields keyword-filtered open roles per site spec. One dlt resource
per slug so the filesystem destination lays files out under
`<bucket>/raw/polymer/<slug>/`.

Polymer's `datePosted` field uses a non-ISO format
(`YYYY-MM-DD HH:MM:SS UTC`); the extractor reformats to ISO before
storage so the canonical view's `TRY_CAST(posted_at AS TIMESTAMP)`
handles it.
"""

from __future__ import annotations

import json
import re
import time
from datetime import UTC, datetime
from typing import Iterator, NamedTuple

import dlt
import requests

USER_AGENT = "dream-job-radar/0.1"
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
)
TITLE_KEYWORDS = ("data", "engineer", "gis", "geospatial")
PAGE_FETCH_DELAY_S = 0.5

JSONLD_BLOCK_RE = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)
ISO_HINT_RE = re.compile(r"\d{4}-\d{2}-\d{2}T")
POLYMER_DATE_FMT = "%Y-%m-%d %H:%M:%S UTC"


class SiteSpec(NamedTuple):
    slug: str
    index_url: str
    id_pattern: str
    role_url_template: str


DEFAULT_SITES: tuple[SiteSpec, ...] = (
    SiteSpec(
        slug="upstream-tech",
        index_url="https://www.upstream.tech/careers",
        id_pattern=r"jobs\.upstream\.tech/(\d+)",
        role_url_template="https://jobs.upstream.tech/{id}",
    ),
)


def _title_matches(title: str) -> bool:
    lowered = title.lower()
    return any(kw in lowered for kw in TITLE_KEYWORDS)


def _get(url: str, *, accept: str) -> requests.Response:
    """GET with polite UA; fall back to browser UA on 403/503."""
    headers = {"User-Agent": USER_AGENT, "Accept": accept}
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code in (403, 503):
        headers["User-Agent"] = BROWSER_USER_AGENT
        resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp


def _fetch_index_ids(spec: SiteSpec) -> list[str]:
    resp = _get(spec.index_url, accept="text/html")
    pattern = re.compile(spec.id_pattern)
    seen: set[str] = set()
    out: list[str] = []
    for m in pattern.finditer(resp.text):
        rid = m.group(1)
        if rid in seen:
            continue
        seen.add(rid)
        out.append(rid)
    return out


def _extract_jobposting_jsonld(html: str) -> dict | None:
    for match in JSONLD_BLOCK_RE.finditer(html):
        try:
            data = json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        type_ = data.get("@type")
        if type_ == "JobPosting" or (
            isinstance(type_, list) and "JobPosting" in type_
        ):
            return data
    return None


def _parse_date_posted(s: str) -> str:
    if not s:
        return ""
    if ISO_HINT_RE.search(s):
        return s
    try:
        dt = datetime.strptime(s, POLYMER_DATE_FMT).replace(tzinfo=UTC)
        return dt.isoformat()
    except ValueError:
        return ""


def _extract_location(jobposting: dict) -> str | None:
    raw = jobposting.get("jobLocation")
    if not raw:
        return None
    candidates = raw if isinstance(raw, list) else [raw]
    for entry in candidates:
        if not isinstance(entry, dict):
            continue
        address = entry.get("address") or {}
        if not isinstance(address, dict):
            continue
        parts = [
            address.get("addressLocality"),
            address.get("addressRegion"),
            address.get("addressCountry"),
        ]
        joined = ", ".join(p for p in parts if p)
        if joined:
            return joined
    return None


def _normalize(jobposting: dict, role_id: str, spec: SiteSpec, fetched_at: str) -> dict:
    canonical_url = jobposting.get("url") or spec.role_url_template.format(id=role_id)
    return {
        "company": spec.slug,
        "source_kind": "polymer",
        "ats_slug": spec.slug,
        "role_id": role_id,
        "title": jobposting.get("title", ""),
        "url": canonical_url,
        "location": _extract_location(jobposting),
        "posted_at": _parse_date_posted(jobposting.get("datePosted", "")),
        "fetched_at": fetched_at,
        "raw_json": json.dumps(jobposting, sort_keys=True, default=str),
    }


def site_resource(spec: SiteSpec):
    """Return a dlt resource named `<slug>` that yields filtered roles."""

    @dlt.resource(name=spec.slug, write_disposition="append")
    def _resource() -> Iterator[dict]:
        fetched_at = datetime.now(UTC).isoformat()
        ids = _fetch_index_ids(spec)
        print(f"[polymer:{spec.slug}] index discovered {len(ids)} role(s)")
        for i, role_id in enumerate(ids):
            if i > 0:
                time.sleep(PAGE_FETCH_DELAY_S)
            role_url = spec.role_url_template.format(id=role_id)
            try:
                resp = _get(role_url, accept="text/html")
            except requests.HTTPError as e:
                print(f"[polymer:{spec.slug}] HTTP error at {role_url}: {e}; skip")
                continue
            jobposting = _extract_jobposting_jsonld(resp.text)
            if jobposting is None:
                print(f"[polymer:{spec.slug}] no JobPosting at {role_url}; skip")
                continue
            title = jobposting.get("title", "")
            matched = _title_matches(title)
            print(
                f"[polymer:{spec.slug}] {'MATCH' if matched else 'skip '} {title!r}"
            )
            if not matched:
                continue
            yield _normalize(jobposting, role_id, spec, fetched_at)

    return _resource


def site_resources(specs: tuple[SiteSpec, ...] = DEFAULT_SITES):
    return [site_resource(spec)() for spec in specs]
