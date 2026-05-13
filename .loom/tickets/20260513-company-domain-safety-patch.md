# Company Domain Safety Patch

ID: ticket:20260513-company-domain-safety-patch
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: low - temporarily hides broad-discovery rows from the user-facing view while preserving raw inventory
Priority: high - prevents irrelevant broad-discovery companies from appearing in the live Dive

## Summary

Immediately stop RemoteOK broad-discovery rows from appearing in `relevant_open_roles` and remove RemoteOK from scheduled refresh until company/domain relevance gating exists. The single closure claim is that Natera-like RemoteOK rows remain in raw/current inventory but cannot appear in the normal Dive surface.

## Related Records

- `plan:20260513-company-domain-relevance` - owns the broader retrieval strategy.
- `plan:20260513-general-job-board-discovery` - completed RemoteOK MVP and exposed the company-fit gap.
- `motherduck/views.sql` - user-facing relevance view to patch.
- `.github/workflows/refresh.yml` - scheduled refresh to disable for RemoteOK.
- `README.md` - should state RemoteOK is manual/raw-only pending company-domain gating.

## Scope

May edit `motherduck/views.sql`, `.github/workflows/refresh.yml`, and README. May apply views and run validation. Must not delete RemoteOK raw data, remove the RemoteOK extractor, or purge `current_open_roles`. Must not implement the full company-domain classifier in this ticket.

## Acceptance

- ACC-001: `relevant_open_roles` excludes RemoteOK rows while retaining RemoteOK rows in `current_open_roles`.
  - Evidence: MotherDuck query shows `remoteok` count is nonzero in `current_open_roles` and zero in `relevant_open_roles`.
  - Audit: Review should challenge whether the patch accidentally hides curated sources.

- ACC-002: Scheduled refresh no longer runs RemoteOK until the domain gate lands.
  - Evidence: Workflow diff removes the RemoteOK scheduled step or otherwise disables it explicitly.
  - Audit: Review should challenge whether an automatic scheduled path still refreshes RemoteOK.

- ACC-003: Documentation warns that RemoteOK is raw/manual only pending company/domain relevance.
  - Evidence: README diff names the pending gate and manual status.
  - Audit: Review should challenge whether future agents might treat RemoteOK as fully radar-ready.

## Current State

Closed. `motherduck/views.sql` now explicitly excludes `source_kind = 'remoteok'` from `relevant_open_roles` until broad-discovery company/domain relevance gating exists. `.github/workflows/refresh.yml` no longer runs the RemoteOK pipeline in scheduled refresh. `README.md` now describes RemoteOK as manual/raw-only pending the company-domain gate.

Validation ran `uv run python scripts/apply_views.py`, `uv run python -m compileall src scripts`, and `uv run python scripts/health_check.py`. MotherDuck validation observed RemoteOK rows remain available in `current_open_roles` (`16`) and are absent from `relevant_open_roles` (`0`). Overall counts after the patch were `current_open_roles = 148` and `relevant_open_roles = 14`; relevant rows came from curated `ashby` (`1`) and `greenhouse` (`13`) only.

No separate audit was run because this is a narrow safety patch with direct view/workflow validation; the follow-up domain gate ticket carries the broader semantic review.

## Journal

- 2026-05-13: Created and set Status `active` as the first execution unit for `plan:20260513-company-domain-relevance`.
- 2026-05-13: Hid RemoteOK from `relevant_open_roles`, removed scheduled RemoteOK workflow step, documented RemoteOK as manual/raw-only pending gate, applied views, validated counts, and closed. ACC-001/002/003 satisfied.
