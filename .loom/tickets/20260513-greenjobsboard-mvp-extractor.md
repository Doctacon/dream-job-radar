# Green Jobs Board MVP Extractor

ID: ticket:20260513-greenjobsboard-mvp-extractor
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - Webflow HTML layout may change and current technical yield may be zero
Priority: high - creates the Green Jobs Board source rows
Depends On: ticket:20260513-greenjobsboard-source-contract

## Summary

Implement a Green Jobs Board extractor and pipeline that parses public visible listing cards and public detail pages, applies a strict technical title filter, and writes normalized rows to raw inventory. The single closure claim is that Green Jobs Board can be loaded safely with preserved context.

## Related Records

- `plan:20260513-greenjobsboard-80000hours-source-expansion` - owns source strategy.
- `ticket:20260513-greenjobsboard-source-contract` - owns source contract.

## Scope

May add one extractor and one pipeline. May fetch public detail pages linked from public cards. Must not access login/employer/hidden paths. Must not weaken title filtering to force rows.

## Acceptance

- ACC-001: Extractor emits canonical fields: company, source_kind, ats_slug, role_id, title, url, location, posted_at, fetched_at, raw_json.
- ACC-002: Extractor captures source-specific fields: pathway/category, workplace, experience, position type, compensation, apply-before date, apply URL, and description when visible.
- ACC-003: Source-only validation loads rows or honestly reports zero strict-technical rows with no failed jobs.

## Current State

Closed. Green Jobs Board extractor and pipeline exist, source-only validation ran, and today's public listings produced zero strict-technical rows without failed jobs. Evidence is recorded in `evidence:20260513-greenjobsboard-80000hours-validation`. Separate audit was not run because this ticket is a narrow source adapter with direct command evidence and zero user-facing rows today.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Implemented `src/dream_job_radar/extractors/greenjobsboard.py` and `src/dream_job_radar/pipelines/greenjobsboard.py`.
- 2026-05-13: Source-only validation parsed 33 public listing cards, matched 0 strict-technical cards, and completed with no failed jobs; closed ticket.
