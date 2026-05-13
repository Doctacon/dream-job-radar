# Relevance Contract

ID: ticket:20260513-relevance-contract
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - defines user-facing eligibility semantics that downstream SQL and Dive work will rely on
Priority: high - prerequisite for the relevance view and general discovery plans

## Summary

Define the location eligibility contract for `relevant_open_roles`. The single closure claim is that future SQL and UI work can distinguish relevant from irrelevant roles without relying on chat: include explicit remote US/worldwide and explicit Arizona locations; exclude non-US/non-Arizona locations and vague remote strings from normal relevant surfaces.

## Related Records

- `plan:20260513-personalized-relevance-filter` - owns the decomposition and approved operator choices.
- `.loom/wiki/extractor-shape.md` - documents that `location` is the existing cross-source field available for relevance classification.
- `motherduck/views.sql` - later ticket will implement this contract as a sibling view over `current_open_roles`.

## Scope

May update Loom records to preserve the executable relevance contract. Must not edit source code, SQL, Dive content, extractors, or README in this ticket. Must not broaden eligibility beyond explicit US/worldwide remote and explicit Arizona without operator approval.

## Acceptance

- ACC-001: The ticket records an include/exclude contract for remote US/worldwide and Arizona-local roles.
  - Evidence: Ticket Current State or Journal names concrete include and exclude classes.
  - Audit: Review should challenge whether SQL implementers can act from the contract without chat history.

- ACC-002: The contract preserves `current_open_roles` as full inventory and routes personalized display through `relevant_open_roles`.
  - Evidence: Ticket records the view split and non-goal of destructive inventory filtering.
  - Audit: Review should challenge whether raw/current inventory remains recoverable for debugging.

- ACC-003: The contract explicitly handles vague or ambiguous remote/location strings with high precision.
  - Evidence: Ticket records that vague `Remote` without US/worldwide scope is excluded until the operator revises the contract.
  - Audit: Review should challenge recall pressure that would silently admit noisy roles.

## Current State

Closed. The executable contract for `relevant_open_roles` is:

- Keep `current_open_roles` as the full matching open-role inventory and do not destructively narrow raw/current inventory for personalized display.
- Add/use `relevant_open_roles` as the normal user-facing relevance surface.
- Include explicit remote roles only when the location text states US, USA, United States, worldwide, global, or equivalent all-country wording.
- Include explicit Arizona-local roles when the location text states Arizona, AZ, Phoenix, Tucson, Tempe, Scottsdale, Mesa, Chandler, Gilbert, Glendale, Peoria, Flagstaff, or similar explicit Arizona place names.
- Exclude vague `Remote` with no US/worldwide scope, non-US remote, and non-Arizona onsite/hybrid roles from `relevant_open_roles`.
- Hard hide excluded roles from normal Dive display; recovery/debugging remains possible through raw storage and `current_open_roles`.
- Prefer high precision over recall. If future implementation needs fuzzy geocoding, ambiguous region inference, or broader remote matching, return to operator shaping before broadening the contract.

No separate audit was run because this ticket only records the operator-approved contract and implementation tickets carry the adversarial checks against the contract.

## Journal

- 2026-05-13: Created ticket with Status `open` as the contract prerequisite for `plan:20260513-personalized-relevance-filter`.
- 2026-05-13: Set Status `active`, recorded the approved include/exclude contract, then closed. ACC-001/002/003 are satisfied by the Current State contract above.
