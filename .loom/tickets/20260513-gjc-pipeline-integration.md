# GJC Pipeline Integration

ID: ticket:20260513-gjc-pipeline-integration
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: low - source should be isolated and RSS-backed
Priority: medium - required for recurring GJC refresh
Depends On: ticket:20260513-gjc-location-parsing

## Summary

Wire GJC into local and scheduled refresh, update docs, apply views, and validate MotherDuck surfaces. The single closure claim is that GJC refreshes safely and eligible rows appear through the existing relevance path.

## Related Records

- `plan:20260513-gis-jobs-clearinghouse-rss` - owns the integration milestone.
- `src/dream_job_radar/pipelines/radar.py` - local all-source runner.
- `.github/workflows/refresh.yml` - scheduled refresh workflow.
- `README.md` - source documentation target.

## Scope

May edit runner, workflow, README, extractor-shape wiki, and Loom records. Must keep GJC failures isolated from existing source refresh.

## Acceptance

- ACC-001: GJC runs in local and scheduled refresh with failure isolation.
- ACC-002: MotherDuck validation shows GJC rows in `current_open_roles` and eligible rows in `relevant_open_roles` when present.
- ACC-003: Health check passes.

## Current State

Closed. GJC is wired into `src/dream_job_radar/pipelines/radar.py` with exception isolation and into `.github/workflows/refresh.yml` with `continue-on-error: true`. README documents the `gjc/rss` source and manual command. `.loom/wiki/extractor-shape.md` includes GIS Jobs Clearinghouse as source kind `gjc`.

Validation ran `uv run python -m compileall src scripts`, `uv run python -m dream_job_radar.pipelines.radar`, `uv run python scripts/apply_company_domain_review.py`, `uv run python scripts/apply_views.py`, and `uv run python scripts/health_check.py`. Health check passed with `gjc/rss` fresh and `latest_count=10`.

MotherDuck validation after all-source refresh: `current_open_roles = 194`, `relevant_open_roles = 37`, GJC current rows `10`, GJC relevant rows `2`.

No separate audit was run because local, scheduled-path, view, and health validations support the integration claim.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, wired GJC into local/scheduled refresh, updated docs/wiki, ran all-source and health validation, then closed. ACC-001/002/003 satisfied.
