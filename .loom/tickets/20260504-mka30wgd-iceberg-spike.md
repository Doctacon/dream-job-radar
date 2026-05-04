---
id: ticket:mka30wgd
kind: ticket
status: complete_pending_acceptance
change_class: research-spike
risk_class: low
created_at: 2026-05-04T02:49:06Z
updated_at: 2026-05-04T03:05:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:lakehouse-iceberg
  plan: plan:lakehouse-iceberg
  research:
    - research:lakehouse-iceberg-spike
  constitution: constitution:main
external_refs: {}
---

# Summary

Phase 0 spike for `initiative:lakehouse-iceberg`. Prove (or
disprove) the R2 Data Catalog ↔ MotherDuck attach path on a
trivial Iceberg table. Halt gate.

# Goal

End-to-end demonstration:

1. R2 Data Catalog provisioned on an R2 bucket.
2. Tiny Iceberg table created and populated via PyIceberg
   (preferred; fall back to dlt iceberg destination only if
   PyIceberg ergonomics fail outright).
3. MotherDuck attaches the catalog and SELECTs from the table
   successfully.
4. `research:lakehouse-iceberg-spike` updated with findings,
   evidence, decision (continue / halt).

# In Scope

- Provisioning the catalog (Cloudflare dashboard or wrangler).
- One bucket — existing radar bucket OR a fresh isolation
  bucket; spike chooses and documents.
- One namespace, one table, ≤10 rows, 2-3 columns, no
  partitioning, no sort order, no schema evolution.
- Auth shape: R2 access key vs. scoped token, what MotherDuck
  needs to attach.
- Capture exact error messages and version pins.
- Update research record with everything learned.

# Out Of Scope

- The actual mart table (`mart_job_postings_daily_snapshot` or
  similar). That is Phase 1, gated on this ticket.
- UPDATE / DELETE / MERGE / time travel.
- Cron / Actions integration.
- Performance comparison vs Parquet hive.
- Self-hosted catalog evaluation.
- Touching `pipelines/_r2.py` or `motherduck/views.sql`.

# Acceptance Criteria

- AC1: R2 Data Catalog exists and is documented in
  `research:lakehouse-iceberg-spike` (URI / endpoint, auth
  shape, bucket binding).
- AC2: A trivial Iceberg table exists in the catalog with
  ≥1 row written via PyIceberg (or dlt) — code or notebook
  preserved as evidence.
- AC3: From a MotherDuck SQL session, `ATTACH` succeeds and
  `SELECT * FROM <attached>.<schema>.<table>` returns the
  expected rows. OR: explicit, reproducible failure with the
  exact error message captured.
- AC4: `research:lakehouse-iceberg-spike` Findings + Decision
  sections populated. Decision is one of: continue / partial /
  halt. Halt cancels Phase 1 until re-scoped.
- AC5: Versions pinned in the research record: dlt, pyiceberg,
  duckdb, MotherDuck client / extension version.
- AC6: No changes to live ingest. `pipelines/_r2.py`,
  `motherduck/views.sql`, and the cron workflow remain
  untouched.

# Verification Posture

`observation-first`. The spike is fundamentally about observing
whether the stack composes. Evidence shape:

- Captured terminal output / SQL session output for catalog
  creation, table write, MotherDuck attach + select.
- Saved Python script(s) under
  `.loom/evidence/lakehouse-iceberg-spike/` (or similar) so the
  exact reproduction is preserved.
- Screenshots only if textual capture is insufficient.

A green run requires the full chain observed live, not just
"PyIceberg wrote a table". A red run requires the failure
captured at the exact step and documented.

# Notes For Implementer

- Use `uv` per project standard. `uv add pyiceberg` (with
  appropriate extras for REST + S3/R2).
- DuckDB / MotherDuck Iceberg extension auto-loads when iceberg
  functions or `ATTACH ... TYPE iceberg` is used.
- R2 Data Catalog endpoint is bucket-scoped; check the
  Cloudflare dashboard for the exact REST URI shape.
- Auth: R2 Data Catalog uses R2 API tokens (scoped) per recent
  Cloudflare docs. PyIceberg accepts these via REST catalog
  properties (`uri`, `token`, `warehouse`, etc.).
- MotherDuck attach syntax (per docs): roughly
  `ATTACH '<rest-catalog-uri>' AS <alias> (TYPE iceberg, ...)`
  — verify in the live session, do not invent options.
- If MotherDuck attach fails, try `iceberg_scan('<metadata
  uri>')` direct read as a diagnostic — useful for the partial
  outcome case.
- Keep the spike's secrets out of the repo. R2 tokens go in
  env / `.env` / MotherDuck secret surface, not committed.

# Status Summary

Drafted 2026-05-04. Executed same day.

## Outcome 2026-05-04: PARTIAL — halt gate triggered

R2 Data Catalog provisioned + write path proven (PyIceberg).
MotherDuck `ATTACH` succeeds at metadata layer; `SELECT *`
catalog-mediated SIGSEGVs (exit 139) on MotherDuck server.
Local DuckDB 1.5.2 reads cleanly. MotherDuck +
`iceberg_scan(metadata_path)` direct also works.

Acceptance review:

- AC1: catalog provisioned, URI/auth/binding documented in
  `research:lakehouse-iceberg-spike` — done.
- AC2: trivial Iceberg table written via PyIceberg (≥1 row,
  6 rows after 2 appends) — done.
- AC3: ATTACH succeeds; SELECT fails reproducibly with SIGSEGV;
  exact failure captured — done (failure path).
- AC4: Findings + Decision populated; decision = partial; halt —
  done.
- AC5: versions pinned (duckdb 1.5.2, pyiceberg 0.11.1,
  pyiceberg-core 0.8.0, MotherDuck server v1.5.2) — done.
- AC6: live ingest untouched — done.

All ACs met. Decision per halt-gate is partial → halt Phase 1
pending explicit user re-scope. No auto-pivot to Lakekeeper /
Polaris / S3 / engine swap.

Ticket parks at `complete_pending_acceptance` until user closes
or reroutes via initiative update.
