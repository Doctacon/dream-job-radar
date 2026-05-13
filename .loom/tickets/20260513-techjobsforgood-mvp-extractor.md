# Tech Jobs for Good MVP Extractor

ID: ticket:20260513-techjobsforgood-mvp-extractor
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - adds a new public HTML source that may change layout
Priority: high - expected to increase high-signal relevant roles
Depends On: ticket:20260513-techjobsforgood-source-contract

## Summary

Implement a Tech Jobs for Good extractor and source-kind pipeline that writes public visible mission-fit jobs into the canonical raw shape. The single closure claim is that one source-kind pipeline can produce normalized Tech Jobs for Good rows without bypassing locked/premium/login-only content.

## Related Records

- `plan:20260513-broaden-mission-source-discovery` - owns the MVP route and non-goals.
- `ticket:20260513-techjobsforgood-source-contract` - defines allowed public pages, role functions, impact areas, and field mapping.
- `.loom/wiki/extractor-shape.md` - defines the raw layout and canonical row expectations.
- `src/dream_job_radar/extractors/` - expected extractor location.
- `src/dream_job_radar/pipelines/` - expected pipeline location.

## Scope

May add one extractor module and one pipeline module for Tech Jobs for Good. May use public HTML parsing and source-specific enrichment fields. Must not bypass premium/locked/login-only results, must not add multiple new sources, and must not weaken existing relevance gates. Keep parsing minimal and fail visibly if the public layout no longer matches.

## Acceptance

- ACC-001: Extractor emits canonical fields: company, source_kind, ats_slug, role_id, title, url, location, posted_at, fetched_at, and raw_json.
- ACC-002: Extractor captures source-specific mission fields, including job function and impact areas when visible.
- ACC-003: Source-only validation proves public visible listings load locally with `uv` and no failed jobs.
- ACC-004: Existing curated and RemoteOK extractor behavior is unchanged.

## Current State

Closed. Added `src/dream_job_radar/extractors/techjobsforgood.py` and `src/dream_job_radar/pipelines/techjobsforgood.py`. The extractor parses public visible Tech Jobs for Good listing cards for `Software Engineering` and `Data + Analytics`, keeps only approved impact areas, captures canonical fields, and adds source-specific fields: `tjfg_job_function`, `tjfg_impact_areas`, `tjfg_company_blurb`, `tjfg_salary`, and `tjfg_posted_text`.

Validation found 30 public cards on page 1 and 25 on page 2, with 36 matched public visible roles after function/impact filtering. `uv run python -m dream_job_radar.pipelines.techjobsforgood` loaded 36 rows with no failed jobs. Existing curated and RemoteOK extractor files were not changed.

No separate audit was run because this is a single-source extractor with command validation and downstream SQL validation in the following tickets.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, implemented Tech Jobs for Good extractor/pipeline, validated 36 matched public visible roles, ran the source pipeline successfully, and closed. ACC-001/002/003/004 satisfied.
