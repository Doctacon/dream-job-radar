# Re-enable RemoteOK Schedule

ID: ticket:20260513-reenable-remoteok-schedule
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - reintroduces broad discovery into scheduled refresh
Priority: medium - only safe after company/domain gate validation
Depends On: ticket:20260513-company-domain-gate

## Summary

Re-enable RemoteOK in scheduled refresh after company/domain gating proves broad-discovery rows cannot pollute the user-facing Dive. The single closure claim is that RemoteOK runs automatically again with failure isolation and relevance gating intact.

## Related Records

- `plan:20260513-company-domain-relevance` - owns the safe re-enable milestone.
- `.github/workflows/refresh.yml` - expected workflow target.
- `src/dream_job_radar/pipelines/radar.py` - local all-source runner may also need alignment.

## Scope

May edit scheduled workflow and README. May run validation. Must not re-enable RemoteOK before `ticket:20260513-company-domain-gate` closes.

## Acceptance

- ACC-001: Scheduled RemoteOK refresh is enabled with continue-on-error/failure isolation.
- ACC-002: Validation after a run shows broad rows pass through company/domain gating before `relevant_open_roles`.
- ACC-003: README no longer describes RemoteOK as disabled pending gate.

## Current State

Closed. `.github/workflows/refresh.yml` re-enables the `RemoteOK pipeline` step with `continue-on-error: true` before company-domain review seed/view application. README no longer describes RemoteOK as disabled; it describes RemoteOK as broad discovery gated by company-domain review/rules in `relevant_open_roles`.

Validation ran `uv run python -m dream_job_radar.pipelines.remoteok`, `uv run python scripts/apply_company_domain_review.py`, and `uv run python scripts/apply_views.py`. RemoteOK loaded 16 rows, `current_open_roles` contained 16 RemoteOK rows, and `relevant_open_roles` contained 0 RemoteOK rows because no current RemoteOK row satisfies both location and company/domain relevance. Curated relevant counts remained `ashby = 1` and `greenhouse = 13`.

No separate audit was run because the workflow re-enable is guarded by direct validation of the domain gate after a fresh RemoteOK run.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, re-enabled scheduled RemoteOK with failure isolation, updated README, ran RemoteOK plus seed/view validation, and closed. ACC-001/002/003 satisfied.
