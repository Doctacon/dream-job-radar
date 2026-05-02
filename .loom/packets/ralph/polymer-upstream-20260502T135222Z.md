---
id: packet:ralph-polymer-upstream-20260502T135222Z
kind: packet
packet_kind: ralph
status: consumed
target: ticket:7n0yj21k
mode: execution
change_class: code-behavior
style: reference-first
verification_posture: observation-first
iteration: 1
created_at: 2026-05-02T13:52:22Z
updated_at: 2026-05-02T14:00:00Z
scope:
  kind: repository
  repositories:
    - repo:root
child_write_scope:
  records: []
  paths:
    - src/dream_job_radar/extractors/polymer.py
    - src/dream_job_radar/extractors/__init__.py
    - src/dream_job_radar/pipelines/polymer.py
    - src/dream_job_radar/pipelines/radar.py
    - .github/workflows/refresh.yml
    - README.md
parent_merge_scope:
  records:
    - ticket:7n0yj21k
    - plan:expand-radar
  paths: []
source_fingerprint:
  git_commit: 2220f4b8f5a3e3265ad8443c5b19159d1a62756c
  integration_remote: origin
  integration_ref: main
  integration_commit: 2220f4b8f5a3e3265ad8443c5b19159d1a62756c
  git_status_summary: clean
  compiled_from:
    - ticket:7n0yj21k
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
    - ticket:7n0yj21k
  wiki:
    - wiki:extractor-shape
  predecessor:
    - ticket:xwfvoj4o
    - ticket:vr6iel5o
links: {}
---

# Mission

Ship Wave 3 / PM3 of `plan:expand-radar`: build the Polymer
extractor + pipeline for Upstream Tech. Land Parquet at
`r2://<bucket>/raw/polymer/upstream-tech/`. Honest 0-yield is
acceptable today (none of 3 upstream roles match v1 keyword
filter).

# Bound Context

- `wiki:extractor-shape` (load-bearing) — read first. All Wave 2
  inheritance lessons apply.
- `ticket:7n0yj21k` — primary contract; AC1–AC7 + execution
  notes.
- `ticket:vr6iel5o` (closed) — Rippling reference (per-source
  pipeline shape, workflow extension).
- `ticket:xwfvoj4o` (closed) — sitemap-monitor precedent for
  JSON-LD parsing + polite-sleep convention.
- `ticket:k0ftbmsi` (closed) — page-monitor precedent for per-
  site SiteSpec model.
- `research:ats-discovery-v2` — confirms Upstream Tech surface
  shape.

API verification at packet compile time (per
`research:ats-discovery-v2` + 2026-05-02 deeper probe):

Index page:
`GET https://www.upstream.tech/careers` → HTTP 200, ~84KB HTML.
Contains 3 references to `jobs.upstream.tech/<id>`:

- `jobs.upstream.tech/23408`  — title "Open Call for Applications"
- `jobs.upstream.tech/39157`  — title "Account Executive, North America - HydroForecast"
- `jobs.upstream.tech/39581`  — title "Account Executive, North America - Lens"

Per-role page (sample for 23408):
`GET https://jobs.upstream.tech/23408` → HTTP 200, JSON-LD
`<script type="application/ld+json">` block with `@type =
"JobPosting"`. Fields:

- `title` (string)
- `datePosted` (string, format `'YYYY-MM-DD HH:MM:SS UTC'` — NOT
  ISO; needs reformatting in the extractor before storage)
- `url` (string, canonical role URL)
- `jobLocation` (dict: `{"@type":"Place","address":{
  "@type":"PostalAddress","addressCountry":"US"}}`; may include
  `addressLocality`, `addressRegion` for other roles; may be a
  list for multi-location postings)
- `employmentType`, `hiringOrganization`, `description`,
  `applicantLocationRequirements`, `directApply`, `identifier`
  (informational; NOT exposed in canonical row)

Today's 3 titles: 0 match v1 keyword filter
(`data | engineer | gis | geospatial`). Honest 0-yield expected.

# Source Snapshot

Read these directly:

- `.loom/tickets/20260502-7n0yj21k-polymer-upstream.md` — primary
  contract.
- `.loom/wiki/extractor-shape.md` — canonical pattern, especially
  sitemap-monitor section (closest precedent for JSON-LD
  parsing).
