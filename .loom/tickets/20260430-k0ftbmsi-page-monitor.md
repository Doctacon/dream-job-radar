---
id: ticket:k0ftbmsi
kind: ticket
status: closed
change_class: code-behavior
risk_class: medium
created_at: 2026-04-30T02:51:25Z
updated_at: 2026-04-30T03:08:00Z
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
  regrid_gusto: https://jobs.gusto.com/boards/regrid-map-your-future-c265c805-0902-4628-bd27-d013fdcfb5bc
  felt_careers: https://felt.com/careers
depends_on:
  - ticket:gjkpkpum
---

# Summary

Wave 2 #3: build the page-monitor extractor kind and connect it to
Regrid and Felt. Lands Parquet at
`r2://<bucket>/raw/page/regrid/` and `r2://<bucket>/raw/page/felt/`.
Closes the last v1 source kind. PM2 of `plan:v1-radar` then closes.

# Context

`wiki:extractor-shape` is the canonical reference. Read it first.
This ticket inherits all Wave 2 lessons:

- canonical row must NOT contain Python list values
- slug-case policy (data preserves source casing; R2 path may be
  lowercased)
- defensive listed/published checks (sitemap-presence is the
  signal for sitemap-style sources; for page-monitor sources, the
  presence of the role on the careers page IS the signal)
- duplicate-by-title is upstream behavior

Per `research:ats-discovery`, Felt and Regrid are both confirmed
v1 sources via "page monitor" — fetch HTML, parse role blocks,
filter. Verified 2026-04-30:

**Regrid → Gusto job board.** `regrid.com/careers` is a marketing
landing page; "View open positions" links to
`https://jobs.gusto.com/boards/regrid-map-your-future-c265c805-0902-4628-bd27-d013fdcfb5bc`.
That page server-renders the role list as plain HTML. Today:
- 2 roles total
- structured as `<a class="block hover:bg-gray-50" href="/postings/<slug-with-uuid>">`
  wrapping `<h3 class="text-lg">Title</h3>` plus location text.
- canonical role URL: `https://jobs.gusto.com/postings/<slug-with-uuid>`
- stable role_id: the trailing UUID segment of the postings slug
- 0 keyword-filter matches today
  ("Join Our Talent Pool", "Product Marketing Manager")

**Felt → careers page.** `felt.com/careers` is a single-page
Webflow site. Today:
- 8 roles, each in `<div class="h4 careers">Title</div>` blocks
- no per-role URL; apply is via `mailto:hello@felt.com`
- no posted_at signal
- 1 keyword-filter match today ("Sales/Solution Engineer")

# Why Now

Last Wave 2 ticket. Closing it closes PM2. Already built three
source kinds; this one inherits the established refactor (`_r2.py`,
meta-runner) and the canonical-row contract.

# Scope

- Add `src/dream_job_radar/extractors/page.py`. Use per-site parser
  strategies because the two surfaces are structurally different:
  - Define a `SiteSpec` (NamedTuple or dataclass) with:
    - `slug` (e.g. `"regrid"`, `"felt"`)
    - `url` (careers page or board page URL)
    - `parser_kind` (literal: `"gusto_board"` | `"felt_careers"`)
  - `_parse_gusto_board(html, slug)` — extract role list from
    `<a class="block hover:bg-gray-50" href="/postings/...">` +
    `<h3 class="text-lg">` pattern. Return list of dicts with at
    least `title`, `role_id` (trailing UUID of `/postings/<slug>`),
    `url` (`https://jobs.gusto.com/postings/<slug>`).
  - `_parse_felt_careers(html, slug)` — extract titles from
    `<div class="h4 careers">` blocks. Return list of dicts with
    `title`, `role_id` (sha1 of slug + title — stable until title
    changes), `url` (the careers page URL itself, since there is no
    per-role link).
  - `_normalize(role, spec, fetched_at)` — produce the canonical
    row:
    - `company`: spec.slug
    - `source_kind`: `"page"`
    - `ats_slug`: spec.slug
    - `role_id`: from parser
    - `title`: from parser
    - `url`: from parser
    - `location`: from parser if available, else `None`
    - `posted_at`: `""` (page monitor sources have no upstream
      posting date; the view's `first_seen_at` covers the practical
      need)
    - `fetched_at`: ISO timestamp at run start
    - `raw_json`: JSON-serialized parsed role dict
  - `site_resource(spec)` — `@dlt.resource(name=spec.slug,
    write_disposition="append")`. Inside: GET HTML, parse with the
    appropriate strategy, apply title-keyword filter, yield
    matches.
  - `site_resources(specs=DEFAULT_SITES)` returns one resource per
    spec.
  - `DEFAULT_SITES = (
       SiteSpec(slug="regrid",
                url="https://jobs.gusto.com/boards/regrid-map-your-future-c265c805-0902-4628-bd27-d013fdcfb5bc",
                parser_kind="gusto_board"),
       SiteSpec(slug="felt",
                url="https://felt.com/careers",
                parser_kind="felt_careers"),
     )`

