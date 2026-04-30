---
id: packet:ralph-sitemap-gohunt-20260430T022113Z
kind: packet
packet_kind: ralph
status: consumed
target: ticket:xwfvoj4o
mode: execution
change_class: code-behavior
style: reference-first
verification_posture: observation-first
iteration: 1
created_at: 2026-04-30T02:21:13Z
updated_at: 2026-04-30T02:35:00Z
scope:
  kind: repository
  repositories:
    - repo:root
child_write_scope:
  records: []
  paths:
    - src/dream_job_radar/extractors/sitemap.py
    - src/dream_job_radar/extractors/__init__.py
    - src/dream_job_radar/pipelines/sitemap.py
    - src/dream_job_radar/pipelines/radar.py
    - README.md
parent_merge_scope:
  records:
    - ticket:xwfvoj4o
    - plan:v1-radar
  paths: []
source_fingerprint:
  git_commit: 0bf7c44cbf50e05071732c34952b633afab13b30
  integration_remote: origin
  integration_ref: main
  integration_commit: 0bf7c44cbf50e05071732c34952b633afab13b30
  git_status_summary: dirty
  compiled_from:
    - ticket:xwfvoj4o
    - wiki:extractor-shape
    - plan:v1-radar
    - research:ats-discovery
    - ticket:gjkpkpum
    - ticket:oy172mt9
    - constitution:main
    - decision:0001-storage-backend-r2
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
    - initiative:close-the-loop
  research:
    - research:ats-discovery
  spec: []
  plan:
    - plan:v1-radar
  ticket:
    - ticket:xwfvoj4o
  wiki:
    - wiki:extractor-shape
  predecessor:
    - ticket:gjkpkpum
    - ticket:oy172mt9
links:
  decision:
    - decision:0001-storage-backend-r2
---

# Mission

Ship Wave 2 #4: build the sitemap-monitor extractor + pipeline for
GoHunt. Land Parquet at `r2://<bucket>/raw/sitemap/gohunt/` (or
nothing under `gohunt/` if zero roles match — both honest). The
existing `current_open_roles` view glob already covers the new
source kind without DDL change.

A 0-row outcome is acceptable. The probe found 4 sitemap URLs, none
of which match the v1 keyword filter today. The pipeline must still
run cleanly and produce truthful evidence.

# Bound Context

- `wiki:extractor-shape` (load-bearing) — read first. Inherited
  contract for canonical row shape, slug-case policy, defensive
  listed/published checks, no-list-fields rule.
- `ticket:xwfvoj4o` — primary contract; AC1–AC5 + execution notes.
- `ticket:gjkpkpum` (closed) — Wave 1 reference.
  `extractors/greenhouse.py` and `pipelines/ashby.py` are the
  patterns to mirror.
- `ticket:oy172mt9` (closed) — Wave 2 #2 reference.
  `pipelines/_r2.py` shared destination factory; meta-runner shape
  in `pipelines/radar.py` to extend.
- `research:ats-discovery` — null-result evidence on GoHunt's
  ATS-less surface; sitemap monitor as the viable path.
- `decision:0001-storage-backend-r2` — Cloudflare R2 only.

API verification at packet compile time (2026-04-30):

- `GET https://www.gohunt.com/sitemap.xml` → HTTP 200, ~1.2MB,
  8718 `<loc>` entries.
- 4 URLs match the heuristic
  `'job-opportunity' in url.lower()`:
  - `https://www.gohunt.com/browse/news-and-updates/multimedia-content-producer-job-opportunity-with-gohunt`
  - `https://www.gohunt.com/browse/news-and-updates/showroom-associate-part-time-job-opportunity-with-gohunt`
  - `https://www.gohunt.com/browse/news-and-updates/showroom-lead-job-opportunity-with-gohunt`
  - `https://www.gohunt.com/browse/news-and-updates/archery-shop-lead-job-opportunity-with-gohunt`
- Per role page: HTML carries one
  `<script type="application/ld+json">` block with `@type:
  "Article"` and these keys:
  - `headline` (string, role title)
  - `datePublished` (ISO 8601 with TZ)
  - `dateModified` (ISO 8601 with TZ)
  - `url` (canonical)
  - plus `description`, `image`, `author`, `publisher`,
    `mainEntityOfPage`
- Today's 4 headlines: "Content Producer ...", "Showroom Associate ...",
  "Showroom Lead ...", "Archery Shop Lead ...". None contain `data`,
  `engineer`, `gis`, or `geospatial` substrings (case-insensitive).
  Expected match count: 0.

# Source Snapshot

Read these directly:

- `.loom/wiki/extractor-shape.md` — canonical pattern.
- `.loom/tickets/20260430-xwfvoj4o-sitemap-gohunt.md` — primary
  contract.
