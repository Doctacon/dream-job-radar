---
id: packet:ralph-walking-skeleton-20260429T231616Z
kind: packet
packet_kind: ralph
status: consumed
target: ticket:gjkpkpum
mode: execution
change_class: code-behavior
style: reference-first
verification_posture: observation-first
iteration: 1
created_at: 2026-04-29T23:16:16Z
updated_at: 2026-04-29T23:35:00Z
scope:
  kind: repository
  repositories:
    - repo:root
child_write_scope:
  records: []
  paths:
    - src/dream_job_radar/__init__.py
    - src/dream_job_radar/extractors/__init__.py
    - src/dream_job_radar/extractors/greenhouse.py
    - src/dream_job_radar/pipelines/__init__.py
    - src/dream_job_radar/pipelines/radar.py
    - motherduck/views.sql
    - pyproject.toml
    - README.md
parent_merge_scope:
  records:
    - ticket:gjkpkpum
    - plan:v1-radar
  paths: []
source_fingerprint:
  git_commit: 29e1b17b0e76a10599efff4adf5c2a6368e8650b
  integration_remote: origin
  integration_ref: main
  integration_commit: 29e1b17b0e76a10599efff4adf5c2a6368e8650b
  git_status_summary: dirty
  compiled_from:
    - ticket:gjkpkpum
    - plan:v1-radar
    - initiative:close-the-loop
    - research:ats-discovery
    - decision:0001-storage-backend-r2
    - constitution:main
execution_context:
  branch: main
  push_remote: origin
  worktree: none
  isolation: none
  git_shared_metadata_mutations: forbidden
  destructive_commands: forbidden
  network: required
context_budget:
  posture: normal
  max_source_files: 8
  max_excerpt_lines_per_file: 80
  avoid_full_file_reads: true
sources:
  constitution:
    - constitution:main
  initiative:
    - initiative:close-the-loop
  research:
    - research:ats-discovery
  spec: []
  plan:
    - plan:v1-radar
  ticket:
    - ticket:gjkpkpum
links:
  decision:
    - decision:0001-storage-backend-r2
---

# Mission

Ship the dream-job-radar walking skeleton: one dlt Greenhouse extractor
for `onxmaps`, writing keyword-filtered open roles as Parquet to an
existing Cloudflare R2 bucket, plus a MotherDuck view DDL that exposes a
stable `current_open_roles` shape over the R2 prefix.

The Dive UI setup and `loughondata.com` iframe-embed attempt are parent
work after this packet returns. Do not attempt them in the child.

# Bound Context

- `constitution:main` — R2 is the system of record; MotherDuck reads R2
  natively; Open Source First; v1 title-keyword filter is
  `data | engineer | GIS | geospatial`, case-insensitive substring
  match.
- `initiative:close-the-loop` — six confirmed v1 sources; this packet
  covers only onX (Greenhouse `onxmaps`).
- `research:ats-discovery` — confirms onX uses the Greenhouse public API
  at `https://boards-api.greenhouse.io/v1/boards/onxmaps/jobs`.
- `decision:0001-storage-backend-r2` — Cloudflare R2 only; no AWS S3, no
  DuckLake.
- `plan:v1-radar` — Wave 1 walking skeleton; observation-first; the
  patterns established here propagate into Wave 2 extractor kinds.
- `ticket:gjkpkpum` — eight acceptance criteria; this packet covers
  AC1–AC5, AC8. AC6 (Dive renders) and AC7 (iframe-embed attempt) are
  parent work after the packet returns.

Intended behavior (per ticket) and current implementation reality (per
W0 commit `29e1b17`) currently diverge: no extractor code, no view DDL.
This packet closes the gap.

Branch posture: `main`, no worktree, dirty status (Loom records added
in this conversation, including `ticket:gjkpkpum` itself, are
uncommitted). Treat the dirty state as expected and do not try to clean
or commit Loom records; the parent owns those.

# Source Snapshot

Read these files directly for full context (reference-first style):

- `.loom/tickets/20260429-gjkpkpum-walking-skeleton.md` — primary
  contract; AC1–AC8, write boundary, execution notes.
