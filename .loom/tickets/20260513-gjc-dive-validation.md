# GJC Dive Validation

ID: ticket:20260513-gjc-dive-validation
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: low - existing Dive should consume GJC through relevant_open_roles
Priority: medium - validates user-facing effect
Depends On: ticket:20260513-gjc-pipeline-integration

## Summary

Validate the Dream Job Radar Dive after GJC lands. The single closure claim is that GJC rows, when eligible, appear through the existing `relevant_open_roles` path with source provenance and no MotherDuck data sharing.

## Related Records

- `plan:20260513-gis-jobs-clearinghouse-rss` - owns final validation.
- `.dive-preview/src/dive.tsx` - local mirror if copy changes are needed.
- Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` - private published Dive.

## Scope

May update Dive/README copy if needed. Must not share the Dive or underlying MotherDuck data.

## Acceptance

- ACC-001: Dive still queries `relevant_open_roles` and shows `source_kind` provenance.
- ACC-002: Non-AZ onsite GJC rows do not appear; eligible Remote/AZ rows can appear.
- ACC-003: No MotherDuck data sharing is performed.

## Current State

Closed. No Dive code or publish was needed: the existing Dive queries `relevant_open_roles` and shows `source_kind` provenance. MotherDuck validation showed GJC contributes 2 eligible rows to `relevant_open_roles`, and non-AZ onsite GJC rows remain excluded. No MotherDuck data sharing was performed.

Relevant GJC rows at validation time: `GIS Strategic Planning Manager` at Geographic Technologies Group (`Remote`) and `GIS Web Developer` at CAI Technologies (`Remote`).

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, validated existing Dive path via MotherDuck counts and relevant GJC row samples, confirmed no sharing, then closed. ACC-001/002/003 satisfied.
