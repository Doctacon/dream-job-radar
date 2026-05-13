# Tech Jobs for Good Dive Validation

ID: ticket:20260513-techjobsforgood-dive-validation
Type: Ticket
Status: open
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

Ready after pipeline integration closes.

## Journal

- 2026-05-13: Created ticket with Status `open`.