- `.loom/initiatives/close-the-loop.md` — v1 keyword filter wording.
- `.loom/research/ats-discovery.md` — onX endpoint shape.
- `.loom/constitution/constitution.md` — R2 system-of-record posture.
- `.loom/plans/v1-radar.md` — Wave 1 verification expectations.
- `scripts/smoke_r2.py` — known-working R2 boto3 config; reuse the
  endpoint URL pattern.
- `scripts/smoke_motherduck.py` — known-working MotherDuck connection
  via `duckdb` + `MOTHERDUCK_TOKEN`.
- `pyproject.toml` — current deps; `dlt[filesystem]`, `boto3`,
  `duckdb`, `pyarrow`, `python-dotenv` already installed; add
  `requests` only if needed.

Greenhouse API shape (no auth): `GET
https://boards-api.greenhouse.io/v1/boards/onxmaps/jobs` returns
`{"jobs": [...]}` where each job has `id` (int), `title` (str),
`absolute_url` (str), `updated_at` (ISO timestamp), `location.name` (str),
`departments` (list of objects with `name`), `offices` (list), and
`metadata`.

R2 destination already provisioned in W0: bucket name `pipelines`,
endpoint `https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com`, env vars
in `.env` (`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`,
`R2_BUCKET`, `MOTHERDUCK_TOKEN`).

MotherDuck has an R2 secret pre-created server-side; `duckdb.connect("md:")`
plus `MOTHERDUCK_TOKEN` env var is enough — no per-query credential
config.

# Change Class

`code-behavior`. Evidence is observation-first: the pipeline must
actually run and produce real Parquet files in R2, and the MotherDuck
view must return real rows. Critique policy on the parent ticket is
`recommended` with two profiles (code-quality, schema-fitness); the
child does not run critique but should self-flag concerns the parent
should raise.

# Verification Targets

None — no spec exists yet. Acceptance is ticket-local against
`ticket:gjkpkpum` AC1–AC5 and AC8.

# Task For This Iteration

Build, in one bounded slice:

1. **`src/dream_job_radar/extractors/greenhouse.py`** — one dlt
   resource family.
   - Accept a list of board slugs (default `["onxmaps"]`, configurable
     via function arg or constant for now).
   - For each slug, GET `https://boards-api.greenhouse.io/v1/boards/<slug>/jobs`
     using `requests` (add to deps if not present) with a polite
     `User-Agent` like `dream-job-radar/0.1`.
   - For each job in the response, normalize to a flat record with at
     minimum these fields:
     `company` (str, the board slug or a friendlier name; for now use
     the slug verbatim — `onxmaps`), `source_kind` (str, `greenhouse`),
     `ats_slug` (str, the board slug), `role_id` (str, stringified
     Greenhouse `id`), `title` (str), `url` (str, `absolute_url`),
     `location` (str, `location.name` if present else `None`),
     `departments` (list of str, names), `posted_at` (str, ISO
     `updated_at`), `fetched_at` (str, ISO timestamp at fetch time),
     `raw_json` (str, the raw job JSON serialized).
   - Apply the v1 title-keyword filter before yield: lowercase
     substring match against `title` for any of `data`, `engineer`,
     `gis`, `geospatial`. Use a simple case-insensitive substring
     check; do not use regex.
   - Emit one record per matched role.

2. **`src/dream_job_radar/pipelines/radar.py`** — one dlt pipeline
   entry point.
   - Configure dlt's filesystem destination pointed at R2 with
     `bucket_url = f"s3://{R2_BUCKET}/raw"`,
     `endpoint_url = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"`,
     `region_name = "auto"`, and AWS-style credentials from
     `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY`.
   - Pipeline name: `dream_job_radar`.
   - Dataset name: `radar`.
   - Resource layout: write Parquet under
     `r2://<bucket>/raw/greenhouse/onxmaps/`. Acceptable to let dlt
     manage the per-run subpath under the resource's table directory
     so long as `boto3 list_objects_v2` against
     `s3://<bucket>/raw/greenhouse/onxmaps/` finds at least one
     Parquet file after a run.
   - `write_disposition='append'`.
   - Loadable via `python -m dream_job_radar.pipelines.radar` or
     `uv run python -m dream_job_radar.pipelines.radar`.
   - Use `python-dotenv` `load_dotenv()` at the entry point so
     `uv run` works with the local `.env`.
   - Emit a normal dlt run summary at exit.

