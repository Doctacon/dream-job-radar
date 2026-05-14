# Green Jobs Board Source Contract

ID: ticket:20260513-greenjobsboard-source-contract
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - current board is mission-fit but sparse for technical roles
Priority: high - prerequisite for implementation

## Summary

Define the executable source contract for Green Jobs Board. The single closure claim is that implementation can proceed from durable rules for public listing/detail pages, strict technical filters, field mapping, and domain-gate behavior.

## Related Records

- `plan:20260513-greenjobsboard-80000hours-source-expansion` - owns the strategy and operator decisions.
- `plan:20260513-company-domain-relevance` - owns broad-source domain gating.

## Scope

May update this ticket and related Loom records. Must not edit source code, SQL, workflows, or README. Must not authorize login-only, employer, or hidden/premium paths.

## Acceptance

- ACC-001: Public-visible source boundary is explicit.
- ACC-002: Strict technical title filter is explicit.
- ACC-003: Canonical and source-specific field mapping is explicit.
- ACC-004: Category/pathway domain-signal behavior and manual-review overrides are explicit.

## Current State

Closed. Green Jobs Board source contract:

- Source kind: `greenjobsboard`.
- Source slug/table: `jobs`.
- Allowed pages: public visible listing page `https://www.greenjobsboard.us/jobboard/explore-jobs` and public job detail pages linked from listing cards under `/jobs/...`.
- Disallowed paths: login-only, employer/admin, hidden, premium, or non-public pages.
- Strict title filter: include software, data, analytics, GIS/geospatial, ML, platform, backend, infrastructure, DevOps/SRE, security engineering, and technical analyst titles. Exclude policy, campaigns, program, operations, development/fundraising, HR, legal, education, marketing, communications, sales, executive director/CEO, intern, technician, field-only, and non-technical roles.
- Category/pathway is a positive mission/domain signal, not sufficient by itself. Manual review decisions in `company_domain_review` can still reject or approve companies.
- Canonical fields: `company`, `source_kind`, `ats_slug`, `role_id`, `title`, `url`, `location`, `posted_at`, `fetched_at`, and `raw_json`.
- Source-specific fields: `gjb_pathway`, `gjb_workplace`, `gjb_experience`, `gjb_position_type`, `gjb_compensation`, `gjb_apply_before`, `gjb_apply_url`, and `gjb_description`.

No separate audit was run because implementation and SQL tickets carry source validation.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, recorded public boundary, strict filter, field mapping, and domain behavior, then closed. ACC-001/002/003/004 satisfied.
