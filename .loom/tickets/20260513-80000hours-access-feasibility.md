# 80,000 Hours Access Feasibility

ID: ticket:20260513-80000hours-access-feasibility
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - app-driven source may not expose safe public job rows
Priority: medium - research-only decision for future source expansion

## Summary

Research whether 80,000 Hours job rows can be accessed safely and stably without auth or brittle reverse engineering. The single closure claim is a go/no-go recommendation for future implementation.

## Related Records

- `plan:20260513-greenjobsboard-80000hours-source-expansion` - owns this research track.

## Scope

May fetch public pages/payloads and record research. Must not implement an extractor, bypass auth, or use hidden/credentialed app paths.

## Acceptance

- ACC-001: Public Nuxt payload/app behavior is inspected enough to determine whether job rows are exposed.
- ACC-002: Terms/access posture and brittleness risks are recorded.
- ACC-003: Ticket or linked research gives a go/no-go recommendation.

## Current State

Closed. Public Nuxt runtime config exposes public Algolia app/index configuration, and public Algolia search returns job rows without auth/session scraping. Recommendation: cautious go for a future lightweight extractor using public Algolia search with rate limiting, narrow `attributesToRetrieve`, attribution/source URLs, and non-contractual schema handling; do not implement in this plan. Evidence is recorded in `evidence:20260513-greenjobsboard-80000hours-validation`. Separate audit was not run because this is a research-only recommendation backed by public-source inspection, not a code-change acceptance claim.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Inspected public page/runtime payload and public Algolia behavior via saved HTML plus public API probing. Full job rows are not in the Nuxt payload, but public Algolia search returns rows.
- 2026-05-13: Recorded access risks: public browser key/index names are not a stable contract, terms restrict overburdening/unauthorized use and may restrict redistribution, and schema/index/key rotation can break an extractor.
- 2026-05-13: Closed with cautious-go recommendation for a future extractor; no extractor implemented in this plan.
