# 80,000 Hours Source Contract

ID: ticket:20260513-80000hours-source-contract
Type: Ticket
Status: open
Created: 2026-05-13
Updated: 2026-05-13
Risk: medium - source access is public but non-contractual and content reuse must stay conservative
Priority: high - implementation must not proceed without a bounded source contract

## Summary

Define the executable source contract for 80,000 Hours. The single closure claim is that implementation can proceed from durable rules for public Algolia access, minimal stored fields, strict title filtering, polling behavior, and broad-source relevance gating.

## Related Records

- `plan:20260513-80000hours-public-algolia-mvp` - owns the implementation strategy and ticket sequence.
- `evidence:20260513-greenjobsboard-80000hours-validation` - records public Algolia feasibility and risks.
- `ticket:20260513-80000hours-access-feasibility` - prior research-only ticket with cautious-go recommendation.

## Scope

May update this ticket and related Loom records. Must not edit source code, SQL, workflows, or README. Must not authorize auth/session scraping, hidden endpoints, high-volume crawling, or full-description storage unless the operator explicitly changes the content posture.

## Acceptance

- ACC-001: Public access boundary is explicit: public Algolia browser search only, no auth/session scraping, no hidden app paths, and no treatment of the public browser key as a project secret.
- ACC-002: Source identifiers and canonical field mapping are explicit, including source kind, slug, role ID, title, company, URL, location, date fields, fetched timestamp, and raw metadata posture.
- ACC-003: Minimal source-specific fields are explicit and exclude full descriptions by default unless a later authorized change revises the contract.
- ACC-004: Strict technical title filtering and conservative polling behavior are explicit, including narrow attributes and daily scheduled refresh as the maximum default cadence.
- ACC-005: Broad-source domain gate behavior is explicit, including manual review overrides and deterministic mission/domain signals.

## Current State

Ready to start. First move is to record the source contract in this ticket using the operator decisions and feasibility evidence, then close if all acceptance criteria are satisfied.

## Journal

- 2026-05-13: Created ticket with Status `open`.
