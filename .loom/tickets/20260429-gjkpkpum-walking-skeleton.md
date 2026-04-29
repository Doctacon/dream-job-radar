---
id: ticket:gjkpkpum
kind: ticket
status: review_required
change_class: code-behavior
risk_class: medium
created_at: 2026-04-29T22:53:30Z
updated_at: 2026-04-29T23:35:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:close-the-loop
  plan: plan:v1-radar
  constitution: constitution:main
  decision: decision:0001-storage-backend-r2
external_refs:
  greenhouse: https://boards-api.greenhouse.io/v1/boards/onxmaps/jobs
depends_on:
  - ticket:9mtt9h6j
---

# Summary

Build the v1-radar walking skeleton: a dlt Greenhouse extractor for one
company (onX), writing filtered open-roles records as Parquet to R2, with
MotherDuck reading R2 via a view that exposes a stable
`open_roles` shape, surfaced as a MotherDuck Dive.

This is Wave 1 of `plan:v1-radar`. It proves the entire ingest → store →
query → surface chain on the simplest possible source before any other
extractor kind exists.

# Context

W0 (`ticket:9mtt9h6j`) closed: R2 bucket `pipelines` exists, MotherDuck
has the R2 secret, GitHub Actions secrets are set, smoke scripts proved
the round-trip works end-to-end with a placeholder Parquet.

onX uses Greenhouse:
`GET https://boards-api.greenhouse.io/v1/boards/onxmaps/jobs` returns a
`jobs` array with `id`, `title`, `absolute_url`, `updated_at`,
`location`, `departments`, `offices`, `metadata`, etc. No auth required.
Per `research:ats-discovery`, this is a confirmed v1 source.

Per `initiative:close-the-loop`, the v1 title-keyword filter is:
`data | engineer | GIS | geospatial`, case-insensitive substring match.

This ticket is critique-recommended per `plan:v1-radar` because the
patterns it establishes (R2 prefix layout, dlt resource shape, MotherDuck
view shape, Dive shape) propagate into every Wave 2 extractor.

# Why Now

Walking skeleton answers four high-uncertainty questions in one slice:

1. Does dlt's filesystem destination write Parquet to R2 cleanly?
2. Does MotherDuck read that R2 prefix natively via the configured
   secret?
3. Does a Dive over a MotherDuck view render usefully?
4. Is iframe embed available on the personal MotherDuck plan, or do we
   link?

Without those answers, Wave 2 is guesswork.

# Scope

- create `extractors/greenhouse.py` — one dlt resource that:
  - reads a config-driven list of Greenhouse board slugs (v1: just
    `onxmaps`)
  - hits `boards-api.greenhouse.io/v1/boards/<slug>/jobs`
  - normalizes each job to a flat record:
    `(company, source_kind, ats_slug, role_id, title, url, locations,
    departments, posted_at, fetched_at, raw_json)`
  - applies the v1 title-keyword filter before yield
  - emits one record per matched role
- create `dlt_pipeline.py` (or `pipelines/radar.py`) that:
  - configures dlt's filesystem destination pointed at R2 via
    `endpoint_url` + the env vars set in W0
  - runs the Greenhouse resource
  - writes Parquet to `r2://<bucket>/raw/greenhouse/onxmaps/`
  - uses `write_disposition='append'`
- create `motherduck/views.sql` with:
  - a `current_open_roles` view that reads the Parquet across
    `r2://<bucket>/raw/greenhouse/**/*.parquet` and adds derived
    `first_seen_at` / `last_seen_at` columns from the Parquet writes
- run the pipeline locally; verify Parquet appears in R2
- run the view in MotherDuck; verify rows for onX appear
- create a Dive in MotherDuck over `current_open_roles` showing:
  title, company, location, posted_at, last_seen_at, link
- attempt iframe embed of the Dive on a scratch HTML page on
  `loughondata.com`; capture whether it works (this answers question 4
  but does not gate this ticket)
- add a `README.md` section describing the manual run command:
  `uv run python -m dream_job_radar.pipelines.radar`

# Non-goals

- no other extractor kinds (Wave 2)
- no other Greenhouse companies beyond onX (Planet Labs is a Wave 2
  config-only addition)
- no GitHub Actions schedule (Wave 3)
- no dedup beyond what `first_seen_at`/`last_seen_at` derivation gives
  for free
- no role removal detection ("role disappeared from board"); v1 only
  tracks observed open roles
- no application-status surface (Phase 3 in the initiative)
- no published blog post (Wave 4)

# Acceptance Criteria

1. `uv run python -m <pipeline_module>` (one command) runs the
   Greenhouse extractor against `onxmaps` and writes Parquet to
   `r2://pipelines/raw/greenhouse/onxmaps/` without error.
2. The R2 prefix contains at least one Parquet file after the run
   (verifiable via `boto3` list).
3. `MotherDuck` query
   `SELECT count(*) FROM current_open_roles WHERE company='onX'`
   returns a positive integer.
4. The `current_open_roles` view exposes at minimum:
   `company, title, url, location, posted_at, last_seen_at`.
