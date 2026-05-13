# Dive Local And Live Parity

ID: ticket:20260513-dive-code-parity
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - publishes live Dive changes and verifies local/live source parity.
Depends On: ticket:20260513-dive-product-story

## Summary

Publish the refreshed Dream Job Radar Dive and verify that the live Dive and local preview mirror tell the same story. This ticket owns the publication and parity closure claim: `.dive-preview/src/dive.tsx` and live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` are aligned, the live Dive version is recorded, and validation evidence supports the update.

## Related Records

- `plan:20260513-dive-radar-refresh` - parent plan and publication sequencing.
- `ticket:20260513-dive-product-story` - design/content implementation expected before publication.
- `.dive-preview/src/dive.tsx` - local source to compare against live Dive content.
- `.dive-preview/package.json` - local preview/build command source.
- Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` - publication target.

## Scope

In scope:

- Validate local preview or build using the existing `.dive-preview` project where feasible.
- Update live Dive content through MotherDuck MCP after local content is ready and approved by the implementation ticket evidence.
- Read back the live Dive with `read_dive` and record the version.
- Compare key source markers between local and live content.

Out of scope:

- Further product redesign beyond parity fixes required to publish safely.
- Data pipeline, view, mart, or cron changes.
- Sharing/permission changes for the Dive unless the publish step reveals a concrete access blocker.

Stop and return to the parent plan if the MotherDuck Dive MCP tools fail in a way that requires manual operator resolution; do not manually fix MCP server configuration.

## Acceptance

- ACC-001: Local validation passes or any skipped validation is explicitly justified.
  - Evidence: Command output from the existing local preview/build path, or a recorded reason validation could not run.
  - Audit: Review should challenge whether skipped validation leaves material runtime risk.

- ACC-002: Live Dive is updated to a new version and the version number is recorded.
  - Evidence: MotherDuck `read_dive` or `list_dives` output after update.
  - Audit: Review should challenge whether the updated live content is the intended refreshed content, not a stale intermediate.

- ACC-003: Local and live Dive content match on required databases, table references, metric labels, and section hierarchy.
  - Evidence: Source comparison or explicit inspection notes after `read_dive`.
  - Audit: Review should challenge any intentional differences and require them to be named.

- ACC-004: Live Dive queries use fully qualified quoted table names and preserve progressive loading behavior.
  - Evidence: `read_dive` content inspection.
  - Audit: Review should focus on saved Dive runtime compatibility.

## Current State

Closed. Local validation ran in `.dive-preview` with `npm exec vite build` and passed; Vite emitted only the dependency chunk-size warning. The live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` was updated through MotherDuck MCP, then read back successfully as current version `7` with updated description and source containing the same required database, fully qualified table references, metric labels, section hierarchy, and progressive loading paths as the local component.

Known parity note: MotherDuck normalizes `REQUIRED_DATABASES` formatting in the read-back content to single quotes and no trailing comma, but the database path and alias match the local file. MotherDuck update returned `unshared_databases: ["acorn-granary"]`; this is not a regression from this ticket because sharing/permission changes were out of scope unless requested. Audit `audit:20260513-dive-radar-refresh-closure` did not independently query the live Dive, so the live parity claim rests on implementation-context `read_dive` evidence; `FIND-001` record follow-through is resolved here.

## Journal

- 2026-05-13: Created ticket with Status `open` as the publication/parity slice for the Dive refresh.
- 2026-05-13: Built local preview, published the refreshed component to the live Dive, read back version 7, verified key parity markers, and closed after audit follow-through.
