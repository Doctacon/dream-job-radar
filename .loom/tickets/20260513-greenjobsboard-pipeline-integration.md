# Green Jobs Board Pipeline Integration

ID: ticket:20260513-greenjobsboard-pipeline-integration
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: low - source should be isolated from existing refresh
Priority: medium - required for recurring Green Jobs Board refresh
Depends On: ticket:20260513-greenjobsboard-domain-gate

## Summary

Wire Green Jobs Board into local and scheduled refresh with failure isolation, update docs, apply views, and validate MotherDuck/health state. The single closure claim is that Green Jobs Board refreshes safely without breaking existing sources.

## Related Records

- `src/dream_job_radar/pipelines/radar.py` - local all-source runner.
- `.github/workflows/refresh.yml` - scheduled refresh workflow.
- `README.md` - source documentation target.
- `.loom/wiki/extractor-shape.md` - source-kind documentation target.

## Scope

May edit runner, workflow, README, wiki, and Loom records. Must keep source failure isolated.

## Acceptance

- ACC-001: Green Jobs Board runs in local/scheduled refresh with failure isolation.
- ACC-002: MotherDuck validation shows Green Jobs Board current/relevant counts.
- ACC-003: Health check passes.

## Current State

Closed. Green Jobs Board is wired into the local all-source runner and scheduled refresh workflow with failure isolation, docs/wiki were updated, views applied, MotherDuck counts were checked, and health passed. Evidence is recorded in `evidence:20260513-greenjobsboard-80000hours-validation`. Separate audit was not run because acceptance is covered by direct command/query evidence and the workflow keeps the source isolated.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Wired Green Jobs Board into `radar.py`, `.github/workflows/refresh.yml`, `README.md`, and `.loom/wiki/extractor-shape.md`.
- 2026-05-13: Full radar refresh, view application, count query, and health check passed; closed ticket.
