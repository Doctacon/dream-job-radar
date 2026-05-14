# 80,000 Hours Source Contract

ID: ticket:20260513-80000hours-source-contract
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - source access is public but non-contractual and content reuse must stay conservative
Priority: high - implementation must not proceed without a bounded source contract

## Summary

Define the executable source contract for 80,000 Hours. The single closure claim is that implementation can proceed from durable rules for public Algolia access, minimal stored fields, strict title filtering, polling behavior, and broad-source relevance gating.

## Related Records

- `plan:20260513-80000hours-public-algolia-mvp` - owns the implementation strategy and ticket sequence.
- `evidence:20260513-greenjobsboard-80000hours-validation` - records public Algolia feasibility and risks.
- `ticket:20260513-80000hours-access-feasibility` - prior research-only ticket with cautious-go recommendation.

## Scope

May update this ticket and related Loom records. Must not edit source code, SQL, workflows, or README. Must not authorize auth/session scraping, hidden endpoints, high-volume crawling, or full-description storage unless the operator explicitly changes the content posture.

## Acceptance

- ACC-001: Public access boundary is explicit: public Algolia browser search only, no auth/session scraping, no hidden app paths, and no treatment of the public browser key as a project secret.
- ACC-002: Source identifiers and canonical field mapping are explicit, including source kind, slug, role ID, title, company, URL, location, date fields, fetched timestamp, and raw metadata posture.
- ACC-003: Minimal source-specific fields are explicit and exclude full descriptions by default unless a later authorized change revises the contract.
- ACC-004: Strict technical title filtering and conservative polling behavior are explicit, including narrow attributes and daily scheduled refresh as the maximum default cadence.
- ACC-005: Broad-source domain gate behavior is explicit, including manual review overrides and deterministic mission/domain signals.

## Current State

Closed. 80,000 Hours source contract:

- Source kind: `eightythousandhours`.
- Source slug/table: `jobs`.
- Allowed access: public Algolia browser search endpoint for the public jobs index only. No auth/session scraping, no login/app-user paths, no hidden/admin paths, no bypassing access controls, and no treating the public browser key as a project secret.
- Default index posture: use the public super-ranked jobs index observed in feasibility research unless the public runtime config indicates a safe successor. If the index/key stops returning rows, block or replan instead of inventing a workaround.
- Polling: at most the existing daily scheduled refresh by default. Use narrow `attributesToRetrieve`, bounded pagination, ordinary request timeouts, and no high-volume crawling.
- Canonical fields: `company`, `source_kind`, `ats_slug`, `role_id`, `title`, `url`, `location`, `posted_at`, `fetched_at`, and `raw_json`.
- Minimal source-specific fields allowed: company ID/name if distinct from canonical company, external/source URL, salary text, closing date, short description/snippet when needed for context, seniority/location tags, category/tag names, and other compact metadata useful for gating.
- Disallowed by default: full descriptions, bulk content mirrors, authenticated recommendations, personalized app state, and hidden ranking/debug fields that are not needed for relevance.
- Strict title filter: include software, data, analytics, GIS/geospatial, ML/AI engineering, platform, backend, infrastructure, DevOps/SRE, cloud, security, and technical analyst/architect titles. Exclude policy, campaigns, program, operations, fundraising/development, HR, legal, education, marketing, communications, sales, support, executive, intern, and non-technical roles.
- Relevance behavior: treat as a broad-discovery source. Rows may enter `current_open_roles` after strict title filtering, but `relevant_open_roles` must also require location eligibility plus manual company/domain review or deterministic mission/domain signals from approved minimal metadata.

Separate audit was not run because this ticket only records operator-approved source rules from prior feasibility evidence; implementation and validation tickets carry executable evidence.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Recorded public-search boundary, source identifiers, minimal field posture, title filter, polling limit, and broad-source relevance behavior; closed ticket.