- `src/dream_job_radar/extractors/sitemap.py` — JSON-LD parsing +
  polite-sleep convention.
- `src/dream_job_radar/extractors/page.py` — per-site SiteSpec
  pattern (regex parsers per site).
- `src/dream_job_radar/extractors/rippling.py` — fresh
  per-source extractor reference (Wave 2 PM2).
- `src/dream_job_radar/pipelines/rippling.py` — fresh pipeline
  reference.
- `src/dream_job_radar/pipelines/_r2.py` — shared destination
  factory; do not duplicate.
- `src/dream_job_radar/pipelines/radar.py` — meta-runner to
  extend.
- `.github/workflows/refresh.yml` — workflow to extend.
- `README.md` — extend source-coverage + entry-point list.

stdlib `re`, `json`, `time`, `urllib.parse`, `datetime` cover all
parsing needs. No new deps.

# Change Class

`code-behavior`. Evidence is observation-first: pipeline must run
end-to-end against live Upstream Tech surfaces; R2 reflects
truthful output (dlt-metadata-only on 0-yield); per-role
MATCH/skip log is captured.

# Verification Targets

None — no spec exists. Acceptance is ticket-local against
`ticket:7n0yj21k` AC1–AC7.

# Task For This Iteration

Build, in one bounded slice:

1. **`src/dream_job_radar/extractors/polymer.py`** — new resource
   factory:
   - `USER_AGENT = "dream-job-radar/0.1"`.
   - `TITLE_KEYWORDS = ("data", "engineer", "gis", "geospatial")`.
   - `PAGE_FETCH_DELAY_S = 0.5`.
   - `JSONLD_BLOCK_RE = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)`
     (mirrors sitemap.py).
   - `class SiteSpec(NamedTuple)`:
     `slug: str`, `index_url: str`, `id_pattern: str`,
     `role_url_template: str`.
   - `DEFAULT_SITES = (
        SiteSpec(
            slug="upstream-tech",
            index_url="https://www.upstream.tech/careers",
            id_pattern=r"jobs\.upstream\.tech/(\d+)",
            role_url_template="https://jobs.upstream.tech/{id}",
        ),
     )`.
   - `_title_matches(title)` — same lowercase substring helper.
   - `_fetch_index_ids(spec)` — GET `spec.index_url` with browser-ish UA
     fallback if needed (try polite UA first; if 403 / 503, retry
     with the standard browser UA). Apply
     `re.findall(spec.id_pattern, html)`. Dedupe while preserving
     order. Return list of id strings.
   - `_extract_jobposting_jsonld(html)` — iterate JSONLD_BLOCK_RE
     matches; JSON-parse each (skip on JSONDecodeError); return
     the first dict whose `@type` is `"JobPosting"` (also accept
     `@type` lists containing `"JobPosting"`); return `None` if
     none found.
   - `_parse_date_posted(s)` — accept Polymer's
     `'YYYY-MM-DD HH:MM:SS UTC'` and reformat to ISO via
     `datetime.strptime("%Y-%m-%d %H:%M:%S UTC")
     .replace(tzinfo=UTC).isoformat()`. If `s` already contains a
     `T` (looks ISO), return unchanged. On parse failure, return
     `""`.
   - `_extract_location(jobposting)` — flatten nested
     `Place > address > PostalAddress`. If `jobLocation` is a list,
     pick the first usable entry. Build location string from
     `addressLocality, addressRegion, addressCountry` joined by
     `, ` (skip empty parts). Return `None` if no usable
     address.
   - `_normalize(jobposting, role_id, spec, fetched_at)`:
     - `company`: spec.slug
     - `source_kind`: `"polymer"`
     - `ats_slug`: spec.slug
     - `role_id`: the discovered id string (stable upstream ID)
     - `title`: `jobposting.get("title", "")`
     - `url`: `jobposting.get("url", "")` — fall back to
       `spec.role_url_template.format(id=role_id)` if absent
     - `location`: from `_extract_location`
     - `posted_at`: from `_parse_date_posted`
     - `fetched_at`: ISO timestamp at run start
     - `raw_json`: `json.dumps(jobposting, sort_keys=True,
       default=str)`
   - `site_resource(spec)` —
     `@dlt.resource(name=spec.slug, write_disposition="append")`
     factory. Inside:
     - fetch index IDs
     - print `[polymer:<slug>] index discovered N role(s)` so the
       run log mirrors sitemap convention
     - for each id:
       - skip first sleep, otherwise `time.sleep(PAGE_FETCH_DELAY_S)`
       - fetch role page, extract JobPosting JSON-LD
       - if missing, log `[polymer:<slug>] no JobPosting at <url>;
         skip` and continue
       - apply title-keyword filter on `title`; log MATCH/skip
       - if matched, yield `_normalize(...)`
   - `site_resources(specs=DEFAULT_SITES)` — list of resources.

