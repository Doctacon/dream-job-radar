# Relevant Dive Wiring

ID: ticket:20260513-relevant-dive-wiring
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - changes the public Dive's primary data source and wording
Priority: medium - follows the relevance view and prepares the UI for general discovery
Depends On: ticket:20260513-relevant-open-roles-view

## Summary

Update the Dream Job Radar Dive and README so normal user-facing counts and lists use `relevant_open_roles`, while `current_open_roles` remains the full inventory/debug surface. The single closure claim is that excluded roles are hard hidden from normal display and the Dive tells a personalized relevance story without losing role provenance.

## Related Records

- `plan:20260513-personalized-relevance-filter` - owns the user-facing route and milestones.
- `ticket:20260513-relevant-open-roles-view` - provides the database surface this ticket consumes.
- `README.md` - current public description of pipeline and Dive semantics.
- `.dive-preview/src/dive.tsx` - local Dive mirror expected to change before live publish.

## Scope

May edit `.dive-preview/src/dive.tsx`, README wording, and live Dive content if publishing is part of execution. May update ticket evidence with local build/readback output. Must not change extractor filtering, raw storage, `current_open_roles`, or general discovery sources. Excluded roles should not appear in normal Dive sections unless the operator authorizes a separate debug surface.

## Acceptance

- ACC-001: Primary Dive KPIs and role lists query `relevant_open_roles` rather than `current_open_roles`.
  - Evidence: Local Dive diff and/or live Dive readback show the relevant view is the primary source.
  - Audit: Review should challenge stale `current_open_roles` queries in normal user-facing sections.

- ACC-002: The Dive still exposes source provenance for mixed curated/discovered roles where roles are listed.
  - Evidence: Role list/table content includes source/source-kind/company provenance fields or labels.
  - Audit: Review should challenge whether future general-board results would be indistinguishable from curated company boards.

- ACC-003: README explains the split between full inventory and personalized relevance.
  - Evidence: README diff states `current_open_roles` is full inventory and `relevant_open_roles` is the user-facing relevance layer.
  - Audit: Review should challenge whether future agents might still confuse inventory and relevance semantics.

## Current State

Closed. `.dive-preview/src/dive.tsx` now uses `"acorn-granary"."main"."relevant_open_roles"` for primary KPIs, company coverage, source coverage, and recent role listings. The full inventory snapshot section remains explicitly labeled as broader `current_open_roles` / Iceberg mart history. Role listings include `source_kind` provenance on desktop and mobile.

`README.md` now documents the split: `current_open_roles` is full inventory for recovery/debugging/snapshot history, and `relevant_open_roles` is the normal user-facing surface for explicit remote US/worldwide and explicit Arizona-local roles. Validation ran with `rtk npm exec vite build -- --outDir "/var/folders/xk/pmxkhd7x635cskr6l4qw0mx00000gn/T/opencode/dream-job-radar-dive-build" --emptyOutDir`; build passed, with only the existing Vite chunk-size warning.

Operator approved the local preview. Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` was updated to version 8 with title `dream-job-radar - relevant open roles` and read back successfully. URL: https://app.motherduck.com/dives/391d1329-70d7-4223-89c8-d0dfde66ef7f.

## Journal

- 2026-05-13: Created ticket with Status `open` as the UI/documentation slice for `plan:20260513-personalized-relevance-filter`.
- 2026-05-13: Set Status `active`, updated local Dive queries/copy and README, validated with Vite build, and closed for local/docs wiring. ACC-001/002/003 satisfied locally; live publish intentionally deferred pending preview approval.
- 2026-05-13: Operator approved preview. Published live Dive version 8 via MotherDuck `update_dive` and read back version 8 successfully. Publication deferral resolved.
