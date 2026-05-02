---
id: ticket:vr6iel5o
kind: ticket
status: review_required
change_class: code-behavior
risk_class: medium
created_at: 2026-05-02T13:32:31Z
updated_at: 2026-05-02T15:45:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:expand-radar
  plan: plan:expand-radar
  constitution: constitution:main
  research: research:ats-discovery-v2
  wiki: wiki:extractor-shape
  predecessor:
    - ticket:gjkpkpum
    - ticket:oy172mt9
external_refs:
  rippling: https://api.rippling.com/platform/api/ats/v1/board/kalkomey/jobs
depends_on: []
---

# Summary

Wave 2 / PM2 of `plan:expand-radar`: build the **Rippling**
extractor kind and connect it to Kalkomey (HuntStand /
HuntWise). Lands Parquet at
`r2://<bucket>/raw/rippling/kalkomey/`. The existing
`current_open_roles` view glob absorbs the new source kind
without DDL change.

# Context

`research:ats-discovery-v2` confirmed the Rippling public board
API:

`GET https://api.rippling.com/platform/api/ats/v1/board/<slug>/jobs`

→ HTTP 200, JSON list of records with shape:

```json
{
  "uuid": "86cb9df0-2d01-4994-8e75-06e21ce17534",
  "name": "Content Editor (Contractor)",
  "department": {"id": "Marketing", "label": "Marketing"},
  "url": "https://ats.rippling.com/kalkomey/jobs/86cb9df0-...",
  "workLocation": {"label": "Remote (United States)", "id": "..."}
}
```

6 records at probe time. Constitutional allow-list updated
2026-05-02 to admit Rippling. No `posted_at` exposed in the list
response (treat as empty string, like page-monitor sources).

`wiki:extractor-shape` is the canonical inheritance pattern. New
extractor must honor:

- canonical row contains no Python list values
- slug case preserved in data column; R2 path follows dlt's
  snake_case normalization
