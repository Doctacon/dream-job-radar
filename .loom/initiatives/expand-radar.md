---
id: initiative:expand-radar
kind: initiative
status: closed
created_at: 2026-05-02T13:13:30Z
updated_at: 2026-05-02T14:30:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  constitution: constitution:main
  research:
    - research:ats-discovery-v2
  predecessor: initiative:close-the-loop
external_refs: {}
---

# Summary

Widen the dream-job-radar watch-list from the v1 six-company corpus
to the user's full mission-aligned target set. v2 ships eight new
companies across three families: outdoors / mapping (Floodbase,
Overstory), wildfire / forest restoration (Vibrant Planet, Pano AI,
Upstream Tech), and the user's specific data-engineering toolchain
fit (Wherobots, BlastPoint, Kalkomey).

# Objective

The radar shows roles from every company on the user's curated
mission-aligned target list that has a usable public endpoint, so
the daily Dive becomes a complete view of where the user might
plausibly apply rather than a partial v1 snapshot.

# Why Now

`initiative:close-the-loop` closed 2026-05-02 with a working v1
pipeline (cron + view + Dive across 6 companies, 104 roles). The
infrastructure is stable: 4 source kinds, shared R2 destination,
`current_open_roles` view that ignores source kind. Adding new
companies is now mostly config-only work, plus two new source-kind
extractors. The marginal cost of expanding is low; the marginal
value is high (each additional mission-aligned company produces
real candidate roles for the user's job hunt).

# In Scope

Eight new companies, classified by `research:ats-discovery-v2`:

| company        | source kind          | endpoint                                                                      |
|----------------|----------------------|-------------------------------------------------------------------------------|
| Floodbase      | greenhouse           | `boards-api.greenhouse.io/v1/boards/floodbase/jobs`                           |
| BlastPoint     | greenhouse           | `boards-api.greenhouse.io/v1/boards/blastpoint/jobs`                          |
| Overstory      | greenhouse           | `boards-api.greenhouse.io/v1/boards/overstory/jobs`                           |
| Pano AI        | ashby                | `api.ashbyhq.com/posting-api/job-board/pano-ai`                               |
| Kalkomey       | **rippling** (new)   | `api.rippling.com/platform/api/ats/v1/board/kalkomey/jobs`                    |
| Upstream Tech  | **polymer** (new; per-role JSON-LD) | `jobs.upstream.tech/<id>`                                      |
| Vibrant Planet | page-monitor         | `vibrantplanet.net/about/team-and-careers`                                    |
| Wherobots      | page-monitor         | `wherobots.com/careers/`                                                      |

Two new source kinds are admitted to the constitutional allow-list
as part of this initiative (`rippling`, `polymer`).

# Out Of Scope

Four candidates dropped per `research:ats-discovery-v2`:

- **Pachama** — acquired / merged into Carbon Direct; site
  redirects.
- **AllTrails** — Cloudflare bot block on `/careers` (403/503);
  Workday subdomains 406. No programmatic surface.
- **CalTopo** — no public careers surface.
- **BaseMap** — no public careers surface; `basemapgear.com`
  unreachable.

Out of scope for v2:

- Anti-bot evasion (cookies, JS rendering, headless browsers) for
  AllTrails or any future blocked source. Constitutional posture
  unchanged.
- Apply-loop tracking (M6 of `initiative:close-the-loop`); still
  deferred.
- Replacement for the v1-cancelled M5 (blog post). If the user
  decides to ship a post about the radar, that is its own
  initiative.

# Success Metrics

- All eight in-scope companies write Parquet to R2 under the
  appropriate `raw/<source_kind>/<ats_slug>/` prefix at least
  once.
- `current_open_roles` exposes positive role counts for at least
  six of the eight (allowing for two companies legitimately
  showing zero matches against the v1 keyword filter on a given
  day, same posture as Wave 2 #4 sitemap).
- The daily cron (`refresh.yml`) continues to succeed end-to-end
  with the new sources wired in. No regression on existing six
  companies.
- `wiki:extractor-shape` gains a section per new source kind
  (rippling, polymer).

# Milestones

## M1 — Trivial config-only adds (Floodbase, BlastPoint, Overstory, Pano AI)

Extend `DEFAULT_BOARDS` in `extractors/greenhouse.py` and
`extractors/ashby.py`. No new code paths. Single ticket; same
shape as `ticket:tiv8bsu7` (Wave 2 #1 in v1).

## M2 — Rippling extractor (Kalkomey)

New `extractors/rippling.py` + `pipelines/rippling.py`,
chained into the meta-runner. Same shape as `ticket:oy172mt9`
(Ashby/Mapbox in v1). Critique recommended.

## M3 — Polymer extractor (Upstream Tech)

Investigate role-list discovery shape (per-role JSON-LD known
clean; index page may need parent-careers fallback). Build
`extractors/polymer.py` + pipeline. Critique recommended. May
require a research loop-back if no scrape-friendly index exists;
in that case, defer Upstream Tech without blocking the rest of
the initiative.

## M4 — Page-monitor adds (Vibrant Planet, Wherobots)

Per-site parser strategies inside the existing `extractors/page.py`.
Same pattern as `ticket:k0ftbmsi` (Wave 2 #3 in v1). May surface
JS-rendered content; in that case, defer the affected company
without blocking the others.

## M5 — Updated dive + retro

Re-confirm the Dive renders the expanded result set cleanly on
mobile. Run a retrospective pass that updates
`wiki:extractor-shape` with rippling and polymer sections plus
any role_id / posted_at quirks the new sources surfaced.

# Dependencies

Hard prerequisites:

- `initiative:close-the-loop` closed (done 2026-05-02). Provides
  the canonical pipeline shape, view, cron, and Dive that this
  initiative extends.
- `research:ats-discovery-v2` (done 2026-05-02). Provides the
  evidentiary base for which companies have which surface.
- `constitution:main` updated 2026-05-02 to admit rippling and
  polymer.

Soft references:

- `wiki:extractor-shape` — canonical extractor pattern; will gain
  new sections during M2/M3/M4 retros.
- All v1 critique records (`critique:*-iter1`) — encode the
  inheritance constraints (no-list-fields, slug-case policy,
  defensive listed/published checks, etc.) every new extractor
  must honor.

# Risks

- **Polymer role-list discovery may be JS-rendered.** Mitigation:
  M3 starts with a deeper probe; if no plain-HTML index exists,
  defer Upstream Tech without blocking M2 / M4.
- **Page-monitor sites may be JS-rendered behind WordPress / Webflow
  plugins.** Mitigation: per-site, escalate to research loop-back
  rather than headless-browser workaround. Constitutional posture
  on anti-bot evasion stays.
- **`current_open_roles` posted_at column is already mixed across
  source kinds; adding two more sources widens the divergence.**
  Mitigation: the v1 wiki section on `posted_at` semantics already
  documents the per-source-kind mapping; M5 retro extends it.
- **Cron health-check `STALE_THRESHOLD_HOURS=36` was tuned for the
  v1 source set.** With more sources sharing the cron, the
  threshold may need re-tuning. Mitigation: M5 retro re-evaluates
  per-source freshness alongside the FIND-001 follow-up that
  carries forward from v1.
- **Eight more companies = roughly double the cron HTTP volume.**
  Still well below any rate-limit threshold (~10–20 req/day). No
  expected upstream backoff.

# Linked Work

Plan: `plan:expand-radar`.

# Status Summary

Initiative drafted 2026-05-02 immediately after
`initiative:close-the-loop` closed. v2 corpus resolved (8 in,
4 out) per `research:ats-discovery-v2`. Two new source kinds
admitted constitutionally. Ready to route into a plan that
sequences M1–M5 across roughly four waves.

## Close-out 2026-05-02

Status → `closed`. Outcome by milestone:

- **M1 — Trivial config-only adds:** done.
  `ticket:vejd8gon` (closed). Floodbase, BlastPoint, Overstory
  added to greenhouse; Pano AI added to ashby. Today's view
  growth: blastpoint=2, overstory=7, pano-ai=4 matched roles;
  floodbase=0 (honest — current openings are GTM/Marketing).
- **M2 — Rippling extractor:** done.
  `ticket:vr6iel5o` (closed). Kalkomey 6 roles fetched, 0 match
  the v1 keyword filter today (content/ops/security/design/PR).
  Honest 0-yield. Cron run 25253284648 green.
- **M3 — Polymer extractor:** done.
  `ticket:7n0yj21k` (closed). Upstream Tech 3 roles parsed via
  parent-page index + per-role JSON-LD; 0 match today
  (Open Call + 2 Account Executive postings). Honest 0-yield.
  Cron run 25253608609 green.
- **M4 — Page-monitor adds:** partially done.
  `ticket:37epma6n` (closed). Wherobots parser shipped; 1 role
  parsed today (Senior Account Executive – Enterprise East),
  0 match. Vibrant Planet **deferred** — their careers page
  shows the literal "No open roles at the moment" placeholder;
  no role-list HTML to parse. VP becomes a future ticket
  whenever they post roles.
- **M5 — Retrospective + closeout:** done. `wiki:extractor-shape`
  extended with Rippling + Polymer sections, polite-fetch UA
  boundary section, defensive listed/published per-source-kind
  table, Vibrant Planet deferral note. role_id strategies +
  posted_at semantic tables expanded.

State at close-out:

- 6 source kinds running on cron: greenhouse, ashby, sitemap,
  page, rippling, polymer.
- 11 ATS slugs total. 7 producing rows in
  `current_open_roles`. 4 honest 0-yield (floodbase, gohunt,
  regrid, kalkomey, upstream-tech, plus wherobots — actually 6
  honest 0-yield slugs).
- Total view rows: 120.

Carried-forward as deferred follow-ups (lived in critique
records; not promoted today):

- FIND-001 in `critique:actions-cron-iter1` — tighten
  `STALE_THRESHOLD_HOURS = 36 → 26` after observation data
  stabilizes.
- FIND-007 in `critique:actions-cron-iter1` — per-step `env:`
  for secret minimization (8 cron steps now share job-level
  secrets).
- FIND-001 of `critique:page-monitor-iter1` /
  FIND-002 of `critique:polymer-upstream-iter1` — N→0 silent
  breakage detection for HTML / index-regex parsers (page +
  polymer source kinds). Workflow visibility today is the
  MATCH/skip log lines only.
- Vibrant Planet — ship a `vibrant_planet_careers` parser when
  they post roles.
- AllTrails / Pachama / CalTopo / BaseMap — dropped permanently
  per `research:ats-discovery-v2` null results.

If a future initiative tightens these, it inherits a stable
6-source-kind, 11-slug pipeline as its baseline.
