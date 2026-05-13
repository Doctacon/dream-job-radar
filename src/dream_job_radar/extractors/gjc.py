"""GIS Jobs Clearinghouse RSS extractor."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Iterator

import dlt
import requests

RSS_URL = "https://www.gjc.org/cgi-bin/rssjobs.pl"
USER_AGENT = "dream-job-radar/0.1"
ATS_SLUG = "rss"


def _clean(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(unescape(value).split())


def _role_id(url: str) -> str:
    found = re.search(r"[?&]id=(\d+)", url)
    return found.group(1) if found else url.rstrip("/").rsplit("/", 1)[-1]


def _posted_at(pub_date: str) -> str:
    if not pub_date:
        return ""
    try:
        return parsedate_to_datetime(pub_date).isoformat()
    except (TypeError, ValueError):
        return pub_date


def _parse_company_location(title: str, description: str) -> tuple[str, str, str]:
    """Parse `Title - Company, Location posted on DATE` conservatively."""
    text = _clean(description)
    before_posted = re.split(r"\s+posted on\s+", text, maxsplit=1, flags=re.I)[0]
    if " - " in before_posted:
        _, rest = before_posted.split(" - ", 1)
    elif before_posted.lower().startswith(title.lower()):
        rest = before_posted[len(title) :].lstrip(" -")
    else:
        rest = before_posted

    if "," not in rest:
        return _clean(rest), "", text

    company, location = rest.split(",", 1)
    return _clean(company), _clean(location), text


def _fetch_items() -> list[dict]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/xml"}
    resp = requests.get(RSS_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    items: list[dict] = []
    for item in root.findall("./channel/item"):
        title = _clean(item.findtext("title"))
        link = _clean(item.findtext("link"))
        guid = _clean(item.findtext("guid"))
        description = _clean(item.findtext("description"))
        pub_date = _clean(item.findtext("pubDate"))
        company, location, parsed_description = _parse_company_location(title, description)
        items.append(
            {
                "title": title,
                "link": link,
                "guid": guid,
                "description": parsed_description,
                "pubDate": pub_date,
                "company": company,
                "location": location,
            }
        )
    return items


def _normalize(item: dict, fetched_at: str) -> dict:
    url = item.get("link") or item.get("guid") or ""
    return {
        "company": item.get("company", ""),
        "source_kind": "gjc",
        "ats_slug": ATS_SLUG,
        "role_id": _role_id(url),
        "title": item.get("title", ""),
        "url": url,
        "location": item.get("location", ""),
        "posted_at": _posted_at(item.get("pubDate", "")),
        "fetched_at": fetched_at,
        "gjc_description": item.get("description", ""),
        "gjc_guid": item.get("guid", ""),
        "gjc_pub_date": item.get("pubDate", ""),
        "raw_json": json.dumps(item, sort_keys=True),
    }


@dlt.resource(name=ATS_SLUG, write_disposition="append")
def gjc_resource() -> Iterator[dict]:
    fetched_at = datetime.now(UTC).isoformat()
    items = _fetch_items()
    print(f"[gjc:{ATS_SLUG}] fetched {len(items)} RSS item(s)")
    for item in items:
        print(
            f"[gjc:{ATS_SLUG}] MATCH {item.get('title')!r} "
            f"at {item.get('company')!r} / {item.get('location')!r}"
        )
        yield _normalize(item, fetched_at)
