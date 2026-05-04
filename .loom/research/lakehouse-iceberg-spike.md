---
id: research:lakehouse-iceberg-spike
kind: research
status: complete
created_at: 2026-05-04T02:49:06Z
updated_at: 2026-05-04T03:05:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:lakehouse-iceberg
  constitution: constitution:main
  predecessor:
    - research:r2-hive-partitioning
    - research:storage-backend
external_refs: {}
---

# Question

Does the R2 Data Catalog ↔ MotherDuck attach path work
end-to-end on a trivial Iceberg table, with dlt or PyIceberg as
the writer? If yes, what is the exact connection / auth /
configuration shape? If no, what fails, and is the failure
inherent to the stack or a config issue?

# Why This Matters

`initiative:lakehouse-iceberg` rests entirely on this triangle
working. MotherDuck's own Iceberg docs (May 2026) list REST
catalog reads as supported on "S3, S3 Tables, GCS" — R2 is not
in the named list. Cloudflare R2 Data Catalog (public beta as of
2025-04, broadly available 2026) speaks the Iceberg REST spec,
which DuckDB's iceberg extension consumes. Whether
"REST-compliant" is enough in practice is the question this
spike answers.

If the path works, M1 (one mart table) follows. If it fails,
the initiative halts and we re-scope from scratch — explicitly
not auto-pivoting to Lakekeeper / Polaris / Glue. User
direction.

# Scope

In scope:

- Provision an R2 Data Catalog on a R2 bucket (existing or new).
- Write at least one trivial Iceberg table (handful of rows, 2-3
  columns, no partitioning, no sorting) via PyIceberg or dlt's
  iceberg destination.
- Attach the catalog from MotherDuck and run a simple SELECT
  against the table.
- Capture: catalog URI, auth shape, env vars / secrets shape on
  both writer and reader sides, any error messages, version
  numbers of dlt / pyiceberg / DuckDB / MotherDuck client.

Out of scope:

- Schema evolution, time travel, MERGE, UPDATE, DELETE.
- Performance comparison against Parquet hive.
- Multi-table or partitioned tables.
- Self-hosted catalog comparison (Lakekeeper, Polaris). Only
  evaluate if the spike comes back null AND a follow-up
  initiative is explicitly approved.

# Method

Empirical end-to-end probe. Steps:

1. R2 side: create Data Catalog on a bucket; capture the REST
   endpoint, warehouse name, and required auth (token / API key
   / scoped credential).
2. Writer side: pick PyIceberg or dlt. Start with PyIceberg for
   minimum surface area; switch to dlt if PyIceberg path is
   working but has hostile ergonomics. Create a tiny table,
   insert a few rows.
3. Reader side: from MotherDuck, attempt
   `ATTACH 'r2-data-catalog-uri' AS lake (TYPE iceberg, ...)`,
   then `SELECT * FROM lake.<schema>.<table>`. Record exact
   syntax, exact errors, exact success state.
4. If reader path fails: try `iceberg_scan(...)` direct against
   the table's metadata pointer (catalog-less read). If that
   works, document the constraint; it does not satisfy M0
   green-state (we want catalog attach), but it is useful prior
   art for a re-scope.
5. Write findings here in this record. Continue or halt per
   initiative gate.

# Sources

To be populated as the spike runs. Initial reading:

- DuckDB Iceberg extension overview —
  `duckdb.org/docs/current/core_extensions/iceberg/overview`
- DuckDB Iceberg writes (v1.4) —
  `duckdb.org/2025/11/28/iceberg-writes-in-duckdb`
- MotherDuck Iceberg docs —
  `motherduck.com/docs/integrations/file-formats/apache-iceberg/`
- Cloudflare R2 Data Catalog —
  `developers.cloudflare.com/r2/data-catalog/`
- Cloudflare R2 Data Catalog public beta announcement —
  `blog.cloudflare.com/r2-data-catalog-public-beta/`
- dlt Iceberg destination —
  `dlthub.com/docs/hub/ecosystem/iceberg`
- PyIceberg configuration —
  `py.iceberg.apache.org/configuration/`
- Lakekeeper REST catalog —
  `github.com/lakekeeper/lakekeeper` (reference only;
  not in spike scope)

# Evidence

Located under `.loom/evidence/lakehouse-iceberg-spike/`:

- `spike_pyiceberg.py` — write path (PyIceberg → R2 Data Catalog).
- `run1.log`, `run2.log` — successful PyIceberg runs (3 rows
  per append, 2 snapshots after 2 appends).
- `spike_motherduck_attach.py` — MotherDuck ATTACH probe.
- `run_md_attach.log`, `run_md_attach2.log`,
  `run_md_attach3.log`, `run_md_attach4.log` — progressive
  diagnostics. `run_md_attach4.log` confirms ATTACH succeeds,
  catalog/schema/table list succeed, SELECT crashes with
  SIGSEGV (exit 139).
- `spike_local_duckdb.py` + `spike_md_scan.py` — diagnostic
  scripts isolating the failure.
- `run_md_scan.log` — MotherDuck + direct `iceberg_scan` succeeds.

Versions pinned at the time of spike (2026-05-04):

- `duckdb` 1.5.2 (local + MotherDuck client)
- `pyiceberg` 0.11.1
- `pyiceberg-core` 0.8.0
- DuckDB iceberg extension auto-loaded by `INSTALL iceberg; LOAD
  iceberg;` (version not surfaced)
