---
id: initiative:close-the-loop
kind: initiative
status: closed
created_at: 2026-04-29T14:17:56Z
updated_at: 2026-05-02T12:56:43Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  constitution: constitution:main
  research:
    - research:ats-discovery
    - research:storage-backend
  decisions:
    - decision:0001-storage-backend-r2
  plans:
    - plan:v1-radar
---

# Objective

Close the loop on `found role → tracked role → applied to role` for a
curated set of dream-fit companies, so a top-three role does not slip past
unnoticed between scheduled checks.

The end-state surface is a live MotherDuck Dive over an R2-backed dataset
of recently-seen open roles, refreshed on a GitHub Actions schedule.

# Why Now

A real top-fit role surfaced via a chat agent during a casual walk and would
otherwise have been missed. That single event proved the discovery gap is
real and that the current "happen to look at the right careers page on the
right day" pattern is unreliable. The pipeline shape is small, the
surrounding tooling (dlt, R2, MotherDuck, GitHub Actions) is already
familiar, and the project doubles as a public artifact on
`loughondata.com`.

# In Scope

- dlt pipeline against free, programmatic endpoints for a curated company
  list (Greenhouse API, Lever API, or polite HTML page monitors)
- title-keyword filter for data/geospatial roles
- Cloudflare R2 as the system of record
- MotherDuck reading R2 natively
- a Dive that lists open roles with links and last-seen timestamps
- GitHub Actions schedule for refresh
- a follow-up blog post on `loughondata.com` documenting the build

## v1 Curated Company List

| Company       | Source            | Endpoint                                                                  | Status    |
| ------------- | ----------------- | ------------------------------------------------------------------------- | --------- |
| onX           | Greenhouse        | `boards-api.greenhouse.io/v1/boards/onxmaps/jobs`                         | confirmed |
| Planet Labs   | Greenhouse        | `boards-api.greenhouse.io/v1/boards/planetlabs/jobs`                      | confirmed |
| Mapbox        | Ashby             | `api.ashbyhq.com/posting-api/job-board/Mapbox`                            | confirmed |
| Regrid        | Page monitor      | `regrid.com/careers`                                                      | confirmed |
| Felt          | Page monitor      | `felt.com/careers` (client-rendered; diff for "Open role" blocks)         | confirmed |
| GoHunt        | Sitemap monitor   | `gohunt.com/sitemap.xml`, filter `*job-opportunity*` under news-and-updates | confirmed |
| Spartan Forge | (none found)      | dropped from v1 — no public careers surface                               | dropped   |

All v1 entries resolved. See `research:ats-discovery` for method and
evidence.

## v1 Title Keywords

Match if the role title contains any of:

- `data`
- `engineer`
- `GIS`
- `geospatial`

Case-insensitive. Combinations like "data engineer" or "GIS analyst" both
match. Filtering happens in the dlt pipeline before write to R2.

# Out Of Scope

- ATS providers requiring auth or paid access (Workday, Ashby, gated career
  sites)
- LinkedIn job alerts (no free programmatic pull)
- heuristic discovery of new companies; the list stays curated
- public surfacing of which roles the author actually applies to
- any custom front end as the canonical surface (the Dive is canonical)
- offline-first behavior beyond what a normal web page already provides
- a paid MotherDuck plan upgrade purely to unlock embed

# Success Metrics

- a new open role at a curated company appears on the live Dive within one
  schedule cycle of being posted on Greenhouse
- the Dive is shareable via a stable URL
- the GitHub Actions pipeline runs end-to-end on schedule without manual
  intervention for at least one full week
- a Part Two blog post is published linking to (or embedding) the live Dive

# Milestones

## M1 — Pipeline lands data in R2

dlt run against the curated Greenhouse company list writes filtered open
roles to a known R2 prefix, manually invoked.

## M2 — MotherDuck queries R2 directly

MotherDuck workspace reads the R2 prefix via its native R2 secret and
exposes the `current_open_roles` view.

## M3 — Dive ships

A Dive over the MotherDuck view lists roles, links, and last-seen
timestamps. Reachable via a stable URL.

## M4 — Scheduled refresh

GitHub Actions runs the dlt pipeline on a recurring schedule. Dive reflects
fresh data each cycle.

## M5 — Blog post live

Part Two post on `loughondata.com` links to the Dive. If iframe embed is
supported on the personal MotherDuck plan, the Dive is embedded; otherwise
linked.

