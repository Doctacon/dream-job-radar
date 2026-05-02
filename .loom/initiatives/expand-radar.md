---
id: initiative:expand-radar
kind: initiative
status: active
created_at: 2026-05-02T13:13:30Z
updated_at: 2026-05-02T13:13:30Z
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
