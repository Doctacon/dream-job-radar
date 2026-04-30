---
id: ticket:oy172mt9
kind: ticket
status: closed
change_class: code-behavior
risk_class: medium
created_at: 2026-04-30T00:48:00Z
updated_at: 2026-04-30T01:15:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:close-the-loop
  plan: plan:v1-radar
  constitution: constitution:main
  decision: decision:0001-storage-backend-r2
  wiki: wiki:extractor-shape
  predecessor: ticket:gjkpkpum
external_refs:
  ashby: https://api.ashbyhq.com/posting-api/job-board/Mapbox
depends_on:
  - ticket:gjkpkpum
---

# Summary

Wave 2 #2: build the second extractor kind — Ashby — and connect it
to Mapbox. Lands Parquet at `r2://<bucket>/raw/ashby/Mapbox/` and
exposes Mapbox roles through the existing `current_open_roles` view.

Critical for the close-the-loop plan: this is the first test that the
shape established in Wave 1 (`wiki:extractor-shape`) generalizes to a
non-Greenhouse source kind. Field names, slug casing, and id format
all differ from Greenhouse.

# Context

`wiki:extractor-shape` is the canonical reference. Read it first. The
contract:
- one dlt pipeline per source kind, `pipeline_name = dream_job_radar`,
  `dataset_name = <source_kind>`
- `bucket_url = s3://<R2_BUCKET>/raw`, default layout
- one resource per slug, named after the slug, table-per-slug under
  `raw/<source_kind>/<ats_slug>/`
- v1 keyword filter applied at extract time, before yield
- view stays unchanged; the glob `raw/*/*/*.parquet` already covers
  any new source kind

Per `research:ats-discovery`, Mapbox hosts on Ashby with slug `Mapbox`
(case-sensitive). Verified 2026-04-30:
`GET https://api.ashbyhq.com/posting-api/job-board/Mapbox` returns
HTTP 200 with `apiVersion` + `jobs` keys. `jobs` is a list of objects
with the following shape (relevant fields only):

| Field             | Type            | Notes                                |
|-------------------|-----------------|--------------------------------------|
| `id`              | string (UUID)   | stable per role                      |
| `title`           | string          | role title                           |
| `department`      | string          | single value (Greenhouse uses list)  |
| `team`            | string          | single value                         |
| `location`        | string          | single value                         |
| `secondaryLocations` | list of strs | usually empty                        |
| `publishedAt`     | ISO timestamp   | use as `posted_at`                   |
| `isListed`        | bool            | filter to `true` defensively         |
| `isRemote`        | bool            | informational                        |
| `workplaceType`   | string          | informational                        |
| `jobUrl`          | string          | use as `url`                         |
| `applyUrl`        | string          | not exposed in view                  |
| `descriptionHtml` | long string     | not exposed; lives in raw_json       |
| `descriptionPlain`| long string     | not exposed; lives in raw_json       |

Probe shows 84 total roles; 59 match the v1 keyword filter
(case-insensitive substring against
`data | engineer | gis | geospatial`). Mapbox publishes many
duplicates by title across regions (each with distinct UUIDs) — the
view's `(source_kind, ats_slug, role_id)` dedup preserves them, same
as the Planet Labs case.

# Why Now

Ashby is the first non-Greenhouse extractor. Shipping it before the
heavier #3 (page monitor) and #4 (sitemap monitor) tickets:
- proves the shape generalizes across structurally different APIs
- de-risks the Wave 2 retrospective (we want at least two source kinds
  in the view before re-evaluating the keyword filter and column
  semantics)
- keeps the harder HTML-parsing tickets isolated so a setback in one
  cannot block the others

# Scope

- Add `src/dream_job_radar/extractors/ashby.py` modeled on
  `extractors/greenhouse.py`. Mirror the resource-factory shape:
  - `DEFAULT_BOARDS = ("Mapbox",)` — preserve case, Ashby is
    case-sensitive in the URL.
  - `board_resource(slug)` returns one dlt resource named after the
    slug (so the table directory becomes
    `raw/ashby/<slug>/`).
  - `board_resources(boards)` returns a list of one resource per slug.
  - Filter `isListed == True` before applying the title keyword
    filter (defensive against unlisted drafts).
  - Apply the same v1 title-keyword substring filter.
  - Normalize each job to the canonical column shape:
    `company` (slug verbatim), `source_kind` (`ashby`), `ats_slug`
    (slug verbatim), `role_id` (the UUID string), `title`, `url`
    (`jobUrl`), `location` (`location` if present, else
    `secondaryLocations[0]` if available, else `None`),
    `departments` (`[department]` wrapped in a list to match
    Greenhouse), `posted_at` (`publishedAt`), `fetched_at`
    (run start ISO), `raw_json` (full payload JSON-serialized).
