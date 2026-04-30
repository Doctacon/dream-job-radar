---
id: ticket:xwfvoj4o
kind: ticket
status: closed
change_class: code-behavior
risk_class: medium
created_at: 2026-04-30T02:13:53Z
updated_at: 2026-04-30T02:38:00Z
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
  sitemap: https://www.gohunt.com/sitemap.xml
depends_on:
  - ticket:gjkpkpum
---

# Summary

Wave 2 #4: build the sitemap-monitor extractor kind and connect it
to GoHunt. Lands Parquet at `r2://<bucket>/raw/sitemap/gohunt/`.
GoHunt has no ATS; jobs ship as CMS blog posts under
`/browse/news-and-updates/*-job-opportunity-with-gohunt`. The
sitemap exposes their canonical URLs; each role page carries a
JSON-LD `Article` block with `headline` and `datePublished`.

# Context

`wiki:extractor-shape` is the canonical reference. Read it first.
This ticket inherits the Wave 2 lessons:

- canonical row must NOT contain Python list values
- slug-case policy: data preserves source casing, R2 path follows
  dlt's snake_case normalization
- defensive listed/published checks before keyword filter
- duplicate-by-title is upstream behavior, not a defect

Per `research:ats-discovery`, GoHunt does not use an ATS. Verified
2026-04-30:

- `GET https://www.gohunt.com/sitemap.xml` → HTTP 200, ~1.2MB,
  ~8718 `<loc>` entries.
- 4 URLs match the heuristic
  `'job-opportunity' in url.lower()` (case-insensitive substring on
  the full URL):
  - `multimedia-content-producer-job-opportunity-with-gohunt`
  - `showroom-associate-part-time-job-opportunity-with-gohunt`
  - `showroom-lead-job-opportunity-with-gohunt`
  - `archery-shop-lead-job-opportunity-with-gohunt`
- Per role page: HTML carries one
  `<script type="application/ld+json">` block with `@type: Article`
  and the following keys:
  - `headline` (role title, e.g.
    "Content Producer - Job Opportunity with GOHUNT")
  - `datePublished` (ISO 8601 with TZ, e.g.
    "2026-04-08T16:18:41.994Z")
  - `dateModified` (ISO 8601 with TZ)
  - `url` (canonical role URL — already in the sitemap)
  - `description`, `image`, `author`, `publisher`, etc.

None of today's 4 GoHunt roles match the v1 keyword filter. This is
the most likely v1 outcome: GoHunt's hand-maintained CMS jobs are
mostly retail / media. The pipeline must still run cleanly and
produce truthful evidence (count = 0 is honest).

# Why Now

Wave 2 #3 (page monitor) and Wave 2 #4 (sitemap monitor) are
independent. Plan says they run in parallel since R2 prefixes are
separate. Doing #4 first is a deliberate ordering choice: GoHunt's
sitemap is well-formed XML and the role pages have clean JSON-LD,
so the extractor shape is mechanical. #3 (page monitor for Regrid +
Felt) is more brittle because it parses unstructured HTML; ship the
mechanical one first to lock the sitemap-monitor pattern before the
fragile-HTML pattern.

# Scope

- Add `src/dream_job_radar/extractors/sitemap.py`, mirroring the
  resource-factory shape:
  - `DEFAULT_SITES = ({"slug": "gohunt", "sitemap_url":
    "https://www.gohunt.com/sitemap.xml", "url_filter": lambda u:
    "job-opportunity" in u.lower()},)` (or equivalent dataclass /
    NamedTuple).
  - `_fetch_sitemap_urls(sitemap_url, url_filter)` — GET the
    sitemap, parse `<loc>` entries (regex or `xml.etree`), apply the
    filter callable.
  - `_fetch_role_page(url)` — GET the role page; extract the first
    JSON-LD block with `@type == "Article"`; return a dict with at
    least `headline`, `datePublished`, `url`.
  - `_normalize(article, slug, fetched_at)` — produce the canonical
    row. Notable mappings:
    - `company`: slug verbatim (`gohunt`)
    - `source_kind`: `"sitemap"`
    - `ats_slug`: slug verbatim
    - `role_id`: last path segment of the URL (stable, sitemap-derived)
    - `title`: `headline` (without trailing
      "Job Opportunity with GOHUNT" suffix? See execution notes)
    - `url`: `url`
    - `location`: `None` (sitemap-derived has no location)
    - `posted_at`: `datePublished` (or `dateModified` as fallback if
      missing)
    - `fetched_at`: ISO timestamp at run start
    - `raw_json`: full Article dict serialized
  - `board_resource(slug)` factory creates a dlt resource named
    after slug. Inside: iterate sitemap URLs, fetch each role page,
    parse JSON-LD, apply title-keyword filter on `headline`, yield
    matches.
  - `board_resources(sites=DEFAULT_SITES)` returns a list of
    resources. Each site spec produces one resource named after its
    slug.
