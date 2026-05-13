# General Board Pipeline Integration

ID: ticket:20260513-general-board-pipeline-integration
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - wires a new external source into scheduled refresh and MotherDuck visibility
Priority: medium - required before discovered roles can appear in the Dive
Depends On: ticket:20260513-general-board-mvp-extractor, ticket:20260513-relevant-open-roles-view

## Summary

Wire the MVP general-board source into the project refresh path and verify its rows reach MotherDuck and the relevance surface without breaking curated sources. The single closure claim is that general discovery participates in the pipeline safely and is visible through `relevant_open_roles` before user-facing display.

## Related Records

- `plan:20260513-general-job-board-discovery` - owns the integration order and validation posture.
- `ticket:20260513-general-board-mvp-extractor` - provides the source pipeline to wire.
- `ticket:20260513-relevant-open-roles-view` - provides the relevance filter that must gate display.
- `src/dream_job_radar/pipelines/radar.py` - meta-runner expected to include the new source after validation.
- `.github/workflows/refresh.yml` - scheduled refresh workflow if a new explicit step is required.
- `README.md` - expected to document the new source once integrated.

## Scope

May update the meta-runner, GitHub Actions refresh workflow, README source list, and minimal validation notes. May run source-specific and all-source commands with `uv`. Must not change the source extractor beyond wiring fixes, must not alter curated source semantics, and must not expose discovered roles in the Dive until the display ticket.

## Acceptance

- ACC-001: The new general source runs through the project refresh path with error isolation consistent with existing sources.
  - Evidence: `uv` command output and workflow/meta-runner diff show the source is wired safely.
  - Audit: Review should challenge whether a general-source failure could break curated refresh.

- ACC-002: Discovered rows are visible in MotherDuck inventory and, where eligible, `relevant_open_roles`.
  - Evidence: MotherDuck validation queries compare source-kind counts in `current_open_roles` and `relevant_open_roles` after a run.
  - Audit: Review should challenge whether rows are actually passing relevance rather than bypassing it.

- ACC-003: Documentation identifies the new source and its provenance model.
  - Evidence: README diff names the source kind, upstream source, and expected role provenance.
  - Audit: Review should challenge whether future agents can distinguish curated company boards from broad discovery.

## Current State

Closed. `src/dream_job_radar/pipelines/radar.py` imports and runs the RemoteOK pipeline after curated sources, catching RemoteOK exceptions so a RemoteOK failure does not abort the local all-source runner. `.github/workflows/refresh.yml` includes a `RemoteOK pipeline` step with `continue-on-error: true` before view application, matching the chosen failure posture. `README.md` documents the new `remoteok/remoteok` source and manual invocation. `.loom/wiki/extractor-shape.md` now includes RemoteOK in the source-kind table.

Validation ran `uv run python -m compileall src scripts` and `uv run python -m dream_job_radar.pipelines.radar`; all source slices, including RemoteOK, completed. `uv run python scripts/apply_views.py` materialized views. `uv run python scripts/health_check.py` passed. MotherDuck validation observed `remoteok` has 16 rows in `current_open_roles` and 2 rows in `relevant_open_roles`; overall counts were `current_open_roles = 148` and `relevant_open_roles = 16`.

The relevant RemoteOK rows at validation time were `Cloud Enablement Engineer US` at Quanata (`Remote-US`) and `Manager Platform Engineering` at Natera (`US Remote`).

## Journal

- 2026-05-13: Created ticket with Status `open` as the pipeline/MotherDuck integration slice for `plan:20260513-general-job-board-discovery`.
- 2026-05-13: Wired RemoteOK into local all-source runner and scheduled workflow, documented source coverage, updated extractor-shape wiki, ran compile/all-source/apply-views/health-check, and validated RemoteOK counts in MotherDuck. Closed ticket; ACC-001/002/003 satisfied.
