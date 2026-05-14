# 80,000 Hours MVP Validation

ID: evidence:20260513-80000hours-mvp-validation
Type: Evidence Dossier
Status: recorded
Created: 2026-05-13
Updated: 2026-05-13
Observed: 2026-05-13

## Summary

Validation dossier for `plan:20260513-80000hours-public-algolia-mvp`, covering the source contract, extractor, relevance gate, refresh integration, and Dive path.

## Observations

- Observation: Python compilation succeeded.
  - Procedure/source: `uv run python -m compileall src scripts` from repository root.
  - Actual result: command completed successfully after adding `eightythousandhours` extractor/pipeline and refresh wiring.
- Observation: Source-only 80,000 Hours pipeline ran against public Algolia with narrow attributes and no failed jobs.
  - Procedure/source: `uv run python -m dream_job_radar.pipelines.eightythousandhours`.
  - Actual result: the extractor fetched `804` public hits across five bounded pages, yielded `106` strict technical matches after the corrected title filter, and dlt loaded the package with no failed jobs.
- Observation: An initial validation run exposed an over-broad `gis` substring matcher.
  - Procedure/source: first source-only run before matcher correction.
  - Actual result: `113` rows were yielded, including false positives such as `Strategist`, `Biologist`, and `Legislative` titles caused by `gis` substring matches. The extractor was corrected to require word-boundary `GIS` and exclude those title patterns. `current_open_roles` also quarantines the initial false-positive raw rows until they age out of the 30-day view window.
- Observation: Full all-source radar refresh ran with 80,000 Hours wired into the runner.
  - Procedure/source: `uv run python -m dream_job_radar.pipelines.radar`.
  - Actual result: the 80,000 Hours slice ran in sequence, yielded `106` matches, and loaded with no failed jobs. Full output artifact: `/Users/crlough/.local/share/opencode/tool-output/tool_e23e29821001xMhE3BZokHdE2C`.
- Observation: MotherDuck review seed and views applied successfully.
  - Procedure/source: `uv run python scripts/apply_company_domain_review.py` and `uv run python scripts/apply_views.py`.
  - Actual result: commands printed `company domain review seed applied` and `view materialized`.
- Observation: Final MotherDuck counts show 80,000 Hours enters current inventory and broad-source-gated relevant inventory.
  - Procedure/source: read-only DuckDB query against MotherDuck via local env credentials.
  - Actual result: `current_open_roles` source counts were `ashby=70`, `eightythousandhours=106`, `gjc=10`, `greenhouse=59`, `page=3`, `remoteok=19`, `techjobsforgood=36`; `relevant_open_roles` source counts were `ashby=1`, `eightythousandhours=20`, `gjc=2`, `greenhouse=13`, `remoteok=2`, `techjobsforgood=20`. Query for known false-positive title patterns in 80,000 Hours current inventory returned `0`.
- Observation: Health check passed.
  - Procedure/source: `uv run python scripts/health_check.py`.
  - Actual result: `PASS`; `eightythousandhours/jobs` was fresh with latest count `106`; `page/felt` remained the known zero-match stale warning.
- Observation: Existing Dive mirror still uses `relevant_open_roles` and source provenance.
  - Procedure/source: prior source inspection of `.dive-preview/src/dive.tsx` during this source-expansion work.
  - Actual result: `RELEVANT_TABLE` points to `"acorn-granary"."main"."relevant_open_roles"`; result rendering references `source_kind`. No MotherDuck data sharing command was run.

## Artifacts

- `/Users/crlough/.local/share/opencode/tool-output/tool_e23e29821001xMhE3BZokHdE2C` - full all-source radar refresh output, including the 80,000 Hours slice.
- `src/dream_job_radar/extractors/eightythousandhours.py` - public Algolia extractor with minimal attributes and strict title filter.
- `src/dream_job_radar/pipelines/eightythousandhours.py` - dlt pipeline entry point.
- `motherduck/views.sql` - relevance gate and false-positive quarantine guard.

## What This Shows