- Add `src/dream_job_radar/pipelines/ashby.py` modeled on
  `pipelines/radar.py` but with `SOURCE_KIND = "ashby"` and
  `DATASET_NAME = "ashby"`. Reuse `_r2_destination()` shape (or
  factor it to a shared helper at `pipelines/_r2.py` if cleaner).
  Layout: `bucket_url = s3://<bucket>/raw`, default
  `{table_name}/{load_id}.{file_id}.{ext}` layout. Pipeline
  invocation: `uv run python -m dream_job_radar.pipelines.ashby`.
- Update `src/dream_job_radar/pipelines/radar.py` to also run the
  Ashby pipeline after Greenhouse, so the existing
  `python -m dream_job_radar.pipelines.radar` invocation continues to
  be the "run everything" entry point.
- Update `README.md` to document the per-source entry points and
  what each one writes.
- No view DDL change (the existing view glob is invariant under new
  source kinds).

# Non-goals

- No view change. If the Ashby data forces a view change, that is a
  loop-back to plan revision, not silent scope widening here.
- No revision of the title-keyword filter (FIND-002 still deferred).
- No GitHub Actions schedule (Wave 3).
- No new tests (FIND-007 still deferred until Wave 2 retrospective).
- No exposing `descriptionHtml` / `descriptionPlain` in the view; they
  live in `raw_json` for re-derivation if ever needed.

# Acceptance Criteria

1. `uv run python -m dream_job_radar.pipelines.ashby` runs end-to-end
   without error and writes Parquet to
   `r2://pipelines/raw/ashby/Mapbox/`.
2. `uv run python -m dream_job_radar.pipelines.radar` runs end-to-end
   without error and writes Parquet to both
   `r2://pipelines/raw/greenhouse/...` and
   `r2://pipelines/raw/ashby/Mapbox/`. (Existing onX + Planet Labs
   row counts must not regress.)
3. `boto3 list_objects_v2 Prefix=raw/ashby/Mapbox/` returns at least
   one Parquet object key.
4. MotherDuck query
   `SELECT count(*) FROM current_open_roles
    WHERE source_kind='ashby' AND ats_slug='Mapbox'`
   returns a positive integer (probe suggests ~59).
5. All Mapbox rows in the view satisfy the title-keyword filter
   (substring match). Verify by sampling at least 10 returned titles.
6. Existing onX (`source_kind='greenhouse', ats_slug='onxmaps'`) and
   Planet Labs (`ats_slug='planetlabs'`) row counts in the view are
   unchanged or higher (no regression).
7. README documents `python -m dream_job_radar.pipelines.ashby` and
   the all-sources `radar` entry point.

# Coverage

Ticket-local acceptance criteria above. No spec contract.
`wiki:extractor-shape` is the inheritable design.

# Claim Matrix

None — no spec contract; ticket-local acceptance criteria only.

# Execution Notes

- Ashby slug is case-sensitive in the URL. `mapbox` (lowercase) 404s.
  Preserve case both in the API call and in `ats_slug` / R2 path.
- Ashby publishes the same role multiple times per region with
  distinct UUIDs. The view dedup keys on
  `(source_kind, ats_slug, role_id)`, so all entries survive. This is
  upstream behavior, not a defect.
- `department` is a single string in Ashby vs a list in Greenhouse.
  Wrap in `[department]` so the canonical `departments` column stays
  list-shaped across source kinds.
- `descriptionHtml` is large (~2KB+ per role). Keeping it only in
  `raw_json` keeps Parquet small; the view does not select it.
- For the shared R2 destination config: a small refactor to
  `pipelines/_r2.py` is acceptable but optional. If left inline,
  copy the `_r2_destination()` shape and only change `SOURCE_KIND`.
  The destination configuration itself is identical across source
  kinds because `bucket_url` is `s3://<bucket>/raw` (no source-kind
  segment); only `dataset_name` differs.
- Polite User-Agent header: reuse `dream-job-radar/0.1`.

# Blockers

None.

# Next Move / Next Route

Ralph implementation packet. The work spans two new files, a touched
file (`pipelines/radar.py`), and a README update — wider write
boundary than the trivial Planet Labs ticket. Bounded packet keeps
the diff scope explicit and gives critique a concrete artifact to
inspect.

# Ralph Readiness

Bounded iteration: one new source-kind extractor + one new pipeline
entry + one all-sources runner update + README.

Write boundary:
- `src/dream_job_radar/extractors/ashby.py`
- `src/dream_job_radar/extractors/__init__.py` (only if a re-export
  is genuinely needed; otherwise leave empty)