5. All onX roles in the result satisfy the title-keyword filter
   (`data | engineer | GIS | geospatial`, case-insensitive). Verify by
   eyeballing at least 10 rows; if onX has fewer than 10 matching open
   roles, eyeball all of them.
6. A MotherDuck Dive over `current_open_roles` renders the columns
   above and is reachable at a stable URL.
7. Iframe-embed attempt on a scratch page on `loughondata.com` is
   documented in the ticket Evidence section as either working
   (with a screenshot) or not-working (with the failure mode). Either
   outcome closes this AC.
8. README.md documents the manual run command for the pipeline.

# Coverage

Covers: ticket-local acceptance criteria above. No spec exists yet for
this work. Promote to a spec before W2 if multiple extractor kinds need
to share a contract.

# Claim Matrix

None - no spec contract; ticket-local acceptance criteria only.

# Execution Notes

- Project module path should be `src/dream_job_radar/` (PEP 420 namespace
  not needed; standard src layout). Update `pyproject.toml`
  `[tool.hatch.build.targets.wheel]` if needed when uv generates the
  wheel.
- dlt filesystem destination R2 config (in `.dlt/config.toml` or env):
  ```toml
  [destination.filesystem]
  bucket_url = "s3://pipelines/raw"

  [destination.filesystem.credentials]
  aws_access_key_id   = "<from R2_ACCESS_KEY_ID>"
  aws_secret_access_key = "<from R2_SECRET_ACCESS_KEY>"
  endpoint_url = "https://<R2_ACCOUNT_ID>.r2.cloudflarestorage.com"
  region_name = "auto"
  ```
  Prefer reading from `os.environ` rather than committing config.toml.
- Title-keyword filter is a simple lowercase substring check across
  `title`. Do not use regex unless evidence shows it's needed.
- `posted_at` should come from Greenhouse's `updated_at` for v1; rename
  later if a Wave 2 extractor uses a different shape.
- `first_seen_at` / `last_seen_at` derivation: dlt writes a load-id and
  load-timestamp metadata per file. The view can derive
  `first_seen_at = min(load_ts) over (partition by role_id)` and
  `last_seen_at = max(load_ts) over (partition by role_id)`. If that
  proves awkward, fall back to writing an explicit `fetched_at` column
  in the resource.
- Dive setup is UI-driven on MotherDuck; document the step-by-step
  rather than scripting it.
- Keep the placeholder file at `r2://pipelines/smoke/placeholder.parquet`
  alone for now; delete in a later cleanup.

# Blockers

None.

# Next Move / Next Route

Ralph implementation packet. The extractor + pipeline + view fit one
bounded iteration with a clear write boundary
(`extractors/`, `pipelines/`, `motherduck/`). The Dive setup and embed
attempt are local edits the parent (you) drives after the child returns.

# Ralph Readiness

Bounded iteration: one dlt resource for Greenhouse + one pipeline entry
point + one MotherDuck view DDL. Single uv-managed Python repo.

Write boundary:
- `src/dream_job_radar/extractors/greenhouse.py`
- `src/dream_job_radar/pipelines/radar.py`
- `src/dream_job_radar/__init__.py`
- `src/dream_job_radar/extractors/__init__.py`
- `src/dream_job_radar/pipelines/__init__.py`
- `motherduck/views.sql`
- `pyproject.toml` (only if a new dep like `requests` is needed)
- `README.md` (run-command section only)

Likely verification posture: `observation-first`. Evidence is the
Parquet files in R2 and the SELECT count(*) result from MotherDuck.

Expected output contract:
- code that produces a successful pipeline run end-to-end
- a `motherduck/views.sql` file that the parent runs once in MotherDuck
- terminal output: dlt run summary showing rows written + Parquet
  filenames
- the `(company, count)` SELECT result from MotherDuck

# Evidence

Expected on completion:

- terminal output of the pipeline run
- output of a `boto3 list_objects_v2` against
  `s3://pipelines/raw/greenhouse/onxmaps/` showing Parquet files
- terminal output of the MotherDuck count query
- screenshot of the rendered Dive
- pass/fail outcome of the iframe-embed attempt on
  `loughondata.com`, with screenshot or failure log

Captured (Ralph iteration 1, 2026-04-29T23:32Z):

AC1 — pipeline runs end-to-end:
```
$ uv run python -m dream_job_radar.pipelines.radar
... onxmaps: 8 ...
Pipeline dream_job_radar load step completed in 3.60 seconds
1 load package(s) were loaded to destination filesystem and into dataset greenhouse
The filesystem destination used s3://pipelines/raw location to store data
Load package 1777505542.5649621 is LOADED and contains no failed jobs
```

AC2 — Parquet under the contracted prefix:
```
$ list_objects_v2 Bucket=pipelines Prefix=raw/greenhouse/onxmaps/
KeyCount= 1
  raw/greenhouse/onxmaps/1777505542.5649621.8c17618d4c.parquet  8373 bytes
```

AC3 — view returns rows:
```
md: SELECT count(*) FROM current_open_roles
    WHERE source_kind='greenhouse' AND ats_slug='onxmaps'
-> 8
```

