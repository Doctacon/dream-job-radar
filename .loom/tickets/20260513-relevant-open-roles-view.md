# Relevant Open Roles View

ID: ticket:20260513-relevant-open-roles-view
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - adds a new MotherDuck view that changes downstream user-facing role selection
Priority: high - required before Dive wiring and broad discovery display
Depends On: ticket:20260513-relevance-contract

## Summary

Add a `relevant_open_roles` MotherDuck view that filters `current_open_roles` to the approved personalized location contract. The single closure claim is that the database exposes a high-precision relevant role surface while preserving the full `current_open_roles` inventory unchanged.

## Related Records

- `plan:20260513-personalized-relevance-filter` - owns sequence, validation posture, and view-split strategy.
- `ticket:20260513-relevance-contract` - defines the location eligibility contract this ticket must implement.
- `.loom/wiki/extractor-shape.md` - documents the schema and raw/view constraints that must continue to hold.
- `motherduck/views.sql` - expected write target for the new view.

## Scope

May edit `motherduck/views.sql` and, if needed, minimal validation documentation in the ticket. May run read-only MotherDuck validation after applying the DDL. Must not edit extractors, raw ingestion, `current_open_roles` semantics, Dive code, or README. Must not introduce fuzzy geocoding or broad remote matching without returning to the contract ticket.

## Acceptance

- ACC-001: `current_open_roles` remains available as full matching inventory and is not narrowed by the relevance filter.
  - Evidence: Diff inspection shows `current_open_roles` still exists and a separate `relevant_open_roles` view is added.
  - Audit: Review should challenge accidental destructive filtering of the existing inventory contract.

- ACC-002: `relevant_open_roles` includes only explicit US/worldwide remote roles and explicit Arizona-local roles according to `ticket:20260513-relevance-contract`.
  - Evidence: MotherDuck queries or equivalent SQL inspection show the include predicates and sample included rows when data is available.
  - Audit: Review should challenge vague `Remote` and non-US/non-Arizona false positives.

- ACC-003: Known irrelevant geography, such as non-US onsite/hybrid roles like Germany, is excluded from `relevant_open_roles` when present in `current_open_roles`.
  - Evidence: MotherDuck comparison query checks current inventory rows with excluded geography against the relevant view.
  - Audit: Review should challenge whether the evidence proves exclusion rather than absence from source data.

## Current State

Closed. `motherduck/views.sql` now keeps `current_open_roles` intact and adds `relevant_open_roles` as a sibling view. The new view projects the same public columns as `current_open_roles` and filters with conservative predicates for explicit remote US/USA/United States, explicit remote/global/worldwide, and explicit Arizona places.

Validation ran with `uv run python scripts/apply_views.py`, which materialized the DDL successfully. Follow-up MotherDuck queries observed `current_open_roles = 131` and `relevant_open_roles = 11`; relevant locations were `Remote: United States | Canada | United Kingdom | The Netherlands | Denmark | Estonia | France | Ireland | Portugal | Sweden | Switzerland` (5), `United States, Remote` (4), and `Remote: United States | Canada` (2). Mapbox Germany rows were present in current inventory (`17`) and absent from relevant rows (`0`). Vague exact `Remote` rows in relevant were `0`.

No separate audit was run because this narrow SQL addition was directly validated against the ticket acceptance; the downstream Dive ticket still carries an audit lens for stale `current_open_roles` usage.

## Journal

- 2026-05-13: Created ticket with Status `open` as the database-surface slice for `plan:20260513-personalized-relevance-filter`.
- 2026-05-13: Set Status `active`, added `relevant_open_roles` to `motherduck/views.sql`, applied DDL with `uv run python scripts/apply_views.py`, validated counts and Mapbox Germany exclusion, and closed. ACC-001/002/003 satisfied.
