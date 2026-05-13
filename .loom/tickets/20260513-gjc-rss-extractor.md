# GJC RSS Extractor

ID: ticket:20260513-gjc-rss-extractor
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: low - RSS feed is simple but parsing is description-based
Priority: high - creates the GJC source rows
Depends On: ticket:20260513-gjc-source-contract

## Summary

Implement a GIS Jobs Clearinghouse RSS extractor and pipeline that writes normalized public RSS items into raw inventory. The single closure claim is that GJC RSS rows load locally with canonical fields and preserved raw source context.

## Related Records

- `plan:20260513-gis-jobs-clearinghouse-rss` - owns the GJC source route.
- `ticket:20260513-gjc-source-contract` - defines field mapping and source boundary.
- `src/dream_job_radar/extractors/` - expected extractor location.
- `src/dream_job_radar/pipelines/` - expected pipeline location.

## Scope

May add one extractor and one pipeline module. Must not crawl GJC job detail pages or account/admin/posting pages. Must preserve raw RSS item payload.

## Acceptance

- ACC-001: Extractor emits canonical fields: company, source_kind, ats_slug, role_id, title, url, location, posted_at, fetched_at, raw_json.
- ACC-002: Extractor captures GJC-specific fields: RSS description, guid, and pubDate.
- ACC-003: Source-only validation loads rows with `uv` and no failed jobs.

## Current State

Closed. Added `src/dream_job_radar/extractors/gjc.py` and `src/dream_job_radar/pipelines/gjc.py`. The extractor fetches the public GJC RSS feed, parses RSS item title/link/guid/description/pubDate, normalizes to canonical fields, and preserves `gjc_description`, `gjc_guid`, `gjc_pub_date`, and `raw_json`.

Validation probed 10 RSS items and loaded them with `uv run python -m dream_job_radar.pipelines.gjc`; the dlt load completed with no failed jobs.

No separate audit was run because this is a narrow RSS source with source-only command validation.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, implemented GJC RSS extractor/pipeline, validated 10 parsed items and source-only load, then closed. ACC-001/002/003 satisfied.
