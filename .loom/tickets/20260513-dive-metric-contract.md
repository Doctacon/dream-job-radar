# Dive Metric Contract

ID: ticket:20260513-dive-metric-contract
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - metric semantics constrain subsequent live Dive queries and public-facing copy.
Priority: high - downstream Dive repair and redesign depend on this contract.

## Summary

Define the metric contract for the refreshed Dream Job Radar Dive. The approved direction is that the Dive's primary story is current matching open-role inventory, daily snapshots track that full inventory over time, and roles posted or first observed in the last 7 days are a secondary recent/new lens. This ticket closes when the contract is recorded with read-only MotherDuck evidence and downstream tickets can implement from it without relying on chat.

## Related Records

- `plan:20260513-dive-radar-refresh` - parent plan that sequences this contract before visual repair.
- `.loom/tickets/20260504-0y0u48df-iceberg-mart-dive-panel.md` - original Dive snapshot ticket whose last-7-day page context now needs clarification.
- `.dive-preview/src/dive.tsx` - current local Dive mirror where `RECENT_FILTER` drives the headline KPIs and role list.
- `src/dream_job_radar/pipelines/iceberg_mart.py` - establishes that the mart stores one full `current_open_roles` snapshot per UTC day.
- Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` - published surface whose metric story is being corrected.

## Scope

In scope:

- Read-only MotherDuck probes over `"acorn-granary"."main"."current_open_roles"` and `"acorn-granary"."mart"."job_postings_daily_snapshot"`.
- A durable contract statement in this ticket or a linked Loom record that later tickets can cite.
- Explicit naming of inventory metrics versus recent/new metrics.

Out of scope:

- Editing `.dive-preview/src/dive.tsx` or the live Dive.
- Changing `motherduck/views.sql`, the Iceberg mart writer, cron workflow, or mart schema.
- Choosing a complete visual redesign.

Stop and return to plan shaping if the live data suggests the mart is not a full `current_open_roles` snapshot or if the approved inventory-first direction cannot be supported without schema changes.

## Acceptance

- ACC-001: The ticket records a concise metric contract: primary Dive inventory, daily inventory history, and separate recent/new lens.
  - Evidence: Ticket Current State or Journal includes the final contract in plain language.
  - Audit: Closure review should challenge whether later tickets can implement queries and copy from the contract without unstated chat context.

- ACC-002: Read-only MotherDuck evidence compares full inventory, current recent count, and mart snapshot history.
  - Evidence: Query outputs or summarized evidence include counts equivalent to current `current_open_roles`, current last-7-day roles, and per-day mart snapshot counts.
  - Audit: Closure review should challenge whether the evidence proves the mismatch being corrected and supports the chosen direction.

- ACC-003: The ticket identifies which existing labels or concepts must change downstream.
  - Evidence: Current State names at least the headline copy, KPI semantics, snapshot section caption, and recent roles section as affected downstream concepts.
  - Audit: Separate audit is useful if the contract is ambiguous; otherwise ticket closure may explain why the contract is straightforward after evidence.

## Current State

Closed. The accepted metric contract is: the Dive's primary story is current matching open-role inventory from `"acorn-granary"."main"."current_open_roles"`; daily snapshot history tracks that full inventory once per UTC day from `"acorn-granary"."mart"."job_postings_daily_snapshot"`; roles posted or first observed in the last 7 days are a separate recent/new lens.

Read-only MotherDuck evidence on 2026-05-13 supported the contract and mismatch being corrected: current inventory returned 131 roles, 8 companies, 28 locations, and last refresh `2026-05-13 17:14 UTC`; the recent lens returned 41 roles across 4 companies; mart snapshot counts returned 120, 123, 123, 123, 123, 125, 125, 125, and 128 rows for UTC dates 2026-05-05 through 2026-05-13.

Downstream labels and concepts that needed to change were the headline copy, KPI semantics, snapshot section caption, and recent roles section. Audit `audit:20260513-dive-radar-refresh-closure` found no material issue with the contract itself; `FIND-001` only required ticket record follow-through and is resolved here.

## Journal

- 2026-05-13: Created ticket with Status `open` from `plan:20260513-dive-radar-refresh`. Operator approved inventory-first primary story with recent/new roles as a separate lens.
- 2026-05-13: Ran read-only MotherDuck probes comparing full inventory, recent-role count, and mart snapshot history; recorded final metric contract and closed the ticket.
