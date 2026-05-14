# Green Jobs Board And 80,000 Hours Source Expansion

ID: plan:20260513-greenjobsboard-80000hours-source-expansion
Type: Plan
Status: completed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - adds another mission board with likely low technical yield and investigates an app-driven board without implementing brittle access

## Summary

Add Green Jobs Board as a mission-specific source even if current technical yield is low, and research 80,000 Hours access feasibility without implementing it yet. Green Jobs Board should use public visible listing and detail pages, strict technical title filtering, category/pathway as a positive mission signal, and existing `relevant_open_roles` location/company-domain gates. 80,000 Hours should remain research-only until public job-row access is proven safe and stable.

## Related Records

- `plan:20260513-broaden-mission-source-discovery` - established mission-specific source expansion and completed Tech Jobs for Good.
- `plan:20260513-gis-jobs-clearinghouse-rss` - added GJC and relaxed vague Remote eligibility.
- `plan:20260513-company-domain-relevance` - owns broad-source company/domain gating and manual review behavior.
- `motherduck/views.sql` - owns `current_open_roles` and `relevant_open_roles`.
- `README.md` - documents sources and relevance semantics.

## Strategy

Implement Green Jobs Board as a low-maintenance public HTML source. Parse listing cards from `/jobboard/explore-jobs`, fetch public detail pages for apply URL, compensation, full description, workplace, experience, and category/pathway, then apply a very strict technical title filter before writing raw rows. Current yield may be zero; that is acceptable because the source is mission-fit and may produce relevant technical roles later.

Do not implement 80,000 Hours yet. Its public Nuxt payloads expose counts/tags/navigation but not obvious job rows, and matched/recommended job flows point at the app. Research should determine whether a safe public job-row path exists without auth, brittle reverse engineering, or terms-hostile access.

## Execution Units

### Unit: Green Jobs Board Source Contract

Ticket: ticket:20260513-greenjobsboard-source-contract

Define public-visible source boundaries, strict title filters, canonical field mapping, detail-page fields, category/pathway domain signals, and manual-review override behavior.

### Unit: Green Jobs Board MVP Extractor

Ticket: ticket:20260513-greenjobsboard-mvp-extractor

Implement listing-card parsing plus public detail-page fetches for Green Jobs Board. Normalize to canonical raw fields and source-specific enrichment fields. Load even if zero rows pass strict technical filtering today.

### Unit: Green Jobs Board Domain Gate

Ticket: ticket:20260513-greenjobsboard-domain-gate

Extend broad-source domain context so Green Jobs Board category/pathway and detail text can satisfy deterministic mission-fit rules, with manual review overrides still applying.

### Unit: Green Jobs Board Pipeline Integration

Ticket: ticket:20260513-greenjobsboard-pipeline-integration

Wire Green Jobs Board into local and scheduled refresh with failure isolation, update README/wiki, apply views, and validate MotherDuck counts and health checks.

### Unit: Green Jobs Board Dive Validation

Ticket: ticket:20260513-greenjobsboard-dive-validation

Validate the existing Dive path. Publish only if copy needs changing. Do not share MotherDuck data.

### Unit: 80,000 Hours Access Feasibility

Ticket: ticket:20260513-80000hours-access-feasibility

Inspect public Nuxt payloads, app/API behavior, and terms/access posture. Produce a go/no-go and recommended next step. Do not implement an extractor in this plan.

## Milestones

### Milestone: Green Jobs Board Writes Rows

Child tickets: ticket:20260513-greenjobsboard-source-contract, ticket:20260513-greenjobsboard-mvp-extractor

Green Jobs Board public visible rows can be parsed and loaded safely, even if strict filtering yields zero rows today.

### Milestone: Green Jobs Board Safely Enters Radar

Child tickets: ticket:20260513-greenjobsboard-domain-gate, ticket:20260513-greenjobsboard-pipeline-integration, ticket:20260513-greenjobsboard-dive-validation

Green Jobs Board is scheduled with failure isolation and eligible rows can appear in the relevance-first Dive without weakening existing gates.

### Milestone: 80,000 Hours Decision Ready

Child tickets: ticket:20260513-80000hours-access-feasibility

80,000 Hours has a durable go/no-go recommendation for future implementation.

## Current State

Completed. Green Jobs Board is implemented as a public HTML/detail-page source, wired into local and scheduled refresh, and protected by the relevance/domain gate. Today's validation found zero strict-technical Green Jobs Board rows (`current=0`, `relevant=0`), which is an accepted outcome for this source. 80,000 Hours remains unimplemented in this plan; feasibility research found public Algolia job rows and recommends a cautious future extractor with rate limiting and narrow fields.

## Journal

- 2026-05-13: Created plan from operator decisions: implement Green Jobs Board anyway, fetch details, strict technical titles, category/pathway as domain signal, 80,000 Hours research-only, combined plan.
- 2026-05-13: Completed Green Jobs Board source contract, extractor, domain gate, pipeline integration, and Dive validation tickets. Evidence recorded in `evidence:20260513-greenjobsboard-80000hours-validation`.
- 2026-05-13: Completed 80,000 Hours access feasibility ticket with cautious-go recommendation for a future public-Algolia extractor; no extractor implemented in this plan.
