---
id: ticket:7n0yj21k
kind: ticket
status: review_required
change_class: code-behavior
risk_class: medium
created_at: 2026-05-02T13:52:22Z
updated_at: 2026-05-02T14:00:00Z
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
    - ticket:xwfvoj4o
    - ticket:vr6iel5o
external_refs:
  upstream_careers: https://www.upstream.tech/careers
  upstream_jobs_subdomain: https://jobs.upstream.tech
depends_on: []
---

# Summary

Wave 3 / PM3 of `plan:expand-radar`: build the **Polymer**
extractor kind and connect it to Upstream Tech. Lands Parquet at
`r2://<bucket>/raw/polymer/upstream-tech/`. The existing
`current_open_roles` view glob absorbs the new source kind without
DDL change.

# Context

Polymer is an ATS used by Upstream Tech and (potentially) others.
The shape is hybrid: index from a parent careers page, role data
from per-role JSON-LD on a custom `jobs.<company>.<tld>` subdomain.

Probe at packet compile time (2026-05-02):

- `https://www.upstream.tech/careers` → 200, parses cleanly,
  contains 3 references to `jobs.upstream.tech/<id>` (IDs:
  23408, 39157, 39581).
- `https://jobs.upstream.tech/<id>` → 200, each page carries a
  clean JSON-LD `<script type="application/ld+json">` block with
  `@type="JobPosting"` and Schema.org-standard fields:
  - `title` (string)
  - `datePosted` (timestamp, format
    `'YYYY-MM-DD HH:MM:SS UTC'` — non-ISO, needs reformatting)
  - `url` (canonical role URL)
  - `jobLocation` (nested `Place > address > addressCountry`)
  - `employmentType`, `hiringOrganization`, `description`,
    `applicantLocationRequirements`, `directApply`, `identifier`
- `jobs.upstream.tech` does NOT expose a sitemap or JSON API
  (root, `/sitemap.xml`, `/jobs.json`, `/api/jobs` all 404 / 500).
  Index discovery has to come from the parent careers page.

Today's 3 roles are all non-engineering (Open Call, two Account
Executive postings); 0 will match the v1 keyword filter. Same
honest-0-yield posture as floodbase / gohunt / regrid / kalkomey.

`wiki:extractor-shape` is the canonical inheritance pattern:

- canonical row contains no Python list values (FIND-001 of
  Ashby/Mapbox critique)
- slug case preserved in `ats_slug` column; R2 path follows dlt's
  snake_case normalization
- defensive listed/published checks: presence-as-signal (no flag
  exists for Polymer responses) — same posture as sitemap +
  Rippling
- duplicate-by-title is upstream behavior; canonical view stays
  role_id-keyed

Constitutional allow-list updated 2026-05-02 to admit Polymer.

# Why Now

PM2 (Rippling) just closed (Wave 3 cron run 25253284648 green).
Polymer is the only research-loopback-prone wave in this
initiative — if `jobs.<company>.<tld>` or the parent careers page
turns out to be JS-rendered for a future Polymer-hosted company,
the extractor needs a different shape. Shipping it now while the
Upstream Tech surface is plain HTML proves the inheritance shape;
PM4 (page-monitor adds) inherits cleanly afterward.

# Scope

