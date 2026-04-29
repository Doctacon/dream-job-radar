---
id: research:ats-discovery
kind: research
status: complete
created_at: 2026-04-29T14:17:56Z
updated_at: 2026-04-29T14:17:56Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:close-the-loop
  constitution: constitution:main
external_refs: {}
---

# Question

For each curated company without a confirmed ingestion endpoint, which free
programmatic source — Greenhouse public API, Lever public API, Ashby public
API, polite HTML page monitor, or sitemap monitor — should be used to track
open roles?

Per `constitution:main`, ingestion sources must be free, programmatic, and
unauthenticated. LinkedIn job alerts and gated/paid sources are out of
scope.

# Why This Matters

`initiative:close-the-loop` cannot fully wire its pipeline until each
target company has a confirmed endpoint.

# Scope

In scope: discover the public ATS or careers source for GoHunt, Mapbox,
Planet Labs, Felt, Spartan Forge.

Out of scope: actually wiring the dlt extractors. That happens in a plan or
ticket after this research lands.

# Method

For each company:

1. Probe Greenhouse: `boards-api.greenhouse.io/v1/boards/<slug>/jobs` with
   plausible slugs.
2. Probe Lever: `api.lever.co/v0/postings/<slug>?mode=json` with plausible
   slugs.
3. Probe Ashby: `api.ashbyhq.com/posting-api/job-board/<slug>` with
   plausible slugs.
4. Fetch the company careers page and grep for ATS hostnames
   (`greenhouse.io`, `lever.co`, `ashbyhq.com`, `workday`).
5. Inspect sitemap.xml for role-shaped URLs when no ATS surfaces.
6. Drop the company from v1 if no free programmatic source exists.

# Sources

- `boards-api.greenhouse.io` (public)
- `api.lever.co` (public)
- `api.ashbyhq.com` (public)
- per-company careers pages and sitemaps

# Evidence

## Planet Labs → Greenhouse

`GET https://boards-api.greenhouse.io/v1/boards/planetlabs/jobs` returns
HTTP 200 with a `jobs` array.

## Mapbox → Ashby

Greenhouse and Lever probes 404. `mapbox.com/careers` HTML contains a link
to `ashbyhq.com/Mapbox/form/company-interest`.
`GET https://api.ashbyhq.com/posting-api/job-board/Mapbox` returns HTTP 200
with a `jobs` array containing real listings (e.g.
"Engineering Manager, Navigation SDK"). Ashby was not in the original
allowed-source list; constitution updated to admit it.

## Felt → page monitor

Greenhouse, Lever, Ashby probes 404. `felt.com/careers` returns HTTP 200
but contains only one "Open role" block and no external ATS hostname.
Listings appear to be hand-maintained on the page. Page monitor on the
careers HTML is the viable path (diff for "Open role" blocks).

## GoHunt → sitemap monitor

Greenhouse and Lever probes 404 across multiple slug variants
(`gohunt`, `gohuntllc`, `go-hunt`, `gohuntinc`, `gohuntcom`).
`gohunt.com/careers` 404s. `gohunt.com/sitemap.xml` returns HTTP 200 and
exposes role posts under `/browse/news-and-updates/` with slugs like
`*-job-opportunity-with-gohunt` and a landing page
`/browse/news-and-updates/announcements/careers-at-gohunt`. GoHunt does not
appear to use any ATS; jobs ship as blog posts in their CMS. Sitemap
monitor for new `*job-opportunity*` URLs is the viable path. Sitemap-
monitor was not in the original allowed-source list; constitution updated
to admit it.

## Spartan Forge → dropped

Greenhouse, Lever, Ashby probes 404. `/careers` and `/jobs` both 404 on
both `www.spartanforge.ai` and `spartanforge.ai`. Root page contains no
hiring or career keywords. No public careers surface located. Per
constitution, dropped from v1. Reconsider only if a public surface
appears.

# Rejected Options

- **LinkedIn job alerts** — not a free programmatic pull; excluded by
  constitution before the investigation began.
- **Aggregator scraping** (LinkedIn jobs, Indeed, Glassdoor) — gated,
  fragile, hostile to scraping.
- **Spartan Forge LinkedIn follow** — would require LinkedIn account-side
  notifications. Same reason as above.

# Null Results

- GoHunt has no ATS at all. Multiple Greenhouse and Lever slug variants
  failed. Future agents should not retry ATS probes on GoHunt; the answer
  is "they post jobs as CMS blog entries."
- Spartan Forge appears not to publish a careers surface. Common paths
  (`/careers`, `/jobs`, `/about`) all 404. Future agents should not retry
  unless evidence emerges that a public surface was added.

# Conclusions

Six of seven curated companies have a confirmed free, programmatic source
across four extractor kinds:

- Greenhouse: onX, Planet Labs
- Ashby: Mapbox
- Page monitor: Regrid, Felt
- Sitemap monitor: GoHunt

Spartan Forge has no qualifying source and is dropped from v1.

Two new source kinds (Ashby API, sitemap monitor) are admitted into the
constitutional allow-list as a result of this research.

# Recommendations

- Promote findings into `initiative:close-the-loop` v1 company table
  (done).
- Plan that sequences M1–M5 should treat the dlt pipeline as supporting
  four extractor kinds: Greenhouse, Ashby, page monitor, sitemap monitor.
- Title-keyword filter is applied uniformly post-extraction, since every
  source produces some shape of role record (or candidate URL, in the
  sitemap case).
- For sitemap monitor, the role record is built by fetching each new
  sitemap URL and parsing the blog post for title and posting date. That
  is more work than an API path; budget for it accordingly.

# Open Questions

None blocking v1.

- For Felt, if the careers page becomes more dynamic (JS-rendered
  beyond the current state), the page monitor approach may need to move
  to a headless-browser fetch. Not a v1 blocker.

# Linked Work

- `initiative:close-the-loop` — consumed: v1 company table updated.
- `constitution:main` — consumed: allow-list extended with Ashby and
  sitemap monitor.
