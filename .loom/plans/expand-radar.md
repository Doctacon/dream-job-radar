---
id: plan:expand-radar
kind: plan
status: active
created_at: 2026-05-02T13:13:30Z
updated_at: 2026-05-02T13:13:30Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:expand-radar
  constitution: constitution:main
  research:
    - research:ats-discovery-v2
  decisions:
    - decision:0001-storage-backend-r2
  predecessor: plan:v1-radar
---

# Purpose

Sequence the execution of `initiative:expand-radar`: add eight new
mission-aligned companies to the radar. Reuse the v1 pipeline
shape, the cron, the view, and the Dive without modification where
possible; only introduce new code paths for the two new source
kinds (`rippling`, `polymer`).

This plan owns the route from "research:ats-discovery-v2 lands"
through "all eight new companies are visible in the daily Dive."

# Strategy

Order waves by marginal cost. Trivial config-only adds first
(Wave 1, four companies) so the initiative shows immediate value
even if a later wave hits a research loop-back. New source kinds
next, ordered by clarity of the upstream API: Rippling first
(clean public JSON list) then Polymer (JSON-LD per role, but
role-list discovery still TBD). Page-monitor adds last because
they are the most fragile.

The v1 retrospective produced a stable canonical contract
(`wiki:extractor-shape`); every wave inherits that contract and
adds inheritance-shaped notes (a wiki section per new source kind)
during its retrospective.

# Strategy Snapshot

v1 ships a working pipeline (4 source kinds, 6 companies, 104
roles), cron, view, and mobile-friendly Dive. R2 destination, dlt
project layout, and Loom records are all stable. No infra-prep
wave is needed for this initiative; we go straight from research
into extractor work.

# Workstreams

## Extractors

- Greenhouse: extend `DEFAULT_BOARDS` (Floodbase, BlastPoint,
  Overstory).
- Ashby: extend `DEFAULT_BOARDS` (Pano AI).
- **Rippling (new):** new resource factory + pipeline mirroring
  the Ashby/Wave 2 #2 shape.
- **Polymer (new):** new resource factory + pipeline; per-role
  JSON-LD parser; role-list discovery TBD during the wave.
- Page-monitor: extend `DEFAULT_SITES` and add per-site parser
  strategies for Vibrant Planet and Wherobots.

## View / cron / Dive

No expected changes. The view glob (`raw/*/*/*.parquet`) absorbs
new source kinds without DDL change. The cron meta-runner gains
two new chained pipeline calls. The Dive's queries are
source-kind-agnostic.