- Add `src/dream_job_radar/extractors/polymer.py`:
  - `class SiteSpec(NamedTuple)` with fields:
    `slug` (str), `index_url` (str — parent careers page URL),
    `id_pattern` (str — regex with one capture group that
    extracts role IDs from the index HTML),
    `role_url_template` (str — f-string with `{id}` placeholder).
  - `DEFAULT_SITES = (SiteSpec(slug="upstream-tech",
    index_url="https://www.upstream.tech/careers",
    id_pattern=r"jobs\.upstream\.tech/(\d+)",
    role_url_template="https://jobs.upstream.tech/{id}"),)`.
  - `_title_matches(title)` — same lowercase substring helper.
  - `_fetch_index_ids(spec)` — GET `spec.index_url` with polite
    UA; parse via `re.findall(spec.id_pattern, html)`; dedupe
    while preserving order; return list of IDs.
  - `_extract_jobposting_jsonld(html)` — find every
    `<script type="application/ld+json">` block, JSON-parse each,
    return the first dict whose `@type == "JobPosting"`. Return
    `None` if none found.
  - `_parse_date_posted(s)` — accept `'YYYY-MM-DD HH:MM:SS UTC'`
    (Polymer's format) and convert to ISO. If it already looks
    like ISO (contains `T` or matches `\d{4}-\d{2}-\d{2}T`),
    return unchanged. On parse failure, return `""`.
  - `_extract_location(jobposting)` — flatten the nested Place /
    PostalAddress structure to a single string. Prefer
    `addressLocality + ", " + addressRegion + ", " + addressCountry`,
    falling back to `addressCountry` alone. Return `None` if
    absent.
  - `_normalize(jobposting, role_id, spec, fetched_at)` — produce
    canonical row:
    - `company`: spec.slug
    - `source_kind`: `"polymer"`
    - `ats_slug`: spec.slug
    - `role_id`: the ID string from index discovery (stable —
      Polymer's numeric ID is server-side and persists across
      title rewrites)
    - `title`: `jobposting.get("title", "")`
    - `url`: `jobposting.get("url", "")` (canonical from
      JSON-LD; falls back to constructed URL if absent)
    - `location`: from `_extract_location`
    - `posted_at`: `_parse_date_posted(jobposting.get("datePosted",""))`
    - `fetched_at`: ISO timestamp at run start
    - `raw_json`: `json.dumps(jobposting, sort_keys=True,
      default=str)`
  - `site_resource(spec)` —
    `@dlt.resource(name=spec.slug, write_disposition="append")`
    factory. Inside: fetch index IDs; for each, fetch role page,
    extract JobPosting JSON-LD, apply title-keyword filter, log
    MATCH/skip per role, yield matches via `_normalize`. Polite
    `time.sleep(0.5)` between role-page fetches (mirror sitemap
    convention).
  - `site_resources(specs=DEFAULT_SITES)` — list of resources.

- Add `src/dream_job_radar/pipelines/polymer.py` mirroring
  `pipelines/rippling.py`:
  - `PIPELINE_NAME = "dream_job_radar"`
  - `SOURCE_KIND = "polymer"`
  - `DATASET_NAME = SOURCE_KIND`
  - Use `r2_destination()` from `pipelines._r2`
  - `run(specs=DEFAULT_SITES)` builds dlt pipeline (progress log)
    and runs `site_resources(specs)` with
    `loader_file_format="parquet"`
  - `main()` calls `load_dotenv()` then `run()`
  - Entry point: `python -m dream_job_radar.pipelines.polymer`

- Update `src/dream_job_radar/pipelines/radar.py` meta-runner to
  chain polymer after rippling.

- Update `.github/workflows/refresh.yml` to add a Polymer
  per-source step (continue-on-error: true) between Rippling and
  Apply Views.

- Update `README.md` source-coverage table + per-source
  entry-point + chain comment.

# Non-goals

- No headless browser. Both surfaces (parent + role pages) are
  plain HTML.
- No anti-bot evasion. If a future Polymer-hosted site requires
  cookies, defer that company.
- No detail-fetch dance — JSON-LD on the role page is the data
  source.
- No view DDL change. The view's `TRY_CAST(posted_at AS
  TIMESTAMP)` already handles the reformatted ISO string.
- No revision of the title-keyword filter.

# Acceptance Criteria

1. `uv run python -m dream_job_radar.pipelines.polymer` runs
   end-to-end without error against Upstream Tech. Today:
   3 roles fetched, 0 expected matches, dlt 0-yield clean.
2. `uv run python -m dream_job_radar.pipelines.radar` runs
   end-to-end exercising greenhouse + ashby + sitemap + page +
   rippling + polymer. Existing view counts unchanged or higher
   (no regression).
3. `boto3 list_objects_v2 Prefix=raw/polymer/` returns at least
   the dlt metadata (or, if any role matched, the `<slug>/`
   table dir).
4. MotherDuck `count(*) FROM current_open_roles WHERE
   source_kind='polymer'` returns the truthful count
   (today: 0).
5. If positive count, all sampled titles satisfy the keyword
   filter; `posted_at` parses to a TIMESTAMP correctly via the
   view's TRY_CAST.
6. `.github/workflows/refresh.yml` validates locally
   (hand-walked) and the new step matches the existing
   per-source step shape.
7. README documents `pipelines.polymer` and adds a row to the
   source-coverage table.

# Coverage

Ticket-local. `wiki:extractor-shape` is the inheritable design.

# Claim Matrix

None.

# Execution Notes

- Index discovery via regex against the parent careers page is
  v1's pragmatic shape. If a future Polymer site uses
  JS-rendering for the index, escalate (loopback to research /
  spec) — do NOT add headless-browser scraping silently.
- `datePosted` format `'YYYY-MM-DD HH:MM:SS UTC'` is non-ISO;
  reformat to ISO inside the extractor so the view's TRY_CAST
  handles it. Empty / unparseable → `""` (NULL after view
  TRY_CAST). Same downstream behavior as page-monitor's
  hard-coded empty string.
- Some `jobLocation` values may be lists (multi-location roles).
  Defensive: handle both dict and list-of-dicts; flatten to the
  first usable address. Do NOT yield the list directly (would
  trigger dlt's nested-table behavior, FIND-001).
- Polite-fetch sleep `time.sleep(0.5)` between role-page GETs
  (skip before first). Today's 3 fetches → ~1s sleep total;
  trivial.
- Polymer slug case: `upstream-tech` is the natural slug derived
  from the company-handle subdomain. Hyphen survives dlt's
  snake_case normalization (per Ashby's `pano-ai` evidence in
  Wave 1). R2 path will be `raw/polymer/upstream-tech/`.

# Blockers

None.

# Next Move / Next Route

Ralph implementation packet. Bounded scope; new extractor +
pipeline + meta-runner + workflow + README.

# Ralph Readiness

Bounded iteration: per-source extractor with per-site config + per-
source pipeline + meta-runner chain + workflow step + README.

Write boundary:
- `src/dream_job_radar/extractors/polymer.py`
- `src/dream_job_radar/extractors/__init__.py`
- `src/dream_job_radar/pipelines/polymer.py`
- `src/dream_job_radar/pipelines/radar.py`
- `.github/workflows/refresh.yml`
- `README.md`

Verification posture: `observation-first`.

# Evidence

Expected on completion:

- terminal output of standalone `pipelines.polymer` and
  all-sources radar runs
- the 3 Upstream Tech role IDs (and titles) the index discovery
  identified
- `boto3 list_objects_v2 Prefix=raw/polymer/`
- MotherDuck per-`(source_kind, ats_slug)` counts
- workflow YAML diff

Captured 2026-05-02T14:00Z (Ralph iteration 1):

AC1 — `pipelines.polymer` runs end-to-end:
```
[polymer:upstream-tech] index discovered 3 role(s)
[polymer:upstream-tech] skip  'Account Executive, North America - Lens'
[polymer:upstream-tech] skip  'Account Executive, North America - HydroForecast'
[polymer:upstream-tech] skip  'Open Call for Applications'
Pipeline dream_job_radar load step completed in 4.68 seconds
1 load package(s) were loaded to destination filesystem and into dataset polymer
```

AC2 — `pipelines.radar` chains all 6 source kinds end-to-end. No
regression: existing 7 slugs unchanged (ashby/Mapbox=61,
ashby/pano-ai=4, greenhouse/blastpoint=2, greenhouse/onxmaps=8,
greenhouse/overstory=7, greenhouse/planetlabs=37, page/felt=1).

AC3 — `raw/polymer/` after run: dlt metadata only (no
`upstream-tech/` table dir — 0-yield, same posture as floodbase /
gohunt / regrid / kalkomey).

AC4 — `count(*) WHERE source_kind='polymer'` = 0. Today's 3
roles (Open Call + 2 Account Executive postings) all skipped by
the v1 keyword filter.

AC5 — N/A today (no matched titles to sample).

AC6 — workflow YAML extended: new "Polymer pipeline" step with
`id: polymer`, `continue-on-error: true`, between Rippling and
Apply Views. Inherits job-level env. Hand-validated.

AC7 — README updated:
- Source-coverage row:
  `polymer | upstream-tech | upstream.tech/careers (index) → jobs.upstream.tech/{id} (per-role JSON-LD)`
- Per-source entry-point block.
- All-sources chain comment updated to include polymer.

Index URL list captured: 3 role IDs (23408, 39157, 39581) extracted
from `https://www.upstream.tech/careers` via regex
`r"jobs\.upstream\.tech/(\d+)"`. Each role page returned a clean
JSON-LD JobPosting with `title`, `datePosted` (non-ISO format
`'YYYY-MM-DD HH:MM:SS UTC'`, reformatted to ISO inside the
extractor), `url`, `jobLocation` (nested
Place > address > PostalAddress).

