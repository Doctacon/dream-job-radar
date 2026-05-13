# Tech Jobs for Good Domain Gate

ID: ticket:20260513-techjobsforgood-domain-gate
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - changes broad-source gating so Tech Jobs for Good impact areas can admit jobs
Priority: high - required before Tech Jobs for Good rows should appear in the Dive
Depends On: ticket:20260513-techjobsforgood-mvp-extractor

## Summary

Extend broad-source company/domain gating so Tech Jobs for Good impact areas count as mission-fit signals, while manual review decisions still override. The single closure claim is that Tech Jobs for Good rows can enter `relevant_open_roles` only when role/location relevance and approved impact/domain signals both pass.

## Related Records

- `plan:20260513-broaden-mission-source-discovery` - owns the source-expansion strategy.
- `plan:20260513-company-domain-relevance` - owns current company/domain gate semantics.
- `motherduck/views.sql` - expected view-gate target.
- `motherduck/company_domain_review.sql` - manual override surface.

## Scope

May edit `motherduck/views.sql`, `motherduck/company_domain_review.sql`, and apply scripts/docs as needed. Must not rename `relevant_open_roles`, weaken location rules, or let unknown/non-allowed impact areas appear in the Dive by default.

## Acceptance

- ACC-001: Tech Jobs for Good source rows with allowed impact areas can satisfy company/domain relevance.
- ACC-002: Manual `rejected` review decisions still block Tech Jobs for Good companies.
- ACC-003: Non-allowed impact areas or unknown impact areas remain hidden unless manually approved.
- ACC-004: Validation proves at least one expected Tech Jobs for Good row is eligible or explains why current public listings fail location/domain rules.

## Current State

Closed. Updated `motherduck/views.sql` broad-source context to read mission/domain text from `raw_json` for both RemoteOK and Tech Jobs for Good. `relevant_open_roles` now treats `techjobsforgood` as a broad-discovery source rather than a curated bypass source. Allowed impact areas and company blurbs can satisfy deterministic mission-fit rules, while manual review decisions still override.

Validation ran company-review seed and view application, then queried MotherDuck. Tech Jobs for Good had 36 rows in `current_open_roles` and 20 rows in `relevant_open_roles`; RemoteOK remained at 16 current rows and 0 relevant rows. Overall `relevant_open_roles` increased to 34 rows.

No separate audit was run because validation directly exercised the new source gate and the known RemoteOK noise guard.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, extended the domain gate for Tech Jobs for Good impact/context fields, validated 20 eligible TJFG rows and 0 RemoteOK relevant rows, and closed. ACC-001/002/003/004 satisfied.
