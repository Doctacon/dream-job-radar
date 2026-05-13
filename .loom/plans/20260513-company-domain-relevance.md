# Company Domain Relevance For Discovery

ID: plan:20260513-company-domain-relevance
Type: Plan
Status: completed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - changes what broad-discovery jobs may reach the user-facing radar while preserving raw inventory

## Summary

Add a company/domain relevance gate for broad-discovery sources so technically relevant roles from irrelevant companies, such as Natera from RemoteOK, do not appear in the Dream Job Radar Dive. `current_open_roles` remains full inventory. `relevant_open_roles` stays the final user-facing view, but broad-discovery sources must pass role/location relevance and company/domain relevance before they appear there. Existing curated company-board sources bypass company/domain review.

## Related Records

- `plan:20260513-general-job-board-discovery` - completed RemoteOK MVP and exposed the need for company/domain relevance.
- `research:20260513-general-board-source-selection` - selected RemoteOK as the first broad source.
- `plan:20260513-personalized-relevance-filter` - owns the current `relevant_open_roles` location-relevance layer.
- `motherduck/views.sql` - current home of `current_open_roles` and `relevant_open_roles`.
- `.github/workflows/refresh.yml` - scheduled refresh must not run RemoteOK again until company/domain gating exists.
- `src/dream_job_radar/extractors/remoteok.py` - first broad source that should gain job-description/tag enrichment.

## Strategy

Treat broad discovery as candidate generation, not direct radar output. The immediate safety patch hides RemoteOK from `relevant_open_roles` and disables scheduled RemoteOK refresh while raw/current inventory remains recoverable. Then add a deterministic, auditable company/domain relevance system: repo-owned SQL seed data for manual approvals/rejections, job-description/tags enrichment from RemoteOK, and keyword rules for mission-fit company/domain signals.

The MVP should optimize for few high-signal leads. Unknown broad-discovery companies stay hidden pending review. Curated source kinds and slugs remain trusted and continue to bypass company/domain review. Do not introduce website crawling or LLM classification in this plan; those can be separate follow-ups if deterministic job-text/profile signals are insufficient.

## Execution Units

### Unit: Safety Patch

Ticket: ticket:20260513-company-domain-safety-patch

Immediately hide RemoteOK from `relevant_open_roles` and remove it from scheduled refresh while company/domain gating is missing. Scope is the view, workflow, and documentation state needed to stop Natera-like rows from appearing. This ticket may be closed in the same build turn.

### Unit: Domain Contract

Ticket: ticket:20260513-company-domain-contract

Define the executable company/domain relevance contract: mission-fit include domains, excluded generic domains, curated bypass semantics, unknown-company behavior, and manual review posture.

### Unit: Review Seed

Ticket: ticket:20260513-company-review-seed

Add a repo-owned SQL seed file for company approvals/rejections. It should support at least source_kind, company, decision, reason, and updated_at. Unknown companies remain hidden until approved or classified relevant.

### Unit: RemoteOK Enrichment

Ticket: ticket:20260513-remoteok-enrichment

Extend RemoteOK raw output with job-description/tags/company-profile signals available in the API response, without website crawling. This supports deterministic keyword classification and manual review.

### Unit: Domain Gate

Ticket: ticket:20260513-company-domain-gate

Update `relevant_open_roles` so curated sources bypass company/domain review while RemoteOK and future broad sources must pass approval or deterministic mission-domain rules. Unknown/rejected broad companies remain hidden.

### Unit: Re-enable RemoteOK

Ticket: ticket:20260513-reenable-remoteok-schedule

Re-enable RemoteOK in scheduled refresh only after the domain gate validates that Natera-like rows stay hidden and high-signal companies can pass.

### Unit: Dive And Docs Validation

Ticket: ticket:20260513-company-domain-dive-docs

Validate the existing Dive still works with gated broad-discovery rows and update README wording so broad discovery is described as company/domain gated.

## Milestones

### Milestone: Immediate Risk Removed

Child tickets: ticket:20260513-company-domain-safety-patch

RemoteOK no longer appears in `relevant_open_roles` and no scheduled job refreshes RemoteOK while the smarter gate is missing.

### Milestone: Contract And Data Shape Ready

Child tickets: ticket:20260513-company-domain-contract, ticket:20260513-company-review-seed, ticket:20260513-remoteok-enrichment

The domain-fit semantics, manual review seed, and RemoteOK enrichment fields are ready to drive a deterministic gate.

### Milestone: Broad Discovery Gated

Child tickets: ticket:20260513-company-domain-gate

`relevant_open_roles` admits broad-discovery rows only when company/domain relevance passes, while curated boards bypass review.

### Milestone: RemoteOK Safely Scheduled

Child tickets: ticket:20260513-reenable-remoteok-schedule, ticket:20260513-company-domain-dive-docs

RemoteOK is scheduled again only after validation proves broad-discovery rows are high signal and the Dive/docs tell the correct story.

## Current State

Completed. All child tickets are closed. RemoteOK remains in `current_open_roles`, is enriched with source-provided description/tags, and is scheduled again with failure isolation. `relevant_open_roles` now keeps curated source kinds on the existing location relevance path while broad-discovery RemoteOK rows must pass company/domain approval or deterministic mission-fit rules plus location relevance. Current validation shows RemoteOK has 16 rows in `current_open_roles` and 0 rows in `relevant_open_roles`; Natera is excluded. The live Dive was published as version 9 with company-domain-gated wording.

## Journal

- 2026-05-13: Created plan from operator decisions: keep `relevant_open_roles`, SQL seed review data, hide unknown companies, job-description/tags enrichment first, keyword rules, curated bypass, and disable RemoteOK until gated.
- 2026-05-13: Closed `ticket:20260513-company-domain-safety-patch`; RemoteOK count is 16 in `current_open_roles` and 0 in `relevant_open_roles`. Next ticket is `ticket:20260513-company-domain-contract`.
- 2026-05-13: Closed contract, review seed, enrichment, domain gate, schedule re-enable, and Dive/docs tickets. Published live Dive version 9 and set plan Status `completed`.