- `src/dream_job_radar/extractors/ashby.py` — reference resource
  factory (Wave 2 pattern: per-source extractor module).
- `src/dream_job_radar/extractors/greenhouse.py` — older reference
  for the resource factory + filter shape.
- `src/dream_job_radar/pipelines/ashby.py` — reference per-source
  pipeline (uses `pipelines._r2.r2_destination`).
- `src/dream_job_radar/pipelines/radar.py` — meta-runner to extend.
- `src/dream_job_radar/pipelines/_r2.py` — shared R2 destination
  factory; do not duplicate.
- `README.md` — extend the source-coverage table and per-source
  entry-point list.

`pyproject.toml` already has `requests`, `dlt[filesystem]`, etc.
The Python stdlib (`xml.etree.ElementTree`, `json`) covers
sitemap + JSON-LD parsing. Do not add new deps.

# Change Class

`code-behavior`. Evidence is observation-first: pipeline must run
end-to-end, R2 must reflect the run (even if only as
metadata-with-no-data-rows), view counts must reflect honest
results.

# Verification Targets

None — no spec exists. Acceptance is ticket-local against
`ticket:xwfvoj4o` AC1–AC5.

# Task For This Iteration

Build, in one bounded slice:

1. **`src/dream_job_radar/extractors/sitemap.py`** — new resource
   factory for sitemap-driven sources:
   - `USER_AGENT = "dream-job-radar/0.1"`.
   - `TITLE_KEYWORDS = ("data", "engineer", "gis", "geospatial")`.
   - A site spec: prefer a small `dataclass` or `NamedTuple`:
     ```python
     class SiteSpec(NamedTuple):
         slug: str          # used as ats_slug AND dlt resource name
         sitemap_url: str
         url_substring: str # case-insensitive substring filter on URL
     ```
   - `DEFAULT_SITES = (
       SiteSpec(slug="gohunt",
                sitemap_url="https://www.gohunt.com/sitemap.xml",
                url_substring="job-opportunity"),
     )`
   - `_title_matches(title)` — same lowercase substring helper.
   - `_fetch_sitemap_urls(sitemap_url, url_substring)` — GET the
     sitemap, parse `<loc>` text using `xml.etree.ElementTree`
     (strip the XML namespace before reading), case-insensitive
     substring filter on the URL string. If the document is a
     sitemapindex (root tag `sitemapindex`), raise / escalate; do
     not silently traverse sub-sitemaps in v1.
   - `_extract_jsonld_article(html)` — find every
     `<script type="application/ld+json">` block, JSON-parse each,
     return the first dict whose `@type` equals `"Article"` (also
     accept `@type` lists containing `"Article"`); return `None` if
     no Article block found.
   - `_fetch_role_page(url)` — GET the URL; pass `html.text` into
     `_extract_jsonld_article`; return the article dict (or `None`).
   - `_normalize(article, slug, fetched_at)` — produce the
     canonical row:
     - `company`: slug verbatim (`gohunt`)
     - `source_kind`: `"sitemap"`
     - `ats_slug`: slug verbatim
     - `role_id`: last path segment of `article["url"]` (i.e.
       `urlsplit(article["url"]).path.rstrip("/").split("/")[-1]`).
       If the slug has no path segment somehow, fall back to a
       SHA-1 of the URL — but in practice the GoHunt URLs always
       have one.
     - `title`: `article.get("headline", "")`
     - `url`: `article.get("url", "")` (the article's own URL —
       use it instead of the sitemap URL in case the article carries
       a canonical/normalized form)
     - `location`: `None` (sitemap-derived sources have no
       structured location; do NOT invent one)
     - `posted_at`: `article.get("datePublished") or
       article.get("dateModified") or ""`
     - `fetched_at`: ISO timestamp at run start
     - `raw_json`: `json.dumps(article, sort_keys=True,
       default=str)` — `default=str` is defensive against any
       datetime object that sneaks in.
   - `site_resource(spec: SiteSpec)` — returns a
     `@dlt.resource(name=spec.slug, write_disposition="append")`
     factory. Inside:
     - `time.sleep` between role-page fetches: use
       `time.sleep(0.5)` to be polite (sitemap-monitor traffic
       hits the host harder than ATS APIs do).
     - Fetch sitemap URLs, then for each URL:
       - if it does not look like a job URL, skip
       - GET the page; if `_extract_jsonld_article` returns `None`,
         log + skip (do not yield)
       - apply `_title_matches` against `headline` (the keyword
         filter)
       - if matched, yield `_normalize(...)`
   - `site_resources(sites: tuple[SiteSpec, ...] = DEFAULT_SITES)`
     returns one resource per spec.