3. **`motherduck/views.sql`** — one DDL file.
   - `CREATE OR REPLACE VIEW current_open_roles AS ...` over the
     full Parquet glob across all source-kind subdirectories of
     `r2://<bucket>/raw/`. For Wave 1, the only subdirectory is
     `greenhouse/onxmaps/`, but the view should already glob across
     all source kinds so Wave 2 inherits it without rewrite.
   - Expose at minimum these columns from the read:
     `company, source_kind, ats_slug, role_id, title, url, location,
     posted_at, fetched_at`.
   - Add derived `first_seen_at` and `last_seen_at` columns:
     `first_seen_at = min(fetched_at) over (partition by source_kind, ats_slug, role_id)`,
     `last_seen_at  = max(fetched_at) over (partition by source_kind, ats_slug, role_id)`.
   - Final SELECT should return one row per
     `(source_kind, ats_slug, role_id)` (use `qualify` or a CTE to
     dedup; the latest `fetched_at` row wins for the non-derived
     columns).

4. **`pyproject.toml`** — only adjustments needed for the above. If
   `requests` is needed for the HTTP fetch, add it via `uv add` (do
   not edit by hand). Do not bump existing pin versions.

5. **`README.md`** — add or extend a "Run the pipeline" section with
   the manual command and the prerequisite environment (load `.env`,
   ensure W0 acceptance state).

Run the pipeline once locally to produce real Parquet in R2, then run
the MotherDuck view DDL once via `duckdb.connect("md:")` to materialize
it server-side. Capture before/after evidence (see Verification Posture).

# Verification Posture

`observation-first`.

Before-state evidence (capture once):
- `aws s3 ls s3://<bucket>/raw/greenhouse/onxmaps/ --endpoint-url ...` or
  equivalent `boto3 list_objects_v2` showing zero objects (or only the
  smoke placeholder which is at `smoke/`, not `raw/`). Output should be
  empty.
- A MotherDuck query `SHOW VIEWS LIKE 'current_open_roles'` showing the
  view does not yet exist, or fails cleanly.

After-state evidence (capture once, after the implementation runs end-
to-end):
- `boto3 list_objects_v2` against
  `s3://<bucket>/raw/greenhouse/onxmaps/` returning at least one
  Parquet object key.
- Terminal output of the pipeline run including dlt's summary line
  (rows loaded).
- MotherDuck query
  `SELECT count(*) FROM current_open_roles WHERE source_kind = 'greenhouse' AND ats_slug = 'onxmaps'`
  returning a positive integer.
- MotherDuck query
  `SELECT title FROM current_open_roles WHERE source_kind='greenhouse' AND ats_slug='onxmaps' LIMIT 10`
  returning rows whose titles all contain at least one of `data`,
  `engineer`, `gis`, `geospatial` (case-insensitive). If onX has fewer
  than 10 matching roles right now, return whatever it has and verify
  all of them.

Both before and after observations belong in the Output Contract below.

# Stop Conditions

Stop and report `blocked` or `escalate` (instead of widening scope) if:

- the Greenhouse API for `onxmaps` returns a non-200 status or an
  unexpected JSON shape that does not match the documented schema in
  Source Snapshot
- dlt's filesystem destination cannot be configured for R2 from the
  current dep set without adding new dependencies beyond `requests`
- MotherDuck refuses to run the view DDL because of an R2 read error
  (the smoke script proves the credential path; if this fails, the
  failure mode is news and should escalate, not be patched around)
- the view shape proposed cannot be expressed in DuckDB SQL without
  significant gymnastics (note the difficulty and propose a simpler
  shape instead of forcing it)
- governing records (ticket, initiative, plan, constitution, decision,
  research) appear materially newer than the source fingerprint
  declared in this packet — re-read those, then decide whether to
  proceed or escalate
