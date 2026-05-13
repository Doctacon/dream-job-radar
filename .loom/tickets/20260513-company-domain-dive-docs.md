# Company Domain Dive And Docs

ID: ticket:20260513-company-domain-dive-docs
Type: Ticket
Status: closed
Created: 2026-05-13
Updated: 2026-05-13
Risk: low - mostly validates existing Dive semantics after the domain gate
Priority: low - follows the gate and schedule re-enable
Depends On: ticket:20260513-company-domain-gate

## Summary

Validate the live/local Dive and README after company/domain gating so the user-facing story is accurate. The single closure claim is that screenshots from the private Dive show only high-signal broad-discovery jobs and documentation explains the company/domain gate.

## Related Records

- `plan:20260513-company-domain-relevance` - owns the final validation milestone.
- `.dive-preview/src/dive.tsx` - local mirror if copy or labels need changes.
- `README.md` - expected documentation target.

## Scope

May update Dive copy/README if validation reveals confusing wording. Must not share the Dive/data; the operator will take screenshots for external sharing.

## Acceptance

- ACC-001: Dive still queries `relevant_open_roles` and shows source provenance.
- ACC-002: Documentation says broad discovery is company/domain gated and unknown companies are hidden pending review.
- ACC-003: No MotherDuck Dive data sharing is performed.

## Current State

Closed. Local Dive copy now describes company- and location-relevant roles and says broad-discovery companies are gated by domain-fit review/rules. README documents that RemoteOK and future broad-discovery sources must pass company/domain review or deterministic mission-fit rules before appearing in `relevant_open_roles`, while unknown/pending/rejected companies remain in `current_open_roles` only.

Validation ran `rtk npm exec vite build -- --outDir "/var/folders/xk/pmxkhd7x635cskr6l4qw0mx00000gn/T/opencode/dream-job-radar-dive-build" --emptyOutDir`; build passed with the existing Vite chunk-size warning. Live Dive `391d1329-70d7-4223-89c8-d0dfde66ef7f` was updated and read back successfully as version 9 with the company-domain-gated description. No MotherDuck data sharing was performed; the database remains unshared.

No separate audit was run because the final validation was build plus live readback, and the operator previously stated screenshots will be used instead of sharing the Dive/data.

## Journal

- 2026-05-13: Created ticket with Status `open`.
- 2026-05-13: Set Status `active`, updated Dive copy/README, built local preview, published live Dive version 9, read it back, confirmed no data sharing, and closed. ACC-001/002/003 satisfied.
