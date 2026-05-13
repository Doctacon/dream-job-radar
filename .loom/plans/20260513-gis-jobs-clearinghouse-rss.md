# GIS Jobs Clearinghouse RSS

ID: plan:20260513-gis-jobs-clearinghouse-rss
Type: Plan
Status: completed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - adds a geospatial RSS source and changes global remote-location eligibility

## Summary

Add GIS Jobs Clearinghouse as a lightweight geospatial discovery source using its public RSS feed at `https://www.gjc.org/cgi-bin/rssjobs.pl`. Before GJC implementation, relax the global location rule so vague `Remote` is eligible while explicitly non-US/non-worldwide remote regions remain excluded. This makes GJC remote rows useful without admitting clearly irrelevant geography.

## Related Records

- `research:20260513-next-source-wave` - recommends GJC RSS as the next implementation candidate.
- `plan:20260513-broaden-mission-source-discovery` - completed Tech Jobs for Good and identified GJC as the next source.
- `plan:20260513-company-domain-relevance` - owns broad-source company/domain gating and manual review behavior.
- `motherduck/views.sql` - owns `current_open_roles` and `relevant_open_roles`.
- `README.md` - documents source coverage and relevance semantics.

## Strategy

Execute the global location rule change first because the operator changed the definition of eligible remote work: plain/vague `Remote` should now be eligible, but explicitly non-US/non-worldwide remote regions should remain excluded. Then add GJC as a small RSS-backed source kind. GJC is intrinsically GIS/geospatial, so source text can satisfy the existing deterministic mission/domain rules, while final user-facing visibility still depends on `relevant_open_roles` location eligibility.

Keep the implementation narrow: public RSS only, no account/admin/posting pages, no detail-page crawling unless a future ticket needs it. Parse company/location conservatively from RSS descriptions. If parsing is uncertain, preserve the raw description and avoid inventing data.

## Execution Units

### Unit: Relax Vague Remote Rule

Ticket: ticket:20260513-relax-vague-remote-location-rule

Update `relevant_open_roles` so `Remote` is eligible globally unless the location explicitly names a non-US/non-worldwide remote region. Validate that plain Remote rows can appear and Mapbox Germany remains excluded.

### Unit: GJC Source Contract

Ticket: ticket:20260513-gjc-source-contract

Define the source contract: source kind `gjc`, slug `rss`, public RSS only, field mapping, parsing rules, and relevance behavior.

### Unit: GJC RSS Extractor

Ticket: ticket:20260513-gjc-rss-extractor

Implement the RSS extractor and source-kind pipeline. Parse RSS item title/link/guid/description/pubDate, normalize to canonical raw fields, and preserve source-specific context.

### Unit: GJC Location Parsing

Ticket: ticket:20260513-gjc-location-parsing

Conservatively parse company and location from RSS descriptions. This may close with the extractor if parsing is implemented there, but it owns the parsing validation claim.

### Unit: GJC Pipeline Integration

Ticket: ticket:20260513-gjc-pipeline-integration

Wire GJC into local all-source runner and scheduled refresh with failure isolation. Update README and extractor-shape wiki. Apply views and validate MotherDuck counts.

### Unit: GJC Dive Validation

Ticket: ticket:20260513-gjc-dive-validation

Validate that existing Dive behavior works through `relevant_open_roles` and `source_kind` provenance. Publish only if copy needs changing. Do not share MotherDuck data.

## Milestones

### Milestone: Remote Rule Updated

Child tickets: ticket:20260513-relax-vague-remote-location-rule

Vague `Remote` is globally eligible and explicitly foreign/region-limited remote remains excluded.

### Milestone: GJC Writes Inventory Rows

Child tickets: ticket:20260513-gjc-source-contract, ticket:20260513-gjc-rss-extractor, ticket:20260513-gjc-location-parsing

GJC public RSS rows write to `current_open_roles` with conservative company/location parsing.

### Milestone: GJC Safely Enters Radar

Child tickets: ticket:20260513-gjc-pipeline-integration, ticket:20260513-gjc-dive-validation

GJC is scheduled with failure isolation and eligible rows can appear in the relevance-first Dive.

## Current State

Completed. The global remote rule now admits vague `Remote` while excluding observed explicitly foreign-region remote rows. GJC RSS is implemented, loaded, scheduled with failure isolation, documented, and validated. Current MotherDuck counts: GJC has 10 rows in `current_open_roles` and 2 rows in `relevant_open_roles`; total `relevant_open_roles` is 37. The existing Dive can show GJC rows through `relevant_open_roles` without code changes.

## Journal

- 2026-05-13: Created plan from operator decisions: global vague `Remote` eligibility, still exclude explicitly non-US/non-worldwide remote, implement GJC RSS next.
- 2026-05-13: Closed all child tickets, validated all-source refresh and health check, and set plan Status `completed`.