2. **`src/dream_job_radar/pipelines/sitemap.py`** — mirror
   `pipelines/ashby.py`:
   - `PIPELINE_NAME = "dream_job_radar"`.
   - `SOURCE_KIND = "sitemap"`.
   - `DATASET_NAME = SOURCE_KIND`.
   - Use `r2_destination()` from `pipelines._r2`.
   - `run(sites=DEFAULT_SITES)` builds the dlt pipeline and runs
     `site_resources(sites)` with `loader_file_format="parquet"`.
   - `main()` calls `load_dotenv()` then `run()`.
   - Entry point: `python -m dream_job_radar.pipelines.sitemap`.
   - Acceptable for the dlt run to write zero data rows. The
     pipeline must not raise just because the resource yielded
     nothing.

3. **`src/dream_job_radar/pipelines/radar.py`** — extend the
   meta-runner so `python -m dream_job_radar.pipelines.radar` runs
   greenhouse → ashby → sitemap. Print clear section markers
   between runs.

4. **`README.md`** — extend the source-coverage table and the
   per-source entry-point list:
   - Add row: `sitemap` / `gohunt` / `https://www.gohunt.com/sitemap.xml`
   - Add command: `uv run python -m dream_job_radar.pipelines.sitemap`

Run both `pipelines.sitemap` and `pipelines.radar` once locally to
produce truthful evidence (which may be a 0-row outcome for
sitemap).

# Verification Posture

`observation-first`.

Before-state evidence (capture once):

- `boto3 list_objects_v2 Prefix=raw/sitemap/` → empty.
- View counts per `(source_kind, ats_slug)`:
  greenhouse/onxmaps=8, greenhouse/planetlabs=36, ashby/Mapbox=59,
  no sitemap rows.

After-state evidence (capture once):

- The 4 GoHunt sitemap URLs the extractor identified (echo them
  for transparency).
- For each URL: whether the JSON-LD Article was found, and what
  `headline` it returned.
- The keyword-filter outcome per URL (matched / skipped).
- dlt run summaries for both `pipelines.sitemap` and
  `pipelines.radar`.
- `boto3 list_objects_v2 Prefix=raw/sitemap/` after the run.
- View counts per `(source_kind, ats_slug)` — onx + planetlabs +
  Mapbox unchanged; sitemap row count is whatever it honestly is.
- If sitemap row count > 0, sample matched titles to confirm the
  filter holds.

# Stop Conditions

Stop and report `blocked` or `escalate` (instead of widening scope)
if:

- The GoHunt sitemap returns a non-200 status, an unexpected XML
  shape, or contains a `<sitemapindex>` root (do not silently
  recurse).
- Any role page returns a non-200 status (timeouts and 429s are real
  signals — do not retry-with-backoff in v1; flag the failure mode).
- A role page lacks any JSON-LD `Article` block (today's 4 pages
  all have one — flag if that changes).
- The dlt pipeline fails because it cannot configure with zero
  yielded records — if so, this is a real Wave 3 implication and
  should be raised, not patched around.
- A real GoHunt role would slip through the title-keyword filter
  despite matching it (or vice versa) — flag rather than silently
  broadening.
- Any file outside `child_write_scope.paths` would need to change.
- `motherduck/views.sql` would need to change (it should not — the
  view glob is invariant).

For `observation-first`: do not declare success without both
before-state and after-state evidence. A 0-match outcome is
acceptable but must be reported truthfully (which 4 URLs were seen,
each headline, why each was filtered out).

Do not run `git fetch`, `git push`, `git checkout`, `git config`,
`git remote`, force operations, or any command that would mutate
shared Git metadata. The parent owns Git operations.

Do not write any Loom records. The parent owns ticket, plan,
packet, critique, and wiki mutations.

Do not add new dependencies. `xml.etree.ElementTree` and `json`
cover the parsing needs.

# Output Contract

Return:

- **outcome**: one of `continue`, `stop`, `blocked`, `escalate`.
- **files changed**: paths inside `child_write_scope.paths` only.
- **records changed**: should be `[]`.
- **evidence gathered**:
  - before-state observations
  - after-state observations including the URL-by-URL breakdown
  - exact commands run, with commands echoed before output
- **self-review findings or concerns**:
  - role_id derivation choice + rationale
  - title sanitization decision (kept verbatim vs trimmed)
  - any sleep / pagination / sitemap-index assumptions worth
    raising in critique
  - 0-match outcome handling vs how dlt reports the empty
    resource
- **blockers or risks**: real ones; if none, write `None`.
- **ticket recommendation**: one of:
  - "advance ticket:xwfvoj4o to `review_required` for critique
    (recommended profiles: code-quality, schema-fitness)"
  - "ticket:xwfvoj4o requires another iteration; reason: ..."
  - "ticket:xwfvoj4o should escalate to plan revision; reason: ..."

