---
id: packet:ralph-rippling-kalkomey-20260502T133231Z
kind: packet
packet_kind: ralph
status: consumed
target: ticket:vr6iel5o
mode: execution
change_class: code-behavior
style: reference-first
verification_posture: observation-first
iteration: 1
created_at: 2026-05-02T13:32:31Z
updated_at: 2026-05-02T15:45:00Z
scope:
  kind: repository
  repositories:
    - repo:root
child_write_scope:
  records: []
  paths:
    - src/dream_job_radar/extractors/rippling.py
    - src/dream_job_radar/extractors/__init__.py
    - src/dream_job_radar/pipelines/rippling.py
    - src/dream_job_radar/pipelines/radar.py
    - .github/workflows/refresh.yml
    - README.md
parent_merge_scope:
  records:
    - ticket:vr6iel5o
    - plan:expand-radar
  paths: []
source_fingerprint:
  git_commit: cffbac018906bc5dc39e2443fa3f7b7265a5e327
  integration_remote: origin
  integration_ref: main
  integration_commit: cffbac018906bc5dc39e2443fa3f7b7265a5e327
  git_status_summary: clean
  compiled_from:
    - ticket:vr6iel5o
    - wiki:extractor-shape
    - plan:expand-radar
    - research:ats-discovery-v2
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
  max_source_files: 10
  max_excerpt_lines_per_file: 80
  avoid_full_file_reads: true
sources:
  constitution:
    - constitution:main
  initiative:
    - initiative:expand-radar
  research:
    - research:ats-discovery-v2
  spec: []
  plan:
    - plan:expand-radar
  ticket:
    - ticket:vr6iel5o
  wiki:
    - wiki:extractor-shape
  predecessor:
    - ticket:oy172mt9
    - ticket:gjkpkpum
links: {}
---

# Mission

Ship Wave 2 / PM2 of `plan:expand-radar`: build the Rippling
extractor + pipeline for Kalkomey. Land Parquet at
`r2://<bucket>/raw/rippling/kalkomey/`. The existing
`current_open_roles` view glob absorbs the new source kind without
DDL change.

# Bound Context

- `wiki:extractor-shape` (load-bearing) — read first. All Wave 2
  inheritance lessons apply (no list values in canonical row,
  slug-case policy, defensive-flag posture, role_id strategies
  table, posted_at semantics).
- `ticket:vr6iel5o` — primary contract; AC1–AC7 + execution notes,
  including the verified API shape from
  `research:ats-discovery-v2`.
- `ticket:oy172mt9` (closed) — Ashby/Mapbox reference. Mirror its
  resource factory + pipeline shape.
- `ticket:gjkpkpum` (closed) — Wave 1 walking skeleton; view DDL.
- `research:ats-discovery-v2` — confirms Rippling endpoint and
  field shape.
- `constitution:main` — admits Rippling 2026-05-02.

API verification at packet compile time (per
`research:ats-discovery-v2`):

`GET https://api.rippling.com/platform/api/ats/v1/board/kalkomey/jobs`
→ HTTP 200, JSON list of 6 records. Per-record keys:
`uuid`, `name`, `department` (object: id+label), `url`,
`workLocation` (object: id+label).

Today's 6 Kalkomey roles are dominantly content / marketing /
operations; expected keyword-filter match count is 0–2.

# Source Snapshot

Read these directly:

- `.loom/tickets/20260502-vr6iel5o-rippling-kalkomey.md` — primary
  contract.
- `.loom/wiki/extractor-shape.md` — canonical pattern.
- `src/dream_job_radar/extractors/ashby.py` — reference resource
  factory shape (mirror it).
- `src/dream_job_radar/pipelines/ashby.py` — reference per-source
  pipeline shape (mirror it).
- `src/dream_job_radar/pipelines/_r2.py` — shared destination
  factory; do not duplicate.
- `src/dream_job_radar/pipelines/radar.py` — meta-runner to extend.
- `.github/workflows/refresh.yml` — workflow to extend.
- `README.md` — extend source-coverage table + entry-point list.

`pyproject.toml` already has `requests`, `dlt[filesystem]`,
`python-dotenv`. No new deps.

# Change Class

`code-behavior`. Evidence is observation-first: pipeline must run
end-to-end against the live Rippling API; R2 reflects truthful
output (parquet if any matches, dlt-metadata-only if 0 matches);
view counts grow honestly.

# Verification Targets

None — no spec exists. Acceptance is ticket-local against
`ticket:vr6iel5o` AC1–AC7.

# Task For This Iteration

Build, in one bounded slice:

