# Broaden Mission Source Discovery

ID: plan:20260513-broaden-mission-source-discovery
Type: Plan
Status: completed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - adds new broad discovery sources while preserving relevance gates that protect the Dive from noise

## Summary

Increase the number of relevant roles by adding mission-specific job sources instead of relying only on generic broad boards like RemoteOK. The first implementation source is Tech Jobs for Good because its public listings expose mission categories, role functions, location labels such as `Remote (US)`, company blurbs, and public job URLs. A parallel research ticket should evaluate GIS Jobs Clearinghouse, Climatebase, and USAJobs for the next source wave.

## Related Records

- `plan:20260513-company-domain-relevance` - owns the broad-source company/domain gate that new sources must use or explicitly extend.
- `plan:20260513-general-job-board-discovery` - added RemoteOK and showed that generic broad boards can have low user-facing yield.
- `research:20260513-general-board-source-selection` - records first-source research and rejected paths.
- `motherduck/views.sql` - owns `current_open_roles` and `relevant_open_roles` gating.
- `motherduck/company_domain_review.sql` - repo-owned manual review seed for broad-discovery company decisions.
- `README.md` - documents source coverage and relevance semantics.

## Strategy

Use a two-track plan. Track one is implementation-ready: add Tech Jobs for Good as a mission-specific discovery source using only public visible jobs. Track two is research: evaluate additional mission or geospatial sources for a later implementation slice.

For Tech Jobs for Good, only public visible listings should be ingested; do not bypass login, premium, or locked results. The MVP should target `Software Engineering` and `Data + Analytics` roles, and only allow impact areas selected by the operator: Climate Change, Environment, Clean Energy, Public Infrastructure, Public Service & Civic Engagement, and Partners & Advocates. These impact areas are accepted as positive company/domain signals, while `motherduck/company_domain_review.sql` remains the manual override surface for approvals/rejections.

Location relevance still gates user-facing display. `current_open_roles` remains full inventory for ingested public listings; `relevant_open_roles` remains the final Dive surface. If Tech Jobs for Good public HTML cannot be parsed reliably without login/premium access, stop and route back to research instead of widening to brittle scraping.

## Execution Units

### Unit: Tech Jobs for Good Source Contract

Ticket: ticket:20260513-techjobsforgood-source-contract

Define the exact MVP source contract for Tech Jobs for Good: allowed public pages, source fields, role functions, impact areas, location handling, premium/locked result handling, and company/domain gate semantics. Scope is Loom/source contract only.

### Unit: Tech Jobs for Good MVP Extractor

Ticket: ticket:20260513-techjobsforgood-mvp-extractor

Implement a `techjobsforgood` source extractor and source-kind pipeline that parses public visible listings for Software Engineering and Data + Analytics roles in the approved impact areas. Scope is one source only; do not bypass premium/login/locked results.

### Unit: Tech Jobs for Good Domain Gate

Ticket: ticket:20260513-techjobsforgood-domain-gate

Extend broad-source company/domain gating so Tech Jobs for Good impact areas can serve as positive mission-fit signals while manual review decisions can still reject or approve companies. Scope is SQL/view/seed changes, not extractor parsing.

### Unit: Tech Jobs for Good Pipeline Integration

Ticket: ticket:20260513-techjobsforgood-pipeline-integration

Wire Tech Jobs for Good into the local all-source runner and scheduled refresh with failure isolation, apply views, and validate that rows appear in `current_open_roles` and eligible rows flow to `relevant_open_roles`.

### Unit: Tech Jobs for Good Dive Validation

Ticket: ticket:20260513-techjobsforgood-dive-validation

Validate the existing Dive and README after Tech Jobs for Good lands. Update copy only if needed; the expected path is that the Dive already works because it queries `relevant_open_roles` and displays `source_kind` provenance.

### Unit: Next Source Research

Ticket: ticket:20260513-next-source-research-gjc-climatebase-usajobs

Research GIS Jobs Clearinghouse, Climatebase, and USAJobs as candidates for the next source wave. Preserve source feasibility, field mapping, access constraints, expected volume, and rejection/no-go results.

## Milestones

### Milestone: Tech Jobs for Good Contract Ready

Child tickets: ticket:20260513-techjobsforgood-source-contract

Future implementation can proceed without relying on chat history for allowed role functions, impact areas, location handling, or premium-result limits.

### Milestone: Public Mission Source Writes Rows

Child tickets: ticket:20260513-techjobsforgood-mvp-extractor

Tech Jobs for Good public visible listings write normalized rows to raw inventory without affecting existing curated or RemoteOK sources.

### Milestone: User-Facing Relevance Preserved

Child tickets: ticket:20260513-techjobsforgood-domain-gate, ticket:20260513-techjobsforgood-pipeline-integration

Tech Jobs for Good increases high-signal candidates while `relevant_open_roles` still enforces location and company/domain relevance.

### Milestone: Source Expansion Roadmap Updated

Child tickets: ticket:20260513-next-source-research-gjc-climatebase-usajobs

The next likely source after Tech Jobs for Good is selected or rejected with durable reasoning.

## Current State

Completed. Tech Jobs for Good was implemented as a public-visible mission-specific source and wired into local/scheduled refresh with failure isolation. Current validation shows 36 Tech Jobs for Good rows in `current_open_roles` and 20 in `relevant_open_roles`, increasing total relevant roles to 34 while RemoteOK remains at 0 relevant rows. The existing Dive can display the new source through `relevant_open_roles` without code changes. Follow-up research recommends GIS Jobs Clearinghouse RSS as the next implementation candidate, while Climatebase and USAJobs are deferred pending access feasibility.

## Journal

- 2026-05-13: Created plan from operator choices: Tech Jobs for Good first, two-track implementation plus research, civic/climate/infrastructure impact areas, Software Engineering and Data + Analytics roles, impact areas as domain signal, public visible jobs only.
- 2026-05-13: Closed all child tickets. Tech Jobs for Good source landed and next-source research completed. Set Status `completed`.