- Add `src/dream_job_radar/pipelines/page.py` mirroring
  `pipelines/sitemap.py` with `SOURCE_KIND = "page"` and
  `DATASET_NAME = "page"`. Reuse `pipelines._r2.r2_destination`.
  Entry point: `python -m dream_job_radar.pipelines.page`.

- Update `src/dream_job_radar/pipelines/radar.py` meta-runner to
  also call `page_pipeline.run()` at the end.

- Update `README.md` source-coverage table and per-source entry
  points.

# Non-goals

- No headless browser. Both surfaces server-render the role list.
  If either becomes JS-rendered later, escalate to a fresh
  research/spec ticket.
- No Gusto-API integration. The Gusto job board page is HTML,
  Gusto does not publish a public board API for embedding outside
  apps. We treat the Gusto page as a structured HTML surface, not
  an API.
- No per-role detail-page fetch. We extract everything the list
  page shows. The detail page would add description and posted_at
  for Gusto — defer until a v2 retro shows it matters.
- No revision of the title-keyword filter (FIND-002 from Wave 1
  critique still deferred).

# Acceptance Criteria

1. `uv run python -m dream_job_radar.pipelines.page` runs
   end-to-end without error against both Regrid and Felt.
2. `uv run python -m dream_job_radar.pipelines.radar` runs
   end-to-end and exercises greenhouse + ashby + sitemap + page.
   Existing onx (8) + planetlabs (36) + Mapbox (59) + sitemap (0)
   row counts in the view are unchanged or higher. No regressions.
3. `boto3 list_objects_v2 Prefix=raw/page/` returns at least the
   dlt-managed metadata. `raw/page/regrid/` and `raw/page/felt/`
   table directories may exist or not depending on whether each
   resource yields ≥1 record (today: regrid yields 0, felt yields
   1).
4. MotherDuck query
   `SELECT count(*) FROM current_open_roles WHERE source_kind='page'`
   returns the truthful count. With today's data, expect 1 (the
   Felt "Sales/Solution Engineer" role).
5. Per-slug counts:
   `SELECT ats_slug, count(*) FROM current_open_roles
    WHERE source_kind='page' GROUP BY 1`
   returns regrid=0 (or no row) + felt=1 (today).
6. README documents `python -m dream_job_radar.pipelines.page` and
   the source-coverage table includes both `page/regrid` and
   `page/felt` rows.

# Coverage

Ticket-local acceptance criteria above. No spec contract.
`wiki:extractor-shape` is the inheritable design.

# Claim Matrix

None — no spec contract; ticket-local acceptance criteria only.

# Execution Notes

- Regrid Gusto board pattern (verified 2026-04-30):
  ```html
  <a class="block hover:bg-gray-50" href="/postings/regrid-map-your-future-join-our-talent-pool-ff451599-4c55-47e8-866a-c5ac1e2e4c7c">
    <div class="px-4 py-4 sm:px-6">
      <h3 class="text-lg">Join Our Talent Pool</h3>
      ...
    </div>
  </a>
  ```
  Extract via regex over the `<a>` open tag + nested `<h3>`.
- Felt careers pattern (verified 2026-04-30):
  ```html
  <div class="h4 careers">Sales/Solution Engineer</div>
  ```
  Extract via regex against that exact class name.
- HTML parsing: prefer regex for the two specific patterns above
  (avoids a new BS4/lxml dep). If a future page change breaks the
  regex, escalate.
- role_id derivation:
  - regrid (Gusto): trailing UUID-shape segment of `/postings/<slug>`
    (split on `-`, take last 5 segments and join with `-` to get the
    UUID — hex-only is unsafe because slugs may end in hex).
    Simpler: take everything after the LAST `-` of length 12 where a
    UUID block starts. Cleanest: regex
    `r'-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$'`
    against the slug.
  - felt: `hashlib.sha1((slug + ":" + title).encode()).hexdigest()[:16]`.
    Stable while title doesn't change. Title rename creates a new
    role_id (acceptable v1 trade-off; same as sitemap).
