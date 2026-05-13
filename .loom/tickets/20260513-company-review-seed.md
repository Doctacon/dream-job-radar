# Company Review Seed

ID: ticket:20260513-company-review-seed
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - manual decisions directly affect what broad-discovery companies appear in the radar
Priority: high - required before deterministic company/domain gating is reviewable
Depends On: ticket:20260513-company-domain-contract

## Summary

Add repo-owned SQL seed data for manual company approvals and rejections. The single closure claim is that broad-discovery company decisions can be reviewed and loaded reproducibly from the repository.

## Related Records

- `plan:20260513-company-domain-relevance` - owns the review strategy.
- `ticket:20260513-company-domain-contract` - defines allowed decision semantics.
- `motherduck/views.sql` - will consume the seed or a generated table/view in the domain gate ticket.

## Scope

May add a SQL seed file and narrow scripts/docs to apply it. Must not manually mutate MotherDuck state without a repo-owned way to reproduce it. Must not approve unknown companies opportunistically without recording a reason.

## Acceptance

- ACC-001: Seed shape supports source_kind, company, decision, reason, and updated_at.
- ACC-002: Initial decisions include explicit rejection or pending state for current irrelevant RemoteOK examples such as Natera.
- ACC-003: README or ticket notes explain how to update/apply review decisions.

## Current State

Closed. Added `motherduck/company_domain_review.sql` as the repo-owned review seed and `scripts/apply_company_domain_review.py` as the reproducible apply path. The seed shape is `source_kind`, `company`, `decision`, `reason`, and `updated_at`, with decisions constrained by convention to `approved`, `rejected`, and `pending`.

Initial decisions include explicit rejections for current irrelevant RemoteOK examples: Natera, Quanata, Valon Mortgage, and Cast AI. Civitech is approved as civic-tech/public-benefit domain fit, but it still must pass the separate location gate before appearing in `relevant_open_roles`. Contact Government Services and Prove are pending and therefore hidden until reviewed.

Validation ran `uv run python scripts/apply_company_domain_review.py` and read back 7 rows from `"acorn-granary"."main"."company_domain_review"`. README now documents that company review decisions live in `motherduck/company_domain_review.sql` and should be applied before views.

No separate audit was run because the seed is a small, repo-owned deterministic data surface with direct readback validation.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, added review seed SQL and apply script, documented the apply path, validated 7 rows in MotherDuck, and closed. ACC-001/002/003 satisfied.
