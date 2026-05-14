# Green Jobs Board Domain Gate

ID: ticket:20260513-greenjobsboard-domain-gate
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - adds a new broad mission source to relevance SQL
Priority: medium - required before Green Jobs Board rows should appear in the Dive
Depends On: ticket:20260513-greenjobsboard-mvp-extractor

## Summary

Extend broad-source domain context so Green Jobs Board category/pathway and detail-page text can satisfy deterministic mission-fit rules, with manual review decisions still able to reject or approve companies. The single closure claim is that Green Jobs Board rows only appear in `relevant_open_roles` when title/location and mission/domain gates pass.

## Related Records

- `plan:20260513-greenjobsboard-80000hours-source-expansion` - owns source strategy.
- `motherduck/views.sql` - expected implementation target.
- `motherduck/company_domain_review.sql` - manual review override surface.

## Scope

May edit view SQL and review seed if needed. Must not rename views or weaken existing gates.

## Acceptance

- ACC-001: Green Jobs Board category/pathway/detail text can be used as domain context.
- ACC-002: Manual rejected decisions still block Green Jobs Board companies.
- ACC-003: Existing source relevant counts remain plausible and RemoteOK generic-company guard is preserved.

## Current State

Closed. `motherduck/views.sql` now includes Green Jobs Board description/pathway/position/workplace context in broad-source domain text and applies the broad-source domain gate to RemoteOK, Tech Jobs for Good, GJC, and Green Jobs Board. Evidence is recorded in `evidence:20260513-greenjobsboard-80000hours-validation`. Separate audit was not run because the SQL change is small, deterministic, and validated by counts/health.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Extended domain context and broad-source gating in `motherduck/views.sql`.
- 2026-05-13: Reapplied views; relevant counts remained plausible (`gjc=2`, `remoteok=1`, `techjobsforgood=20`, `greenjobsboard=0`); closed ticket.