If a wave surfaces a real schema-drift issue, the view's
NOT-NULL guards (added in v1 Wave 2 #2 retro) catch it; loopback
to retrospective.

## Documentation

`wiki:extractor-shape` gains a section per new source kind during
each wave's retrospective. README's source-coverage table grows
by one row per new company.

# Milestones

## PM1 — M1 trivial adds shipped

Floodbase + BlastPoint + Overstory + Pano AI all writing Parquet
to R2; visible in `current_open_roles`. One ticket.

## PM2 — Rippling extractor shipped

Kalkomey writing Parquet under `raw/rippling/kalkomey/`. New
extractor + pipeline + `wiki:extractor-shape` section. One ticket.

## PM3 — Polymer extractor shipped

Upstream Tech writing Parquet under `raw/polymer/upstream-tech/`.
New extractor + pipeline + wiki section. One ticket; deferable if
role-list discovery requires JS rendering.

## PM4 — Page-monitor adds shipped

Vibrant Planet + Wherobots writing Parquet under
`raw/page/vibrant-planet/` and `raw/page/wherobots/`. Existing
page-monitor extractor extended; per-site parsers added. One
ticket; either company deferable per-site if JS-rendered.

## PM5 — Retrospective + closeout

`wiki:extractor-shape` reflects all four new source-kind / parser
notes. Cron continues green. Dive renders the expanded set cleanly
on mobile. Initiative closes.

These map onto initiative milestones as: PM1 = M1, PM2 = M2,
PM3 = M3, PM4 = M4, PM5 = M5.

# Sequencing

PM1 first because it is config-only and proves the inheritance
shape works at the new scale (8 companies → ~150 roles
expected). PM2 second because Rippling is the cleanest new API
and the lowest-risk new source kind. PM3 third because Polymer's
role-list discovery is the only real research-risk in this
initiative. PM4 last because page-monitor sites are inherently
the most fragile.

PM2 / PM3 / PM4 are independent of each other (separate
extractors, separate dataset_names, separate R2 prefixes) and
could run in parallel if the user prefers — but a single agent
running them sequentially is the default.

PM5 retrospective happens after the last successful wave, not
per-wave (per-wave retros happen inside each ticket close-out as
in v1).

# Execution Waves

## Wave 1 — Trivial config-only adds

Sequential, single ticket.

- `ticket:vejd8gon` — Extend `DEFAULT_BOARDS` for Greenhouse
  (Floodbase, BlastPoint, Overstory) and Ashby (Pano AI).
  Status: `closed` (2026-05-02). Adds 13 new view rows
  (blastpoint=2, overstory=7, pano-ai=4; floodbase=0 honest).
  Total view rows now 120.

## Wave 2 — Rippling extractor (Kalkomey)

Sequential, single ticket.

- `ticket:vr6iel5o` — Build `extractors/rippling.py` +
  `pipelines/rippling.py`, chain into meta-runner, extend
  workflow. Status: `closed` (2026-05-02). Kalkomey 6 roles, 0
  match the v1 keyword filter today (honest 0-yield). Manual
  workflow dispatch on new shape green
  (run 25253284648). Wiki updates for FIND-001/002/003 deferred
  to PM5 retro.

## Wave 3 — Polymer extractor (Upstream Tech)

Sequential, single ticket. Research-loopback-prone.

- `ticket:7n0yj21k` — Build `extractors/polymer.py` (SiteSpec with
  index regex + role URL template) + `pipelines/polymer.py`,
  chain into meta-runner, extend workflow. Status: `closed`
  (2026-05-02). Index discovery from parent careers page resolved
  3 role IDs; 0 match keyword filter today. Manual workflow
  dispatch green (run 25253608609). Wiki updates deferred to PM5
  retro.

## Wave 4 — Page-monitor adds (Vibrant Planet + Wherobots)

Sequential, single ticket; per-company-deferable.

- `ticket:<TBD>` — Extend `extractors/page.py` with two new
  per-site parsers + `DEFAULT_SITES` entries. Critique
  recommended. Posture: observation-first. If either site is
  JS-rendered, defer that company without blocking the other.

# Risks

- **Polymer role-list discovery** (mirrored from initiative). Wave 3
  starts with a probe; if no plain-HTML index, defer Upstream Tech.
- **Page-monitor JS-rendering** on Webflow / WordPress. Wave 4
  starts with a probe; defer per-company if blocked.
- **Wave 1 doubles the cron's HTTP volume.** Negligible at this
  scale; no expected throttling.
- **Health-check threshold** (`STALE_THRESHOLD_HOURS=36`) was tuned
  for v1's source set. PM5 retro re-evaluates.

# Evidence Strategy

- Wave 1: observation-first. Evidence is per-slug counts in
  `current_open_roles` after a manual run.
- Wave 2: observation-first. Evidence is the new R2 prefix
  populated + Kalkomey rows in the view.
- Wave 3: observation-first AFTER the discovery probe succeeds. If
  the probe surfaces a JS-rendering blocker, the wave returns
  `escalate` without writing extractor code.
- Wave 4: observation-first per company. Evidence is per-site
  parsed-N + matched-titles per the page-monitor MATCH/skip log
  convention.

Critique disposition: `recommended` on Wave 2 / 3 / 4 (each
introduces or extends source-kind coverage). `optional` on Wave 1
(config-only, low risk).

# Plan Readiness Review

Spec / acceptance coverage:

- No separate spec exists. Acceptance criteria stay ticket-local.
- The `current_open_roles` column contract is fixed by v1 and
  documented in `wiki:extractor-shape`; new extractors must honor
  it (no list values, slug-case policy, etc.).

Placeholder scan:

- Ticket IDs are `<TBD>` because tickets do not exist yet. Filled
  when each ticket is created.
- No `TODO` or "handle edge cases" placeholders in the work
  itself.

Ticket-sized slices:

- Wave 1 = 1 ticket. Waves 2 / 3 / 4 = 1 ticket each.

Likely write scopes:

- Wave 1: `extractors/greenhouse.py`, `extractors/ashby.py`,
  `README.md`.
- Wave 2: `extractors/rippling.py`,
  `pipelines/rippling.py`,
  `pipelines/radar.py` (chain),
  `README.md`,
  `.loom/wiki/extractor-shape.md` (during retro).
- Wave 3: `extractors/polymer.py`,
  `pipelines/polymer.py`,
  `pipelines/radar.py` (chain),
  `README.md`,
  `.loom/wiki/extractor-shape.md` (during retro).
- Wave 4: `extractors/page.py`,
  `README.md`,
  `.loom/wiki/extractor-shape.md` (during retro).

Likely verification posture: observation-first throughout.

Stop / loopback conditions:

- Wave 3: if Polymer role-list discovery requires JS, escalate to
  research and consider deferring Upstream Tech to a future
  initiative.
- Wave 4: if either Webflow / WordPress site is JS-rendered,
  escalate per-company and defer without blocking the rest.
- Any wave: if the canonical-row contract or view DDL would need
  to change, escalate to retrospective rather than mutating
  silently.

# Exit Criteria

- All eight in-scope companies have written Parquet to R2 at
  least once and are visible in `current_open_roles` (or
  explicitly deferred with a documented reason).
- The cron `refresh.yml` continues to succeed end-to-end.
- The Dive renders the expanded set cleanly on mobile.
- `wiki:extractor-shape` covers all six source kinds (greenhouse,
  ashby, sitemap, page, rippling, polymer) plus role_id /
  posted_at quirks per source.
- Initiative milestones M1–M5 closed.