2. **`src/dream_job_radar/pipelines/polymer.py`** — mirror
   `pipelines/rippling.py`:
   - `PIPELINE_NAME = "dream_job_radar"`
   - `SOURCE_KIND = "polymer"`
   - `DATASET_NAME = SOURCE_KIND`
   - Use `r2_destination()` from `pipelines._r2`
   - `run(specs=DEFAULT_SITES)` builds dlt pipeline (progress log)
     and runs `site_resources(specs)` with
     `loader_file_format="parquet"`.
   - `main()` calls `load_dotenv()` then `run()`.
   - Entry point: `python -m dream_job_radar.pipelines.polymer`.

3. **`src/dream_job_radar/pipelines/radar.py`** — extend the
   meta-runner to chain greenhouse → ashby → sitemap → page →
   rippling → **polymer**. Print clear section markers.

4. **`.github/workflows/refresh.yml`** — add a new step:
   ```yaml
   - name: Polymer pipeline
     id: polymer
     continue-on-error: true
     run: uv run python -m dream_job_radar.pipelines.polymer
   ```
   Place AFTER Rippling and BEFORE Apply Views. Inherit
   job-level env.

5. **`README.md`** — extend the source-coverage table with one
   row:
   ```
   | `polymer` | `upstream-tech` | https://www.upstream.tech/careers (index) → https://jobs.upstream.tech/<id> (per-role JSON-LD) |
   ```
   Add a per-source entry-point line and update the all-sources
   chain comment to include polymer.

