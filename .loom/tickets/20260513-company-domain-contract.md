# Company Domain Contract

ID: ticket:20260513-company-domain-contract
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - defines the semantic gate for broad-discovery companies
Priority: high - prerequisite for review seed and view-gate implementation
Depends On: ticket:20260513-company-domain-safety-patch

## Summary

Define the executable company/domain relevance contract for broad-discovery sources. The single closure claim is that future tickets can decide whether an unknown company belongs in the radar without relying on chat history.

## Related Records

- `plan:20260513-company-domain-relevance` - owns the strategy and operator decisions.
- `research:20260513-general-board-source-selection` - explains why RemoteOK is a broad candidate source.
- `ticket:20260513-company-review-seed` - will encode manual approval/rejection data from this contract.
- `ticket:20260513-company-domain-gate` - will implement this contract in SQL/view logic.

## Scope

May update this ticket and, if useful, add a Loom spec or knowledge record for company/domain relevance. Must not edit code, SQL views, or workflows. Must not introduce LLM or website-crawling requirements in the MVP contract.

## Acceptance

- ACC-001: Include and exclude domain categories are explicit enough for deterministic keyword rules.
- ACC-002: Curated-source bypass semantics are explicit.
- ACC-003: Unknown/rejected broad-discovery company behavior is explicit: hidden from normal Dive until approved/classified relevant.

## Current State

Closed. The executable company/domain relevance contract is:

- `current_open_roles` remains full inventory for all source kinds, including broad-discovery sources.
- `relevant_open_roles` remains the final user-facing Dive surface and must include both location relevance and company/domain relevance for broad-discovery sources.
- Curated source kinds bypass company/domain review: `greenhouse`, `ashby`, `page`, `sitemap`, `rippling`, and `polymer`. They still use the existing title/location relevance semantics.
- Broad-discovery source kinds require company/domain gating. The initial broad source is `remoteok`; future broad sources should opt into the same gate unless explicitly promoted to curated.
- Include company/domain signals for outdoor/recreation, geospatial/GIS/maps, climate/environment/conservation, earth observation/satellite/remote sensing, public infrastructure/civic tech, and map/spatial/data-heavy mobility or logistics.
- Exclude generic healthcare/biotech, generic fintech/insurance/mortgage, generic SaaS/platform/internal developer tooling, sales/marketing/customer-support businesses, and unrelated enterprise software unless manually approved.
- Unknown broad-discovery companies are hidden from `relevant_open_roles` pending deterministic classification or manual approval.
- Manual review decisions live in repo-owned SQL seed data. `approved` decisions allow a broad company through the company/domain gate; `rejected` decisions block it even if keywords match; `pending` records document review state but do not show in the Dive.
- MVP automated classification uses only source-provided job description/tags/title/company/location fields and deterministic keyword rules. No website crawling and no LLM classification in this plan.

Examples from current RemoteOK output: Natera and Quanata remain hidden as generic healthcare/insurance-adjacent companies. Civitech may pass the company/domain gate because the job description indicates civic tech/public-benefit democracy infrastructure, but it still must separately pass the location contract before reaching `relevant_open_roles`.

No separate audit was run because this ticket records operator-selected semantics and implementation tickets carry command-level validation.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, recorded include/exclude categories, curated bypass, unknown-company hiding, SQL seed review posture, and deterministic source-field-only classification. Closed; ACC-001/002/003 satisfied.
