---
id: research:storage-backend
kind: research
status: complete
created_at: 2026-04-29T14:17:56Z
updated_at: 2026-04-29T14:17:56Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:close-the-loop
  constitution: constitution:main
  decision: decision:0001
external_refs: {}
---

# Question

Which object-storage backend should serve as the v1 system of record for
the dream-job-radar pipeline output: AWS S3, Cloudflare R2, or MotherDuck
Managed DuckLake?

# Why This Matters

`initiative:close-the-loop` writes pipeline output to an object store and
has MotherDuck read from it. The choice affects cost ceiling, blast-radius
risk on the personal-IC budget, portability, and integration shape with
both `dlt` (writer) and MotherDuck (reader).

# Scope

- AWS S3 — author's original assumption from the founding article.
- Cloudflare R2 — flagged by the author as a possible swap due to AWS
  bill anxiety.
- MotherDuck Managed DuckLake — surfaced during research as another
  candidate.

Out of scope: GCS, Azure Blob, self-hosted MinIO. Skip until v1 ships.

# Method

Web research against vendor docs and pricing pages, plus a check of dlt
and MotherDuck integration shapes. No live provisioning yet.

# Sources

- Cloudflare R2 Pricing — `developers.cloudflare.com/r2/pricing/`
- Cloudflare R2 S3 API compatibility — `developers.cloudflare.com/r2/api/s3/api/`
- Cloudflare community threads on R2 spend caps (multiple, 2022–2024)
- MotherDuck Cloudflare R2 docs — `motherduck.com/docs/integrations/cloud-storage/cloudflare-r2/`
- MotherDuck DuckLake docs — `motherduck.com/docs/integrations/file-formats/ducklake/`
- MotherDuck pricing — `motherduck.com/product/pricing/`
- MotherDuck DuckLake 1.0 announcement
- dlt filesystem destination docs — `dlthub.com/docs/dlt-ecosystem/destinations/filesystem`

# Evidence

## AWS S3

- No hard spend cap (Budgets are alert-only, not kill-switch). Multiple
  well-known horror stories of small projects with public buckets racking
  large bills via egress or attack traffic.
- Egress charges per GB out. MotherDuck reads from S3 would incur egress
  on every query.
- Mature, ubiquitous, every tool integrates.

## Cloudflare R2

- S3-compatible API at `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`.
  dlt's filesystem destination supports it via `endpoint_url` plus the
  same `aws_access_key_id` / `aws_secret_access_key` config shape.
- MotherDuck has native R2 support via
  `CREATE SECRET IN MOTHERDUCK (TYPE R2, KEY_ID, SECRET, ACCOUNT_ID)`.
- **Zero egress fees** at all tiers. MotherDuck reads cost nothing in
  bandwidth.
- Free tier: 10 GB storage, 1M Class A ops/month, 10M Class B ops/month
  (Standard storage only).
- No hard spend cap either; multiple feature requests open since 2022,
  not implemented as of this research.

## MotherDuck Managed DuckLake

- DuckLake is a table format + catalog (Parquet files + SQL metadata).
- Two flavors: Managed (MotherDuck owns the storage; opaque, not
  externally accessible) and BYOB (you bring R2/S3, MotherDuck owns the
  catalog).
- Managed DuckLake currently has a "single-account write access" limit;
  multi-writer support is roadmap, not shipped.
- Pricing page lists Managed DuckLake on paid tiers; free Lite plan
  inclusion is unclear at best.
- Free Lite plan: 10 GB storage, 10 hrs Pulse compute, 3 users, 2 service
  accounts.

## Workload profile for v1

- Six confirmed companies, each polled at most hourly.
- Per source: a few small JSON or Parquet files per cycle, low KB each.
- Estimated steady-state storage: well under 100 MB.
- Estimated Class A ops (writes/list): well under 100k/month.
- Estimated Class B ops (reads): bounded by MotherDuck queries; even
  generous use is well under 1M/month.

# Rejected Options

## AWS S3 — rejected

- **Egress cost shape is the real risk**, not storage. MotherDuck
  reading from S3 would generate egress on every query for free, while
  R2 charges nothing. Even at modest query volume the operational cost
  story is worse on S3.
- The lack of a hard kill-switch is the same on both, but S3's *cost
  per byte of mistake* is meaningfully higher, especially under attack
  or accidental public-bucket scenarios.
- AWS budget anxiety is a real friction the author has already named.
  Eliminating it is worth the proprietary swap.

## MotherDuck Managed DuckLake — rejected for v1

- Workload profile (tens of MB, hourly writes, personal-IC) does not
  benefit from a lakehouse table format. ACID writers, time travel, and
  petabyte-scale clustering are all costs paid for capabilities we do
  not need.
- Storage is opaque on Managed DuckLake; raw files are not externally
  accessible. That conflicts with the constitutional "open source first"
  principle in spirit (portability) even though the format itself is
  open. R2 keeps Parquet files we own.
- Free-plan availability is unclear; introducing a paid-tier dependency
  to ship v1 is exactly what the constitution refuses elsewhere
  (no plan upgrade for embed; same rule applies here).
- BYOB DuckLake is technically interesting but adds catalog complexity
  for no v1 benefit. R2 alone is simpler.

## Self-hosted MinIO — rejected for v1

- Constitutional "open source first" would prefer it on principle.
- Fails the operational bar for a one-person project: managing a server,
  TLS, backups, uptime, and credentials adds weeks of yak-shaving for
  zero v1 functional gain.
- Reconsider only if R2 vendor lock or pricing changes materially.

# Null Results

None.

# Conclusions

Cloudflare R2 is the right v1 system of record:

- zero egress eliminates the dominant AWS cost risk
- free tier covers the entire v1 workload by 1–2 orders of magnitude
- S3-compatible API keeps the integration surface narrow (one config
  line) and the swap path back to S3 or sideways to MinIO trivial
- MotherDuck has a native R2 secret type
- spend-cap absence is the same as S3 but the realistic cost ceiling is
  far lower because there is no egress

Managed DuckLake is a future upgrade path, not a v1 substitute. Revisit
only if pipeline output grows beyond raw-Parquet ergonomics or if
multi-writer ACID becomes useful.

# Recommendations

- Codify R2 as the constitutional system of record (decision record
  follows).
- Update `initiative:close-the-loop`, `plan:v1-radar`, and the Wave 0
  ticket to swap AWS S3 for R2 and AWS IAM for an R2 API token.
- Set Cloudflare billing notifications at $1, $5 thresholds for personal
  comfort even though the workload should never approach the free tier
  cap.
- Keep DuckLake on the shelf. Do not introduce it in v1.

# Open Questions

- None blocking v1.
- If pipeline output ever crosses ~5 GB or hourly poll cadence rises by
  10x, revisit Managed DuckLake or BYOB DuckLake.

# Linked Work

- `decision:0001-storage-backend-r2` — codifies the choice.
- `initiative:close-the-loop` — consumes: in-scope text and risk list.
- `plan:v1-radar` — consumes: workstreams and Wave 0 expectations.
- `ticket:9mtt9h6j` — consumes: full rewrite of infra-prep ticket.