- Add `src/dream_job_radar/pipelines/sitemap.py` modeled on
  `pipelines/ashby.py` with `SOURCE_KIND = "sitemap"` and
  `DATASET_NAME = "sitemap"`. Reuse `pipelines._r2.r2_destination`.
  Entry point: `python -m dream_job_radar.pipelines.sitemap`.
- Update `src/dream_job_radar/pipelines/radar.py` meta-runner to
  also call `sitemap_pipeline.run()` after Ashby.
- Update `README.md` source-coverage table and per-source entry
  points.
- No view DDL change.

# Non-goals

- No HTML page-monitor (that is Wave 2 #3, separate ticket).
- No headless browser. JSON-LD is plain HTML.
- No anti-bot evasion. If GoHunt 403s a sane User-Agent, escalate
  rather than rotating UAs or adding sleeps.
- No revision of the title-keyword filter (FIND-002 from
  Wave 1 critique still deferred).

# Acceptance Criteria

1. `uv run python -m dream_job_radar.pipelines.sitemap` runs
   end-to-end without error. The pipeline must not fail even when
   zero roles match the keyword filter.
2. `uv run python -m dream_job_radar.pipelines.radar` runs end-to-end
   and exercises greenhouse + ashby + sitemap in sequence. Existing
   onx (8) + planetlabs (36) + Mapbox (59) row counts in the view
   are unchanged or higher.
3. `boto3 list_objects_v2 Prefix=raw/sitemap/` returns at least the
   dlt-managed metadata (`_dlt_loads/`, `_dlt_pipeline_state/`,
   `_dlt_version/`, `init`). If any role matched the keyword filter,
   `raw/sitemap/gohunt/` also contains a Parquet file. If zero
   matched, the absence of a `gohunt/` table directory is honest
   evidence (document this either way).
4. MotherDuck query
   `SELECT count(*) FROM current_open_roles WHERE source_kind='sitemap'`
   returns the truthful count for today's GoHunt corpus
   (probe predicts 0). If the count is positive, all returned rows
   must satisfy the title-keyword filter.
5. README's source-coverage table includes a row for sitemap →
   gohunt.

# Coverage

Ticket-local acceptance criteria above. No spec contract.
`wiki:extractor-shape` is the inheritable design.

# Claim Matrix

None — no spec contract; ticket-local acceptance criteria only.

# Execution Notes

- Sitemap parsing: prefer `xml.etree.ElementTree` for clarity over
  regex. Strip the XML namespace before reading `<loc>` text. If the
  sitemap is a sitemap-index pointing at sub-sitemaps, traverse one
  level (GoHunt's appears to be a single flat sitemap based on the
  probe; if not, escalate, do not silently widen).
- JSON-LD parsing: there can be multiple `<script
  type="application/ld+json">` blocks per page. Iterate them, parse
  each, return the first with `@type == "Article"`. If `@type` is a
  list (rare), check membership.
- Title sanitization: GoHunt's `headline` includes
  " - Job Opportunity with GOHUNT". For the filter, the trailing
  "GOHUNT" is fine to keep; substring match against
  `data | engineer | gis | geospatial` ignores it. For the stored
  `title`, keep the headline verbatim — do not surgically strip the
  suffix in v1, since the canonical column is "what the source says".
- Polite User-Agent: reuse `dream-job-radar/0.1`. Add a
  short-but-not-zero `time.sleep(0.5)` between role-page fetches to
  be polite (sitemap monitor will hammer the host more than ATS APIs
  do). Single-pass, single-process, no async.
- Role id stability: last path segment of the URL is stable as long
  as GoHunt does not rename slugs. Document this so future critique
  can flag it if a renamed post produces a duplicate first_seen_at.
- 0-match outcome: if the resource yields zero records, dlt's
  filesystem destination may or may not write a `gohunt/` table
  directory. Either is acceptable for AC3, as long as the run is
  truthful.

# Blockers

None.

# Next Move / Next Route

Ralph implementation packet. New extractor kind, new pipeline file,
meta-runner update, README update — same shape as Wave 2 #2.

# Ralph Readiness

Bounded iteration: one new source-kind extractor + one new pipeline
entry + one all-sources runner update + README.

Write boundary:
- `src/dream_job_radar/extractors/sitemap.py`
- `src/dream_job_radar/extractors/__init__.py` (only if a re-export
  is genuinely needed)
- `src/dream_job_radar/pipelines/sitemap.py`
- `src/dream_job_radar/pipelines/radar.py`
- `README.md`

Verification posture: `observation-first`. Evidence is the dlt run
summary, the R2 listing, and the view count (which may legitimately
be 0).

# Evidence

Expected on completion:

- terminal output of both `pipelines.sitemap` and `pipelines.radar`
  invocations
- `boto3 list_objects_v2` for `s3://pipelines/raw/sitemap/`
- MotherDuck `count(*)` per `(source_kind, ats_slug)`
- the GoHunt URL list extracted from the sitemap (4 URLs per probe)
  echoed for transparency
- an explicit "0 matches today" or matched-titles list

Captured 2026-04-30T02:35Z (Ralph iteration 1):

AC1 — `pipelines.sitemap` runs end-to-end with 0 matches:
```
[sitemap:gohunt] skip  'Content Producer - Job Opportunity with GOHUNT'
[sitemap:gohunt] skip  'Showroom Associate (Part Time) - Job Opportunity with GOHUNT'
[sitemap:gohunt] skip  'Showroom Lead - Job Opportunity with GOHUNT'
[sitemap:gohunt] skip  'Archery Shop Lead - Job Opportunity with GOHUNT'
Pipeline dream_job_radar load step completed in 3.67 seconds
1 load package(s) were loaded to destination filesystem and into dataset sitemap
```
Pipeline did not raise on 0 yielded records.

AC2 — `pipelines.radar` runs end-to-end (greenhouse → ashby →
sitemap):
```
====== running greenhouse pipeline ======
... onxmaps: 8 ; planetlabs: 36 ...
completed in 1.76s, dataset greenhouse
====== running ashby pipeline ======
... mapbox: 59 ...
completed in 2.30s, dataset ashby
====== running sitemap pipeline ======
... [sitemap:gohunt] 4 URLs, 0 matches ...
completed in 3.08s, dataset sitemap
```

AC3 — `raw/sitemap/` after run contains dlt metadata only; no
`gohunt/` table directory because the resource yielded 0 records.
Honest evidence:
```
raw/sitemap/_dlt_loads/dream_job_radar__1777516195.390474.jsonl
raw/sitemap/_dlt_pipeline_state/...
raw/sitemap/_dlt_version/...
raw/sitemap/init
```

AC4 — view counts:
```
md: SELECT source_kind, ats_slug, count(*) FROM current_open_roles
    GROUP BY 1,2 ORDER BY 1,2
-> ('ashby', 'Mapbox', 59)
   ('greenhouse', 'onxmaps', 8)
   ('greenhouse', 'planetlabs', 36)
```
No sitemap rows (truthful 0). onx + planetlabs + Mapbox unchanged
from `ticket:oy172mt9` close-out.

AC5 — README updated with sitemap row + per-source entry point.

GoHunt URLs seen on this run (4):
- `https://www.gohunt.com/browse/news-and-updates/multimedia-content-producer-job-opportunity-with-gohunt`
- `https://www.gohunt.com/browse/news-and-updates/showroom-associate-part-time-job-opportunity-with-gohunt`
- `https://www.gohunt.com/browse/news-and-updates/showroom-lead-job-opportunity-with-gohunt`
- `https://www.gohunt.com/browse/news-and-updates/archery-shop-lead-job-opportunity-with-gohunt`

Per-URL outcome: all 4 produced a clean JSON-LD `Article` block with
`headline` + `datePublished`; all 4 filtered out by the v1 keyword
filter (none contain `data | engineer | gis | geospatial`).

# Critique Disposition

Risk class: medium

Critique policy: recommended

Policy rationale: this is the second new source kind in Wave 2 and
the first that depends on HTML parsing. The JSON-LD path is clean,
but a subtly wrong `role_id` derivation, sitemap parsing assumption,
or sleep policy will inherit into Wave 3 (scheduled runs) and into
any future sitemap-style source. Same risk profile as Ashby.

Required critique profiles:
- code-quality (extractor shape vs the inherited pattern; sitemap
  parsing; JSON-LD extraction)
- schema-fitness (role_id stability, title sanitization decision,
  0-match honesty)

Findings: see `critique:sitemap-gohunt-iter1` (7 findings, all
low/medium, none `changes_required`). Verdict:
`pass_with_findings`.

Disposition status: resolved — FIND-001/002/003/005/007 deferred to
retrospective for wiki updates and Wave 3/PM4 future
considerations. FIND-004/006 resolved by inspection. None block
ticket closure.

Deferral / not-required rationale: N/A

# Wiki Disposition

Likely no new wiki page. If sitemap parsing surfaces a meaningful
new pattern (e.g., multi-level sitemap-index handling, JSON-LD
fallback rules, polite-fetch defaults), update `wiki:extractor-shape`
during the retrospective.

Promoted 2026-04-30 during the retrospective:

- `wiki:extractor-shape` extended with a sitemap-monitor section
  covering URL-as-identity (FIND-001), JSON-LD via regex tradeoff
  (FIND-002), sitemap-presence-as-published-signal note added to
  the existing defensive-checks section (FIND-003), and a
  sitemap-index escalation note.

Intentionally not promoted:

- Per-spec sleep override (FIND-005) — defer until Wave 3
  scheduling forces the question.
- "Sources monitored" vs "sources with current matches" Dive
  distinction (FIND-007) — defer to PM4 Dive iteration.

# Acceptance Decision

Accepted by: Connor
Accepted at: 2026-04-30T02:38:00Z
Basis: AC1–AC5 satisfied with observation-first evidence (see
Evidence section). 0-match outcome accepted as v1 delivery —
pipeline is in place to surface any future GoHunt
data/engineer/GIS/geospatial role automatically. Required critique
profiles ran (`critique:sitemap-gohunt-iter1`); verdict
`pass_with_findings`, all 7 findings low/medium and tracked as
deferred follow-up.
Residual risks:
- `role_id` slug-rename fragility (FIND-001). Tracked for wiki
  promotion; defer fix until a real rename is observed.
- View glob requires at least one parquet match somewhere across
  source kinds (FIND-004). Today greenhouse + ashby keep the glob
  populated; an all-sources-zero state would re-introduce a
  view-render failure. Wave 3 (scheduling) should be aware.
- Hard-coded `time.sleep(0.5)` between role fetches (FIND-005).
  Becomes meaningful only at scale.

# Dependencies

Hard prerequisites:
- `ticket:gjkpkpum` (closed) — provides the canonical resource
  shape and view.

Soft references:
- `wiki:extractor-shape` — canonical pattern.
- `research:ats-discovery` — null-result evidence on GoHunt's
  ATS-less surface; sitemap monitor as the viable path.
- `ticket:oy172mt9` (closed) — established the second-source-kind
  refactor (`_r2.py`, meta-runner).

# Journal

- 2026-04-30 — ticket created from `plan:v1-radar` Wave 2 #4 after
  manual sitemap probe confirmed structure: 4 job-opportunity URLs;
  each role page carries clean JSON-LD `Article` data with
  `headline` and `datePublished`. Risk classified `medium`; critique
  `recommended` with two named profiles. Next route: Ralph
  implementation packet.
- 2026-04-30 — Ralph packet compiled at
  `.loom/packets/ralph/sitemap-gohunt-20260430T022113Z.md`
  (style: reference-first, posture: observation-first, source SHA
  `0bf7c44`). Awaiting child execution.
- 2026-04-30 — Ralph iteration 1 returned `continue`. All 4 GoHunt
  sitemap URLs fetched cleanly; clean JSON-LD `Article` on each;
  zero keyword-filter matches today (retail/media). Pipeline did
  not raise on 0-row outcome. `pipelines.radar` chains
  greenhouse → ashby → sitemap; existing 8 + 36 + 59 row counts
  preserved. Status → `review_required`. Critique pass next.
- 2026-04-30 — Critique landed at
  `.loom/critique/sitemap-gohunt-iter1.md`. Verdict
  `pass_with_findings`; 7 findings, all low/medium, none
  `changes_required`. FIND-001/002/003 deferred to retrospective
  for wiki updates; FIND-005/007 deferred to Wave 3/PM4 future
  iterations; FIND-004/006 resolved by inspection. Parent accepted;
  status → `closed`.
- 2026-04-30 — Retrospective complete. `wiki:extractor-shape`
  extended with sitemap-monitor section (URL-as-identity, JSON-LD
  regex tradeoff, sitemap-index escalation) plus the
  sitemap-presence note added to defensive-checks.
