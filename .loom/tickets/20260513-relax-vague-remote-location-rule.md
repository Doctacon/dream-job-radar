# Relax Vague Remote Location Rule

ID: ticket:20260513-relax-vague-remote-location-rule
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - broadens user-facing location eligibility globally
Priority: high - prerequisite for making GJC remote RSS rows useful

## Summary

Update the global location rule so vague `Remote` is eligible, while explicitly non-US/non-worldwide remote regions remain excluded. The single closure claim is that `relevant_open_roles` admits plain remote rows without admitting clearly foreign-region remote or Mapbox Germany-style rows.

## Related Records

- `plan:20260513-gis-jobs-clearinghouse-rss` - owns the source plan that depends on this rule change.
- `plan:20260513-personalized-relevance-filter` - originally defined stricter explicit remote rules.
- `motherduck/views.sql` - expected implementation target.

## Scope

May edit `motherduck/views.sql`, README wording, and this ticket. May apply views and run validation queries. Must not change title filters, company/domain gates, or source extractors in this ticket.

## Acceptance

- ACC-001: Plain/vague `Remote` locations are eligible in `relevant_open_roles` if company/domain gates pass.
- ACC-002: Explicitly non-US/non-worldwide remote regions remain excluded unless they also name US/worldwide/global eligibility.
- ACC-003: Mapbox Germany-style non-remote foreign roles remain excluded.

## Current State

Closed. `motherduck/views.sql` now treats `Remote` as eligible by default, unless the same location string explicitly names a non-US/non-worldwide remote region and does not also name US/worldwide/global eligibility. The exclusion list covers current observed foreign-region strings such as Canada-only, UK, Europe, EMEA, APAC, Asia, Australia, Austria, Belgium, Germany, Slovenia, France, Netherlands, Denmark, Estonia, Ireland, Portugal, Sweden, Switzerland, India, Mexico, Brazil, and Latin America.

Validation applied views and queried MotherDuck. Mapbox Germany remained excluded (`0` relevant rows). Explicit non-US remote rows such as `Slovenia, Remote`, `Austria, Remote`, and `Belgium, Remote` were excluded after adding those observed country names. A vague remote row with approved company/domain context now passes: RemoteOK/Civitech `Analytics Engineer` at `Austin, TX or Remote`.

No separate audit was run because the rule change was validated directly against expected included/excluded examples.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, relaxed remote eligibility, applied views, validated Mapbox Germany exclusion and observed foreign-remote exclusions, then closed. ACC-001/002/003 satisfied.
