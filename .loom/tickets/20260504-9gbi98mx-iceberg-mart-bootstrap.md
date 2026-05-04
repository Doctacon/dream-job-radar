---
id: ticket:9gbi98mx
kind: ticket
status: closed
change_class: code-behavior
risk_class: low
created_at: 2026-05-04T03:22:28Z
updated_at: 2026-05-04T03:35:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:lakehouse-iceberg
  plan: plan:lakehouse-iceberg
  research:
    - research:lakehouse-iceberg-spike
  predecessor:
    - ticket:mka30wgd
  constitution: constitution:main
external_refs: {}
---

# Summary

P1.1 of `initiative:lakehouse-iceberg`. Bootstrap the
Iceberg-on-R2 mart layer: confirm and document the persistent
MotherDuck S3 secret, add a shared `_iceberg.py` catalog
factory mirroring `_r2.py`, and smoke-create the `mart`
namespace in R2 Data Catalog. No mart table writes yet —
that's P1.2.

# Goal

Foundations in place so P1.2 can drop a writer in cleanly and
P1.3 can wire it into cron without ambiguity about which
secrets exist where, how the catalog is constructed, or where
the mart namespace lives.

# In Scope

- `src/dream_job_radar/pipelines/_iceberg.py` — catalog factory:
  `iceberg_catalog()` returning a configured
  `pyiceberg.catalog.rest.RestCatalog` from env vars
  (`R2_ACCOUNT_ID`, `R2_BUCKET`, `R2_TOKEN_VALUE`). Mirror the
  shape of `_r2.py` (no class wrapper, just a function).
- `motherduck/bootstrap_iceberg.sql` — idempotent SQL run once
  against MotherDuck workspace to ensure `r2_pipelines_s3`
  persistent secret exists with correct scope. Document the
  one-time `unsafe_enable_version_guessing` posture for
  reader sessions.
- Smoke: `iceberg_catalog().create_namespace('mart')` (or no-op
  if already present). One-shot script under `scripts/` or run
  inline; not committed as a pipeline entrypoint.
- Move (or keep) the existing `r2_pipelines_s3` persistent
  MotherDuck secret created during Phase 0. Verify scope
  `s3://pipelines` and visibility via
  `SELECT * FROM duckdb_secrets()`.
- Update `.env.example` if it lacks `R2_TOKEN_VALUE`.

# Out Of Scope

- Mart table creation. Leave `mart.job_postings_daily_snapshot`
  to P1.2 so the writer owns the schema bind.
- Writer logic, append flow, materialization, idempotency,
  cron wire — all P1.2/P1.3.
- Dive panel — P1.4.
- Wiki / retro — P1.5.
- Any change to `pipelines/_r2.py`, `motherduck/views.sql`, or
  the existing radar cron workflow.
- Cleanup of the Phase 0 spike artifacts (`spike.trivial`
  table, `spike` namespace). May reuse during P1.2 testing;
  drop in P1.5 retro if still around.

# Acceptance Criteria

- AC1: `src/dream_job_radar/pipelines/_iceberg.py` exists,
  exports `iceberg_catalog()`, returns a working
  `RestCatalog`. Tested by a one-line smoke: `from
  dream_job_radar.pipelines._iceberg import iceberg_catalog;
  print(iceberg_catalog().list_namespaces())`.
- AC2: `mart` namespace exists in R2 Data Catalog. Verifiable
  via `iceberg_catalog().list_namespaces()` returning
  `[('mart',), ('spike',)]` (order may differ).
- AC3: `motherduck/bootstrap_iceberg.sql` exists, is idempotent,
  documents how to run once (e.g., `python -c "import duckdb;
  duckdb.connect('md:?...').execute(open('motherduck/bootstrap_iceberg.sql').read())"`),
  and creates / refreshes the `r2_pipelines_s3` persistent
  secret with scope `s3://<bucket>`.
- AC4: `r2_pipelines_s3` persistent secret visible in
  `duckdb_secrets()` from a fresh MotherDuck connection
  (already true post-Phase-0; this AC is a verification, not a
  re-creation).
- AC5: `.env.example` lists `R2_TOKEN_VALUE` with a comment
  pointing at the R2 API token requirement (Admin Read &
  Write).
- AC6: No changes to `pipelines/_r2.py`, `motherduck/views.sql`,
  `.github/workflows/`, or any radar source pipelines.

# Verification Posture

`observation-first`. The work is structural plumbing; behavior
is "does the catalog handshake and the secret introspection
return what we expect". Evidence shape:

- Capture stdout of the AC1 smoke import.
- Capture `list_namespaces()` output before and after `mart`
  creation (AC2).
- Capture `SELECT name, type, scope, persistent FROM
  duckdb_secrets() WHERE name='r2_pipelines_s3';` output
  (AC4).
- Save under `.loom/evidence/lakehouse-iceberg-spike/p1_1_*`.

# Notes For Implementer

- `RestCatalog` constructor: `name` arg is local-only; use
  e.g. `"r2"`. `warehouse=f"{ACCOUNT_ID}_{BUCKET}"`.
  `uri=f"https://catalog.cloudflarestorage.com/{ACCOUNT_ID}/{BUCKET}"`.
  `token=os.environ["R2_TOKEN_VALUE"]`.
- Don't load `dotenv` inside `_iceberg.py`; entrypoints handle
  that. Match the convention in `_r2.py`.
- Persistent MotherDuck secrets sometimes need a fresh
  connection to reflect after creation; the smoke can open a
  second connection if needed.
- Don't burn time on tests — these are wiring functions
  exercised by the next ticket's writer flow.

# Status Summary

Drafted 2026-05-04 immediately after `ticket:mka30wgd`
(Phase 0 spike) closed. Executed same session.

## Outcome 2026-05-04: closed

All ACs met:

- AC1: `src/dream_job_radar/pipelines/_iceberg.py` created.
  Smoke `iceberg_catalog().list_namespaces()` returns
  `[('spike',)]` pre-mart, `[('mart',), ('spike',)]` post-mart.
  Evidence: `p1_1_smoke_factory.log`, `p1_1_create_mart.log`.
- AC2: `mart` namespace created in R2 Data Catalog. Idempotent
  on re-run.
- AC3: `motherduck/bootstrap_iceberg.sql` + matching
  `scripts/bootstrap_motherduck_iceberg.py` exist. Idempotent
  via `CREATE OR REPLACE PERSISTENT SECRET`. Confirmed by
  running twice.
- AC4: `r2_pipelines_s3` persistent secret visible:
  `[('r2_pipelines_s3', 's3', ['s3://pipelines'], True)]`.
  Evidence: `p1_1_bootstrap_run.log`.
- AC5: `.env.example` adds `R2_TOKEN_VALUE` with comment
  pointing at Admin Read & Write scope.
- AC6: no changes to `pipelines/_r2.py`, `motherduck/views.sql`,
  `.github/workflows/`, or radar source pipelines. Verified
  via `git status --short`.

Side effect not in original ACs but warranted: pyiceberg moved
from dev to main dependency since `_iceberg.py` is imported
from `src/` and will be runtime-required at P1.3 (cron). Lock
file refreshed.

Next: P1.2 (writer pipeline `iceberg_mart.py`). Will be opened
as a fresh ticket when ready to start.
