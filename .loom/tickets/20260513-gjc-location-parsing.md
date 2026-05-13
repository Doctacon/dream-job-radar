# GJC Location Parsing

ID: ticket:20260513-gjc-location-parsing
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - RSS descriptions combine title, company, location, and posted date in free text
Priority: medium - affects relevance eligibility
Depends On: ticket:20260513-gjc-rss-extractor

## Summary

Validate conservative company/location parsing from GJC RSS descriptions. The single closure claim is that parsing handles current feed examples without inventing data when descriptions are ambiguous.

## Related Records

- `plan:20260513-gis-jobs-clearinghouse-rss` - owns the parsing expectation.
- `ticket:20260513-gjc-rss-extractor` - implementation target if parsing lives in extractor code.

## Scope

May edit the GJC extractor if parsing needs adjustment. May run parser probes. Must not add detail-page crawling.

## Acceptance

- ACC-001: Current examples parse company/location correctly enough for relevance: `Geographic Technologies Group, Remote`, `CAI Technologies, Remote`, and non-AZ onsite examples.
- ACC-002: Ambiguous descriptions preserve raw description and avoid fabricated company/location values.
- ACC-003: Parsed `Remote` GJC rows can pass the updated remote rule; non-AZ onsite rows remain excluded from `relevant_open_roles`.

## Current State

Closed. GJC parsing is implemented inside `src/dream_job_radar/extractors/gjc.py`. Current feed examples parsed as expected: Geographic Technologies Group / Remote; CAI Technologies / Remote; Metropolitan Area Planning Agency (MAPA) / Omaha, NE; Office of Energy Infrastructure Safety / Sacramento. CA; MTA (LIRR) / Queens, NY. USA.

MotherDuck validation showed GJC has 10 rows in `current_open_roles` and 2 rows in `relevant_open_roles`: `GIS Strategic Planning Manager` at Geographic Technologies Group (`Remote`) and `GIS Web Developer` at CAI Technologies (`Remote`). Non-AZ onsite GJC rows remained out of `relevant_open_roles`.

No separate audit was run because parser examples and relevance counts directly validate the parsing behavior for current feed data.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, validated company/location parsing examples and relevance behavior, then closed. ACC-001/002/003 satisfied.