- `src/dream_job_radar/pipelines/ashby.py`
- `src/dream_job_radar/pipelines/radar.py`
- `src/dream_job_radar/pipelines/_r2.py` (optional refactor; only if
  the duplication is uglier than the helper)
- `README.md`

Verification posture: `observation-first`. Evidence is the Parquet
files in R2 plus the MotherDuck row counts.

Expected output contract:
- working `python -m dream_job_radar.pipelines.ashby` invocation
- working `python -m dream_job_radar.pipelines.radar` invocation that
  runs both Greenhouse and Ashby
- ats-side regression evidence (onX + Planet Labs counts unchanged)
- 10-row Mapbox title sample confirming the filter

# Evidence

Expected on completion:

- terminal output of both pipeline invocations
- `boto3 list_objects_v2` for `s3://pipelines/raw/ashby/Mapbox/`
- MotherDuck `count(*)` per `(source_kind, ats_slug)`
- 10-row Mapbox title sample

Captured 2026-04-30T01:05Z (Ralph iteration 1):

AC1 — `python -m dream_job_radar.pipelines.ashby` runs end-to-end.
Verified after fix-and-rerun (initial run produced a polluting child
table; see Journal).

AC2 — `python -m dream_job_radar.pipelines.radar` runs end-to-end:
```
========================================================================
[radar] running greenhouse pipeline
========================================================================
... onxmaps: 8 ; planetlabs: 36 ...
Pipeline dream_job_radar load step completed in 1.76 seconds
1 load package(s) were loaded to destination filesystem and into dataset greenhouse
========================================================================
[radar] running ashby pipeline
========================================================================
... mapbox: 59 ...
Pipeline dream_job_radar load step completed in 2.72 seconds
1 load package(s) were loaded to destination filesystem and into dataset ashby
```

AC3 — Parquet under `raw/ashby/<slug>/`:
```
list_objects_v2 raw/ashby/  →
  raw/ashby/_dlt_loads/dream_job_radar__1777511068.398608.jsonl
  raw/ashby/_dlt_pipeline_state/...
  raw/ashby/_dlt_version/...
  raw/ashby/init
  raw/ashby/mapbox/1777511068.398608.4eb86a19f6.parquet  168073
```
Note: dlt lowercased the table-directory to `mapbox/` (slug case
policy resolved — see Acceptance Decision residual risks).

AC4 — view rows per `(source_kind, ats_slug)`:
```
md: SELECT source_kind, ats_slug, count(*) FROM current_open_roles
    GROUP BY 1,2 ORDER BY 1,2
-> ('ashby', 'Mapbox', 59)
   ('greenhouse', 'onxmaps', 8)
   ('greenhouse', 'planetlabs', 36)
```

AC5 — keyword filter holds for Mapbox sample (all 10 contain
`engineer` or `data`):
```
Software Development Engineer II, Traffic
Software Development Engineer II, Logistics API
Software Development Engineer II, iOS, Maps SDK
Software Development Engineer II (Data Engineer), HD Maps
Software Development Engineer II, NavNative
Engineering Manager,  Navigation SDK
Software Development Engineer I, Android, Navigation SDK
Senior Cloud Platform Engineer
Software Development Engineer II, Incidents
Software Development Engineer II, Incidents
```

AC6 — onX (8) and Planet Labs (36) row counts unchanged from
`ticket:tiv8bsu7` close-out.

AC7 — README documents per-source entry points (`pipelines.ashby`)
and the all-sources `pipelines.radar` entry, plus a source-coverage
table.

# Critique Disposition

Risk class: medium

Critique policy: recommended

Policy rationale: this is the first non-Greenhouse extractor. The
field shape and slug casing differ; how this extractor handles those
differences will be inherited by #3 (page monitor) and #4 (sitemap
monitor). A subtly wrong handling of department/location wrapping or
slug case will multiply across the remaining Wave 2 work.

Required critique profiles:
- code-quality (extractor shape vs Wave 1 reference)
- schema-fitness (canonical column wrapping vs upstream divergence;
  ats_slug case policy)

Findings: see `critique:ashby-mapbox-iter1` (7 findings, all low or
medium, none `changes_required`). Verdict: `pass_with_findings`.

Disposition status: resolved — FIND-001/002/003/006/007 are
deferred to retrospective for wiki/view updates. FIND-004 (`_r2.py`
refactor) and FIND-005 (radar.py rewrite) resolved by inspection.
None block ticket closure.

Deferral / not-required rationale: N/A

# Wiki Disposition

Likely no new wiki page if the shape generalizes cleanly. If Ashby
forces a meaningful refinement (e.g., a documented slug-case policy,
or a `secondaryLocations` fallback rule that other source kinds will
inherit), update `wiki:extractor-shape` rather than creating a new
page. Decide during the Wave 2 retrospective.

