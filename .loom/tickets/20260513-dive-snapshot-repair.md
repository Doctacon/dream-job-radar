# Dive Snapshot Repair

ID: ticket:20260513-dive-snapshot-repair
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - changes public Dive semantics and live MotherDuck query presentation.
Priority: high - fixes the visible confusing snapshot section before broader polish.
Depends On: ticket:20260513-dive-metric-contract

## Summary

Repair the Dream Job Radar Daily Snapshot section so its SQL, labels, and visual treatment honestly represent full current open-role inventory by UTC snapshot day. The current strip counts all rows in `mart.job_postings_daily_snapshot`, but surrounding copy frames the page as last-7-day roles. This ticket closes when the snapshot section no longer appears to be the same metric as recent/new roles and the local Dive mirror reflects the repaired section.

## Related Records

- `plan:20260513-dive-radar-refresh` - parent plan and sequencing context.
- `ticket:20260513-dive-metric-contract` - defines the metric contract this ticket implements.
- `.dive-preview/src/dive.tsx` - primary code-facing write boundary for the local Dive mirror.
- `.loom/tickets/20260504-0y0u48df-iceberg-mart-dive-panel.md` - original implementation notes and acceptance for the current snapshot strip.
- Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` - eventual publication target; publication may be finalized by `ticket:20260513-dive-code-parity`.

## Scope

In scope:

- Update local Dive copy and section naming around daily snapshots.
- Update the snapshot query if needed to express inventory history explicitly.
- Replace the crude equal-height strip if a minimal clearer representation is needed, but keep this ticket focused on semantic repair rather than full redesign.
- Gather read-only MotherDuck evidence for the snapshot query used by the section.

Out of scope:

- Changing the Iceberg writer, mart schema, cron workflow, or `current_open_roles` view.
- Full Dive redesign beyond the snapshot section.
- Final live publication parity unless explicitly coordinated with `ticket:20260513-dive-code-parity`.

Stop and return to plan shaping if the snapshot repair requires a different mart table shape or historical backfill.

## Acceptance

- ACC-001: Snapshot section copy explicitly says it tracks current matching open-role inventory snapshots by UTC day, not roles newly posted in the last 7 days.
  - Evidence: Inspection of `.dive-preview/src/dive.tsx` after the edit.
  - Audit: Closure review should challenge whether a reasonable viewer could still confuse the snapshot metric with the recent/new lens.

- ACC-002: Snapshot SQL is fully qualified and consistent with the metric contract.
  - Evidence: Read-only MotherDuck query output for the same aggregate shape used in the Dive; source inspection shows fully qualified quoted table references in saved/live-ready Dive SQL.
  - Audit: Closure review should challenge whether the query is measuring full inventory history rather than recent roles.

- ACC-003: The section has loading and empty states that still describe inventory semantics.
  - Evidence: Source inspection or local preview confirms loading/empty paths do not use misleading recent-role language.
  - Audit: Separate audit should focus on semantic correctness, not broad visual polish.

## Current State

Closed. `.dive-preview/src/dive.tsx` now names the section `Inventory history` / `Daily UTC snapshots` and states that each point is the full current matching open-role inventory captured once per UTC day, not the last-7-day recent-role count. The snapshot SQL uses the fully qualified quoted table `"acorn-granary"."mart"."job_postings_daily_snapshot"`, groups by formatted `snapshot_date`, and counts full rows without the recent filter. Loading and empty states use inventory wording.

Evidence: MotherDuck snapshot probe returned UTC daily inventory counts from 2026-05-05 through 2026-05-13 ending at 128 rows; source inspection confirms the saved-ready local query and copy. Audit `audit:20260513-dive-radar-refresh-closure` found the local Dive supports the inventory-vs-recent contract; `FIND-001` record follow-through is resolved here.

## Journal

- 2026-05-13: Created ticket with Status `open` as the semantic repair slice after metric-contract approval.
- 2026-05-13: Repaired local Dive snapshot section copy and query semantics; closed after source inspection, MotherDuck probe evidence, and audit follow-through.
