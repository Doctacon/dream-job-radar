# Radar Quality Cleanup Validation

ID: evidence:20260513-radar-quality-cleanup-validation
Type: Evidence Dossier
Status: recorded
Created: 2026-05-13
Updated: 2026-05-13
Observed: 2026-05-13

## Summary

Validation dossier for `ticket:20260513-radar-quality-cleanup`, covering user-facing seniority exclusions and the Dive recent KPI/table mismatch.

## Observations

- Observation: The original mismatch was caused by the Dive table query, not the KPI query.
  - Procedure/source: inspected `.dive-preview/src/dive.tsx` and queried MotherDuck.
  - Actual result: KPI query counted all recent rows; the recent roles query had `LIMIT 10`. Before cleanup, recent count was `32` while the rendered query returned `10` rows.
- Observation: `motherduck/views.sql` now excludes unwanted seniority/title patterns from `relevant_open_roles`.
  - Procedure/source: source inspection and `uv run python scripts/apply_views.py`.
  - Actual result: view materialized successfully after adding a title-quality regex for junior, entry-level, intern, graduate, director, executive, VP, vice president, and chief patterns.
- Observation: Broad-source extractors touched by the reported rows were tightened.
  - Procedure/source: `uv run python -m dream_job_radar.pipelines.techjobsforgood` and `uv run python -m dream_job_radar.pipelines.eightythousandhours`.
  - Actual result: 80,000 Hours yielded `103` matches after excluding junior/graduate titles; Tech Jobs for Good yielded `28` matches after excluding junior/director/executive/etc. titles. A parallel dlt validation attempt first caused a local pipeline-state race for Tech Jobs for Good; rerunning Tech Jobs for Good sequentially loaded successfully with no failed jobs.
- Observation: The Dive was updated to align recent KPI and table semantics.
  - Procedure/source: local edit to `.dive-preview/src/dive.tsx`, then MotherDuck MCP `edit_dive_content` on Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f`.
  - Actual result: live Dive current version is `10`; the recent query no longer has `LIMIT 10`, and the section title includes the recent total.
- Observation: Python compile validation passed.
  - Procedure/source: `uv run python -m compileall src scripts`.
  - Actual result: command completed successfully.
- Observation: Final MotherDuck validation showed no unwanted seniority rows and aligned recent counts.
  - Procedure/source: read-only DuckDB query against MotherDuck via local env credentials after applying views.
  - Actual result: `relevant_open_roles` source counts were `ashby=1`, `eightythousandhours=20`, `gjc=2`, `greenhouse=12`, `remoteok=2`, `techjobsforgood=16`; recent KPI count was `27`; recent list query count was `27`; unwanted seniority query returned `[]`.
- Observation: Health check passed.
  - Procedure/source: `uv run python scripts/health_check.py`.
  - Actual result: `PASS`; `page/felt` remained the known zero-match stale warning.

## What This Shows

- `ticket:20260513-radar-quality-cleanup#ACC-001` - supports - `relevant_open_roles` excludes the unwanted seniority/title patterns and validation returned zero matching rows.
- `ticket:20260513-radar-quality-cleanup#ACC-002` - supports - 80,000 Hours and Tech Jobs for Good extractors yielded fewer, cleaner rows after source-side filters were added.
- `ticket:20260513-radar-quality-cleanup#ACC-003` - supports - Dive recent query no longer silently caps at 10 and title includes the recent total.
- `ticket:20260513-radar-quality-cleanup#ACC-004` - supports - final validation showed recent count/list count both equal `27` and unwanted seniority rows equal `[]`.
- `ticket:20260513-radar-quality-cleanup#ACC-005` - supports - compile and health checks passed.
- `ticket:20260513-radar-quality-cleanup#ACC-006` - supports - live Dive was updated to version `10`.

## What This Does Not Show

- It does not delete historical raw parquet rows; the relevance view hides unwanted rows immediately and extractor filters reduce future raw noise.
- It does not prove every possible unwanted title synonym is covered.
- It does not share MotherDuck data with the organization; the Dive remains dependent on existing private database access.
- It does not run a browser screenshot of the live Dive.

## Related Records

- `ticket:20260513-radar-quality-cleanup` - cleanup ticket consuming this evidence.
- Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` - updated to version `10`.
