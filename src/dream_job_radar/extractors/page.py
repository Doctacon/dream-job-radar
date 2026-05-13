"""Page-monitor extractor.

For sources that publish open roles directly on a careers / job-board
HTML page with a stable structure but no API. Parser strategies:

- `gusto_board`: server-rendered Gusto job-board page
  (kept for Gusto boards; Regrid is currently inactive because its board returns
  403 to the scheduled runner).
- `felt_careers`: Felt's hand-maintained Webflow careers page.
- `wherobots_careers`: Wherobots WordPress careers page with
  `<li class="job-item">` blocks.

The pattern generalizes by adding a new parser strategy plus a
SiteSpec entry. Each new strategy must produce role dicts with at
least `title`, `role_id`, and `url`.

Vibrant Planet (`vibrantplanet.net/about/team-and-careers`) is
intentionally absent from `DEFAULT_SITES`. Their careers page
today shows the literal placeholder "No open roles at the moment.
Check back soon!" — there is no role-list HTML to parse against.
Add a `vibrant_planet_careers` parser only after they post roles
and the populated HTML structure is observable.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import UTC, datetime
from typing import Iterator, NamedTuple
from urllib.parse import urlsplit

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
WHEROBOTS_ITEM_RE = re.compile(
    r'<li[^>]*class="[^"]*job-item[^"]*"[^>]*>'
    r'(?P<block>.*?)'
    r'</li>',
    re.DOTALL,
)
WHEROBOTS_TITLE_RE = re.compile(
    r'<div[^>]*class="[^"]*job-item__position[^"]*"[^>]*>(.+?)</div>',
    re.DOTALL,
)
WHEROBOTS_APPLY_HREF_RE = re.compile(
    r'<a[^>]*href="(https?://[^"]+)"[^>]*class="[^"]*job-item__apply[^"]*"',
)
WHEROBOTS_LOCATION_RE = re.compile(
    r'<div[^>]*class="[^"]*job-item__location[^"]*"[^>]*>(.+?)</div>',
    re.DOTALL,
)


class SiteSpec(NamedTuple):
    slug: str
    url: str
    parser_kind: str


DEFAULT_SITES: tuple[SiteSpec, ...] = (
    SiteSpec(
        slug="felt",
        url="https://felt.com/careers",
        parser_kind="felt_careers",
    ),
    SiteSpec(
        slug="wherobots",
        url="https://wherobots.com/careers/",
        parser_kind="wherobots_careers",
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


def _parse_wherobots_careers(page_html: str, spec: SiteSpec) -> list[dict]:
    out: list[dict] = []
    for m in WHEROBOTS_ITEM_RE.finditer(page_html):
        block = m.group("block")
        title_m = WHEROBOTS_TITLE_RE.search(block)
        href_m = WHEROBOTS_APPLY_HREF_RE.search(block)
        if not title_m or not href_m:
            continue
        title = html.unescape(re.sub(r"<[^>]+>", "", title_m.group(1))).strip()
        url = href_m.group(1).strip()
        loc_m = WHEROBOTS_LOCATION_RE.search(block)
        location = (
            html.unescape(re.sub(r"<[^>]+>", "", loc_m.group(1))).strip()
            if loc_m
            else None
        )
        path = urlsplit(url).path.rstrip("/")
        slug_segment = path.rsplit("/", 1)[-1] if path else ""
        role_id = slug_segment or url
        out.append(
            {
                "title": title,
                "role_id": role_id,
                "url": url,
                "location": location,
            }
        )
    return out


def _parse(spec: SiteSpec, page_html: str) -> list[dict]:
    if spec.parser_kind == "gusto_board":
        return _parse_gusto_board(page_html, spec)
    if spec.parser_kind == "felt_careers":
        return _parse_felt_careers(page_html, spec)
    if spec.parser_kind == "wherobots_careers":
        return _parse_wherobots_careers(page_html, spec)
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
        try:
            html = _fetch_page(spec.url)
            roles = _parse(spec, html)
        except (requests.RequestException, ValueError) as exc:
            print(f"[page:{spec.slug}] fetch/parse failed; skip site: {exc}")
            return

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