Run both `pipelines.polymer` and `pipelines.radar` once locally
to produce truthful evidence (today's 0-yield).

# Verification Posture

`observation-first`.

Before-state evidence:

- `boto3 list_objects_v2 Prefix=raw/polymer/` → empty
  (KeyCount=0).
- View counts per `(source_kind, ats_slug)` — record current
  values; expect no `polymer/...` row.

After-state evidence:

- The 3 Upstream Tech role IDs the index discovery extracted (or
  the actual count if it differs at run time).
- Per-role MATCH/skip log lines including the parsed `title` and
  whether JobPosting JSON-LD was found.
- dlt run summaries for both standalone and chained runs.
- `boto3 list_objects_v2 Prefix=raw/polymer/` after run.
- View counts per `(source_kind, ats_slug)` — prior counts
  unchanged or higher; polymer row count truthful.
- Workflow YAML diff.

# Stop Conditions

Stop and report `blocked` or `escalate` (not widen scope) if:

- Parent careers page or any role page returns a non-200 status.
  Anti-bot blocks should escalate (do not switch to JS rendering
  silently).
- Index discovery returns 0 IDs unexpectedly (today's 3 should
  hold; if it returns 0, the regex or page shape changed).
- A role page lacks any JSON-LD block, or the JSON-LD's
  `@type` is not `JobPosting` and not in a list containing
  `JobPosting`.
- `datePosted` arrives in a third format that
  `_parse_date_posted` does not handle. Capture the actual
  string and escalate; do not silently NULL it without flagging.
- Any file outside `child_write_scope.paths` would need to
  change.
- `motherduck/views.sql` would need to change.

For `observation-first`: do not declare success without both
before-state and after-state evidence, including per-role MATCH /
skip / no-JSONLD lines for transparency.

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
  - after-state observations including index-discovery list +
    per-role MATCH/skip lines
  - exact commands run
- **self-review findings or concerns**:
  - per-site SiteSpec generality (does the model extend
    cleanly to a hypothetical second Polymer site?)
  - role_id stability rationale (numeric upstream id)
  - posted_at parsing + ISO reformatting decision
  - location flattening for nested PostalAddress, including
    list-typed `jobLocation`
  - any concrete failure modes critique should pressure-test
- **blockers or risks**: real ones; if none, write `None`.
- **ticket recommendation**: one of:
  - "advance ticket:7n0yj21k to `review_required` for critique
    (recommended profiles: code-quality, schema-fitness)"
  - "ticket:7n0yj21k requires another iteration; reason: ..."
  - "ticket:7n0yj21k should escalate to plan revision; reason:
    ..."

# Working Notes

- Reuse `r2_destination()` exactly. Do not duplicate config.
- The view glob `raw/*/*/*.parquet` matches
  `raw/polymer/<slug>/<file>.parquet`. dlt system tables and
  NOT-NULL guards already defend.
- Wave 2 #2 lesson: do NOT yield list values in canonical row.
  `jobLocation` is sometimes a list — defensively flatten to
  the first usable entry inside `_extract_location` rather than
  passing the list through.
- ISO reformat must produce a string the view's TRY_CAST handles.
  `datetime.strptime` + `.isoformat()` produces e.g.
  `'2021-12-06T15:11:51+00:00'` which DuckDB casts cleanly.
- Single-pass, single-process, no async. 3 fetches/run today;
  trivial wall-clock impact.
- Use module-level compiled regex constants for clarity (mirror
  sitemap.py + page.py conventions).

# Child Output

**outcome**: `continue`

**files changed**:
- `src/dream_job_radar/extractors/polymer.py` (new — SiteSpec
  with id_pattern + role_url_template; UA fallback on 403/503;
  JSON-LD JobPosting extraction; non-ISO datePosted reformatting;
  defensive list-typed jobLocation flattening)
- `src/dream_job_radar/pipelines/polymer.py` (new)
- `src/dream_job_radar/pipelines/radar.py` (chain polymer)
- `.github/workflows/refresh.yml` (Polymer step)
- `README.md` (entry-point + source-coverage row)

**records changed**: `[]`.

**evidence gathered**

Before: `raw/polymer/` empty; view rows unchanged from PM2 close
(120 total).

After:
```
[polymer:upstream-tech] index discovered 3 role(s)
[polymer:upstream-tech] skip  'Account Executive, North America - Lens'
[polymer:upstream-tech] skip  'Account Executive, North America - HydroForecast'
[polymer:upstream-tech] skip  'Open Call for Applications'
Pipeline dream_job_radar load step completed in 4.68 seconds
1 load package(s) were loaded to destination filesystem and into dataset polymer
```

Chained radar: 6 source kinds chained successfully (greenhouse →
ashby → sitemap → page → rippling → polymer). No regression on
prior 7 slugs. Total view rows still 120.

**self-review findings or concerns**

1. SiteSpec parameterization (id_pattern + role_url_template)
   makes the extractor reusable for future Polymer-hosted sites.
   Tested today only against Upstream Tech.
2. role_id = upstream numeric ID; rename-stable (matches Rippling
   UUID and Greenhouse integer ID quality).
3. `_parse_date_posted` handles Polymer's non-ISO format
   explicitly + ISO passthrough; unparseable → "" → NULL via view
   TRY_CAST.
4. `_extract_location` flattens nested PostalAddress; defensive
   for list-typed `jobLocation` (multi-location postings).
5. UA fallback (polite → browser) on 403/503 mirrors what manual
   probes used. May be worth flagging if upstream tightens
   anti-bot.
6. No `isListed`-equivalent; presence-as-signal posture (sitemap
   precedent).

**blockers or risks**: None.

**ticket recommendation**: advance `ticket:7n0yj21k` to
`review_required` for critique (recommended profiles:
code-quality, schema-fitness).

# Parent Merge Notes

Parent reconciled 2026-05-02T14:00Z.

- 0-yield outcome accepted as truthful Wave 3 / PM3 delivery.
  Pattern matches floodbase, gohunt, regrid, kalkomey: extractor
  runs cleanly, dlt writes metadata only.
- SiteSpec parameterization is the right inheritance shape for a
  hypothetical second Polymer-hosted company.
- UA fallback (polite → browser on 403/503) is acceptable for v1
  but worth flagging in critique. If upstream tightens further,
  loopback to research.
- Ticket `7n0yj21k` advanced to `review_required`. Critique pass
  next.
- Packet status `compiled` → `consumed`.
