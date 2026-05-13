# Personalized Relevance Filter

ID: plan:20260513-personalized-relevance-filter
Type: Plan
Status: completed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - changes the user-facing definition of useful roles while preserving the raw inventory view

## Summary

Add a personalized relevance layer so the radar surfaces jobs the operator would actually consider: explicit remote US/worldwide roles and explicit Arizona-local roles. The existing `current_open_roles` inventory remains intact for recovery and debugging, while a new `relevant_open_roles` view becomes the user-facing source for the Dive and future discovery work. This needs more than one ticket because it separates the eligibility contract, database/view implementation, and user-facing Dive/documentation changes.

## Related Records

- `.loom/wiki/extractor-shape.md` - documents the canonical raw schema, source-kind layout, and `current_open_roles` contract that this plan must not break.
- `README.md` - currently describes the radar and Dive as inventory-first over `current_open_roles`; user-facing wording must be updated after the relevance view exists.
- `motherduck/views.sql` - owns the current MotherDuck view DDL and is the likely home for `relevant_open_roles`.
- `.dive-preview/src/dive.tsx` - local Dive mirror that should consume the relevant view once implemented.
- `plan:20260513-general-job-board-discovery` - depends on this plan so broad discovery results are filtered before they reach the Dive.

## Strategy

Use a contract-first route. First preserve the exact eligibility semantics in a ticket so later SQL, labels, and tests do not invent broader matching. Then add `relevant_open_roles` as a sibling view over `current_open_roles`, not a destructive rewrite of the inventory. Finally update the Dive and README to use the relevant view for user-facing counts and lists while keeping raw/current inventory available outside normal display.

Precision is more important than recall. The approved include set is explicit remote US/USA/United States, explicit remote worldwide/global, and explicit Arizona locations. Vague `Remote`, non-US remote, and non-Arizona onsite/hybrid roles should be excluded from `relevant_open_roles` until the operator revises the contract. Replan if implementation needs new columns, raw ingestion changes, or fuzzy geocoding to satisfy the contract.

## Execution Units

### Unit: Relevance Contract

Ticket: ticket:20260513-relevance-contract

Record the executable semantics for eligible and ineligible locations. Scope is Loom records only; no code or SQL changes. Evidence should be example-driven: Mapbox Germany-style non-US roles are excluded, explicit Arizona roles are included, and explicit US/worldwide remote roles are included. Stop and return to shaping if the available upstream `location` strings are too ambiguous to support high-precision filtering without new source data.

### Unit: Relevant View

Ticket: ticket:20260513-relevant-open-roles-view

Add `relevant_open_roles` to `motherduck/views.sql` as a high-precision filter over `current_open_roles`. Scope is the MotherDuck DDL and minimal supporting validation commands. The ticket closes when the view exists, keeps `current_open_roles` unchanged, and evidence queries show included/excluded examples according to the contract. It depends on `ticket:20260513-relevance-contract`.

### Unit: Relevant Dive Wiring

Ticket: ticket:20260513-relevant-dive-wiring

Update the local/live Dive and README so user-facing role counts and role lists use `relevant_open_roles`, with provenance still visible where roles appear. Scope is Dive code/content and documentation, not extractor logic or discovery sources. The ticket closes when the Dive presents relevant roles as the primary story, excluded roles are hard hidden from normal display, and local/live parity is validated. It depends on `ticket:20260513-relevant-open-roles-view`.

## Milestones

### Milestone: Contract Ready

Child tickets: ticket:20260513-relevance-contract

The high-precision location eligibility semantics are durable enough for SQL and UI work to implement without relying on chat history.

### Milestone: Relevant Data Surface Ready

Child tickets: ticket:20260513-relevance-contract, ticket:20260513-relevant-open-roles-view

MotherDuck exposes both full inventory and personalized relevance, and evidence shows the new view filters the known irrelevant geography without hiding raw inventory.

### Milestone: User-Facing Radar Updated

Child tickets: ticket:20260513-relevant-dive-wiring

The Dive and README tell the personalized relevance story, with excluded roles hard hidden from normal display and `current_open_roles` still available for recovery/debugging.

## Current State

Completed. All child tickets are closed for contract, MotherDuck view, local Dive, README work, and live Dive publication. `relevant_open_roles` is live in MotherDuck and validated; local Dive source, README, and live Dive version 8 use the relevance-first story. The live Dive URL is https://app.motherduck.com/dives/391d1329-70d7-4223-89c8-d0dfde66ef7f.

## Journal

- 2026-05-13: Created plan with Status `open` from operator-selected choices: new `relevant_open_roles` view, explicit US/worldwide remote, explicit Arizona, hard-hidden excluded roles, high precision.
- 2026-05-13: Child tickets `ticket:20260513-relevance-contract`, `ticket:20260513-relevant-open-roles-view`, and `ticket:20260513-relevant-dive-wiring` closed. Set plan Status `review`; remaining plan-level question is whether/when to publish the live Dive from the updated local source.
- 2026-05-13: Operator approved the local preview. Published live Dive version 8 via MotherDuck `update_dive` and read it back successfully. Set plan Status `completed`.