# Working Notes

- Reuse the existing `r2_destination()` factory exactly. Do not
  duplicate the destination config.
- The view glob `raw/*/*/*.parquet` matches
  `raw/sitemap/gohunt/<file>.parquet` if any file lands there.
  dlt system tables under `raw/sitemap/` will be excluded by the
  existing `WHERE filename NOT LIKE '%/_dlt_%'` filter.
- The view's `WHERE source_kind IS NOT NULL AND ats_slug IS NOT
  NULL AND role_id IS NOT NULL` (added in Wave 2 #2 retro) defends
  against any non-canonical row leaking through.
- Wave 2 #2 lesson: do NOT yield list values in the canonical row.
  Sitemap data shouldn't have any natural list fields, but if you
  decide to capture (say) categories, keep them in `raw_json` only.
- Polite-fetch sleep: `time.sleep(0.5)` between role-page GETs.
  Single-pass, single-process, no async.
- Use `urllib.parse.urlsplit` for slug extraction.
- For sitemap parsing with `xml.etree.ElementTree`, the standard
  trick is to either strip the namespace or query with the explicit
  namespace prefix. Either is fine; pick the readable one.

# Child Output

**outcome**: `continue`

**files changed** (all inside `child_write_scope.paths`):

- `src/dream_job_radar/extractors/sitemap.py` (new)
- `src/dream_job_radar/pipelines/sitemap.py` (new)
- `src/dream_job_radar/pipelines/radar.py` (extended — chains sitemap)
- `README.md` (extended)

**records changed**: `[]`.

**evidence gathered**

Before-state:

- `list_objects_v2 raw/sitemap/` → `KeyCount=0`
- View counts: `ashby/Mapbox=59`, `greenhouse/onxmaps=8`,
  `greenhouse/planetlabs=36`, no sitemap rows.

After-state:

URL-by-URL extractor output:

```
[sitemap:gohunt] skip  'Content Producer - Job Opportunity with GOHUNT'
[sitemap:gohunt] skip  'Showroom Associate (Part Time) - Job Opportunity with GOHUNT'
[sitemap:gohunt] skip  'Showroom Lead - Job Opportunity with GOHUNT'
[sitemap:gohunt] skip  'Archery Shop Lead - Job Opportunity with GOHUNT'
```

All 4 sitemap URLs fetched; JSON-LD `Article` block present on every
page; zero keyword-filter matches. Pipeline did not raise on the
0-row outcome.

R2 after run: `raw/sitemap/{_dlt_loads,_dlt_pipeline_state,_dlt_version,init}`.
No `raw/sitemap/gohunt/` table directory (resource yielded 0
records). Per AC3, honest 0-row evidence.

All-sources `pipelines.radar` run completed end-to-end:
- Greenhouse (1.76s, 8 + 36 records)
- Ashby (2.30s, 59 records)
- Sitemap (3.08s, 0 records)

Post-run view counts unchanged from pre-run.

**self-review findings or concerns**

1. `role_id` derivation: last path segment of canonical URL.
   Stable until GoHunt renames a slug; renamed roles would create a
   new logical role.
2. `title` kept verbatim including " - Job Opportunity with GOHUNT"
   suffix. Per wiki canonical-row-mirrors-source rule.
3. `_fetch_sitemap_urls` raises on `<sitemapindex>` root rather
   than recursing.
4. JSON-LD extraction via regex (no BeautifulSoup dep). Fragile in
   theory; opaque text in practice.
5. Polite-fetch `time.sleep(0.5)` between fetches (skips first).
6. No `isListed`-equivalent for sitemap sources; sitemap presence
   IS the publishedness signal. Honest gap.
7. dlt 0-match handling clean: pipeline wrote metadata only, no
   data parquet, no raise.

**blockers or risks**: None.

**ticket recommendation**: advance `ticket:xwfvoj4o` to
`review_required` for critique (recommended profiles: code-quality,
schema-fitness).

# Parent Merge Notes

Parent reconciled 2026-04-30T02:35Z.

- 0-match outcome accepted as truthful evidence per AC3/AC4.
  Constitution treats GoHunt's hand-maintained CMS jobs as a Wave
  2 entry; the pipeline is now in place to catch any future
  data/engineer/GIS/geospatial role the moment GoHunt posts one.
- Refactor scope honored exactly: regex-based JSON-LD parsing
  avoided a new dep; sitemap-index escalation chosen over silent
  recursion; sleep policy is conservative.
- Ticket `xwfvoj4o` advanced to `review_required`. Critique pass
  next: code-quality + schema-fitness profiles per ticket Critique
  Disposition.
- Packet status `compiled` → `consumed`. No further iteration of
  this packet expected.
