# Tech Jobs for Good Pipeline Integration

ID: ticket:20260513-techjobsforgood-pipeline-integration
Type: Ticket
Status: open
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - wires a public HTML source into scheduled refresh
Priority: medium - required for recurring Tech Jobs for Good discovery
Depends On: ticket:20260513-techjobsforgood-domain-gate

## Summary

Wire Tech Jobs for Good into the all-source runner and scheduled refresh with failure isolation, then validate MotherDuck surfaces. The single closure claim is that Tech Jobs for Good refreshes safely and eligible rows flow through `current_open_roles` and `relevant_open_roles` without breaking existing sources.

## Related Records

- `plan:20260513-broaden-mission-source-discovery` - owns sequencing and validation posture.
- `ticket:20260513-techjobsforgood-mvp-extractor` - provides the source-kind pipeline.
- `ticket:20260513-techjobsforgood-domain-gate` - provides safe user-facing gating.
- `src/dream_job_radar/pipelines/radar.py` - local all-source runner.
- `.github/workflows/refresh.yml` - scheduled refresh workflow.
- `README.md` - expected source documentation target.

## Scope

May edit the all-source runner, scheduled workflow, README source table, and docs. May run source-specific and all-source validation commands. Must keep Tech Jobs for Good failures isolated from curated source refresh.

## Acceptance

- ACC-001: Tech Jobs for Good is wired into local and scheduled refresh with failure isolation.
- ACC-002: MotherDuck validation shows Tech Jobs for Good rows in `current_open_roles` and eligible rows in `relevant_open_roles` when present.
- ACC-003: Existing source counts and health check still pass.
- ACC-004: README documents the source and its public-visible-only constraint.

## Current State

Ready after the domain gate ticket closes.

## Journal

- 2026-05-13: Created ticket with Status `open`.
