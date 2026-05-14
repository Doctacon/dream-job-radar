# 80,000 Hours Public Algolia MVP

ID: plan:20260513-80000hours-public-algolia-mvp
Type: Plan
Status: completed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - uses a public browser search endpoint that is technically accessible but non-contractual and terms-sensitive

## Summary

Add 80,000 Hours as a conservative best-effort source for the personal Dream Job Radar. The source should use public Algolia search only, store minimal metadata, avoid full-description bulk reuse by default, and enter `relevant_open_roles` only through the existing title/location/domain gates. This needs more than one ticket because the access contract, extractor behavior, relevance SQL, scheduled integration, and validation each have distinct closure evidence.

## Related Records

- `evidence:20260513-greenjobsboard-80000hours-validation` - records that public Nuxt runtime config and public Algolia search expose 80,000 Hours job rows, plus access/terms/brittleness risks.
- `ticket:20260513-80000hours-access-feasibility` - closed feasibility ticket recommending cautious future implementation.
- `motherduck/views.sql` - owns `current_open_roles` and broad-source gating for `relevant_open_roles`.
- `motherduck/company_domain_review.sql` - manual company/domain review override surface.
- `README.md` - documents source kinds, run commands, and relevance semantics.
- `.github/workflows/refresh.yml` - scheduled refresh integration target.
- `.loom/wiki/extractor-shape.md` - source-kind and R2 layout reference.

## Strategy

Use a contract-first route because the source is not an official data API. The first ticket must define the acceptable boundary: public Algolia browser search only, no auth/session scraping, no hardcoded secret treatment, no excessive polling, and minimal stored content. The extractor should fetch narrow attributes from the public super-ranked jobs index discovered from public runtime config or safely configured constants, apply strict technical title filtering before writing raw rows, and normalize to existing canonical fields.

Treat 80,000 Hours as a broad-discovery source, not a curated company board. Rows can appear in `current_open_roles` after title filtering, but `relevant_open_roles` must also require location eligibility plus company/domain review or deterministic mission/domain context. The domain context should use minimal tags/company/category-style fields where available, not full descriptions unless a later source contract revision explicitly allows them.

Daily scheduled refresh is acceptable only with narrow `attributesToRetrieve`, conservative pagination/rate behavior, and source failure isolation. Replan if public Algolia access stops returning rows, runtime config changes make index/key discovery brittle, terms/access posture becomes less acceptable, or early extracted rows show that minimal metadata is insufficient for safe relevance gating.

## Execution Units

### Unit: 80,000 Hours Source Contract

Ticket: ticket:20260513-80000hours-source-contract

Define public-search boundaries, source identifiers, allowed fields, filtering rules, polling limits, content-storage posture, and broad-source gating expectations. This must close before implementation so the extractor does not silently choose access or content-reuse behavior.

### Unit: 80,000 Hours MVP Extractor

Ticket: ticket:20260513-80000hours-mvp-extractor

Implement a narrow public Algolia extractor and pipeline that retrieves minimal attributes, applies strict technical title filtering before raw writes, and normalizes rows to the canonical schema plus small source-specific metadata.

### Unit: 80,000 Hours Domain Gate

Ticket: ticket:20260513-80000hours-domain-gate

Extend broad-source relevance SQL so 80,000 Hours rows are gated like RemoteOK, Tech Jobs for Good, GJC, and Green Jobs Board. Use minimal stored source context for deterministic mission/domain rules and preserve manual review overrides.

### Unit: 80,000 Hours Pipeline Integration

Ticket: ticket:20260513-80000hours-pipeline-integration

Wire the source into local all-source refresh and scheduled GitHub refresh with failure isolation, update docs/wiki, apply views, and validate MotherDuck counts and health checks.

### Unit: 80,000 Hours Dive Validation

Ticket: ticket:20260513-80000hours-dive-validation

Validate that the existing Dive path consumes eligible 80,000 Hours rows through `relevant_open_roles` with source provenance and without MotherDuck data sharing. Publish only if copy needs changing.

## Milestones

### Milestone: Public Search Contract Ready

Child ticket: ticket:20260513-80000hours-source-contract

The source has an explicit, reviewable access/content contract that allows implementation without inventing policy or scope.

### Milestone: Source Writes Minimal Rows

Child ticket: ticket:20260513-80000hours-mvp-extractor

The extractor can fetch public Algolia rows conservatively and write strict technical matches to raw inventory with canonical fields.

### Milestone: Source Safely Enters Radar

Child tickets: ticket:20260513-80000hours-domain-gate, ticket:20260513-80000hours-pipeline-integration, ticket:20260513-80000hours-dive-validation

80,000 Hours is scheduled with failure isolation and eligible rows can appear in the relevance-first Dive without weakening existing gates or sharing MotherDuck data.

## Current State

Completed. 80,000 Hours is implemented as a best-effort public Algolia source with minimal metadata, strict title filtering, broad-source relevance gating, local/scheduled refresh integration, and existing Dive validation. Final validation showed `106` current rows and `20` relevant rows. A first-run `gis` substring false-positive issue was corrected and quarantined in the view until the initial raw files age out.

## Journal

- 2026-05-13: Created plan from operator selections after feasibility research: best-effort public Algolia, minimal metadata, broad-source gated relevance, daily narrow fetch, and narrow MVP ticket set.
- 2026-05-13: Executed and closed source contract, extractor, domain gate, pipeline integration, and Dive validation tickets. Evidence recorded in `evidence:20260513-80000hours-mvp-validation`.