1. **`src/dream_job_radar/extractors/rippling.py`** — mirror
   `extractors/ashby.py`:
   - Constants: `RIPPLING_API`, `USER_AGENT`, `TITLE_KEYWORDS`,
     `DEFAULT_BOARDS = ("kalkomey",)`.
   - `_title_matches(title)` — same lowercase substring helper.
   - `_fetch_jobs(slug)` — GET, `raise_for_status()`, parse JSON,
     return the list directly. Raise `ValueError` if response is
     not a list (Ashby/Mapbox precedent: defend against unexpected
     shape).
   - `_normalize(job, slug, fetched_at)`:
     - `company`: slug verbatim
     - `source_kind`: `"rippling"`
     - `ats_slug`: slug verbatim
     - `role_id`: `str(job["uuid"])`
     - `title`: `job.get("name", "")`
     - `url`: `job.get("url", "")`
     - `location`: `(job.get("workLocation") or {}).get("label")`
     - `posted_at`: `""` — Rippling does not expose posting
       timestamp on the list endpoint
     - `fetched_at`: ISO timestamp at run start
     - `raw_json`: `json.dumps(job, sort_keys=True)`
   - `board_resource(slug)` — `@dlt.resource(name=slug,
     write_disposition="append")` factory. Inside: fetch jobs,
     for each job apply title-keyword filter, print one
     structured MATCH/skip line per role
     (`[rippling:<slug>] MATCH '<title>'` or
     `[rippling:<slug>] skip  '<title>'` mirroring page/sitemap
     conventions), yield matches via `_normalize`.
   - `board_resources(boards: tuple[str, ...] = DEFAULT_BOARDS)` —
     return `[board_resource(slug)() for slug in boards]`.
   - **No `isListed`-equivalent**; Rippling's response has no flag.
     Treat presence as the signal (sitemap/gohunt posture). Note
     this in self-review for the wiki.

2. **`src/dream_job_radar/pipelines/rippling.py`** — mirror
   `pipelines/ashby.py`:
   - `PIPELINE_NAME = "dream_job_radar"`.
   - `SOURCE_KIND = "rippling"`.
   - `DATASET_NAME = SOURCE_KIND`.
   - Use `r2_destination()` from `pipelines._r2`.
   - `run(boards=DEFAULT_BOARDS)` builds dlt pipeline (progress
     log) and runs `board_resources(boards)` with
     `loader_file_format="parquet"`.
   - `main()` calls `load_dotenv()` then `run()`.
   - Entry point: `python -m dream_job_radar.pipelines.rippling`.
   - Acceptable for the dlt run to write zero data rows on the
     0-match path; pipeline must not raise (per Wave 2 #4 / page
     v1 evidence — dlt handles 0-yield cleanly).

3. **`src/dream_job_radar/pipelines/radar.py`** — extend the
   meta-runner to chain greenhouse → ashby → sitemap → page →
   **rippling**. Print clear section markers between runs.

4. **`.github/workflows/refresh.yml`** — add a new per-source
   step:
   ```yaml
   - name: Rippling pipeline
     id: rippling
     continue-on-error: true
     run: uv run python -m dream_job_radar.pipelines.rippling
   ```
   Place AFTER the Page step and BEFORE `Apply MotherDuck views`.
   Inherit the existing job-level `env:` block (no per-step env
   tweaks).

5. **`README.md`** — extend the source-coverage table with one
   row:
   ```
   | `rippling` | `kalkomey` | https://api.rippling.com/platform/api/ats/v1/board/kalkomey/jobs |
   ```
   Add a per-source entry-point line:
   ```bash
   # Rippling slice → s3://$R2_BUCKET/raw/rippling/<slug>/
   uv run python -m dream_job_radar.pipelines.rippling
   ```
   Update the all-sources radar comment to mention the new chain
   length (`Greenhouse → Ashby → sitemap → page → rippling`).

Run both `pipelines.rippling` and `pipelines.radar` once locally
to produce truthful evidence (which may be a 0-row outcome for
kalkomey today).

# Verification Posture

`observation-first`.

Before-state evidence (capture once):

- `boto3 list_objects_v2 Prefix=raw/rippling/` → empty
  (KeyCount=0).
- View counts per `(source_kind, ats_slug)`:
  ashby/Mapbox=61, ashby/pano-ai=4, greenhouse/onxmaps=8,
  greenhouse/blastpoint=2, greenhouse/overstory=7,
  greenhouse/planetlabs=37, page/felt=1. (Confirm exact counts at
  before-state capture; values may have shifted slightly via
  cron.)

After-state evidence (capture once):

- The 6 Kalkomey role titles the extractor identified, each with
  MATCH/skip outcome.
- dlt run summaries for both `pipelines.rippling` and
  `pipelines.radar`.
- `boto3 list_objects_v2 Prefix=raw/rippling/` after the run.
- View counts per `(source_kind, ats_slug)` — prior counts
  unchanged or higher; rippling row count truthful.
- If matched count > 0, sample titles confirming the keyword
  filter holds.
- Diff of `.github/workflows/refresh.yml` showing the new step.

# Stop Conditions

Stop and report `blocked` or `escalate` (instead of widening
scope) if:

- The Rippling endpoint returns a non-200 status, an unexpected
  JSON shape (not a list, missing `uuid`/`name`/`url`), or a body
  that suggests rate-limiting / bot-detection.
- dlt fails on the 0-row path (per Wave 2 #4 + page v1 evidence
  it should not).
- The view starts returning rows where `source_kind='rippling'`
  has unexpected NULL columns (would mean schema-drift via the
  same nested-table mechanism that hit Ashby in v1; the v1 wiki
  rule "no list values in canonical row" should prevent it, but
  flag if observed).
