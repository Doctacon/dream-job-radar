# Next Source Research: GJC, Climatebase, USAJobs

ID: ticket:20260513-next-source-research-gjc-climatebase-usajobs
Type: Ticket
Status: open
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - future source choice affects recall, noise, and implementation complexity
Priority: medium - can run in parallel with Tech Jobs for Good implementation

## Summary

Research GIS Jobs Clearinghouse, Climatebase, and USAJobs as candidates for the next source wave after Tech Jobs for Good. The single closure claim is a durable recommendation for the next implementation source, including rejected paths and field/access constraints.

## Related Records

- `plan:20260513-broaden-mission-source-discovery` - owns the two-track source expansion strategy.
- `research:20260513-general-board-source-selection` - prior source research baseline.
- `plan:20260513-company-domain-relevance` - relevance gate that future sources must fit or extend.

## Scope

May fetch public docs/pages, run small read-only probes, and create/update a Loom research record. Must not implement a new extractor. Must not bypass login, paid, premium, anti-bot, or credential-gated access. Must preserve null results and rejected paths.

## Acceptance

- ACC-001: GIS Jobs Clearinghouse feasibility is assessed, including RSS shape, geospatial relevance, location limitations, and expected volume.
- ACC-002: Climatebase feasibility is assessed, including whether public listings can be accessed without brittle SPA scraping, login, or anti-bot issues.
- ACC-003: USAJobs feasibility is assessed, including API/access shape, search parameters, public-sector relevance, and location/remote mapping.
- ACC-004: The ticket or linked research recommends a next source or records a no-go with reasons.

## Current State

Ready to start. Initial shaping found GJC has a public RSS feed with geospatial jobs, Tech Jobs for Good is stronger for immediate implementation, Climatebase is mission-fit but public fetch looked SPA/blocked, and USAJobs needs more targeted API/access research.

## Journal

- 2026-05-13: Created ticket with Status `open` as the parallel research track for `plan:20260513-broaden-mission-source-discovery`.