- MotherDuck server reports `v1.5.2`

R2 Data Catalog state:

- Bucket: `pipelines`
- Catalog enabled via Cloudflare API:
  `POST /accounts/{account_id}/r2-catalog/{bucket}/enable`
- Warehouse name: `<account_id>_<bucket>`
- REST URI:
  `https://catalog.cloudflarestorage.com/<account_id>/<bucket>`
- Auth: R2 API token (existing `R2_TOKEN_VALUE`); no extra
  scoping needed for write + read against this bucket.
- Iceberg metadata stored at
  `s3://<bucket>/__r2_data_catalog/<uuid>/<uuid>/metadata/...`

# Findings

## What works

1. **PyIceberg → R2 Data Catalog (write).** Create namespace,
   create table, append PyArrow batches. Idempotent across runs.
   Snapshots accumulate. No special R2 adapter needed —
   generic `pyiceberg.catalog.rest.RestCatalog` with `uri`,
   `warehouse`, `token`.
2. **Local DuckDB 1.5.2 reads R2 Iceberg cleanly via ATTACH.**
   Both `ATTACH ... TYPE iceberg ...` + `SELECT` and direct
   `iceberg_scan('s3://.../metadata.json')` return rows.
   Requires `unsafe_enable_version_guessing = true` and an S3
   secret scoped to `s3://<bucket>` pointing at the R2
   endpoint.
3. **MotherDuck ATTACH succeeds at the metadata layer.**
   `SHOW DATABASES`, `SHOW SCHEMAS`, listing tables in
   `r2_lake.spike` all return the expected names.
4. **MotherDuck + direct `iceberg_scan(metadata_path)` works.**
   Full row read, correct values, no crash.

## What fails

5. **MotherDuck + `SELECT * FROM r2_lake.spike.trivial`
   (catalog-mediated data read) crashes with SIGSEGV (exit
   139), no error message.** Reproducible across multiple runs.
   The crash happens in MotherDuck-server-side native code; the
   client connection dies hard. Same query on local DuckDB
   1.5.2 with identical secret + extension setup succeeds.

## Failure boundary

The breakage is narrow and specific: **MotherDuck's
catalog-attach-mediated data read against R2 Data Catalog**.
Everything else in the stack composes:

| Path | Result |
|---|---|
| PyIceberg write to R2 Data Catalog | OK |
| Local DuckDB ATTACH + SELECT | OK |
| Local DuckDB `iceberg_scan` direct | OK |
| MotherDuck ATTACH + metadata listing | OK |
| MotherDuck `iceberg_scan` direct | OK |
| **MotherDuck ATTACH + SELECT** | **SIGSEGV** |

This matches MotherDuck's documented constraint that REST
catalog reads are "limited to S3, S3 Tables, GCS" — R2 is not
in their supported set, but the failure is a hard crash rather
than a clean unsupported-backend error.

# Decision

**Partial.** Per `plan:lakehouse-iceberg` halt-gate definition,
this matches the "partial" outcome exactly:

> partial (e.g. PyIceberg writes work but MotherDuck attach
> fails; iceberg_scan direct read works) → halt, document in
> research, decide explicitly whether to proceed with a
> degraded reader path or re-scope.

Halting Phase 1 pending explicit user decision.

## Re-scope options surfaced

A. **Degraded reader path: MotherDuck + `iceberg_scan` direct.**
   Skip catalog ATTACH; query each table by metadata pointer.
   Loses transparent multi-table catalog UX; gains: keeps
   MotherDuck as canonical reader, keeps R2 Data Catalog as
   write surface. Operational cost: code that resolves the
   current metadata pointer per table (PyIceberg can list
   tables and return their metadata locations).

B. **Local-DuckDB reader, MotherDuck demoted.** Run analytics
   queries from a local DuckDB process with full ATTACH.
   Loses MotherDuck's hosted UX (no Dive over Iceberg).

C. **File MotherDuck feature request, wait.** R2 may eventually
   join their supported REST backends. Pause initiative.

D. **Pivot reader to a different engine** (DuckDB CLI, Spark,
   Trino, Daft) — none currently in the stack.

E. **Re-scope catalog**: drop R2 Data Catalog, self-host
   Lakekeeper or use an S3 backend. Loses zero-egress
   advantage, gains MotherDuck compatibility (S3 is in their
   supported list).

F. **Cancel initiative** entirely.

User direction was "if r2 data catalog flops, we need to stop
and rethink." R2 Data Catalog itself did not flop — write
works, generic REST clients work, local DuckDB works.
MotherDuck-as-canonical-reader on R2 Iceberg flopped. That is
the rethink boundary. No automatic pivot; surface for explicit
choice.

# Open Questions

- Will MotherDuck's REST-catalog support for R2 expand? File a
  feature request? (Outside this spike.)
- Does the SIGSEGV reproduce against S3 Tables or GCS REST
  catalogs, or is R2-specific? (Outside this spike; would
  require provisioning either.)
- Does the `unsafe_enable_version_guessing` toggle play any
  role in the MotherDuck crash, or is it a red herring? (Local
  DuckDB needs the toggle and works; MotherDuck has the toggle
  and crashes — likely red herring.)
- If we go with option A (degraded reader), what is the
  ergonomic cost of resolving metadata pointers in SQL views or
  Dive panels?
