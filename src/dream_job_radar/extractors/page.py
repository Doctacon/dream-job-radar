"""Page-monitor extractor.

For sources that publish open roles directly on a careers / job-board
HTML page with a stable structure but no API. Two parser strategies
in v1:

- `gusto_board`: server-rendered Gusto job-board page
  (used by Regrid).
- `felt_careers`: Felt's hand-maintained Webflow careers page.

The pattern generalizes by adding a new parser strategy plus a
SiteSpec entry. Each new strategy must produce role dicts with at
least `title`, `role_id`, and `url`.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from typing import Iterator, NamedTuple

import dlt
import requests

USER_AGENT = "dream-job-radar/0.1"
TITLE_KEYWORDS = ("data", "engineer", "gis", "geospatial")

GUSTO_HOST = "https://jobs.gusto.com"
GUSTO_ROW_RE = re.compile(
    r'<a class="block hover:bg-gray-50" href="(/postings/[^"]+)".*?'
    r'<h3 class="text-lg">([^<]+)</h3>',
    re.DOTALL,
)
GUSTO_UUID_TAIL_RE = re.compile(
    r"-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$"
)
FELT_ROW_RE = re.compile(r'<div class="h4 careers">([^<]+)</div>')


class SiteSpec(NamedTuple):
    slug: str
    url: str
    parser_kind: str


DEFAULT_SITES: tuple[SiteSpec, ...] = (
    SiteSpec(
        slug="regrid",
        url=(
            "https://jobs.gusto.com/boards/"
            "regrid-map-your-future-c265c805-0902-4628-bd27-d013fdcfb5bc"
        ),
        parser_kind="gusto_board",
    ),
    SiteSpec(
        slug="felt",
        url="https://felt.com/careers",
        parser_kind="felt_careers",
    ),
)


def _title_matches(title: str) -> bool:
    lowered = title.lower()
    return any(kw in lowered for kw in TITLE_KEYWORDS)


def _fetch_page(url: str) -> str:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def _parse_gusto_board(html: str, spec: SiteSpec) -> list[dict]:
    out: list[dict] = []
    for posting_path, raw_title in GUSTO_ROW_RE.findall(html):
        title = raw_title.strip()
        slug_segment = posting_path.rsplit("/", 1)[-1]
        m = GUSTO_UUID_TAIL_RE.search(slug_segment)
        role_id = m.group(1) if m else slug_segment
        out.append(
            {
                "title": title,
                "role_id": role_id,
                "url": GUSTO_HOST + posting_path,
                "_posting_slug": slug_segment,
            }
        )
    return out


def _parse_felt_careers(html: str, spec: SiteSpec) -> list[dict]:
    out: list[dict] = []
    for raw_title in FELT_ROW_RE.findall(html):
        title = raw_title.strip()
        digest = hashlib.sha1(
            f"{spec.slug}:{title}".encode("utf-8")
        ).hexdigest()[:16]
        out.append(
            {
                "title": title,
                "role_id": digest,
                "url": spec.url,
            }
        )
    return out


def _parse(spec: SiteSpec, html: str) -> list[dict]:
    if spec.parser_kind == "gusto_board":
        return _parse_gusto_board(html, spec)
    if spec.parser_kind == "felt_careers":
        return _parse_felt_careers(html, spec)
    raise ValueError(f"unknown parser_kind: {spec.parser_kind!r}")


def _normalize(role: dict, spec: SiteSpec, fetched_at: str) -> dict:
    return {
        "company": spec.slug,
        "source_kind": "page",
        "ats_slug": spec.slug,
        "role_id": role["role_id"],
        "title": role["title"],
        "url": role["url"],
        "location": None,
        "posted_at": "",
        "fetched_at": fetched_at,
        "raw_json": json.dumps(role, sort_keys=True),
    }


def site_resource(spec: SiteSpec):
    """Return a dlt resource named `<slug>` that yields filtered roles."""

    @dlt.resource(name=spec.slug, write_disposition="append")
    def _resource() -> Iterator[dict]:
        fetched_at = datetime.now(UTC).isoformat()
        html = _fetch_page(spec.url)
        roles = _parse(spec, html)
        print(f"[page:{spec.slug}] parsed {len(roles)} role(s) from page")
        for role in roles:
            matched = _title_matches(role["title"])
            print(
                f"[page:{spec.slug}] {'MATCH' if matched else 'skip '} "
                f"{role['title']!r}"
            )
            if not matched:
                continue
            yield _normalize(role, spec, fetched_at)

    return _resource


def site_resources(specs: tuple[SiteSpec, ...] = DEFAULT_SITES):
    return [site_resource(spec)() for spec in specs]