- any file outside `child_write_scope.paths` would need to change
- a real onX role would slip through the title-keyword filter despite
  matching it (or vice versa); flag the false-positive/negative case
  rather than silently broadening the filter

For `observation-first`: do not declare success without both
before-state and after-state evidence in the Child Output. If
before-state observation cannot be captured (for example, the bucket
already has stray files), document the actual starting state instead of
faking an empty one.

Do not run `git fetch`, `git push`, `git checkout`, `git config`, `git
remote`, force operations, or any command that would mutate shared Git
metadata. The parent owns Git operations.

Do not delete the W0 smoke placeholder at `r2://<bucket>/smoke/`. The
parent will decide when to delete it.

Do not write any Loom records. The parent owns ticket, plan, packet,
and other Loom mutations.

# Output Contract

Return:

- **outcome**: one of `continue`, `stop`, `blocked`, `escalate`.
- **files changed**: list of paths inside `child_write_scope.paths`
  (and only those).
- **records changed**: should be `[]`. The child does not write Loom
  records.
- **evidence gathered**:
  - before-state observations (R2 prefix listing, view existence
    check)
  - after-state observations (R2 listing, dlt run summary, MotherDuck
    counts, sample of 10 titles confirming the keyword filter)
  - exact commands run, with commands echoed before output
- **self-review findings or concerns**:
  - any place the schema, filter, or layout feels likely to bite
    Wave 2 extractors and should be raised in critique
  - any deviations from the task description and the reason
- **blockers or risks**: real ones; if none, write `None`.
- **ticket recommendation**: one of:
  - "advance ticket:gjkpkpum to `review_required` for critique
    (recommended profiles: code-quality, schema-fitness)"
  - "ticket:gjkpkpum requires another iteration; reason: ..."
  - "ticket:gjkpkpum should escalate to plan revision; reason: ..."
  - The parent commits ticket truth.

# Working Notes

- `dlt`'s filesystem destination supports S3-compatible endpoints via
  `endpoint_url`. The same env var pattern that works in
  `scripts/smoke_r2.py` should work here. Do not invent a new credential
  path.
- DuckDB `read_parquet` accepts globs against R2 once the secret is in
  place. The smoke script proves this works for a single file URI;
  glob support is the same surface.
- The `current_open_roles` view should already use a glob across
  `raw/<source_kind>/<ats_slug>/` so that Wave 2 extractor kinds plug
  in without a view rewrite. This is the schema-fitness concern.
- Reuse existing dependencies before adding new ones. `requests` is
  the only realistic addition; do not pull in `httpx`, `aiohttp`, or
  similar unless a concrete need surfaces.
- Keep the resource synchronous and single-process for v1. dlt async
  patterns are not justified at six companies.
- If the dlt filesystem destination decides to write Parquet under a
  load-id subpath like
  `raw/greenhouse/onxmaps/_dlt_loads/<load_id>/`, that is fine; the view
  glob can still find it.
- Use `pyarrow` (already a dep) over `pandas` for any table shaping.

# Child Output

**outcome**: `continue`

**files changed** (all inside `child_write_scope.paths`):

- `src/dream_job_radar/__init__.py` (new, empty)
- `src/dream_job_radar/extractors/__init__.py` (new, empty)
- `src/dream_job_radar/extractors/greenhouse.py` (new — board resource
  factory, keyword filter, normalization)
- `src/dream_job_radar/pipelines/__init__.py` (new, empty)
- `src/dream_job_radar/pipelines/radar.py` (new — dlt pipeline,
  filesystem destination pointed at R2)
- `motherduck/views.sql` (new — `current_open_roles` DDL with
  `${R2_BUCKET}` placeholder)
- `pyproject.toml` (added `requests`, `[build-system]` hatchling,
  wheel target for src layout)
- `README.md` (Run-the-pipeline section + view-materialize one-liner)

**records changed**: `[]`.

**evidence gathered**

Before-state:

- `list_objects_v2 Bucket=pipelines Prefix=raw/greenhouse/onxmaps/`
  → `KeyCount=0`.