# Critique Disposition

Risk class: medium

Critique policy: recommended

Policy rationale: Polymer is the second new source kind in this
initiative and the only one with a research-loopback risk
(JS-rendering on either index or role pages). Inherits the same
critique surface as Rippling: code-quality (per-site spec model,
JSON-LD parsing, date reformatting) + schema-fitness (role_id
stability across upstream renames, posted_at timestamp parsing,
location flattening from nested address).

Required critique profiles:
- code-quality (extractor + pipeline shape vs Rippling reference)
- schema-fitness (role_id stability, posted_at parsing,
  location flattening)

Findings: see `critique:polymer-upstream-iter1` (7 findings: 3
medium, 4 low; none `changes_required`). Verdict:
`pass_with_findings`.

Disposition status: resolved-with-followup. FIND-001/002/003/007
deferred to PM5 retrospective for wiki updates. FIND-004
resolved by inspection. FIND-005/006 deferred (not v1
priorities).

Deferral / not-required rationale: N/A

# Wiki Disposition

Likely a meaningful update to `wiki:extractor-shape` during PM5
retro: Polymer adds a fifth API/index-driven source-kind row to
the role_id strategies table, a new posted_at parsing convention
(reformat from non-ISO upstream), and a new index-discovery
pattern (parent-page enumeration vs sitemap.xml vs job-list-API).

