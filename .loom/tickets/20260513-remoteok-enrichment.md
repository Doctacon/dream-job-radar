# RemoteOK Enrichment

ID: ticket:20260513-remoteok-enrichment
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - changes broad-source raw row shape for downstream classification
Priority: medium - needed for deterministic company/domain keyword rules
Depends On: ticket:20260513-company-domain-contract

## Summary

Extend RemoteOK raw rows with available job-description, tag, and source metadata needed for company/domain relevance classification. The single closure claim is that RemoteOK rows carry enough API-provided context for deterministic MVP classification without website crawling.

## Related Records

- `plan:20260513-company-domain-relevance` - owns the enrichment-first MVP route.
- `src/dream_job_radar/extractors/remoteok.py` - expected implementation target.
- `ticket:20260513-company-domain-gate` - will consume enriched fields.

## Scope

May edit the RemoteOK extractor and run source-only validation. Must not crawl company websites, add LLM classification, or broaden RemoteOK title filters. Must preserve canonical fields used by `current_open_roles`.

## Acceptance

- ACC-001: RemoteOK raw rows retain canonical fields and include additional source-provided context useful for domain rules.
- ACC-002: Source-only validation proves enriched rows load successfully.
- ACC-003: Existing curated source behavior is unchanged.

## Current State

Closed. `src/dream_job_radar/extractors/remoteok.py` now keeps the canonical fields used by `current_open_roles` and adds source-provided context fields: `remoteok_description`, `remoteok_tags`, `remoteok_slug`, and `remoteok_apply_url`. No website crawling, LLM classification, or title-filter broadening was added.

Validation ran a normalization probe proving enriched rows include all canonical fields and the new context fields. `uv run python -m dream_job_radar.pipelines.remoteok` loaded 16 RemoteOK rows with no failed jobs. Existing curated source files were not changed.

No separate audit was run because the change is limited to one broad-source extractor and directly validated with a source-only load.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, added RemoteOK description/tags/slug/apply-url fields, validated row shape and source-only dlt load, and closed. ACC-001/002/003 satisfied.
