---
id: research:ats-discovery-v2
kind: research
status: closed
created_at: 2026-05-02T13:13:30Z
updated_at: 2026-05-02T13:13:30Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  predecessor: research:ats-discovery
  initiative: initiative:expand-radar
  constitution: constitution:main
external_refs: {}
---

# Question

For the 12 candidate companies the user identified as new
mission-aligned targets (CalTopo, Vibrant Planet, Pachama, AllTrails,
Wherobots, Floodbase, BlastPoint, Pano AI, Upstream Tech, Overstory,
Kalkomey/HuntStand, BaseMap), which ones have a free, programmatic,
unauthenticated endpoint suitable for the radar pipeline, and which
existing or new source-kind extractor handles each?

# Why This Matters

`initiative:expand-radar` builds on the v1 close-the-loop pipeline
(now closed) by widening the company watch-list to the user's actual
target set. Without confirmed endpoints the initiative cannot create
extractor tickets without speculation. The v1 research record
(`research:ats-discovery`) covered six companies (onX, Planet Labs,
Mapbox, Felt, Regrid, GoHunt). This v2 pass covers the next twelve.

# Scope

In scope: probe each of the 12 candidate companies for an ATS or
public careers surface that meets the constitutional criteria
(free, programmatic, unauthenticated). Identify the source-kind
each one falls under: greenhouse, lever, ashby, sitemap-monitor,
page-monitor, or a new kind.

Out of scope: actually wiring the dlt extractors (lives in
`plan:expand-radar` waves).

# Method

For each company:

1. Probe Greenhouse: `boards-api.greenhouse.io/v1/boards/<slug>/jobs`
   with plausible slug variations.
2. Probe Lever: `api.lever.co/v0/postings/<slug>?mode=json`.
3. Probe Ashby: `api.ashbyhq.com/posting-api/job-board/<slug>`.
4. Fetch the company's careers / homepage and grep for ATS hostname
   markers (`greenhouse.io`, `lever.co`, `ashbyhq.com`, `workday`,
   `rippling`, `bamboohr`, `smartrecruiters`, `gusto.com`, etc.).
5. Inspect any custom job subdomain (`jobs.<company>.<tld>`) for
   per-role JSON-LD or a JSON API.
6. Drop the company if no qualifying surface exists.

Probes used the standard polite User-Agent (`dream-job-radar/0.1`)
plus a browser User-Agent on the small number of hosts that
returned 403 to scripts. Constitutional posture: no anti-bot
evasion; if a host requires browser cookies or JS rendering to
return a useful response, the company is dropped or deferred.

# Sources

- `boards-api.greenhouse.io` (public)
- `api.lever.co` (public)
- `api.ashbyhq.com` (public)
- `api.rippling.com/platform/api/ats/v1/board/<slug>/jobs` (public,
  newly added to constitution allow-list this iteration)
- per-company careers pages and sitemaps

# Evidence

## Floodbase → Greenhouse

`GET https://boards-api.greenhouse.io/v1/boards/floodbase/jobs`
→ HTTP 200, `jobs` array of length 4. Slug: `floodbase`.

## BlastPoint → Greenhouse

`GET https://boards-api.greenhouse.io/v1/boards/blastpoint/jobs`
→ HTTP 200, `jobs` array of length 4. Slug: `blastpoint` (the
Greenhouse API treats slug case-insensitively here).

## Overstory → Greenhouse

`GET https://boards-api.greenhouse.io/v1/boards/overstory/jobs`
→ HTTP 200, `jobs` array of length 11. Slug: `overstory`.

## Pano AI → Ashby

`GET https://api.ashbyhq.com/posting-api/job-board/pano-ai`
→ HTTP 200, `jobs` array of length 25. Slug: `pano-ai`. Note the
hyphen — `panoai` and `PanoAI` both 404. Same slug-case-sensitivity
rule as Mapbox.

## Kalkomey (HuntStand / HuntWise) → Rippling (NEW source kind)

Their careers page at `kalkomey.com/careers` referenced
`https://api.rippling.com/platform/api/ats/v1/board/kalkomey/jobs`.
Direct probe: HTTP 200, JSON list of 6 records, each with shape:

```
{
  "uuid": "86cb9df0-2d01-4994-8e75-06e21ce17534",
  "name": "Content Editor (Contractor)",
  "department": {"id": "Marketing", "label": "Marketing"},
  "url": "https://ats.rippling.com/kalkomey/jobs/86cb9df0-...",
  "workLocation": {"label": "Remote (United States)", ...}
}
```

Clean shape: `uuid` is a stable role_id, `name` is the title, `url`
is the canonical apply page, `workLocation.label` maps to
`location`, `department.label` may be useful but does not need to
be exposed in the canonical row. No `posted_at` exposed at the list
level (treat as `""` like page-monitor sources).

Rippling is admitted to the constitutional allow-list as a result
of this finding.

## Upstream Tech → Polymer-hosted portal (NEW pattern)

Their careers page on `upstream.tech/careers` links to per-role
pages on `jobs.upstream.tech/<numeric_id>`. Each role page carries
external links to `app.polymer.co` and
`https://www.polymer.co?utm_source=polymerJobsPage` plus a clean
JSON-LD `JobPosting` block:

```
{
  "@context": "https://schema.org/",
  "@type": "JobPosting",
  "title": "Open Call for Applications",
  "description": "<h2>Opportunity</h2><p>Upstream Tech is a climate
                  technology company...",
  ...
}
```

The `jobs.upstream.tech` ROOT does not appear to expose a JSON list
API publicly; the per-role IDs may need to come from the parent
careers page or a Polymer-side feed. Confirm during the Wave 3
implementation. If no scrape-friendly index exists, escalate (the
company may need to be deferred).

Polymer-style "per-role JSON-LD on a custom jobs subdomain" is
admitted to the constitutional allow-list as a result of this
finding.

## Vibrant Planet → page monitor

`vibrantplanet.net/about/team-and-careers` returns HTTP 200 with the
careers section embedded deep in the Webflow HTML (the substring
"open position" first appears at ~character 189,000 of the page).
No external ATS hostname references. Page-monitor source with a
per-site parser strategy.

## Wherobots → page monitor

`wherobots.com/careers/` returns HTTP 200 and lists role anchors
under `https://wherobots.com/careers/<role-slug>/`. Today's listing
shows only `senior-account-executive-global` — the rest may be
JS-rendered or there may simply be one open role. Page-monitor
source; if the role list turns out to be JS-rendered behind a
WordPress plugin, the company may need to be deferred until a
plain-HTML alternative surfaces.

## Pachama → dropped (acquired)

`pachama.com/`, `pachama.com/careers`, and `pachama.com/jobs` all
redirect (HTTP 200, final URL `https://www.carbon-direct.com/`).
Pachama appears to have been acquired by or merged into Carbon
Direct; their independent careers surface is gone. Dropped from
v2 scope. If Carbon Direct's careers surface is interesting in its
own right, it would be a separate company decision.

## AllTrails → dropped (anti-bot)

`alltrails.com/careers` returns HTTP 403 to both polite and
browser-style User-Agents. `about.alltrails.com/careers` returns
HTTP 503. Lever slug `alltrails` returns 200 with `[]` (the slug
exists in Lever's URL space but no current postings — possibly
moved off Lever). Workday subdomains
(`alltrails.wd1.myworkdayjobs.com`, `alltrails.wd5.myworkdayjobs.com`)
return HTTP 406 to plain GET. Cloudflare and / or Workday are
actively blocking automated reads. Per the constitutional posture
("no anti-bot evasion"), AllTrails is dropped from v2 scope.

## CalTopo → dropped (no public careers surface)

`caltopo.com/careers` and `caltopo.com/jobs` both 404. The site has
a `/join` path but it is for end-user account creation, not roles.
Homepage HTML contains no career-shaped links. CalTopo presumably
hires through informal channels at this company size; no
programmatic surface exists. Dropped.

## BaseMap → dropped (no public careers surface)

`basemap.com/careers` 404. Homepage has no career-shaped links.
`basemapgear.com` is unreachable (no DNS or connection). Dropped.

# Rejected Options

- **AllTrails Workday workaround.** Workday returns HTTP 406 to
  plain GET; making the request "look like a browser" would require
  cookies and possibly JS execution. That violates the
  constitutional "no anti-bot evasion" posture. Dropped.