- `posted_at`: neither source provides one. Set to empty string;
  the view's `first_seen_at = min(fetched_at) over (...)` gives
  the practical "first observed" timestamp.
- Polite User-Agent: reuse `dream-job-radar/0.1`. No sleep needed
  for v1 (only 2 page fetches per run).

# Blockers

None.

# Next Move / Next Route

Ralph implementation packet. Same shape as Wave 2 #2 and #4: new
extractor kind, new pipeline, meta-runner update, README update.

# Ralph Readiness

Bounded iteration: one new source-kind extractor handling two
distinct parser strategies + one new pipeline + meta-runner update +
README.

Write boundary:
- `src/dream_job_radar/extractors/page.py`
- `src/dream_job_radar/extractors/__init__.py` (only if needed)
- `src/dream_job_radar/pipelines/page.py`
- `src/dream_job_radar/pipelines/radar.py`
- `README.md`

Verification posture: `observation-first`. Evidence is the dlt run
summary, R2 listing, and view counts (1 role expected today).

# Evidence

Expected on completion:

- terminal output of both `pipelines.page` and `pipelines.radar`
  invocations
- `boto3 list_objects_v2` for `s3://pipelines/raw/page/`
- per-site URL list extracted (Regrid: 2 today, Felt: 8 today)
- MotherDuck count per `(source_kind, ats_slug)`
- the matched Felt title ("Sales/Solution Engineer" expected)

Captured 2026-04-30T03:05Z (Ralph iteration 1):

AC1 — `pipelines.page` runs end-to-end:
```
[page:regrid] parsed 2 role(s) from page
[page:regrid] skip  'Join Our Talent Pool'
[page:regrid] skip  'Product Marketing Manager'
[page:felt] parsed 8 role(s) from page
[page:felt] skip  'Customer Success Manager'
[page:felt] skip  'Operations Manager'
[page:felt] skip  'Senior Product Marketing Manager'
[page:felt] skip  'Senior Demand Generation Manager'
[page:felt] MATCH 'Sales/Solution Engineer'
[page:felt] skip  'Account Executive - MidMarket'
[page:felt] skip  'Account Executive - Enterprise'
[page:felt] skip  'Sales Development Representative'
Pipeline dream_job_radar load step completed in 4.16 seconds
1 load package(s) were loaded to destination filesystem and into dataset page
```

AC2 — `pipelines.radar` runs end-to-end across all four source
kinds. Greenhouse + Ashby + sitemap + page chained without error.

AC3 — R2 `raw/page/` after run:
```
raw/page/_dlt_loads/...
raw/page/_dlt_pipeline_state/...
raw/page/_dlt_version/...
raw/page/init
raw/page/felt/1777517877.280458.1413e2f327.parquet  3763
```
No `regrid/` table directory (Regrid yielded 0 records). Honest
evidence per packet.

AC4 — `count(*) WHERE source_kind='page'` = 1.

AC5 — per-slug counts:
```
md: SELECT ats_slug, count(*) FROM current_open_roles
    WHERE source_kind='page' GROUP BY 1
-> ('felt', 1)
```
No `regrid` row (truthful — 0 matches today).

AC6 — README updated with both `page/regrid` and `page/felt`
source-coverage rows + `pipelines.page` entry point.

Full view counts post-run:
```
('ashby', 'Mapbox', 59)
('greenhouse', 'onxmaps', 8)
('greenhouse', 'planetlabs', 36)
('page', 'felt', 1)
```
Total: 104 roles. No regressions on prior source kinds.

Matched Felt row stored:
```
source_kind=page, ats_slug=felt,
title='Sales/Solution Engineer',
url='https://felt.com/careers',
role_id='e84ed5eb9e6e19ca' (sha1(slug+":"+title)[:16])
```

# Critique Disposition

Risk class: medium

Critique policy: recommended

Policy rationale: page monitor is the most fragile source kind in
v1 — HTML can change without notice. Subtle parsing bugs would
silently produce wrong data. Critique should pressure-test the
two regex patterns against unanticipated markup variants, the
role_id derivation under upstream renames, and the
posted_at-as-empty-string decision.

Required critique profiles:
- code-quality (per-site parser strategy organization, regex
  fragility surface, error handling for parse failure)
