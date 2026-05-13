# General Board MVP Extractor

ID: ticket:20260513-general-board-mvp-extractor
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - introduces a new broad discovery source kind and external integration
Priority: medium - follows source research and creates the first observable discovery path
Depends On: ticket:20260513-general-board-source-research

## Summary

Implement one researched broad job-board source as a new extractor/pipeline that writes normalized rows in the existing Dream Job Radar raw schema. The single closure claim is that one MVP general-discovery source can produce high-precision, provenance-rich rows locally without changing curated source behavior.

## Related Records

- `plan:20260513-general-job-board-discovery` - owns the vertical MVP route and non-goals.
- `ticket:20260513-general-board-source-research` - selected RemoteOK as the MVP source.
- `research:20260513-general-board-source-selection` - records the source comparison, rejected paths, and RemoteOK field mapping.
- `.loom/wiki/extractor-shape.md` - defines the schema, dlt resource shape, and raw layout to preserve.
- `src/dream_job_radar/extractors/` - expected location for extractor implementation.
- `src/dream_job_radar/pipelines/` - expected location for source-kind pipeline implementation.

## Scope

May add one extractor module and one pipeline module for the selected source, plus narrow tests or validation helpers if appropriate. Must not wire cron or the meta-runner unless needed only for local validation. Must not add more than one general source. Must not relax title/location precision beyond the research conclusion. Must not use browser automation, credentialed scraping, or anti-bot bypassing.

## Acceptance

- ACC-001: The new extractor emits canonical rows with stable provenance and fields compatible with `current_open_roles`.
  - Evidence: Local run or unit-level validation shows rows include company, source_kind, ats_slug, role_id, title, url, location, posted_at, fetched_at, and raw_json.
  - Audit: Review should challenge schema drift and unstable identifiers.

- ACC-002: The extractor applies high-precision title/source filtering appropriate to the selected source before writing rows.
  - Evidence: Logs or tests show matched and skipped roles, including why noisy roles are excluded.
  - Audit: Review should challenge whether broad aggregator noise is entering raw output unnecessarily.

- ACC-003: Existing curated source behavior is unchanged.
  - Evidence: Diff inspection and targeted commands show no unrelated edits to existing extractor semantics.
  - Audit: Review should challenge opportunistic cleanup or cross-source behavior changes.

## Current State

Closed. Added `src/dream_job_radar/extractors/remoteok.py` and `src/dream_job_radar/pipelines/remoteok.py`. The extractor fetches `https://remoteok.com/api`, keeps `source_kind = remoteok` and `ats_slug = remoteok`, uses RemoteOK `id` as `role_id`, and normalizes rows to company, source_kind, ats_slug, role_id, title, url, location, posted_at, fetched_at, and raw_json.

The MVP filter is strict technical and mid-to-staff oriented. It excludes support, sales, admin, marketing, writing, customer success, junior/intern, VP/director/executive, and other non-target rows before writing raw data. Current probe matched 16 of 98 RemoteOK rows and skipped 82. Source-only pipeline runs with `uv run python -m dream_job_radar.pipelines.remoteok` loaded 16 rows without failed jobs.

No separate audit was run because this is a narrow new source slice with command evidence and downstream integration validation; `ticket:20260513-general-board-pipeline-integration` carries the cross-surface validation.

## Journal

- 2026-05-13: Created ticket with Status `open` as the one-source implementation slice for `plan:20260513-general-job-board-discovery`.
- 2026-05-13: Source research closed with RemoteOK selected; ticket is ready to start from `research:20260513-general-board-source-selection`.
- 2026-05-13: Set Status `active`. Re-probed `https://remoteok.com/api`; endpoint returned 200 JSON with 98 job records and stable-looking `id`, `position`, `company`, `url`, and `location` fields.
- 2026-05-13: Added RemoteOK extractor and pipeline. Validated filter output with 16 matched / 82 skipped rows. Ran `uv run python -m dream_job_radar.pipelines.remoteok`; dlt loaded 16 `remoteok/remoteok` rows with no failed jobs. Closed ticket; ACC-001/002/003 satisfied.