AC4 — view exposes contracted shape: `company, source_kind, ats_slug,
role_id, title, url, location, posted_at, fetched_at, first_seen_at,
last_seen_at`. (Ticket spec named `last_seen_at` and the columns above;
view also adds `first_seen_at` per packet for free.)

AC5 — keyword filter holds. All 8 returned roles satisfy the
`data | engineer | gis | geospatial` substring filter:

```
('General Consideration - Engineering', 'Missoula, MT')
('General Consideration - Geospatial', 'Missoula, MT')
('iOS Engineer - Growth', 'Bozeman, MT')
('Staff Data Engineer ', 'Bozeman, MT')
('Senior Software Engineer - Map Viewer', 'Bozeman, MT')
('Senior Geospatial Analyst - Offroad', 'Missoula, MT')
('Staff Software Engineer - AI ', 'Bozeman, MT')
('Data Scientist III - AI & Machine Learning', 'Missoula, MT')
```

Cross-checked vs upstream Greenhouse `onxmaps` board: 27 total roles,
8 matched, no false positives. Excluded titles include "Business
Intelligence Analyst", marketing, customer-experience, product-design,
director-track roles — correctly out of v1 scope.

AC8 — README documents `uv run python -m dream_job_radar.pipelines.radar`
plus the one-liner that materializes `motherduck/views.sql` against
MotherDuck.

AC6 (Dive renders at stable URL) and AC7 (iframe embed attempt on
`loughondata.com`) are parent work after this ticket reaches `closed`.
They were intentionally out of the Ralph packet's scope.

# Critique Disposition

Risk class: medium

Critique policy: recommended

Policy rationale: the patterns this ticket establishes (R2 prefix
layout, dlt resource shape, MotherDuck view shape, the
title-keyword filter, the `current_open_roles` schema) propagate into
every Wave 2 extractor. A subtly wrong pattern here multiplies into
four extractor kinds and is more painful to undo later than to catch
now.

Required critique profiles:
- code-quality (review of the dlt resource and pipeline shape)
- schema-fitness (review of the `current_open_roles` view shape against
  what Wave 2 extractor kinds will plausibly need to fit into it)

Findings: see `critique:walking-skeleton-iter1` (8 findings, all low or
medium, none `changes_required`). Verdict: `pass_with_findings`.

Disposition status: resolved — all findings are open as deferred follow-up
items (promote `wiki:extractor-shape` and revisit during retrospective);
none block ticket closure.

Deferral / not-required rationale: N/A

# Wiki Disposition

Wiki promotion candidate after closure. The Wave 2 plan slot
("each extractor is one dlt resource family, reading from a
config-driven list of companies") is exactly the kind of compounding
explanation that should not live only in this ticket. Promote a
`wiki:extractor-shape` page during the retrospective pass after this
ticket closes.

# Acceptance Decision

Accepted by: pending
Accepted at: pending
Basis: pending — acceptance criteria 1–8 all met with evidence and the
required critique profiles either passed or had findings resolved or
explicitly accepted.
Residual risks: pending

# Dependencies

Hard prerequisites:

- `ticket:9mtt9h6j` (closed) — provides R2 bucket, MotherDuck workspace,
  R2 secret in MotherDuck, env vars in `.env`.

Soft references:

- `research:ats-discovery` — names onX as a confirmed Greenhouse source.
- `initiative:close-the-loop` — defines the v1 title-keyword filter.

# Journal

- 2026-04-29 — ticket created from `plan:v1-radar` Wave 1. Status set
  directly to `ready` because all readiness-checklist items pass at
  creation time. Critique-recommended; required profiles named. Next
  route: Ralph implementation packet.
- 2026-04-29 — Ralph packet compiled at
  `.loom/packets/ralph/walking-skeleton-20260429T231616Z.md`
  (style: reference-first, posture: observation-first, source SHA
  29e1b17). Awaiting child execution.
- 2026-04-29 — Ralph iteration 1 returned `continue`. AC1–AC5 + AC8
  satisfied with observation-first evidence (see Evidence section).
  Status advanced to `review_required` per packet recommendation;
  required critique profiles are code-quality and schema-fitness.
  Schema-fitness deviation accepted by parent: dlt's filesystem
  destination always prefixes `<dataset_name>/` under bucket_url, so
  honoring the observable path requirement
  `r2://pipelines/raw/greenhouse/onxmaps/` forced
  `dataset_name = "greenhouse"` (not `radar` as the packet wrote).
  Wave 2 will run one pipeline per source_kind with the source_kind
  as `dataset_name`. Parent updated `plan:v1-radar` to record the
  pattern. Critique pass next.
- 2026-04-29 — Critique landed at
  `.loom/critique/walking-skeleton-iter1.md` covering both required
  profiles (code-quality, schema-fitness). Verdict
  `pass_with_findings`; 8 findings, all low/medium, none
  `changes_required`. Disposition resolved — findings tracked as
  deferred retrospective follow-up. AC6 (Dive) and AC7 (iframe embed)
  remain open as parent local work; once recorded, ticket can move to
  `complete_pending_acceptance`.
