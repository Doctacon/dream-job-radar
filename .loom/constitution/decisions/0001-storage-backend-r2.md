---
id: decision:0001-storage-backend-r2
kind: decision
status: active
created_at: 2026-04-29T14:17:56Z
updated_at: 2026-04-29T14:17:56Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  constitution: constitution:main
  research: research:storage-backend
  initiative: initiative:close-the-loop
---

# Decision

Cloudflare R2 is the dream-job-radar system of record for pipeline output.
dlt writes Parquet/JSON files to a private R2 bucket. MotherDuck reads
them via the native R2 secret type. AWS S3 is not used.

# Why This Decision Exists

The author flagged that AWS S3 has no hard kill-switch on spend, which
creates real operational anxiety on a personal-IC project. Research
confirmed:

- AWS S3 charges per GB of egress, including every MotherDuck query,
  raising the realistic cost ceiling.
- Cloudflare R2 charges zero egress at every tier, has S3-compatible API
  shape, and offers a free tier (10 GB / 1M Class A / 10M Class B per
  month) that covers this workload by 1–2 orders of magnitude.
- MotherDuck supports R2 natively as a first-class secret type.
- dlt writes to R2 via its filesystem destination with a single
  `endpoint_url` config addition.

R2 narrows the cost-anxiety blast radius without widening the integration
surface.

# Alternatives Considered

## AWS S3 — rejected

- Egress on every MotherDuck query.
- Cost-per-byte-of-mistake materially higher than R2.
- Same lack of hard kill-switch as R2, with worse worst-case shape.

## MotherDuck Managed DuckLake — rejected for v1

- Workload (tens of MB, hourly writes) does not benefit from lakehouse
  table semantics.
- Storage is opaque and not externally accessible on Managed DuckLake.
- Free-plan availability unclear; would risk a paid-tier dependency for
  v1, which the constitution refuses elsewhere (e.g. embed plan upgrade).
- "Single-account write access" today; multi-writer ACID is roadmap, not
  shipped.

## BYOB DuckLake on R2 — rejected for v1

- Adds catalog complexity for no v1 benefit when raw Parquet in R2
  already satisfies the read path through MotherDuck.
- Reconsider as an upgrade path if data volume or multi-writer needs
  emerge.

## Self-hosted MinIO — rejected for v1

- Aligned with "open source first" on principle but fails the
  one-person operational bar (server, TLS, backups, uptime) for zero
  v1 functional gain.
- Reconsider only if R2 vendor lock or pricing changes materially.

# Consequences

- `constitution:main` updates the system-of-record constraint from S3 to
  R2 and refreshes the allowed-source language only as needed (R2's
  S3-compatible posture means the constraint shape is unchanged).
- `initiative:close-the-loop` updates in-scope language and the
  bill-anxiety risk drops out.
- `plan:v1-radar` updates the Infra workstream, Storage layout
  workstream, and the Wave 0 ticket scope.
- `ticket:9mtt9h6j` is rewritten in place to provision R2 instead of S3.
- All extractor code is unaffected (S3-compatible API + dlt
  `endpoint_url` is a one-line config difference).

# Revisit Conditions

Reopen this decision if any of the following become true:

- pipeline output exceeds ~5 GB steady-state, approaching R2 free-tier
  storage limits
- hourly poll cadence rises by 10x or more
- multi-writer ACID semantics become useful (suggests DuckLake)
- Cloudflare R2 pricing or egress policy changes materially
- a hard spend-cap feature ships on either AWS S3 or R2 and the
  cost-anxiety gap closes

# Supersession

This decision supersedes the implicit AWS-S3 assumption inherited from
the founding article (`Building a Dream-Job Radar`, 2026-04-28).

It does not address dashboarding, query, or ingestion-source policy;
those remain owned by the existing `constitution:main` constraints.