- **Pachama via Carbon Direct.** Carbon Direct is a separate
  company with its own mission framing; folding it in as
  "successor to Pachama" misrepresents the watch-list. If Carbon
  Direct is independently interesting, add as its own entry.

# Null Results

- **CalTopo, BaseMap** have no public careers surface at all. Future
  agents should not retry probes; the answer is "no surface".
- **AllTrails** actively blocks automated reads from at least two
  surfaces (Cloudflare on the main site, Workday on the apparent
  ATS). Future probes are unlikely to succeed without cookies or
  JS.
- **Pachama** is acquired / domain redirects to Carbon Direct.

# Conclusions

Eight of the twelve candidates have a usable surface:

| company        | source kind                | endpoint                                                                            |
|----------------|----------------------------|-------------------------------------------------------------------------------------|
| Floodbase      | greenhouse                 | `boards-api.greenhouse.io/v1/boards/floodbase/jobs`                                 |
| BlastPoint     | greenhouse                 | `boards-api.greenhouse.io/v1/boards/blastpoint/jobs`                                |
| Overstory      | greenhouse                 | `boards-api.greenhouse.io/v1/boards/overstory/jobs`                                 |
| Pano AI        | ashby                      | `api.ashbyhq.com/posting-api/job-board/pano-ai`                                     |
| Kalkomey       | rippling (NEW)             | `api.rippling.com/platform/api/ats/v1/board/kalkomey/jobs`                          |
| Upstream Tech  | polymer (NEW; per-role JSON-LD) | `jobs.upstream.tech/<id>`                                                       |
| Vibrant Planet | page-monitor               | `vibrantplanet.net/about/team-and-careers`                                          |
| Wherobots      | page-monitor               | `wherobots.com/careers/`                                                            |

Four are dropped:

- Pachama (acquired)
- AllTrails (anti-bot)
- CalTopo (no surface)
- BaseMap (no surface)

Two new constitutional source kinds are admitted: **rippling** and
**polymer (per-role JSON-LD on a custom jobs subdomain)**. Both
extend `wiki:extractor-shape`'s established pattern (one pipeline
per source kind, dataset_name = source_kind).

# Recommendations

- Promote findings into `initiative:expand-radar` v1 company table
  (this research is its evidentiary base).
- Plan that sequences the initiative should treat the work as four
  waves:
  - Wave 1: trivial config-only adds (Floodbase + BlastPoint +
    Overstory to greenhouse `DEFAULT_BOARDS`; Pano AI to ashby
    `DEFAULT_BOARDS`).
  - Wave 2: Rippling extractor kind (Kalkomey).
  - Wave 3: Polymer / per-role JSON-LD extractor (Upstream Tech) —
    needs a deeper probe of the role-list discovery shape during
    implementation.
  - Wave 4: page-monitor adds (Vibrant Planet, Wherobots) — risk
    of JS-rendered role lists; deferable.
- AllTrails / CalTopo / BaseMap dropped permanently from v2 scope.
  Pachama likewise (note: Carbon Direct is a separate company; if
  the user wants Carbon Direct in a future initiative, add it
  there).
- Title-keyword filter (`data | engineer | gis | geospatial`,
  case-insensitive substring) is reused as-is from v1. Wave 4
  retrospective on `initiative:close-the-loop` flagged false-
  positive concerns; the v2 retrospective should re-evaluate
  with double the corpus.

# Open Questions

- **Polymer role-list discovery:** can `jobs.upstream.tech` expose a
  list of role IDs without JS, or do we need to derive role IDs from
  the parent careers page (`upstream.tech/careers`)? The Wave 3
  packet should explicitly answer this.
- **Wherobots role list:** are the missing roles JS-rendered, or
  does Wherobots simply have one open role today? Verify during
  Wave 4 probe.
- **Rippling pagination:** the Kalkomey response returned 6
  records with no pagination metadata. If a larger Rippling-hosted
  company appears in a future initiative, confirm whether the API
  paginates.

# Linked Work

- `initiative:expand-radar` — primary consumer of this research.
- `constitution:main` — updated 2026-05-02 to include rippling and
  polymer in the allow-list.
- `wiki:extractor-shape` — will gain rippling + polymer sections
  during Wave 2/3 retrospectives.
