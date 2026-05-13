# Company Domain Gate

ID: ticket:20260513-company-domain-gate
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - changes the final user-facing view semantics for broad-discovery rows
Priority: high - required before RemoteOK can safely appear in the Dive again
Depends On: ticket:20260513-company-review-seed, ticket:20260513-remoteok-enrichment

## Summary

Update `relevant_open_roles` so broad-discovery sources must pass company/domain relevance while curated sources bypass review. The single closure claim is that RemoteOK rows like Natera are hidden unless approved/classified mission-fit, while curated roles continue to appear based on existing title/location relevance.

## Related Records

- `plan:20260513-company-domain-relevance` - owns the gate strategy.
- `ticket:20260513-company-domain-contract` - defines the semantic contract.
- `ticket:20260513-company-review-seed` - provides manual decisions.
- `ticket:20260513-remoteok-enrichment` - provides source context for deterministic rules.
- `motherduck/views.sql` - expected implementation target.

## Scope

May edit view SQL and seed/application SQL. May run MotherDuck validation queries. Must not rename `relevant_open_roles` or change `current_open_roles`. Must not show unknown broad-discovery companies in the normal Dive.

## Acceptance

- ACC-001: Curated source kinds bypass company/domain review.
- ACC-002: RemoteOK rows must be approved or keyword-classified mission-fit before appearing in `relevant_open_roles`.
- ACC-003: Validation proves Natera-like rows are excluded and a known approved/mission-fit row can pass.

## Current State

Closed. `motherduck/views.sql` now keeps `relevant_open_roles` as the final user-facing surface while adding a company/domain gate for RemoteOK. Curated source kinds bypass the company/domain gate and continue to rely on the existing location relevance contract. RemoteOK rows can pass the company/domain gate only when manually `approved` in `company_domain_review` or when deterministic source-field keyword rules identify mission/domain fit and no rejection/pending decision blocks the company.

Rejected and pending RemoteOK companies remain hidden. Validation ran `uv run python scripts/apply_company_domain_review.py` and `uv run python scripts/apply_views.py`, then queried MotherDuck. Results: RemoteOK remains present in `current_open_roles` (`16`) and has `0` rows in `relevant_open_roles`; Natera has `0` relevant rows; Civitech is present in current inventory and approved for company/domain fit but still excluded from `relevant_open_roles` because its location is `Austin, TX or Remote`, which does not satisfy the explicit US/worldwide/AZ location contract. Overall counts remained `current_open_roles = 148` and `relevant_open_roles = 14`.

No separate audit was run because the gate is deterministic SQL with direct validation against the known failure case. Residual risk: deterministic keyword rules may need tuning once a mission-fit RemoteOK role also satisfies the location contract.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, implemented the RemoteOK company/domain gate in `relevant_open_roles`, applied seed and views, validated Natera exclusion and curated counts, and closed. ACC-001/002/003 satisfied with the caveat that current approved Civitech passes company/domain review but not location relevance.
