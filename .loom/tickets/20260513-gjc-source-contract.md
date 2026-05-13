# GJC Source Contract

ID: ticket:20260513-gjc-source-contract
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: low - public RSS source with simple field shape
Priority: high - prerequisite for GJC implementation
Depends On: ticket:20260513-relax-vague-remote-location-rule

## Summary

Define the executable source contract for GIS Jobs Clearinghouse RSS. The single closure claim is that implementation can proceed from durable rules for public RSS access, field mapping, and conservative parsing.

## Related Records

- `plan:20260513-gis-jobs-clearinghouse-rss` - owns the implementation strategy.
- `research:20260513-next-source-wave` - recommends GJC as the next source.
- `.loom/wiki/extractor-shape.md` - defines canonical source layout.

## Scope

May update this ticket and related Loom records. Must not edit code, SQL, workflows, or README. Must not authorize use of account/admin/posting pages.

## Acceptance

- ACC-001: Source kind and slug are explicit: `gjc` / `rss`.
- ACC-002: Public RSS-only boundary is explicit.
- ACC-003: Canonical field mapping is explicit.
- ACC-004: Conservative company/location parsing rules are explicit.

## Current State

Closed. GJC source contract:

- Source kind: `gjc`.
- Source slug/table: `rss`.
- Source URL: `https://www.gjc.org/cgi-bin/rssjobs.pl`.
- Boundary: public RSS only; no account, admin, posting, or detail-page crawling in the MVP.
- Canonical mapping: RSS title -> `title`; RSS link/guid -> `url`; `showjob.pl?id=<id>` -> `role_id`; parsed company/location from description -> `company` and `location`; RSS pubDate -> `posted_at`; current fetch timestamp -> `fetched_at`; full item payload -> `raw_json`.
- Source-specific fields: `gjc_description`, `gjc_guid`, and `gjc_pub_date`.
- Parsing rule: split descriptions shaped like `Title - Company, Location posted on DATE` conservatively. If parsing is ambiguous, preserve the raw description and avoid inventing company/location values.

No separate audit was run because implementation and parsing tickets carry source validation.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, recorded source kind/slug, public RSS boundary, field mapping, and parsing contract, then closed. ACC-001/002/003/004 satisfied.