- schema-fitness (role_id stability across the two sites,
  empty-posted_at decision, view-shape inheritance)

Findings: see `critique:page-monitor-iter1` (7 findings, all
low/medium, none `changes_required`). Verdict:
`pass_with_findings`.

Disposition status: resolved — FIND-001/002/003/004/005/007
deferred to retrospective for wiki updates and Wave 3 alert
design. FIND-006 resolved by inspection. None block ticket closure.

Deferral / not-required rationale: N/A

# Wiki Disposition

Likely a meaningful update to `wiki:extractor-shape` during the
retrospective: page-monitor adds a third "no-API" source-kind
pattern with its own role_id and posted_at semantics. Update during
the retrospective so all four source kinds have a comparable
section.

Promoted 2026-04-30 during the retrospective:

- `wiki:extractor-shape` extended with: page-monitor section
  (per-site parser dispatch + regex fragility, FIND-001),
  role_id-strategies-by-source-kind comparison table (FIND-002),
  posted_at semantics per source kind (FIND-004), Felt-as-careers-
  page note (FIND-003).

Intentionally not promoted:

- N→0 silent breakage alert (FIND-001 + FIND-007) — Wave 3 owns
  scheduling and alerting; Wave 3 ticket should carry the design.
- Apply-action structured field (FIND-005) — defer until a Dive
  iteration needs it.

# Acceptance Decision

Accepted by: Connor
Accepted at: 2026-04-30T03:08:00Z
Basis: AC1–AC6 satisfied with observation-first evidence (see
Evidence section). Felt yielded 1 match
("Sales/Solution Engineer"); Regrid yielded 0 matches today (both
truthful). Required critique profiles ran
(`critique:page-monitor-iter1`); verdict `pass_with_findings`, all
7 findings low/medium and tracked as deferred follow-up. Wave 2
PM2 of `plan:v1-radar` closes with this ticket.
Residual risks:
- HTML parser fragility (FIND-001). Tracked for wiki + Wave 3
  alert design.
- Divergent role_id strategies inside one source kind
  (FIND-002). Tracked for wiki.
- Felt url == careers page itself (FIND-003); apply via mailto not
  exposed in canonical row (FIND-005). Surface concerns for future
  Dive iteration.

# Dependencies

Hard prerequisites:
- `ticket:gjkpkpum` (closed) — provides the canonical resource
  shape and view.

Soft references:
- `wiki:extractor-shape` — canonical pattern with sitemap-monitor
  precedent.
- `research:ats-discovery` — names Regrid + Felt as page-monitor
  sources.
- `ticket:oy172mt9` (closed) — established `_r2.py` factory and
  meta-runner shape.
- `ticket:xwfvoj4o` (closed) — sitemap-monitor precedent for
  no-ATS sources, including 0-row honesty pattern.

# Journal

- 2026-04-30 — ticket created from `plan:v1-radar` Wave 2 #3 after
  manual probes confirmed: Regrid hosts on Gusto job board (server-
  rendered HTML, predictable structure, 2 roles today, 0 matches);
  Felt is a single-page Webflow careers page (8 roles today, 1
  match: "Sales/Solution Engineer"). Risk classified `medium`;
  critique `recommended` with two named profiles. Next route: Ralph
  implementation packet.
- 2026-04-30 — Ralph packet compiled at
  `.loom/packets/ralph/page-monitor-20260430T025403Z.md` (style:
  reference-first, posture: observation-first, source SHA
  `68904ea`). Awaiting child execution.
- 2026-04-30 — Ralph iteration 1 returned `continue`. Regrid 2
  roles parsed, 0 matches; Felt 8 roles parsed, 1 match
  ("Sales/Solution Engineer"). dlt clean on per-site 0-row
  outcome. View row inserted with role_id sha1 hash; Wave 1+2 row
  counts unchanged. Status → `review_required`.
- 2026-04-30 — Critique landed at
  `.loom/critique/page-monitor-iter1.md`. Verdict
  `pass_with_findings`; 7 findings, all low/medium, none
  `changes_required`. FIND-001/002/003/004/005/007 deferred to
  retrospective; FIND-006 resolved by inspection. Parent accepted;
  status → `closed`. **PM2 of `plan:v1-radar` closes** — all four
  v1 source kinds shipped.
- 2026-04-30 — Retrospective complete. `wiki:extractor-shape`
  extended with page-monitor section, role_id-strategies-by-
  source-kind comparison, posted_at-per-source-kind table, Felt
  careers-page note.
