# General Job Board Discovery

ID: plan:20260513-general-job-board-discovery
Type: Plan
Status: completed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - adds broad external sources with higher noise, duplication, and access-friction risk than curated company boards

## Summary

Expand Dream Job Radar beyond company-specific boards so it can discover relevant roles at companies the operator does not already know. The first expansion should prioritize broad aggregators, avoid high-friction sources such as LinkedIn, Indeed, Glassdoor, login-heavy, and anti-bot-heavy sites, and keep precision high. The output should mix discovered and curated jobs in the Dive with provenance, but only after discovered rows pass the personalized relevance layer from `plan:20260513-personalized-relevance-filter`.

## Related Records

- `plan:20260513-personalized-relevance-filter` - prerequisite for filtering broad discovery results to explicit US/worldwide remote and Arizona-local roles.
- `research:20260513-general-board-source-selection` - selected RemoteOK as the first MVP source and rejected The Muse, Remotive, and Arbeitnow for this initial implementation.
- `.loom/wiki/extractor-shape.md` - documents the source-kind, raw layout, and canonical row contract that any new source must satisfy.
- `README.md` - lists current curated source coverage and must grow to describe general discovery.
- `src/dream_job_radar/pipelines/radar.py` - meta-runner that will eventually orchestrate any new source-kind pipeline.
- `motherduck/views.sql` - owns `current_open_roles` and planned `relevant_open_roles`, the surfaces discovered jobs must flow through.

## Strategy

Use a research-first route because the source choice is the riskiest part. Broad aggregators can create high value, but many are unsuitable for a small daily personal radar because of anti-bot defenses, terms friction, poor location structure, or duplicate-heavy output. The first ticket researches candidate broad sources and chooses one MVP source only if it can support high-precision title and location filtering with public, low-friction access.

After source selection, build one vertical MVP source-kind end-to-end: extractor, pipeline, raw schema normalization, cron/meta-runner wiring, and MotherDuck visibility. Keep source provenance explicit so the Dive can mix curated and discovered jobs without hiding origin. The Dive mix happens only after `relevant_open_roles` exists and discovered rows pass that view; otherwise the plan blocks rather than flooding the UI with irrelevant geography.

Replan if the candidate source requires credentials, browser automation, CAPTCHA/anti-bot bypassing, paid access, terms-hostile scraping, or broad fuzzy matching to produce acceptable recall. Prefer high precision over high volume.

## Execution Units

### Unit: Source Research

Ticket: ticket:20260513-general-board-source-research

Research broad aggregator candidates and select one MVP source or record a no-go. Scope is investigation and source synthesis, not extractor code. Candidate sources should be judged on public low-friction access, structured fields, title filtering, explicit remote/location filtering, dedupe/provenance support, cron suitability, and high-precision fit. Avoid LinkedIn, Indeed, Glassdoor, login-heavy, and anti-bot-heavy paths for the first plan. Stop if no source can meet the bar without relaxing the operator's constraints.

### Unit: MVP Extractor

Ticket: ticket:20260513-general-board-mvp-extractor

Implement one chosen broad-source extractor and pipeline that emits rows matching the existing raw schema under a new source kind. Scope includes one source only, schema normalization, role IDs, source provenance, keyword filtering, and local validation. It depends on `ticket:20260513-general-board-source-research`. Stop if source reality differs materially from the research conclusion.

### Unit: Pipeline And View Integration

Ticket: ticket:20260513-general-board-pipeline-integration

Wire the MVP source into the project runner/cron path and verify rows appear through MotherDuck without breaking curated sources. Scope includes `src/dream_job_radar/pipelines/radar.py`, workflow wiring if needed, README source coverage, and validation queries. It depends on the MVP extractor and should also wait for `ticket:20260513-relevant-open-roles-view` so discovered rows can be checked against relevance filtering before UI exposure.

### Unit: Mixed Dive Display

Ticket: ticket:20260513-general-board-dive-display

Update the Dive to mix curated and discovered relevant roles together with clear provenance. Scope is user-facing display over `relevant_open_roles`, not source extraction. It depends on pipeline integration and `ticket:20260513-relevant-dive-wiring`. The ticket closes when discovered roles, if present, appear in the same relevant role flow as curated roles with source labels and high-precision filtering intact.

## Milestones

### Milestone: Source Chosen Or Rejected

Child tickets: ticket:20260513-general-board-source-research

The plan has a specific first broad source that meets the access and precision bar, or it truthfully records that no candidate is acceptable without returning to the operator.

### Milestone: One General Source Writes Raw Rows

Child tickets: ticket:20260513-general-board-mvp-extractor

One broad discovery source writes normalized rows with provenance to the existing R2 raw layout without changing curated source behavior.

### Milestone: Discovery Enters Relevant Surface

Child tickets: ticket:20260513-general-board-pipeline-integration, ticket:20260513-relevant-open-roles-view

General-source rows are visible to MotherDuck and pass through `relevant_open_roles` before any normal user-facing display.

### Milestone: Curated And Discovered Roles Are Mixed

Child tickets: ticket:20260513-general-board-dive-display, ticket:20260513-relevant-dive-wiring

The Dive presents relevant roles from curated company boards and the general source together, with provenance and high precision preserved.

## Current State

Completed. Source research selected RemoteOK. The MVP extractor and pipeline write strict technical RemoteOK rows under `raw/remoteok/remoteok/`; pipeline integration wires RemoteOK into the local runner and scheduled workflow with failure isolation; views and health check validate successfully; and the existing relevance-first Dive can mix discovered RemoteOK rows through `relevant_open_roles` with `source_kind` provenance.

Validation observed 16 RemoteOK rows in `current_open_roles` and 2 RemoteOK rows in `relevant_open_roles` at completion.

## Journal

- 2026-05-13: Created plan with Status `open` from operator-selected choices: broad aggregators first, avoid high-friction sources, mixed Dive ranking, high precision, and dependence on personalized relevance filtering.
- 2026-05-13: Closed `ticket:20260513-general-board-source-research`; selected RemoteOK as the first MVP source and set plan Status `active`.
- 2026-05-13: Closed `ticket:20260513-general-board-mvp-extractor`, `ticket:20260513-general-board-pipeline-integration`, and `ticket:20260513-general-board-dive-display`. Set plan Status `completed`.