Promoted 2026-04-30 during the retrospective:

- `wiki:extractor-shape` — extended with four new sections derived
  from this iteration's findings:
  - "Canonical row must not contain Python list values" (FIND-001)
  - "Slug-case policy" (FIND-002)
  - "Defensive listed/published checks" (FIND-007)
  - "Duplicates by title are upstream behavior" (FIND-006)
  - `departments` removed from the canonical column table.

Direct record fixes (not new pages):

- `motherduck/views.sql` hardened with
  `AND source_kind IS NOT NULL AND ats_slug IS NOT NULL AND role_id IS NOT NULL`
  (FIND-003). Re-materialized; row counts unchanged.

Intentionally not promoted:

- The `r2_destination()` refactor (FIND-004) is implementation detail
  already documented in `pipelines/_r2.py`'s docstring; no wiki
  page needed.
- The `radar.py` rewrite (FIND-005) is a v1 internal API change with
  no external caller; Wave 3 will own scheduler-shape decisions.

# Acceptance Decision

Accepted by: Connor
Accepted at: 2026-04-30T01:15:00Z
Basis: AC1–AC7 satisfied with observation-first evidence (see
Evidence section). Required critique profiles ran
(`critique:ashby-mapbox-iter1`); verdict `pass_with_findings`, all 7
findings low/medium and tracked as deferred retrospective follow-up.
Schema-fitness deviations (drop `departments` from canonical, accept
lowercased path) accepted by parent and recorded in the packet
Parent Merge Notes.
Residual risks:
- `wiki:extractor-shape` is now stale by one column (`departments`)
  and missing the slug-case policy + duplicate-by-title +
  defensive-listed-flag notes. Will be updated immediately during
  this retrospective so Wave 2 #3 / #4 inherit the corrected
  contract.
- View hardening against non-canonical rows (FIND-003) deferred to
  retrospective decision.
- ats_slug case is preserved in data (`Mapbox`) but normalized in
  R2 path (`mapbox/`). Documented; not a defect.

# Dependencies

Hard prerequisites:
- `ticket:gjkpkpum` (closed) — provides the resource-factory shape,
  the dlt pipeline-config pattern, and the view.

Soft references:
- `wiki:extractor-shape` — canonical pattern.
- `research:ats-discovery` — confirms the Ashby endpoint and slug.
- `ticket:tiv8bsu7` (closed) — proved the resource factory
  generalizes within Greenhouse; this ticket proves it generalizes
  across source kinds.

# Journal

- 2026-04-30 — ticket created from `plan:v1-radar` Wave 2 #2 after
  manual API probe confirmed Ashby endpoint, field shape, and match
  count. Risk classified `medium`; critique `recommended` with two
  named profiles. Next route: Ralph implementation packet.
- 2026-04-30 — Ralph packet compiled at
  `.loom/packets/ralph/ashby-mapbox-20260430T004920Z.md`
  (style: reference-first, posture: observation-first, source SHA
  `a7ac43c`). Awaiting child execution.
- 2026-04-30 — Ralph iteration 1 returned `continue`. Initial run
  surfaced a schema-fitness bug: Ashby's non-empty `departments`
  list triggered dlt's nested-table normalization, creating a
  `raw/ashby/mapbox__departments/` parquet that polluted the view
  via `union_by_name=true` with a `(null, null, null)` row. Child
  fixed in-flight by removing `departments` from the canonical row
  in BOTH extractors (Greenhouse never tripped this because the
  `/jobs` endpoint omits departments and dlt dropped the empty
  column). Also surfaced: dlt's snake_case naming convention
  lowercased `Mapbox` → `mapbox` in the table-directory path. Data
  column `ats_slug` preserves source casing (`Mapbox`). Parent
  accepted both deviations: drop `departments` permanently, accept
  lowercased path. Status → `review_required`. Critique pass next.
- 2026-04-30 — Critique landed at
  `.loom/critique/ashby-mapbox-iter1.md`. Verdict
  `pass_with_findings`; 7 findings, all low/medium, none
  `changes_required`. FIND-001/002/003/006/007 deferred to
  retrospective for wiki + view updates. FIND-004/005 resolved by
  inspection. Parent accepted; status → `closed`.
- 2026-04-30 — Retrospective complete. `wiki:extractor-shape`
  updated with 4 new sections (canonical-list rule, slug-case
  policy, defensive listed/published checks, duplicate-by-title
  note) and `departments` removed from canonical columns.
  `motherduck/views.sql` hardened with NOT NULL guards on dedup
  partition keys; view re-materialized; row counts unchanged.
