# General Board Source Research

ID: ticket:20260513-general-board-source-research
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - source choice determines feasibility, precision, and operational risk for broad discovery
Priority: high - prerequisite for any general-board extractor work

## Summary

Research broad job-board or aggregator sources and choose one MVP source for high-precision Dream Job Radar discovery, or record a no-go if none fit. The single closure claim is a source-selection conclusion backed by public-access, data-shape, location-filter, dedupe, and operational-fit evidence.

## Related Records

- `plan:20260513-general-job-board-discovery` - owns the strategy, source constraints, and downstream execution units.
- `plan:20260513-personalized-relevance-filter` - defines the relevance layer broad discovery must ultimately pass through.
- `.loom/wiki/extractor-shape.md` - defines the row contract and raw layout a chosen source must be able to satisfy.
- `README.md` - describes current curated-only coverage and will be updated after a source lands.

## Scope

May research candidate sources, fetch public documentation/pages, run small read-only probes, and record conclusions in this ticket or a research record if the investigation becomes substantial. Must not implement extractor code. Must avoid LinkedIn, Indeed, Glassdoor, login-heavy, anti-bot-heavy, CAPTCHA-bypassing, or terms-hostile paths for the first source. Must prefer high precision over broad recall.

## Acceptance

- ACC-001: Candidate sources are compared against access friction, structured fields, title filtering, explicit location/remote filtering, provenance, dedupe, cron suitability, and expected precision.
  - Evidence: Ticket or linked research records the comparison and rejected paths.
  - Audit: Review should challenge whether the chosen source actually fits the operator's constraints.

- ACC-002: One MVP source is selected with a concrete implementation route, or the ticket records a no-go with reasons and recommended next question.
  - Evidence: Closure state names the selected source and endpoint/page/API shape, or records why none qualifies.
  - Audit: Review should challenge unsupported optimism about scraping or API availability.

- ACC-003: The selected route can emit the existing canonical row shape without changing `current_open_roles` or raw layout contracts.
  - Evidence: Source-shape notes map available fields to company, source_kind, ats_slug, role_id, title, url, location, posted_at, fetched_at, and raw_json.
  - Audit: Review should challenge missing role IDs, unstable URLs, or weak provenance.

## Current State

Closed. Research selected RemoteOK as the MVP general-board source and recorded the comparison in `research:20260513-general-board-source-selection`.

Summary of conclusion: RemoteOK is public, unauthenticated, structured JSON, broad enough to discover companies outside curated boards, and has explicit location strings that can be gated by `relevant_open_roles`. The Muse was rejected for the first MVP because its public API location results are often vague `Flexible / Remote` or loose multi-location results. Remotive was rejected for first MVP because probe precision was poor and the API response includes a redistribution warning. Arbeitnow was rejected because probe results were noisy and EU-heavy for this radar. LinkedIn, Indeed, and Glassdoor remain out of scope by operator constraint.

Recommended next ticket: `ticket:20260513-general-board-mvp-extractor`, implementing RemoteOK only, with stricter source-specific title filtering before raw writes.

## Journal

- 2026-05-13: Created ticket with Status `open` as the research-first slice for `plan:20260513-general-job-board-discovery`.
- 2026-05-13: Set Status `active`, probed The Muse, RemoteOK, Remotive, and Arbeitnow public APIs, created `research:20260513-general-board-source-selection`, selected RemoteOK for the MVP extractor, and closed. ACC-001/002/003 satisfied by the linked research record.
