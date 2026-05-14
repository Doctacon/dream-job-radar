# 80,000 Hours Pipeline Integration

ID: ticket:20260513-80000hours-pipeline-integration
Type: Ticket
Status: open
Created: 2026-05-13
Updated: 2026-05-13
Risk: low - source should be isolated from existing refresh
Priority: medium - required for recurring 80,000 Hours refresh
Depends On: ticket:20260513-80000hours-domain-gate

## Summary

Wire 80,000 Hours into local and scheduled refresh with failure isolation, update documentation, apply views, and validate MotherDuck/health state. The single closure claim is that 80,000 Hours refreshes safely without breaking existing sources.

## Related Records

- `plan:20260513-80000hours-public-algolia-mvp` - owns source strategy.
- `src/dream_job_radar/pipelines/radar.py` - local all-source runner.
- `.github/workflows/refresh.yml` - scheduled refresh workflow.
- `README.md` - source and run documentation target.
- `.loom/wiki/extractor-shape.md` - source-kind documentation target.

## Scope

May edit runner, workflow, README, wiki, and Loom records. Must keep source failure isolated and must not change the daily refresh cadence beyond the source contract.

## Acceptance

- ACC-001: 80,000 Hours runs in local/scheduled refresh with failure isolation.
- ACC-002: Documentation lists the source kind, slug, run command, and broad-source gating posture.
- ACC-003: MotherDuck validation shows 80,000 Hours current/relevant counts after views are applied.
- ACC-004: Health check passes or any expected zero-row behavior is explicitly handled without hiding real regressions.

## Current State

Ready after the domain gate ticket closes.

## Journal

- 2026-05-13: Created ticket with Status `open`.