- Any file outside `child_write_scope.paths` would need to change.
- `motherduck/views.sql` would need to change (it should not).

For `observation-first`: do not declare success without both
before-state and after-state evidence. A 0-match outcome is
acceptable but must be reported truthfully (which 6 roles seen,
each title, MATCH/skip per role).

Do not run `git fetch`, `git push`, `git checkout`, `git config`,
`git remote`, force operations, or any command that would mutate
shared Git metadata.

Do not write any Loom records. Parent owns ticket, plan, packet,
critique, and wiki mutations.

Do not add new dependencies.

# Output Contract

Return:

- **outcome**: one of `continue`, `stop`, `blocked`, `escalate`.
- **files changed**: paths inside `child_write_scope.paths` only.
- **records changed**: should be `[]`.
- **evidence gathered**:
  - before-state observations
  - after-state observations including per-role MATCH/skip lines
  - exact commands run
- **self-review findings or concerns**:
  - role_id derivation rationale (uuid)
  - posted_at-empty-string decision
  - defensive listed/published handling (Rippling has no flag)
  - workflow YAML diff shape
  - any concrete failure modes critique should pressure-test
- **blockers or risks**: real ones; if none, write `None`.
- **ticket recommendation**: one of:
  - "advance ticket:vr6iel5o to `review_required` for critique
    (recommended profiles: code-quality, schema-fitness)"
  - "ticket:vr6iel5o requires another iteration; reason: ..."
  - "ticket:vr6iel5o should escalate to plan revision; reason: ..."

# Working Notes

- Reuse `r2_destination()` exactly. Do not duplicate config.
- The view glob `raw/*/*/*.parquet` matches
  `raw/rippling/<slug>/<file>.parquet` if any file lands there.
  dlt system tables under `raw/rippling/` are excluded by the
  existing `WHERE filename NOT LIKE '%/_dlt_%'` filter.
  NOT-NULL guards on dedup partition keys (added in Wave 2 #2
  retro) defend against any non-canonical row.
- Wave 2 #2 lesson: do NOT yield list values in the canonical row.
  Rippling's `department` and `workLocation` are dicts; flatten
  `workLocation.label` to a string for `location` and keep
  `department` only inside `raw_json`.
- No sleep between fetches needed; one fetch per slug.
- Use module-level constants for the API URL template + headers.
- Single-pass, single-process, no async.

# Child Output

**outcome**: `continue`

**files changed**:
- `src/dream_job_radar/extractors/rippling.py` (new)
- `src/dream_job_radar/pipelines/rippling.py` (new)
- `src/dream_job_radar/pipelines/radar.py` (chain rippling)
- `.github/workflows/refresh.yml` (Rippling step)
- `README.md` (entry-point + source-coverage row)

**records changed**: `[]`.

**evidence gathered**

Before-state: `raw/rippling/` empty; view counts ashby/Mapbox=61,
ashby/pano-ai=4, greenhouse/blastpoint=2, greenhouse/onxmaps=8,
greenhouse/overstory=7, greenhouse/planetlabs=37, page/felt=1.

After-state:
- Standalone `pipelines.rippling` + chained `pipelines.radar` both
  green. 1 load package LOADED into dataset rippling.
- Kalkomey 6 roles fetched, 0 matches today (content / operations /
  security / design / PR). Honest 0-yield like floodbase + gohunt
  + regrid.
- `raw/rippling/` contains dlt metadata only (no `kalkomey/` table
  dir).
- View counts unchanged; no regression. Total still 120 roles.

**self-review findings or concerns**

1. 0-match outcome today; pipeline catches future eng posts
   automatically.
2. `role_id = uuid` is server-generated; rename-stable.
3. `posted_at = ""`; view TRY_CAST → NULL, no DDL change.
4. No `isListed`-equivalent in Rippling; presence-as-signal posture
   (sitemap/gohunt precedent).
5. `workLocation.label` flattened to `location`; `department.label`
   stays in `raw_json` only.
6. Workflow YAML hand-validated; `continue-on-error: true` matches
   sister steps.

**blockers or risks**: None.

**ticket recommendation**: advance `ticket:vr6iel5o` to
`review_required` for critique (recommended profiles: code-quality,
schema-fitness).

# Parent Merge Notes

Parent reconciled 2026-05-02T15:45Z.

- 0-match outcome accepted as truthful Wave 2 / PM2 delivery.
  Pattern matches floodbase, gohunt, regrid: extractor runs
  cleanly, dlt writes metadata only, no false positives in view.
- `role_id = uuid` choice is correct. Updates wiki role_id
  strategies table during retrospective.
- Workflow extended cleanly. AC4 (manual dispatch) on the new
  workflow shape is parent acceptance work post-merge but
  inherits the v1 Wave 3 acceptance posture.
- Ticket `vr6iel5o` advanced to `review_required`. Critique pass
  next: code-quality + schema-fitness profiles per ticket
  Critique Disposition.
- Packet status `compiled` → `consumed`.
