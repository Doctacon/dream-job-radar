# 80,000 Hours Domain Gate

ID: ticket:20260513-80000hours-domain-gate
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - adds a new broad-discovery source to relevance SQL
Priority: medium - required before 80,000 Hours rows should appear in the Dive
Depends On: ticket:20260513-80000hours-mvp-extractor

## Summary

Extend broad-source relevance gating so 80,000 Hours rows can appear in `relevant_open_roles` only when title/location and mission/domain gates pass. The single closure claim is that 80,000 Hours rows do not bypass existing broad-source quality controls.

## Related Records

- `plan:20260513-80000hours-public-algolia-mvp` - owns source strategy.
- `motherduck/views.sql` - expected implementation target.
- `motherduck/company_domain_review.sql` - manual review override surface.
- `ticket:20260513-80000hours-source-contract` - defines allowed source-specific domain context fields.

## Scope

May edit view SQL and review seed if needed. Must not rename views, weaken existing location gates, or add full-description dependence unless the source contract has been explicitly revised.

## Acceptance

- ACC-001: 80,000 Hours source kind is included in broad-source context and final broad-source gating.
- ACC-002: Deterministic mission/domain rules use only approved minimal source context plus title/company fields.
- ACC-003: Manual rejected decisions still block 80,000 Hours companies and approved decisions can allow them.
- ACC-004: Existing source relevant counts remain plausible and RemoteOK/TJFG/GJC/GJB guards are preserved.

## Current State

Closed. `motherduck/views.sql` now includes `eightythousandhours` in broad-source context and final broad-source gating, using minimal tag/snippet fields plus title/company for deterministic domain rules. The view also quarantines the initial false-positive title-pattern rows from the first bad raw run. Evidence is recorded in `evidence:20260513-80000hours-mvp-validation`. Separate audit was not run because acceptance is covered by view inspection, count queries, and health check.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Extended `motherduck/views.sql` broad context and gate for `eightythousandhours`.
- 2026-05-13: Added a narrow view guard for initial false-positive title-pattern rows caused by the pre-correction `gis` substring match.
- 2026-05-13: Final counts showed 80,000 Hours `current=106`, `relevant=20`, and zero known false-positive title patterns in current inventory; closed ticket.
