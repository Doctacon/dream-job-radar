# Tech Jobs for Good Source Contract

ID: ticket:20260513-techjobsforgood-source-contract
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - defines how a public mission-specific board can enter the radar without increasing noise
Priority: high - prerequisite for Tech Jobs for Good implementation

## Summary

Define the executable source contract for Tech Jobs for Good. The single closure claim is that implementation can proceed from durable rules for public pages, role functions, impact areas, location handling, field mapping, and locked/premium result limits.

## Related Records

- `plan:20260513-broaden-mission-source-discovery` - owns the source-expansion strategy.
- `plan:20260513-company-domain-relevance` - owns broad-source company/domain gating and manual review behavior.
- `README.md` - current source and relevance documentation.

## Scope

May update this ticket and related Loom records. Must not edit source code, SQL, workflows, or README. Must not authorize scraping locked, login-only, or premium Tech Jobs for Good results.

## Acceptance

- ACC-001: Allowed Tech Jobs for Good role functions are explicit: Software Engineering and Data + Analytics.
- ACC-002: Allowed impact areas are explicit: Climate Change, Environment, Clean Energy, Public Infrastructure, Public Service & Civic Engagement, and Partners & Advocates.
- ACC-003: Premium/locked/login-only results are explicitly out of scope; only public visible listings may be ingested.
- ACC-004: The ticket maps expected public fields to canonical raw fields and any source-specific enrichment fields.

## Current State

Closed. Tech Jobs for Good MVP contract:

- Source kind: `techjobsforgood`.
- Source slug/table: `jobs`.
- Allowed pages: only public visible Tech Jobs for Good listing/search pages and public job detail pages that are reachable without login, premium access, or bypassing locked content.
- Premium/locked/login-only results are out of scope. Do not attempt to fetch or reconstruct hidden premium listings.
- Allowed role functions: `Software Engineering` and `Data + Analytics`.
- Allowed impact areas: `Climate Change`, `Environment`, `Clean Energy`, `Public Infrastructure`, `Public Service & Civic Engagement`, and `Partners & Advocates`.
- Location handling: ingest public visible rows into `current_open_roles`; `relevant_open_roles` remains responsible for explicit Remote US/worldwide and Arizona-local gating.
- Company/domain handling: allowed impact areas count as source-provided positive mission-fit signals, while `motherduck/company_domain_review.sql` can still reject or approve companies manually.

Expected field mapping:

- `company`: visible company name.
- `source_kind`: `techjobsforgood`.
- `ats_slug`: `jobs`.
- `role_id`: stable numeric job ID parsed from `/jobs/<id>/`.
- `title`: visible role title.
- `url`: absolute public job URL.
- `location`: visible location label, such as `Remote (US)`.
- `posted_at`: best-effort visible posted text or empty string when only relative text is available.
- `fetched_at`: pipeline fetch timestamp.
- `raw_json`: JSON object containing parsed source fields.

Expected source-specific enrichment fields: `tjfg_job_function`, `tjfg_impact_areas`, `tjfg_company_blurb`, `tjfg_salary`, and `tjfg_posted_text` when visible.

No separate audit was run because this ticket records the operator-selected contract; implementation tickets carry source and SQL validation.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, recorded source_kind, role/impact filters, public-only boundary, field mapping, and enrichment fields, then closed. ACC-001/002/003/004 satisfied.
