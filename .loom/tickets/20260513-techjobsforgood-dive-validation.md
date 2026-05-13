# Tech Jobs for Good Dive Validation

ID: ticket:20260513-techjobsforgood-dive-validation
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: low - expected to validate existing relevance-first Dive rather than redesign it
Priority: medium - confirms the new source improves user-facing output
Depends On: ticket:20260513-techjobsforgood-pipeline-integration

## Summary

Validate the Dream Job Radar Dive and documentation after Tech Jobs for Good lands. The single closure claim is that Tech Jobs for Good roles, when eligible, appear through the existing `relevant_open_roles` path with source provenance and without requiring MotherDuck data sharing.

## Related Records

- `plan:20260513-broaden-mission-source-discovery` - owns the final validation milestone.
- `.dive-preview/src/dive.tsx` - local Dive mirror if copy changes are needed.
- Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` - private published Dive.
- `README.md` - documentation target if semantics change.

## Scope

May update Dive copy and README if validation reveals confusing wording. Must not share the Dive or underlying MotherDuck data; screenshots remain the sharing path.

## Acceptance

- ACC-001: Dive still queries `relevant_open_roles` and shows `source_kind` provenance.
- ACC-002: Tech Jobs for Good eligible roles appear in the normal relevant role flow when present.
- ACC-003: Live or local validation confirms no RemoteOK-style generic-company noise leaks through.
- ACC-004: No MotherDuck data sharing is performed.

## Current State

Closed. The existing Dive still queries `relevant_open_roles` and displays `source_kind` provenance, so no Dive code or live publish was needed. MotherDuck validation showed Tech Jobs for Good contributes 20 rows to `relevant_open_roles`; source counts were `ashby = 1`, `greenhouse = 13`, and `techjobsforgood = 20`. RemoteOK remains at 0 relevant rows, so the prior generic-company noise guard remains intact.

No MotherDuck data sharing was performed. Screenshots remain the sharing path.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, validated existing Dive query path/source provenance via MotherDuck counts, confirmed no share operation, and closed. ACC-001/002/003/004 satisfied.