- defensive listed/published flag check before keyword filter
  (Rippling has no obvious flag — sitemap-style "presence is the
  signal" applies; document the choice)
- duplicate-by-title is upstream behavior
- shared `pipelines._r2.r2_destination()` used as-is

# Why Now

PM1 of `plan:expand-radar` just closed (4 new companies via
config-only adds). Rippling is the cleanest of the three new
source kinds in this initiative — flat JSON list with stable
upstream UUIDs. Shipping it next proves the new-source-kind
inheritance pattern at v2 scale before PM3 (Polymer, research
loopback risk) and PM4 (page-monitor, fragility risk).

# Scope

- Add `src/dream_job_radar/extractors/rippling.py` modeled on
  `extractors/ashby.py`:
  - `RIPPLING_API = "https://api.rippling.com/platform/api/ats/v1/board/{slug}/jobs"`
  - `USER_AGENT = "dream-job-radar/0.1"`
  - `TITLE_KEYWORDS = ("data", "engineer", "gis", "geospatial")`
  - `DEFAULT_BOARDS = ("kalkomey",)` — slug verbatim
  - `_title_matches(title)` — same lowercase substring helper
  - `_fetch_jobs(slug)` — GET, raise_for_status, parse JSON,
    return the list (raise `ValueError` if response is not a
    list)
  - `_normalize(job, slug, fetched_at)`:
    - `company`: slug verbatim
    - `source_kind`: `"rippling"`
    - `ats_slug`: slug verbatim
    - `role_id`: `str(job["uuid"])`
    - `title`: `job.get("name", "")`
    - `url`: `job.get("url", "")`
    - `location`: `(job.get("workLocation") or {}).get("label")`
    - `posted_at`: `""` — Rippling does not expose a posting
      timestamp on the list endpoint
    - `fetched_at`: ISO timestamp at run start
    - `raw_json`: `json.dumps(job, sort_keys=True)`
  - `board_resource(slug)` — `@dlt.resource(name=slug,
    write_disposition="append")` factory; iterate jobs, apply
    title-keyword filter, yield matches; print one MATCH/skip
    line per role per Wave 2 v1 convention
  - `board_resources(boards: tuple[str, ...] = DEFAULT_BOARDS)` —
    return list of resources

- Add `src/dream_job_radar/pipelines/rippling.py` mirroring
  `pipelines/ashby.py`:
  - `PIPELINE_NAME = "dream_job_radar"`
  - `SOURCE_KIND = "rippling"`
  - `DATASET_NAME = SOURCE_KIND`
  - Use `r2_destination()` from `pipelines._r2`
  - `run(boards=DEFAULT_BOARDS)` builds dlt pipeline, runs
    `board_resources(boards)` with `loader_file_format="parquet"`
  - `main()` calls `load_dotenv()` then `run()`
  - Entry point: `python -m dream_job_radar.pipelines.rippling`

- Update `src/dream_job_radar/pipelines/radar.py` meta-runner to
  also chain `rippling_pipeline.run()` after `page_pipeline`.

- Update `.github/workflows/refresh.yml` to include a Rippling
  per-source step (with `continue-on-error: true`, mirroring the
  other 4).

- Update `README.md` source-coverage table + add `pipelines.rippling`
  entry point.

# Non-goals

- No HTML parsing — Rippling's response is structured JSON.
- No retry-with-backoff (carry v1 Wave 3 posture).
- No detail-page fetch for `posted_at` discovery — list endpoint is
  enough for v1.
- No view DDL change.
- No revision of the title-keyword filter.

# Acceptance Criteria

1. `uv run python -m dream_job_radar.pipelines.rippling` runs
   end-to-end without error and writes Parquet at
   `r2://pipelines/raw/rippling/kalkomey/` (note: dlt may lowercase
   the slug; record actual path).
2. `uv run python -m dream_job_radar.pipelines.radar` runs
   end-to-end exercising greenhouse + ashby + sitemap + page +
   rippling. Existing view counts unchanged or higher (no
   regression).
3. `boto3 list_objects_v2 Prefix=raw/rippling/` returns at least
   the dlt metadata; if any role matched the keyword filter,
   `raw/rippling/<slug>/` also has a Parquet file.
4. MotherDuck `count(*) FROM current_open_roles WHERE
   source_kind='rippling'` returns the truthful count.
   Probe-day distribution: 6 upstream roles total; expected
   match count is 0–2 today (most upstream roles are content /
   marketing).
5. If positive count, all sampled titles satisfy the v1 keyword
   filter.
6. `.github/workflows/refresh.yml` validates locally (hand-walk OR
   actionlint if available) and the new step matches the existing
   per-source step shape.
7. README documents `pipelines.rippling` and adds a row to the
   source-coverage table.

# Coverage

Ticket-local. No spec contract. `wiki:extractor-shape` is the
inheritable design.

# Claim Matrix

None — no spec contract; ticket-local acceptance criteria only.

# Execution Notes

- Rippling URL host is `api.rippling.com`. The API responds to
  plain GET with no User-Agent gating per probe; reuse the
  standard polite UA.
- `workLocation` may be a dict, a list (theoretically), or absent.
  Defensive code: `(job.get("workLocation") or {}).get("label")`.
- `department.label` is interesting but does NOT belong in the
  canonical row — keeping the row list-free per FIND-001 of the
  Ashby/Mapbox critique. Lives in `raw_json`.
- `posted_at = ""` aligns with the v1 page-monitor convention. The
  view's `TRY_CAST(posted_at AS TIMESTAMP)` already turns this
  into NULL (added 2026-05-01 fix). No view change needed.
- Slug case: probe showed `kalkomey` (lowercase) works. Match the
  Ashby pattern: store slug verbatim in `ats_slug` data column.
  R2 path will follow dlt's snake_case normalization.
- Defensive listed/published: Rippling's response has no
  `isListed`-equivalent. Treat presence as the signal (mirror
  sitemap/gohunt posture). Document explicitly in self-review.

# Blockers

None.

# Next Move / Next Route

Ralph implementation packet. New code (extractor + pipeline),
meta-runner update, workflow update, README. Critique recommended
(new source kind, inherits to future Rippling-hosted companies).

# Ralph Readiness

Bounded iteration: one new extractor + one new pipeline +
meta-runner + workflow + README.

Write boundary:

- `src/dream_job_radar/extractors/rippling.py`
- `src/dream_job_radar/extractors/__init__.py`
- `src/dream_job_radar/pipelines/rippling.py`
- `src/dream_job_radar/pipelines/radar.py`
- `.github/workflows/refresh.yml`
- `README.md`

Verification posture: `observation-first`.

Expected output contract:

- working `python -m dream_job_radar.pipelines.rippling` invocation
- working `python -m dream_job_radar.pipelines.radar` chain
- per-role MATCH/skip log lines
- view counts confirming no regression on prior source kinds
- README + workflow entries

# Evidence

Expected on completion:

- terminal output of standalone `pipelines.rippling` and
  all-sources `pipelines.radar` runs
- `boto3 list_objects_v2 Prefix=raw/rippling/`
- MotherDuck per-`(source_kind, ats_slug)` counts
- per-role MATCH/skip output for kalkomey
- the workflow YAML diff

Captured 2026-05-02T15:45Z (Ralph iteration 1):

AC1 — `pipelines.rippling` runs end-to-end, MATCH/skip per role:
```
[rippling:kalkomey] fetched 6 role(s) from board
[rippling:kalkomey] skip  'Content Editor (Contractor)'
[rippling:kalkomey] skip  'Director, Revenue Operations'
[rippling:kalkomey] skip  'Senior Information Security Manager'
[rippling:kalkomey] skip  'Senior Product Designer'
[rippling:kalkomey] skip  'Sr. Manager Content Strategy & Operations'
[rippling:kalkomey] skip  'Vice President, Public Affairs, Partnerships & Public Relations'
Pipeline dream_job_radar load step completed in 3.17 seconds
1 load package(s) were loaded to destination filesystem and into dataset rippling
```

AC2 — `pipelines.radar` chains greenhouse → ashby → sitemap →
page → rippling end-to-end without error. View counts post-run
unchanged from before-state (no regression on prior 7 slugs).

AC3 — `raw/rippling/` after run: dlt metadata only
(`_dlt_loads/`, `_dlt_pipeline_state/`, `_dlt_version/`, `init`).
No `kalkomey/` table dir — 0-yield is honest, same posture as
floodbase + gohunt + regrid.

AC4 — `count(*) WHERE source_kind='rippling'` = 0 (truthful).
Today's 6 Kalkomey roles are dominantly content / operations /
security / design / PR; none contain
`data | engineer | gis | geospatial`.

AC5 — N/A today (no matched titles to sample).

AC6 — workflow YAML extended: new "Rippling pipeline" step with
`id: rippling`, `continue-on-error: true`, placed between Page
and Apply Views. Job-level `env:` inherited. Hand-validated
against the existing per-source step shape; `actionlint`
unavailable locally.

AC7 — README updated:
- Source-coverage table row:
  `| rippling | kalkomey | https://api.rippling.com/.../kalkomey/jobs |`
- Per-source entry-point block:
  `uv run python -m dream_job_radar.pipelines.rippling`
- All-sources chain comment updated to include rippling.

Total view rows post-run: 120 (no change from 0-yield).

# Critique Disposition

Risk class: medium

Critique policy: recommended

Policy rationale: this is the third new source kind shipped (after
sitemap and page in v1). The Rippling API is clean, but the
extractor shape will be inherited by any future Rippling-hosted
company. Inherited critique profiles:

- code-quality (extractor shape vs Ashby/Mapbox v1 reference)
- schema-fitness (role_id stability, posted_at-empty decision,
  defensive-listed-flag handling, slug-case preservation)

Findings: see `critique:rippling-kalkomey-iter1` (7 findings: 1
medium, 6 low; none `changes_required`). Verdict:
`pass_with_findings`.

Disposition status: resolved-with-followup. FIND-001/002/003
deferred to PM5 retrospective for wiki updates. FIND-004/005
inherited from v1 critiques (no change). FIND-006 resolved by
inspection. FIND-007 deferred to PM5.

Deferral / not-required rationale: N/A

# Wiki Disposition

Likely a meaningful update to `wiki:extractor-shape` during the
retrospective: Rippling adds a fourth API-style source-kind row to
the role_id strategies table and a fifth source-kind to the
`posted_at` semantic table. Update during retrospective so PM3
(Polymer) inherits a complete reference.

# Acceptance Decision

Accepted by: pending
Accepted at: pending
Basis: pending — AC1–AC7 satisfied with observation-first evidence
plus required critique findings either resolved or accepted.
Residual risks: pending

# Dependencies

Hard prerequisites:

- v1 `initiative:close-the-loop` closed; v1 extractor patterns
  available (done 2026-05-02).
- `research:ats-discovery-v2` confirmed Rippling endpoint shape
  (done 2026-05-02).
- `constitution:main` admits Rippling as allowed source
  (done 2026-05-02).

Soft references:

- `wiki:extractor-shape` — canonical pattern.
- `ticket:oy172mt9` (closed) — Ashby/Mapbox reference shape.
- `ticket:gjkpkpum` (closed) — original walking skeleton, view DDL.

# Journal

- 2026-05-02 — ticket created from `plan:expand-radar` Wave 2 after
  PM1 closed. Risk classified `medium`; critique `recommended`
  with two named profiles. Inherits all v1 Wave 2 / Wave 3 critique
  lessons via `wiki:extractor-shape`. Next route: Ralph
  implementation packet.
- 2026-05-02 — Ralph packet compiled at
  `.loom/packets/ralph/rippling-kalkomey-20260502T133231Z.md`
  (style: reference-first, posture: observation-first, source SHA
  `cffbac0`). Awaiting child execution.
- 2026-05-02 — Ralph iteration 1 returned `continue`. Standalone +
  chained pipeline runs both green. Kalkomey 6 roles fetched, 0
  match the v1 keyword filter today (content/ops/security/design/
  PR). Honest 0-yield. Workflow YAML extended with new per-source
  step. Status → `review_required`. Critique pass next.
- 2026-05-02 — Critique landed at
  `.loom/critique/rippling-kalkomey-iter1.md`. Verdict
  `pass_with_findings`; 7 findings (1 medium, 6 low), none
  `changes_required`. Acceptance recommendation: "active
  follow-up required" — close after manual workflow dispatch
  succeeds on the new shape. Wiki updates deferred to PM5
  retrospective.
