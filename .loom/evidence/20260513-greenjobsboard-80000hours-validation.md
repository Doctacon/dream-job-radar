# Green Jobs Board And 80,000 Hours Validation

ID: evidence:20260513-greenjobsboard-80000hours-validation
Type: Evidence Dossier
Status: recorded
Created: 2026-05-13
Updated: 2026-05-13
Observed: 2026-05-13

## Summary

Validation dossier for Green Jobs Board integration and 80,000 Hours access feasibility under `plan:20260513-greenjobsboard-80000hours-source-expansion`.

## Observations

- Observation: Python compilation succeeded for `src` and `scripts`.
  - Procedure/source: `uv run python -m compileall src scripts` from repository root.
  - Actual result: command completed successfully after the Green Jobs Board extractor/pipeline and view edits.
- Observation: Green Jobs Board source-only pipeline ran without failed jobs.
  - Procedure/source: `uv run python -m dream_job_radar.pipelines.greenjobsboard`.
  - Actual result: extractor parsed `33` public listing cards, matched `0` strict-technical cards, and dlt completed with `0` load packages because no rows were yielded.
- Observation: Full radar refresh ran through Green Jobs Board without blocking other sources.
  - Procedure/source: `uv run python -m dream_job_radar.pipelines.radar`.
  - Actual result: all existing source slices loaded successfully; Green Jobs Board parsed `33` cards, matched `0`, and the Green Jobs Board dlt load completed with no failed jobs.
- Observation: MotherDuck review seed and views applied successfully.
  - Procedure/source: `uv run python scripts/apply_company_domain_review.py` and `uv run python scripts/apply_views.py`.
  - Actual result: commands printed `company domain review seed applied` and `view materialized`.
- Observation: MotherDuck counts after applying the broad-source domain gate remained plausible.
  - Procedure/source: read-only DuckDB query against MotherDuck via local env credentials.
  - Actual result: `current_open_roles` counts were `ashby=70`, `gjc=10`, `greenhouse=59`, `page=3`, `remoteok=16`, `techjobsforgood=36`; `relevant_open_roles` counts were `ashby=1`, `gjc=2`, `greenhouse=13`, `remoteok=1`, `techjobsforgood=20`; Green Jobs Board counts were `current=0`, `relevant=0`.
- Observation: Health check passed.
  - Procedure/source: `uv run python scripts/health_check.py`.
  - Actual result: `PASS`; `page/felt` remained a known zero-match stale warning, while observed active slugs were fresh.
- Observation: Existing Dive mirror still queries `relevant_open_roles` and exposes `source_kind` provenance.
  - Procedure/source: source inspection of `.dive-preview/src/dive.tsx`.
  - Actual result: `RELEVANT_TABLE` points to `"acorn-granary"."main"."relevant_open_roles"`; query/result rendering references `source_kind`.
- Observation: 80,000 Hours public site exposes runtime config and job rows through public Algolia search, not through full Nuxt payload rows.
  - Procedure/source: public fetch of `https://jobs.80000hours.org/`, saved HTML inspection, and public asset/API inspection by explore subagent `ses_1dc3b2eebffe7r4uZJUAR8MD4B`.
  - Actual result: Nuxt config included public Algolia app/index names and a public browser search key value, redacted here. Public Algolia search against the super-ranked jobs index returned `nbHits=804` and job-row fields including title, description fields, external URL, company fields, salary, posted/closing dates, and tags.

## Artifacts

- Tool output file `/Users/crlough/.local/share/opencode/tool-output/tool_e23c4a715001xkZnTXl1arK2DG` - saved HTML fetch for `https://jobs.80000hours.org/` used in 80,000 Hours inspection.
- Explore subagent result `ses_1dc3b2eebffe7r4uZJUAR8MD4B` - summarized public Algolia runtime config, robots/terms posture, and feasibility recommendation.

## What This Shows

- `ticket:20260513-greenjobsboard-mvp-extractor#ACC-001` - supports - the extractor emits the canonical fields in code and source-only validation runs without failed jobs.
- `ticket:20260513-greenjobsboard-mvp-extractor#ACC-002` - supports - source inspection shows source-specific Green Jobs Board fields are captured in normalized fields and `raw_json`.
- `ticket:20260513-greenjobsboard-mvp-extractor#ACC-003` - supports - source-only validation honestly reported zero strict-technical rows with no failed jobs.
- `ticket:20260513-greenjobsboard-domain-gate#ACC-001` - supports - view SQL includes Green Jobs Board `description`, `pathway`, `position_type`, and `workplace` in domain context.
- `ticket:20260513-greenjobsboard-domain-gate#ACC-002` - supports - view SQL joins `company_domain_review` and applies rejected-decision blocking before deterministic mission-fit inclusion.
- `ticket:20260513-greenjobsboard-domain-gate#ACC-003` - supports - existing relevant counts remained plausible after applying the gate; RemoteOK still had only `1` relevant row.
- `ticket:20260513-greenjobsboard-pipeline-integration#ACC-001` - supports - local runner and GitHub workflow include Green Jobs Board with failure isolation.
- `ticket:20260513-greenjobsboard-pipeline-integration#ACC-002` - supports - MotherDuck count query showed Green Jobs Board `current=0` and `relevant=0`.
- `ticket:20260513-greenjobsboard-pipeline-integration#ACC-003` - supports - health check passed.
- `ticket:20260513-greenjobsboard-dive-validation#ACC-001` - supports - Dive mirror still uses `relevant_open_roles` and renders `source_kind`.
- `ticket:20260513-greenjobsboard-dive-validation#ACC-002` - supports - Green Jobs Board has no rows today; view SQL would require location plus broad-source domain gates for future rows.
- `ticket:20260513-greenjobsboard-dive-validation#ACC-003` - supports - no MotherDuck data sharing command was run.
- `ticket:20260513-80000hours-access-feasibility#ACC-001` - supports - public Nuxt payload/runtime and public Algolia behavior were inspected enough to determine row exposure.
- `ticket:20260513-80000hours-access-feasibility#ACC-002` - supports - robots, terms, and brittleness risks were recorded in the observation.
- `ticket:20260513-80000hours-access-feasibility#ACC-003` - supports - recommendation is cautious go for a future lightweight public-Algolia extractor, not implementation in this plan.

## What This Does Not Show

- It does not show Green Jobs Board currently has relevant technical roles; today it has zero strict-technical matches.
- It does not prove Green Jobs Board HTML selectors will remain stable.
- It does not prove 80,000 Hours grants permission for bulk reuse or redistribution; public access is technically feasible but still non-contractual.
- It does not implement 80,000 Hours.
- It does not update or publish the live Dive; no copy change appeared necessary.

## Related Records

- `plan:20260513-greenjobsboard-80000hours-source-expansion` - active plan consuming this validation.
- `ticket:20260513-greenjobsboard-mvp-extractor` - Green Jobs Board extractor ticket.
- `ticket:20260513-greenjobsboard-domain-gate` - relevance SQL gate ticket.
- `ticket:20260513-greenjobsboard-pipeline-integration` - scheduled/local integration ticket.
- `ticket:20260513-greenjobsboard-dive-validation` - Dive validation ticket.
- `ticket:20260513-80000hours-access-feasibility` - 80,000 Hours research ticket.
