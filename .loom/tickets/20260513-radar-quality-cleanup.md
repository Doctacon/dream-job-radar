# Radar Quality Cleanup

ID: ticket:20260513-radar-quality-cleanup
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - changes user-facing relevance semantics and Dive rendering
Priority: high - fixes misleading recent count and unwanted seniority rows

## Summary

Clean up the user-facing Dream Job Radar after source expansion. The single closure claim is that `relevant_open_roles` excludes unwanted junior/director-level roles and the Dive recent KPI/table tell one consistent story.

## Related Records

- `.dive-preview/src/dive.tsx` - owns the local Dive query/render behavior.
- `motherduck/views.sql` - owns `current_open_roles` and `relevant_open_roles` semantics.
- `src/dream_job_radar/extractors/techjobsforgood.py` - broad source currently yielding junior/director rows.
- `src/dream_job_radar/extractors/eightythousandhours.py` - broad source title filter should remain aligned with user-facing seniority exclusions.
- `evidence:20260513-80000hours-mvp-validation` - prior evidence that source expansion changed recent/relevant counts.

## Scope

May edit the Dive preview, MotherDuck view SQL, broad-source extractor title filters, this ticket, and evidence records. May apply views, run pipelines or health checks, and publish the Dive if the local Dive changes validate. Must not delete raw parquet data or share MotherDuck data.

## Acceptance

- ACC-001: `relevant_open_roles` excludes junior, entry-level, intern, graduate, director, executive, VP, vice president, and chief title patterns.
- ACC-002: Broad-source extractors touched by current evidence stop yielding the same unwanted seniority patterns in future runs.
- ACC-003: The Dive recent KPI and recent list semantics align: the table returns all recent rows or explicitly communicates any displayed cap.
- ACC-004: Validation shows zero unwanted seniority rows in `relevant_open_roles` and shows recent count/list alignment.
- ACC-005: Health/compile checks pass, or any failure is recorded with a concrete blocker.
- ACC-006: If the Dive is published, the ticket records the resulting version or URL evidence; if not published, the reason is explicit.

## Current State

Closed. `relevant_open_roles` now excludes junior/entry/intern/graduate/director/executive/VP/chief title patterns; Tech Jobs for Good and 80,000 Hours source filters were tightened; the Dive recent query no longer silently limits to 10 rows; the live Dive was updated to version `10`. Evidence is recorded in `evidence:20260513-radar-quality-cleanup-validation`. Separate audit was not run because the cleanup is directly supported by SQL count validation, compile, source pipeline runs, health check, and live Dive version verification.

## Journal

- 2026-05-13: Created ticket and set Status `active` for cleanup execution.
- 2026-05-13: Added central title-quality exclusions to `motherduck/views.sql` and applied the view.
- 2026-05-13: Tightened Tech Jobs for Good and 80,000 Hours source filters; Tech Jobs for Good was rerun sequentially after a local dlt state race from a parallel validation attempt.
- 2026-05-13: Removed the Dive recent-list `LIMIT 10`, added recent total to the section title, and published live Dive version `10`.
- 2026-05-13: Final validation showed recent count/list count both `27`, unwanted seniority rows `[]`, and health `PASS`; closed ticket.
