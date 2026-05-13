# General Board Dive Display

ID: ticket:20260513-general-board-dive-display
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - changes user-facing role presentation to mix curated and discovered sources
Priority: low - depends on relevance and pipeline integration being proven first
Depends On: ticket:20260513-general-board-pipeline-integration, ticket:20260513-relevant-dive-wiring

## Summary

Update the Dream Job Radar Dive so relevant roles from curated company boards and the MVP general discovery source are mixed together with clear provenance. The single closure claim is that broad-discovery roles can appear in the normal relevant role flow without hiding where they came from or admitting irrelevant geography.

## Related Records

- `plan:20260513-general-job-board-discovery` - owns the mixed-display strategy.
- `ticket:20260513-general-board-pipeline-integration` - proves discovered rows reach MotherDuck and relevance surfaces.
- `ticket:20260513-relevant-dive-wiring` - establishes the Dive's relevance-first baseline.
- `.dive-preview/src/dive.tsx` - local Dive mirror expected to change before live publish.
- `README.md` - may need final wording if display semantics change.

## Scope

May update `.dive-preview/src/dive.tsx`, live Dive content, and README wording about mixed curated/discovered display. Must query `relevant_open_roles`, not raw/current inventory, for normal role display. Must preserve source provenance labels. Must not change extractor logic, pipeline wiring, or relevance classification.

## Acceptance

- ACC-001: Curated and discovered relevant roles appear in one normal role flow or ranking, not separate hidden systems.
  - Evidence: Dive query/code inspection and live/local preview show mixed source-kind handling.
  - Audit: Review should challenge whether broad-discovery roles are visually or semantically orphaned.

- ACC-002: Role listings preserve provenance sufficient to tell curated company boards from broad discovery.
  - Evidence: Role table/cards include company/source/source_kind or equivalent source labels.
  - Audit: Review should challenge whether provenance is visible enough for decision-making.

- ACC-003: Excluded roles remain hard hidden from normal display because the Dive uses `relevant_open_roles`.
  - Evidence: Dive queries point at `relevant_open_roles`, and validation checks excluded geography does not appear.
  - Audit: Review should challenge accidental fallback to `current_open_roles` for normal sections.

## Current State

Closed with no code change. The existing live Dive version 8 already queries `relevant_open_roles` for primary display and shows `source_kind` provenance in role listings/source coverage. After RemoteOK pipeline integration, MotherDuck validation showed 2 RemoteOK rows in `relevant_open_roles`, so the live Dive can mix curated and discovered relevant roles through the existing query path without a design change.

No live Dive publish was needed because the data contract and source provenance display were already present from `ticket:20260513-relevant-dive-wiring`.

## Journal

- 2026-05-13: Created ticket with Status `open` as the user-facing mixed-display slice for `plan:20260513-general-job-board-discovery`.
- 2026-05-13: Validated existing Dive design against RemoteOK output. Closed with no code change; ACC-001/002/003 satisfied by live Dive version 8 querying `relevant_open_roles` and displaying `source_kind` provenance.