## M6 — Apply-loop tracking (later phase)

Private surface tracks application status against roles seen by the radar.
Out of band from public Dive.

# Dependencies

- Greenhouse public API stays stable and unauthenticated for the curated
  companies
- Personal Cloudflare account with R2 enabled
- Personal MotherDuck account on the free / personal plan
- `loughondata.com` (Hugo + Blowfish) for the blog post and optional embed
- GitHub Actions minutes on the project repo

# Risks

- **MotherDuck Dive iframe embedding** may be unavailable on the personal
  plan. Mitigation: Dive remains the canonical surface; blog post links to
  it instead of embedding. No plan upgrade.
- **Greenhouse company-board format drift** may break per-company ingestion.
  Mitigation: dlt schema evolution + per-company error isolation so one
  broken board does not block the run.
- **Curated list rot**: target companies stop posting on Greenhouse or
  switch ATS. Mitigation: occasional manual list audit; out-of-scope ATS
  providers stay out of scope until v1 ships.
- **Scope creep into a job-board product.** Mitigation: constitution
  constrains scope to a personal radar over a curated list.

# Linked Work

- `research:ats-discovery` — confirmed source kind for each company (Ashby
  and sitemap-monitor surfaced as new admitted source kinds; Spartan Forge
  dropped).
- `plan:v1-radar` — sequences M1–M5 across four extractor kinds in four
  execution waves.

Tickets will be created beneath `plan:v1-radar`.

# Status Summary

Initiative drafted 2026-04-29 alongside Loom bootstrap and constitution.
v1 curated company list resolved (6 sources confirmed across Greenhouse,
Ashby, page monitor, sitemap monitor; Spartan Forge dropped). v1
title-keyword set defined. Ready to route into a plan that sequences
M1–M5 for the 6 confirmed sources.

## Close-out 2026-05-02

Status → `closed`. Outcome by milestone:

- **M1 — Pipeline lands data in R2:** done. dlt + boto3 against
  Cloudflare R2 in the `pipelines` bucket. Four extractor kinds
  shipped: greenhouse (onxmaps + planetlabs), ashby (Mapbox),
  sitemap (gohunt), page (regrid + felt).
- **M2 — MotherDuck queries R2 directly:** done.
  `current_open_roles` view reads `r2://pipelines/raw/*/*/*.parquet`
  via the MotherDuck-side R2 SECRET.
- **M3 — Dive ships:** done. Saved at
  `https://app.motherduck.com/dives/391d1329-70d7-4223-89c8-d0dfde66ef7f`.
  Mobile-friendly iteration shipped 2026-05-02 (clickable title
  links, location inline on phone, KPI grid responsive).
- **M4 — Scheduled refresh:** partially done. GitHub Actions cron
  `0 12 * * *` UTC live with per-source error isolation, idempotent
  view-apply, and per-(source_kind, ats_slug) freshness health
  check. Manual dispatch verified green. AC5 (first scheduled
  firing observed cleanly) and AC6 (one-week observation window)
  dropped from acceptance scope at close-out.
- **M5 — Blog post live:** **not done.** Wave 4 was cancelled at
  plan close-out. If/when a post is written, it lands under a
  fresh initiative.
- **M6 — Apply-loop tracking:** **not started.** Stays out of v1
  scope as originally framed. Belongs to a future initiative if
  pursued.

Carried forward as deferred follow-ups (lived in critique records;
not promoted to wiki or tickets at close-out, per user direction
to free up bandwidth):

- FIND-001 in `critique:actions-cron-iter1` — tighten
  `STALE_THRESHOLD_HOURS = 36 → 26` after observation data exists.
- FIND-002 in `critique:actions-cron-iter1` — wiki-promote the
  freshness-vs-row-count rationale that drove the health-check
  pivot.
- FIND-007 in `critique:actions-cron-iter1` — per-step `env:` to
  minimize secret exposure to third-party actions.
- 2026-05-02 R2-rotation incident — useful operational lesson
  (rotating R2 keys requires updating BOTH GH Actions secrets AND
  the MotherDuck-side R2 SECRET); not promoted to wiki today.

Total roles in `current_open_roles` at close-out: 104 (8 onxmaps +
36 planetlabs + 59 Mapbox + 0 gohunt + 0 regrid + 1 felt).
