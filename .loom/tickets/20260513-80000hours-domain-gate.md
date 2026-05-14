# 80,000 Hours Domain Gate

ID: ticket:20260513-80000hours-domain-gate
Type: Ticket
Status: open
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

Ready after 80,000 Hours raw rows or a zero-row source validation path exists.

## Journal

- 2026-05-13: Created ticket with Status `open`.