- `ticket:20260513-80000hours-source-contract#ACC-001` - supports - the closed source contract names public Algolia-only access and forbids auth/session scraping or hidden paths.
- `ticket:20260513-80000hours-source-contract#ACC-002` - supports - the contract names source identifiers and canonical field mapping.
- `ticket:20260513-80000hours-source-contract#ACC-003` - supports - the contract excludes full descriptions by default and allows only minimal source metadata.
- `ticket:20260513-80000hours-source-contract#ACC-004` - supports - the contract names strict title filtering, narrow attributes, bounded pagination, and daily max default cadence.
- `ticket:20260513-80000hours-source-contract#ACC-005` - supports - the contract requires broad-source gating with manual overrides and deterministic mission/domain signals.
- `ticket:20260513-80000hours-mvp-extractor#ACC-001` - supports - the extractor uses public Algolia search with `attributesToRetrieve`, `HITS_PER_PAGE=200`, and `MAX_PAGES=5`.
- `ticket:20260513-80000hours-mvp-extractor#ACC-002` - supports - the extractor emits canonical fields in normalized rows.
- `ticket:20260513-80000hours-mvp-extractor#ACC-003` - supports - the extractor stores minimal metadata and omits full descriptions.
- `ticket:20260513-80000hours-mvp-extractor#ACC-004` - supports - strict title filtering happens before yielding rows; the initial `gis` substring bug was corrected and quarantined from views.
- `ticket:20260513-80000hours-mvp-extractor#ACC-005` - supports - source-only validation loaded `106` rows with no failed jobs.
- `ticket:20260513-80000hours-domain-gate#ACC-001` - supports - `motherduck/views.sql` includes `eightythousandhours` in broad context and final broad-source gating.
- `ticket:20260513-80000hours-domain-gate#ACC-002` - supports - domain rules use minimal tags/snippet context plus title/company fields.
- `ticket:20260513-80000hours-domain-gate#ACC-003` - supports - existing `company_domain_review` join and rejected/approved behavior applies to `eightythousandhours`.
- `ticket:20260513-80000hours-domain-gate#ACC-004` - supports - final counts remained plausible and existing broad-source gates were preserved.
- `ticket:20260513-80000hours-pipeline-integration#ACC-001` - supports - local runner and GitHub workflow include the source with failure isolation.
- `ticket:20260513-80000hours-pipeline-integration#ACC-002` - supports - README and extractor-shape wiki list the source kind, slug, run command, and broad-source posture.
- `ticket:20260513-80000hours-pipeline-integration#ACC-003` - supports - MotherDuck count query showed `current=106`, `relevant=20` for 80,000 Hours.
- `ticket:20260513-80000hours-pipeline-integration#ACC-004` - supports - health check passed with 80,000 Hours included.
- `ticket:20260513-80000hours-dive-validation#ACC-001` - supports - existing Dive mirror uses `relevant_open_roles` and shows source provenance.
- `ticket:20260513-80000hours-dive-validation#ACC-002` - supports - 80,000 Hours rows reach relevance only through the broad-source-gated view.
- `ticket:20260513-80000hours-dive-validation#ACC-003` - supports - no MotherDuck data sharing command was run.
- `ticket:20260513-80000hours-dive-validation#ACC-004` - supports - no Dive publish was needed because the existing query path already consumes `relevant_open_roles` generically.

## What This Does Not Show

- It does not prove 80,000 Hours Algolia index/key/schema will remain stable.
- It does not prove permission for commercial reuse or redistribution; this remains best-effort for a personal radar.
- It does not remove the initial false-positive raw parquet files; it quarantines those rows from the current/relevant views and future corrected runs no longer yield them.
- It does not independently audit the implementation beyond the validation commands and record review described here.
- It does not publish the live Dive.

## Related Records

- `plan:20260513-80000hours-public-algolia-mvp` - plan consuming this evidence.
- `ticket:20260513-80000hours-source-contract` - source contract ticket.
- `ticket:20260513-80000hours-mvp-extractor` - extractor ticket.
- `ticket:20260513-80000hours-domain-gate` - relevance gate ticket.
- `ticket:20260513-80000hours-pipeline-integration` - refresh integration ticket.
- `ticket:20260513-80000hours-dive-validation` - Dive validation ticket.
