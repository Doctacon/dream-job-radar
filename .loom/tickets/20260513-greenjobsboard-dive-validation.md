# Green Jobs Board Dive Validation

ID: ticket:20260513-greenjobsboard-dive-validation
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: low - existing Dive should consume rows through relevant_open_roles
Priority: medium - validates user-facing behavior
Depends On: ticket:20260513-greenjobsboard-pipeline-integration

## Summary

Validate the Dream Job Radar Dive after Green Jobs Board lands. The single closure claim is that eligible Green Jobs Board rows, if any, flow through `relevant_open_roles` with provenance and no MotherDuck data sharing.

## Related Records

- `.dive-preview/src/dive.tsx` - local mirror if copy changes are needed.
- Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` - private Dive.

## Scope

May update Dive/README copy if needed. Must not share MotherDuck data.

## Acceptance

- ACC-001: Dive still queries `relevant_open_roles` and shows `source_kind` provenance.
- ACC-002: Green Jobs Board rows appear only when existing gates pass.
- ACC-003: No MotherDuck data sharing is performed.

## Current State

Closed. The existing Dive mirror still queries `relevant_open_roles` and renders `source_kind`; Green Jobs Board has zero relevant rows today, and future rows must pass existing view gates. No MotherDuck data sharing was performed and no Dive publish was needed. Evidence is recorded in `evidence:20260513-greenjobsboard-80000hours-validation`. Separate audit was not run because no live Dive/data sharing change was made.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Inspected `.dive-preview/src/dive.tsx`; it still uses `relevant_open_roles` and shows source provenance.
- 2026-05-13: Closed with no Dive publish because copy/code did not need changing and Green Jobs Board has zero relevant rows today.
