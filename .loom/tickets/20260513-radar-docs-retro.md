# Radar Docs And Retrospective

ID: ticket:20260513-radar-docs-retro
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: low - documentation and reusable context updates after implementation.
Depends On: ticket:20260513-dive-code-parity

## Summary

Preserve the accepted metric semantics and lessons from the Dive refresh so future agents do not rediscover the inventory-versus-recent distinction. This ticket closes when project documentation or Loom knowledge explains the Dive's primary inventory story, the Iceberg mart snapshot role, and the separate recent/new lens.

## Related Records

- `plan:20260513-dive-radar-refresh` - parent plan whose final state should be reflected in documentation.
- `ticket:20260513-dive-metric-contract` - owns the accepted metric contract.
- `ticket:20260513-dive-code-parity` - provides the final live Dive version and publish evidence.
- `README.md` - public project documentation that may need the final semantics.
- `.loom/plans/lakehouse-iceberg.md` - prior plan that may need a note if the Dive proof point changed meaning.

## Scope

In scope:

- Update README, Loom knowledge, or relevant Loom records with accepted metric semantics.
- Record the final live Dive version and any non-obvious Dives-as-code lessons.
- Note residual risks or follow-up work, if any.

Out of scope:

- Changing the Dive UI or live content.
- Changing pipeline behavior or MotherDuck schemas.
- Broad retrospective unrelated to this Dive refresh.

Stop and return to plan shaping if implementation leaves unresolved metric ambiguity; do not document a false settled story.

## Acceptance

- ACC-001: Durable documentation states that the primary Dive story is current matching open-role inventory and that daily snapshots track inventory by UTC day.
  - Evidence: Source inspection of updated README, Loom knowledge, or related Loom record.
  - Audit: Review should challenge whether a future agent would still confuse inventory history with recent/new roles.

- ACC-002: Documentation names the separate recent/new lens and how it differs from inventory.
  - Evidence: Source inspection of the updated record.
  - Audit: Review should challenge whether the distinction is operational enough for future query edits.

- ACC-003: Final live Dive version and validation posture are recorded or linked.
  - Evidence: Ticket journal or linked evidence references the version from `ticket:20260513-dive-code-parity`.
  - Audit: Separate audit is not required if this ticket only records already-audited implementation outcomes; closure should say so.

## Current State

Closed. `README.md` now records the accepted Dive semantics: the primary Dive story is current matching open-role inventory, daily snapshots track inventory by UTC day from the Iceberg mart, and the recent lens is a separate last-7-day query over `posted_at` or fallback `first_seen_at`. Final live Dive version is `7`, validated by MotherDuck `read_dive` after publish. Separate audit is not required for this documentation-only closure beyond `audit:20260513-dive-radar-refresh-closure`, which found the README supports the intended inventory-vs-recent contract; `FIND-001` record follow-through is resolved here.

## Journal

- 2026-05-13: Created ticket with Status `open` as the documentation and learning-preservation slice for the Dive refresh.
- 2026-05-13: Added README Dive semantics, recorded final live version 7 from the parity ticket, and closed after audit follow-through.
