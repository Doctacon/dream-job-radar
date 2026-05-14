# 80,000 Hours MVP Extractor

ID: ticket:20260513-80000hours-mvp-extractor
Type: Ticket
Status: open
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - public Algolia schema, index names, and browser key can change without notice
Priority: high - creates the 80,000 Hours source rows
Depends On: ticket:20260513-80000hours-source-contract

## Summary

Implement a conservative 80,000 Hours extractor and pipeline that uses public Algolia search, retrieves only allowed minimal fields, applies strict technical title filtering before raw writes, and writes normalized rows to R2. The single closure claim is that 80,000 Hours can be loaded safely as a best-effort source with minimal stored content.

## Related Records

- `plan:20260513-80000hours-public-algolia-mvp` - owns source strategy and sequencing.
- `ticket:20260513-80000hours-source-contract` - must define allowed access, fields, and filtering before implementation.
- `evidence:20260513-greenjobsboard-80000hours-validation` - records feasibility and public Algolia row exposure.

## Scope

May add one extractor module and one pipeline module. May use `requests` against public Algolia search endpoints. Must not scrape authenticated/session state, must not store full descriptions by default, must not fetch more attributes/pages than the source contract allows, and must not weaken title filtering to force rows.

Likely source identifiers: source kind `eightythousandhours`, slug `jobs`, R2 path `raw/eightythousandhours/jobs/`.

## Acceptance

- ACC-001: Extractor fetches public Algolia rows using narrow attributes and conservative pagination/rate behavior specified by the source contract.
- ACC-002: Extractor emits canonical fields: company, source_kind, ats_slug, role_id, title, url, location, posted_at, fetched_at, raw_json.
- ACC-003: Extractor stores only approved minimal source-specific fields in `raw_json` and normalized columns; full descriptions are omitted by default.
- ACC-004: Strict technical title filtering happens before raw rows are yielded.
- ACC-005: Source-only validation loads rows or honestly reports zero strict-technical rows with no failed jobs.

## Current State

Ready after the source contract closes. First implementation move should inspect existing broad-source extractor shapes before adding the smallest matching adapter.

## Journal

- 2026-05-13: Created ticket with Status `open`.