- `md: SELECT view_name FROM duckdb_views() WHERE
  view_name='current_open_roles'` → `[]`.

After-state:

- dlt run summary: 1 load package LOADED, 8 records to `onxmaps`,
  no failed jobs.
- `list_objects_v2 Bucket=pipelines Prefix=raw/greenhouse/onxmaps/`
  → 1 Parquet
  (`raw/greenhouse/onxmaps/1777505542.5649621.8c17618d4c.parquet`,
  8373 bytes).
- `md: SELECT count(*) FROM current_open_roles WHERE
  source_kind='greenhouse' AND ats_slug='onxmaps'` → 8.
- `md: SELECT title, location FROM current_open_roles WHERE
  source_kind='greenhouse' AND ats_slug='onxmaps' LIMIT 10` → 8 rows
  (full list captured in ticket Evidence section).
- Filter cross-check vs upstream Greenhouse `onxmaps` board: 27 total
  roles, 8 matched substring, 0 false positives in matched set, no
  obviously-missed data/engineering/GIS roles in unmatched set.

**self-review findings or concerns**

1. **Deviation: dataset_name was changed to `greenhouse` (packet said
   `radar`).** dlt's filesystem destination always prefixes
   `<dataset_name>/` under `bucket_url`. With the packet's setting,
   first-run output landed at `raw/greenhouse/radar/onxmaps/...`,
   violating the observable path requirement `raw/greenhouse/onxmaps/`.
   Resolved by setting `bucket_url=s3://<bucket>/raw` and
   `dataset_name=greenhouse`. Schema-fitness implication for Wave 2:
   each source_kind needs its own pipeline `dataset_name`. Cleanest
   pattern is one pipeline per source_kind. Parent should accept,
   reject (re-iterate with `extra_placeholders`), or route to critique.
2. **`pyproject.toml` got a `[build-system]` block.** Mild
   scope-widening beyond "add requests" — needed so
   `python -m dream_job_radar.pipelines.radar` works.
3. **`requests` added as direct dep** even though dlt and boto3 pull it
   transitively. Per packet's "add to deps if not present".
4. **dlt system tables (`_dlt_loads/`, `_dlt_pipeline_state/`,
   `_dlt_version/`, `init`) sit at `raw/greenhouse/`** as siblings to
   `onxmaps/`. View glob `raw/*/*/*.parquet` does not match them
   (JSONL or extensionless). View also adds defensive
   `WHERE filename NOT LIKE '%/_dlt_%'`.
5. **`raw_json` column not exposed in view** by design — view stays
   thin, raw stays in Parquet for re-derivation.
6. **No tests yet.** Verification posture was observation-first;
   `_title_matches` and `_normalize` are testable when parent wants
   a follow-up ticket.
7. **Title-keyword filter is plain substring**, so `data` matches
   "Database Administrator". No such false positive in current onX
   corpus. Flag for v2 keyword model.
8. **Pyright import-not-resolved warnings** were fired but Pyright was
   running outside the uv venv. Runtime works under `uv run`. Not a
   real defect.

**blockers or risks**: None.

**ticket recommendation**: advance `ticket:gjkpkpum` to
`review_required` for critique (recommended profiles: code-quality,
schema-fitness).

# Parent Merge Notes

Parent reconciled 2026-04-29T23:35Z.

- Accepted the dataset_name deviation. The path contract
  (`r2://<bucket>/raw/<source_kind>/<ats_slug>/`) is the load-bearing
  observable; `dataset_name` is implementation detail. Wave 2 will
  use one pipeline per source_kind. Pattern recorded in
  `plan:v1-radar` Wave 2 sequencing notes.
- Accepted the `[build-system]` addition; required for the packet's
  invocation contract.
- Ticket `gjkpkpum` advanced to `review_required`. Evidence captured
  in ticket Evidence section.
- Critique pass next: code-quality + schema-fitness profiles per
  ticket Critique Disposition.
- Packet status `compiled` → `consumed`. No further iteration of this
  packet expected; AC6 (Dive renders) and AC7 (iframe embed) are
  parent local work, not Ralph work.
