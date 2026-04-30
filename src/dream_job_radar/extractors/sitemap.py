"""Sitemap-monitor extractor.

For sources without an ATS, we walk a public sitemap, filter URLs by
substring, fetch each role page, and extract role metadata from the
page's JSON-LD `Article` block.

GoHunt is the v1 use case. The pattern generalizes to any host that
publishes role posts as CMS articles with JSON-LD.
"""

from __future__ import annotations

import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from typing import Iterator, NamedTuple
from urllib.parse import urlsplit

import dlt
import requests

USER_AGENT = "dream-job-radar/0.1"
TITLE_KEYWORDS = ("data", "engineer", "gis", "geospatial")
PAGE_FETCH_DELAY_S = 0.5

JSONLD_BLOCK_RE = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)
NAMESPACE_RE = re.compile(r"^\{[^}]+\}")


class SiteSpec(NamedTuple):
    slug: str
    sitemap_url: str
    url_substring: str


DEFAULT_SITES: tuple[SiteSpec, ...] = (
    SiteSpec(
        slug="gohunt",
        sitemap_url="https://www.gohunt.com/sitemap.xml",
        url_substring="job-opportunity",
    ),
)


def _title_matches(title: str) -> bool:
    lowered = title.lower()
    return any(kw in lowered for kw in TITLE_KEYWORDS)


def _strip_ns(tag: str) -> str:
    return NAMESPACE_RE.sub("", tag)


def _fetch_sitemap_urls(sitemap_url: str, url_substring: str) -> list[str]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/xml"}
    resp = requests.get(sitemap_url, headers=headers, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    if _strip_ns(root.tag) == "sitemapindex":
        raise ValueError(
            f"sitemap at {sitemap_url} is a sitemapindex; v1 does not recurse"
        )
    needle = url_substring.lower()
    out: list[str] = []
    for elem in root.iter():
        if _strip_ns(elem.tag) == "loc" and elem.text:
            url = elem.text.strip()
            if needle in url.lower():
                out.append(url)
    return out


def _extract_jsonld_article(html: str) -> dict | None:
    for match in JSONLD_BLOCK_RE.finditer(html):
        try:
            data = json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            continue
        type_ = data.get("@type") if isinstance(data, dict) else None
        if type_ == "Article" or (isinstance(type_, list) and "Article" in type_):
            return data
    return None


def _fetch_role_page(url: str) -> dict | None:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return _extract_jsonld_article(resp.text)


def _role_id_from_url(url: str) -> str:
    path = urlsplit(url).path.rstrip("/")
    segment = path.rsplit("/", 1)[-1] if path else ""
    return segment or url


def _normalize(article: dict, slug: str, fetched_at: str) -> dict:
    canonical_url = article.get("url") or ""
    posted_at = article.get("datePublished") or article.get("dateModified") or ""
    return {
        "company": slug,
        "source_kind": "sitemap",
        "ats_slug": slug,
        "role_id": _role_id_from_url(canonical_url),
        "title": article.get("headline", ""),
        "url": canonical_url,
        "location": None,
        "posted_at": posted_at,
        "fetched_at": fetched_at,
        "raw_json": json.dumps(article, sort_keys=True, default=str),
    }


def site_resource(spec: SiteSpec):
    """Return a dlt resource named `<slug>` that yields filtered roles."""

    @dlt.resource(name=spec.slug, write_disposition="append")
    def _resource() -> Iterator[dict]:
        fetched_at = datetime.now(UTC).isoformat()
        urls = _fetch_sitemap_urls(spec.sitemap_url, spec.url_substring)
        for i, url in enumerate(urls):
            if i > 0:
                time.sleep(PAGE_FETCH_DELAY_S)
            article = _fetch_role_page(url)
            if article is None:
                print(f"[sitemap:{spec.slug}] no JSON-LD Article at {url}; skip")
                continue
            headline = article.get("headline", "")
            matched = _title_matches(headline)
            print(
                f"[sitemap:{spec.slug}] {'MATCH' if matched else 'skip '} "
                f"{headline!r}"
            )
            if not matched:
                continue
            yield _normalize(article, spec.slug, fetched_at)

    return _resource


def site_resources(sites: tuple[SiteSpec, ...] = DEFAULT_SITES):
    return [site_resource(spec)() for spec in sites]
