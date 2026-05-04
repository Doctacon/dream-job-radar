---
id: initiative:lakehouse-iceberg
kind: initiative
status: active
created_at: 2026-05-04T02:49:06Z
updated_at: 2026-05-04T02:49:06Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  constitution: constitution:main
  research:
    - research:lakehouse-iceberg-spike
  predecessor:
    - initiative:partition-r2-layout
external_refs: {}
---

# Summary

Stand up a small Iceberg-managed analytics zone on R2 alongside
the existing hive-partitioned Parquet raw zone. R2 Data Catalog
is the catalog, dlt's iceberg destination is the writer, MotherDuck
is the reader. Start with one mart table. DuckLake is explicitly
rejected as a substitute — Iceberg is the format we want.

The first phase is a research spike: prove the
R2 Data Catalog ↔ MotherDuck attach path works end-to-end on a
trivial table. If the spike fails, the initiative halts and is
re-scoped from scratch. No automatic fallback to self-hosted
Lakekeeper, Polaris, or any other catalog without a fresh
research pass and explicit approval.

# Objective

The radar gains an Iceberg-managed mart layer that downstream
analytics can read transactionally, the project surfaces explicit
"open table format on object storage" experience for resume
positioning, and the team learns where the rough edges actually
are in the R2 + DuckDB + MotherDuck + dlt + pyiceberg stack.

# Why Now

`initiative:partition-r2-layout` just closed (2026-05-02). Raw
zone is hive-partitioned Parquet, view is stable, cron is green,
volume is small (KB-MB). Stack quiet enough to take a controlled
spike without endangering the live pipeline.

Industry signals (May 2026):

- DuckDB Iceberg writes landed v1.4.0 (2025-Q4), DELETE/UPDATE in
  v1.4.2 — but only on unpartitioned, unsorted tables.
- Cloudflare R2 Data Catalog in public beta, free during beta,
  Iceberg REST spec compliant. Engines explicitly named: Spark,
  Snowflake, PyIceberg.
- MotherDuck Iceberg docs list REST catalog reads as "limited to
  S3, S3 Tables, GCS" — R2 not in the named list. This is the
  spike's critical unknown.
- dlt iceberg destination supports REST catalogs (Lakekeeper,
  Polaris, AWS) via pyiceberg. R2 Data Catalog not explicitly
  named but spec-compliant.

User explicitly wants Iceberg, not DuckLake. DuckLake was
considered and rejected in this scoping conversation.

# In Scope

Phase 0 — Research spike (halt gate):

- Provision an R2 Data Catalog on the existing R2 bucket (or a
  new one if isolation is preferred).
- Write a trivial Iceberg table to that catalog using either
  PyIceberg directly or `dlt` with `destination='iceberg'`.
- Attach the catalog from MotherDuck via `ATTACH ... (TYPE
  iceberg)` and read the table.
- Document the connection shape, auth, and any failure modes in
  `research:lakehouse-iceberg-spike`.

Phase 1 — One mart table (only if Phase 0 succeeds):

- Pick one analytics table that benefits from Iceberg semantics
  (candidate: `mart_job_postings_daily_snapshot` — daily
  snapshots over the existing `current_open_roles` view).
- Land a writer path (likely a separate dlt pipeline or a
  scheduled job that reads the view and writes Iceberg).
- Land a reader path (MotherDuck attaches the catalog; Dive or
  ad-hoc SQL queries it).
- Document how cron, secrets, and observability extend to the
  Iceberg path.

# Out Of Scope

- **Raw zone migration to Iceberg.** Stays Parquet hive. Touching
  the live ingest is too much risk for a learning initiative.
- **Self-hosted Lakekeeper / Polaris fallback.** If R2 Data
  Catalog flops, halt and re-scope, do not silently pivot.
- **DuckLake.** Explicitly rejected.
- **Multiple mart tables.** One first. Add more in a follow-up
  initiative if the first lands cleanly.
- **UPDATE / DELETE / MERGE flows.** Append-only mart suffices;
  DuckDB's UPDATE/DELETE forbids partitioned tables anyway.
- **Schema evolution / time travel demos.** Nice-to-have if
  cheap; not required.
- **Egress / cost analysis beyond beta-period sanity check.** R2
  Data Catalog is free during beta; revisit if pricing surfaces.

# Success Metrics

Phase 0 (spike):

- Either a green end-to-end demo (R2 Data Catalog created, table
  written, MotherDuck reads it) OR a documented null result with
  the exact failure mode and reproducible repro steps.
- Decision recorded: continue to Phase 1, or halt and re-scope.

Phase 1 (only if Phase 0 green):

- One Iceberg table on R2 Data Catalog, populated by a scheduled
  job, read by MotherDuck.
- `wiki:extractor-shape` (or a new wiki page) documents the
  Iceberg path so the next initiative does not re-derive it.
- Resume-relevant artifact: a single page or repo file that
  summarises "I built Iceberg on R2 with dlt + MotherDuck",
  citing concrete numbers (table count, row count, query
  shape).

# Milestones

## M0 — Spike: R2 Data Catalog ↔ MotherDuck proven (or not)

Single ticket. Compresses to: "create catalog, write a table,
read it from MotherDuck, write findings". Halt gate.

## M1 — One mart table live (only if M0 green)

Append-only Iceberg table written on a schedule, readable from
MotherDuck.

## M2 — Wiki + retrospective

Lessons promoted into wiki + research records. Initiative
closes.

# Dependencies

Hard prerequisites:

- Active R2 account with permission to create a Data Catalog.
- MotherDuck workspace already attached to the R2 bucket
  (current state).
- DuckDB / MotherDuck Iceberg extension available (auto-loaded
  per MotherDuck docs).
- pyiceberg compatible Python env (`uv` per project standard).

Soft references:

- `decision:0001-storage-backend-r2` — unchanged. Iceberg lives
  on R2, no backend swap.
- `wiki:extractor-shape` — gets either a section or a sibling
  page during M2.

# Risks

- **R2 Data Catalog ↔ MotherDuck attach unproven.** MotherDuck
  docs list S3, S3 Tables, GCS only. Spike directly probes this;
  if it fails, halt.
- **DuckDB Iceberg write surface is narrow.** Partitioned /
  sorted tables forbid UPDATE/DELETE. First mart table must
  stay unpartitioned to keep options open.
- **Auth model unknowns.** R2 Data Catalog auth shape and how
  PyIceberg + MotherDuck each present credentials is not yet
  understood; spike must document.
- **Beta status.** R2 Data Catalog is public beta. Behavior may
  change. Acceptable for a learning initiative; flag in any
  resume framing.
- **Scope creep into raw zone.** Tempting to "just migrate the
  raw zone too". Resist; raw stays Parquet hive.
- **Cost surprise.** Free during beta; if Cloudflare ends beta
  pricing mid-initiative, revisit.

# Linked Work

Plan: `plan:lakehouse-iceberg`.

Initial ticket: `ticket:mka30wgd` (Phase 0 spike).

# Status Summary

Drafted 2026-05-04 after `initiative:partition-r2-layout`
closed. User confirmed Iceberg over DuckLake and confirmed
spike-first-with-halt posture. Phase 0 ticket pending compile.
