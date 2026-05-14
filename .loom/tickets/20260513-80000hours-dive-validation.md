# 80,000 Hours Dive Validation

ID: ticket:20260513-80000hours-dive-validation
Type: Ticket
Status: open
Created: 2026-05-13
Updated: 2026-05-13
Risk: low - existing Dive should consume rows through relevant_open_roles
Priority: medium - validates user-facing behavior
Depends On: ticket:20260513-80000hours-pipeline-integration

## Summary

Validate the Dream Job Radar Dive after 80,000 Hours lands. The single closure claim is that eligible 80,000 Hours rows, if any, flow through `relevant_open_roles` with provenance and no MotherDuck data sharing.

## Related Records

- `plan:20260513-80000hours-public-algolia-mvp` - owns source strategy.
- `.dive-preview/src/dive.tsx` - local mirror if copy changes are needed.
- Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` - private Dive.

## Scope

May inspect or update Dive/README copy if needed. Must not share MotherDuck data. Publish only if copy or query behavior needs changing.

## Acceptance

- ACC-001: Dive still queries `relevant_open_roles` and shows `source_kind` provenance.
- ACC-002: 80,000 Hours rows appear only when existing title/location/domain gates pass.
- ACC-003: No MotherDuck data sharing is performed.
- ACC-004: If no Dive publish is needed, the ticket records why the existing Dive path is sufficient.

## Current State

Ready after integration closes.

## Journal

- 2026-05-13: Created ticket with Status `open`.