# Acceptance Decision

Accepted by: pending
Accepted at: pending
Basis: pending — AC1–AC7 satisfied with observation-first
evidence plus required critique findings either resolved or
accepted.
Residual risks: pending

# Dependencies

Hard prerequisites:

- v1 `initiative:close-the-loop` closed (done 2026-05-02).
- `research:ats-discovery-v2` (done 2026-05-02).
- `constitution:main` admits Polymer (done 2026-05-02).
- PM1 + PM2 of `plan:expand-radar` closed (done 2026-05-02).

Soft references:

- `wiki:extractor-shape` — canonical pattern.
- `ticket:xwfvoj4o` (closed) — sitemap-monitor precedent for
  no-API JSON-LD parsing.
- `ticket:vr6iel5o` (closed) — Rippling reference (per-source
  pipeline + workflow shape).
- `ticket:k0ftbmsi` (closed) — page-monitor precedent for per-
  site config strategy.

# Journal

- 2026-05-02 — ticket created from `plan:expand-radar` Wave 3
  after PM2 closed. Risk classified `medium`; critique
  `recommended` with two named profiles. Probed Upstream Tech
  surface: 3 role IDs in parent careers page, JSON-LD JobPosting
  on each role page, no JSON-API endpoint, datePosted in
  non-ISO format. Next route: Ralph implementation packet.
- 2026-05-02 — Ralph packet compiled at
  `.loom/packets/ralph/polymer-upstream-20260502T135222Z.md`
  (style: reference-first, posture: observation-first, source SHA
  `2220f4b`). Awaiting child execution.
- 2026-05-02 — Ralph iteration 1 returned `continue`. Index
  discovered 3 role IDs from upstream.tech/careers; per-role
  JSON-LD parsed cleanly; 0 match keyword filter today. dlt
  0-yield clean. All-sources radar chained end-to-end without
  regression. Status → `review_required`. Critique pass next.
- 2026-05-02 — Critique landed at
  `.loom/critique/polymer-upstream-iter1.md`. Verdict
  `pass_with_findings`; 7 findings (3 medium, 4 low), none
  `changes_required`. Acceptance recommendation: "active
  follow-up required" — close after manual workflow dispatch
  succeeds on new shape. PM5 retro now load-bearing for
  Rippling + Polymer wiki updates.
