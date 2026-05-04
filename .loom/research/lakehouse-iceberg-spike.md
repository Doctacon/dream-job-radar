---
id: research:lakehouse-iceberg-spike
kind: research
status: active
created_at: 2026-05-04T02:49:06Z
updated_at: 2026-05-04T02:49:06Z
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

(Populated by `ticket:mka30wgd` execution.)

# Findings

(Populated post-spike.)

# Decision

(Populated post-spike. One of: continue to Phase 1 / halt
initiative and re-scope.)

# Open Questions

- Does R2 Data Catalog auth integrate with MotherDuck's secrets
  surface, or does the attach require an inline token?
- What is R2 Data Catalog's actual REST endpoint format?
- Does PyIceberg have an out-of-the-box R2 Data Catalog adapter,
  or is it generic REST + extra config?
- Does dlt's iceberg destination need any R2-specific tweaks
  beyond bucket_url + REST catalog config?
