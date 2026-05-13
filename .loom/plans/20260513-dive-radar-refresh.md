# Dive Radar Refresh

ID: plan:20260513-dive-radar-refresh
Type: Plan
Status: completed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - coordinates public Dive semantics, live MotherDuck queries, local preview parity, and project-facing explanation.

## Summary

Refresh the Dream Job Radar Dive so it tells a coherent product story instead of mixing incompatible counts. The current Dive headline says it shows roles posted or first observed in the last 7 days, but the daily snapshot strip counts the full Iceberg mart inventory. This plan makes the primary Dive story the current matching open-role inventory, keeps new or recent roles as a separate lens, repairs the snapshot section so its metric contract is honest, and preserves local/live Dive parity.

This needs more than one ticket because metric semantics, visual/product design, live Dive publishing, and durable documentation have different closure claims and evidence paths.

## Related Records

- `.loom/plans/lakehouse-iceberg.md` - existing strategy that introduced `mart.job_postings_daily_snapshot` and the Dive panel as the public Iceberg proof point.
- `.loom/tickets/20260504-0y0u48df-iceberg-mart-dive-panel.md` - closed ticket that added the current daily snapshot strip and records its original acceptance posture.
- `.dive-preview/src/dive.tsx` - local mirror of live Dive version 6; must stay aligned with any published Dive update.
- `motherduck/views.sql` - defines `current_open_roles`, the source view behind the Dive's current role list and KPI queries.
- `src/dream_job_radar/pipelines/iceberg_mart.py` - defines the Iceberg mart snapshot semantics: append one full `current_open_roles` snapshot per UTC day and materialize it into MotherDuck.
- Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` - current published Dive titled `dream-job-radar - open roles`, version 6 as of plan creation.

## Strategy

Use a contract-first route. First make the metric contract explicit so later UI work does not preserve the current mismatch. The approved direction is: the Dive's primary freshness story is current matching open-role inventory. Daily snapshots track that inventory over time. Roles posted or first observed in the last 7 days become a secondary "new/recent this week" lens, not the top-level definition of the entire Dive.

After the contract is explicit, repair the snapshot section so its SQL, copy, and visual treatment describe the full inventory snapshot honestly. Then redesign the Dive's product story around a compact set of sections: inventory KPIs, inventory-over-time trend, recent/new roles, and a company/source breakdown when it earns its space. Finally publish only after local preview and live Dive content tell the same story, then update project documentation or Loom knowledge so future work does not rediscover the metric distinction.

Tickets should inherit these validation expectations:

- Use MotherDuck read-only probes before changing visuals when a metric is involved.
- Keep saved Dive SQL fully qualified and double-quoted, e.g. `"acorn-granary"."mart"."job_postings_daily_snapshot"`.
- Do not update the live Dive without first preparing or inspecting the local mirror.
- Do not change the Iceberg writer, cron workflow, or mart schema unless a ticket explicitly routes back to this plan for re-scope.
- If implementation shows the mart cannot answer the chosen contract without schema changes, stop and replan instead of silently widening scope.

## Execution Units

### Unit: Metric Contract

Ticket: ticket:20260513-dive-metric-contract

Make the metric semantics executable for the remaining tickets. The outcome is a concise contract saying the Dive's primary story is current matching open-role inventory; the daily snapshot history tracks full inventory over time; and last-7-day roles are a secondary recent/new lens. Scope is limited to Loom records and read-only MotherDuck evidence. This must run first because every later query, label, and layout depends on it. Evidence should include probes comparing current `current_open_roles` counts, full mart snapshot counts, and recent-role counts so the contract is grounded in live data. Stop and return to plan shaping if the live data contradicts the approved direction or reveals a data-quality issue that changes the contract.

### Unit: Snapshot Repair

Ticket: ticket:20260513-dive-snapshot-repair

Repair the Daily Snapshot section so the chart/query/copy agree with the metric contract. Likely scope includes `.dive-preview/src/dive.tsx` and the live Dive content, with read-only MotherDuck query evidence. The single closure claim is that the snapshot section honestly represents full current open-role inventory by UTC snapshot day and no longer appears to be the same metric as last-7-day recent roles. This depends on `ticket:20260513-dive-metric-contract`.

### Unit: Product Story Refresh

Ticket: ticket:20260513-dive-product-story

Reshape the Dive from a crude KPI/table page into a compact, intentional radar. Scope is the React Dive presentation and SQL query selection, not source ingestion or mart writing. The refreshed story should distinguish inventory, recent/new roles, company/source coverage, and role detail without duplicative chart/table clutter. This follows the snapshot repair so the design builds on stable metric semantics.

### Unit: Local And Live Parity

Ticket: ticket:20260513-dive-code-parity

Publish and verify the final Dive update only after the local mirror reflects the intended component. Scope includes `.dive-preview/src/dive.tsx`, the live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f`, local preview/build checks when feasible, and `read_dive` verification after publish. This ticket owns parity and publication evidence; earlier tickets may prepare content but should not claim live parity unless this ticket completes.

### Unit: Documentation And Retrospective

Ticket: ticket:20260513-radar-docs-retro

Preserve the accepted metric semantics and implementation lessons after the Dive refresh. Scope includes README/Loom knowledge or related records that future agents will load when touching the Dive, the Iceberg mart, or MotherDuck query semantics. This follows implementation because it should record what was actually accepted, not what was merely planned.

## Milestones

### Milestone: Metric Story Is Stable

Child tickets: ticket:20260513-dive-metric-contract, ticket:20260513-dive-snapshot-repair

The Dive no longer mixes a recent-role headline with a full-inventory snapshot chart. A future agent can explain which counts are inventory counts and which counts are recent/new role counts using the ticket evidence and live SQL.

### Milestone: Dive Feels Intentional

Child tickets: ticket:20260513-dive-product-story, ticket:20260513-dive-code-parity

The local mirror and live Dive present a coherent compact radar, with progressive loading and fully qualified live SQL. The published Dive version can be inspected with `read_dive` and compared against the local source.

### Milestone: Recovery Context Preserved

Child tickets: ticket:20260513-radar-docs-retro

Future Dive or mart work can recover the metric contract and accepted design posture without relying on this chat.

## Current State

Plan is completed. All five execution-unit tickets are closed: `ticket:20260513-dive-metric-contract`, `ticket:20260513-dive-snapshot-repair`, `ticket:20260513-dive-product-story`, `ticket:20260513-dive-code-parity`, and `ticket:20260513-radar-docs-retro`.

Final outcome: the Dream Job Radar Dive is inventory-first, with daily UTC inventory snapshot history and a separate last-7-day recent/new lens. Local `.dive-preview/src/dive.tsx` was updated, local build passed, the live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` was published as version 7, and README now records the accepted metric semantics. Fresh-context audit `audit:20260513-dive-radar-refresh-closure` found the implementation and README support the intended contract; its record-follow-through finding was resolved by the child ticket updates.

Residual risk: MotherDuck reported `acorn-granary` as unshared for organization viewers during the update. Sharing/permission changes were out of scope and were not changed.

## Journal

- 2026-05-13: Created plan with Status `open` and child tickets linked from the execution units. Shaping evidence included live Dive v6 inspection and read-only MotherDuck probes comparing 7-day counts against full mart snapshot counts.
- 2026-05-13: Executed all child tickets, published live Dive version 7, recorded README semantics, ran fresh-context audit, resolved the audit follow-through finding in ticket records, and marked the plan completed.
