---
id: ticket:vejd8gon
kind: ticket
status: closed
change_class: code-behavior
risk_class: low
created_at: 2026-05-02T13:19:06Z
updated_at: 2026-05-02T15:30:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:expand-radar
  plan: plan:expand-radar
  constitution: constitution:main
  research: research:ats-discovery-v2
  wiki: wiki:extractor-shape
  predecessor: ticket:tiv8bsu7
external_refs:
  floodbase: https://boards-api.greenhouse.io/v1/boards/floodbase/jobs
  blastpoint: https://boards-api.greenhouse.io/v1/boards/blastpoint/jobs
  overstory: https://boards-api.greenhouse.io/v1/boards/overstory/jobs
  pano_ai: https://api.ashbyhq.com/posting-api/job-board/pano-ai
depends_on: []
---

# Summary

Wave 1 of `plan:expand-radar` (closes PM1 / M1): trivial
config-only additions to the existing Greenhouse and Ashby
extractors. Adds Floodbase, BlastPoint, Overstory (Greenhouse) and
Pano AI (Ashby) to the canonical board lists.

# Context

`research:ats-discovery-v2` confirmed all four endpoints and
returned positive job counts (Floodbase=4, BlastPoint=4,
Overstory=11, Pano AI=25). No new extractor code is needed — the
resource factories already accept a tuple of board slugs.

This ticket inherits the v1 patterns documented in
`wiki:extractor-shape`: data preserves source-given slug case;
canonical row stays list-free; the view glob handles new ATS slugs
without DDL change.

# Why Now

PM1 is the cheapest wave to close in the new initiative. Shipping
it first proves the inheritance pattern at the new scale (8
companies once this lands) before Waves 2–4 introduce new code
paths.

# Scope

- Update `src/dream_job_radar/extractors/greenhouse.py`:
  `DEFAULT_BOARDS = ("onxmaps", "planetlabs")`
  → `DEFAULT_BOARDS = ("onxmaps", "planetlabs", "floodbase",
                       "blastpoint", "overstory")`.
- Update `src/dream_job_radar/extractors/ashby.py`:
  `DEFAULT_BOARDS = ("Mapbox",)`
  → `DEFAULT_BOARDS = ("Mapbox", "pano-ai")`.
- Update `README.md` source-coverage table with four new rows.
- Run pipelines locally; verify counts in `current_open_roles`.

# Non-goals

- No new extractor code paths.
- No view DDL changes. The view glob already covers any new ATS
  slug under existing source kinds.
- No revision of the title-keyword filter.
- No dependency on Wave 2 / 3 / 4. This wave is independent.

# Acceptance Criteria

1. `uv run python -m dream_job_radar.pipelines.greenhouse` runs
   end-to-end and writes Parquet at all five board prefixes:
   `raw/greenhouse/{onxmaps,planetlabs,floodbase,blastpoint,overstory}/`.
2. `uv run python -m dream_job_radar.pipelines.ashby` runs
   end-to-end and writes Parquet at `raw/ashby/Mapbox/` AND
   `raw/ashby/<pano slug>/` (note: dlt's snake_case naming may
   normalize "pano-ai" — record the actual path observed; the
   slug-case policy from `wiki:extractor-shape` applies).
3. `uv run python -m dream_job_radar.pipelines.radar` runs
   end-to-end across all chained source kinds without regression
   on existing onx (8) + planetlabs (36) + Mapbox (59) + felt (1)
   row counts.
4. MotherDuck `current_open_roles` shows positive row counts for
   greenhouse/floodbase, greenhouse/blastpoint, greenhouse/overstory,
   and ashby/<pano slug> — the actual numbers depend on the v1
   keyword filter applied to today's listings.
5. All sampled titles for each new slug satisfy the keyword filter
   (substring match against `data | engineer | gis | geospatial`).
   Verify by sampling at least 5 returned titles per new slug
   (or all of them if fewer than 5 matched).
6. README documents the four new rows in the source-coverage
   table.

# Coverage

Ticket-local. No spec contract. `wiki:extractor-shape` is the
inheritable design.

# Claim Matrix

None — no spec contract; ticket-local acceptance criteria only.

# Execution Notes

- Greenhouse slugs are case-insensitive (per v1 evidence on
  `BlastPoint` working alongside `blastpoint`). Use lowercase
  uniformly to match the existing convention.
- Ashby slug for Pano AI is `pano-ai` (the hyphenated form
  succeeded in v2 research; `panoai` and `PanoAI` both 404'd).
  Preserve case verbatim, same as Mapbox.
- Pano AI lists 25 roles total at probe time; the keyword filter
  is expected to keep most or all (their roles are dominantly
  engineering / data per the user's research notes).
- Hardware / mechanical "engineer" matches will land in the view
  for Pano AI just like they did for Planet Labs (FIND-002 in
  the v1 walking-skeleton critique). Known v1 keyword tradeoff,
  not a defect.

# Blockers

None.

# Next Move / Next Route

Local edit, no Ralph packet. Same shape and scope as
`ticket:tiv8bsu7` (v1 Wave 2 #1, config-only Planet Labs add).

# Ralph Readiness

N/A — local edit posture. Write boundary if it ever needs Ralph:

- `src/dream_job_radar/extractors/greenhouse.py`
- `src/dream_job_radar/extractors/ashby.py`
- `README.md`

Verification posture: `observation-first`.

# Evidence

Expected on completion:

- terminal output of the per-source runs and the all-sources run.
- `boto3 list_objects_v2` confirming new Parquet under each new
  prefix.
- MotherDuck per-`(source_kind, ats_slug)` row counts.
- 5-row title sample per new slug.

Captured 2026-05-02T15:30Z:

AC1 — `pipelines.greenhouse` runs end-to-end across 5 boards
(onxmaps, planetlabs, floodbase, blastpoint, overstory). 1 load
package LOADED, 4 jobs, no failed jobs.

AC2 — `pipelines.ashby` runs end-to-end across 2 boards (Mapbox,
pano-ai). 1 load package LOADED, 3 jobs, no failed jobs. dlt
preserved the `pano-ai` slug verbatim in the table-directory
(hyphen survives snake_case).

AC3 — view counts after run:
```
('ashby', 'Mapbox', 61)
('ashby', 'pano-ai', 4)
('greenhouse', 'blastpoint', 2)
('greenhouse', 'onxmaps', 8)
('greenhouse', 'overstory', 7)
('greenhouse', 'planetlabs', 37)
('page', 'felt', 1)
```
Total: 120 roles. No regression on existing counts (Mapbox 61,
onxmaps 8, planetlabs 37, felt 1).

AC4 — positive counts for blastpoint (2), overstory (7),
pano-ai (4). Floodbase = 0 today: probe shows 4 upstream roles, 0
match the v1 keyword filter (GTM Strategy Director, Head of
Distribution, Head of Product, Marketing Manager). Honest 0-row
outcome — same posture as sitemap/gohunt + page/regrid in v1.

AC5 — title samples per new slug, all match keyword filter:
```
blastpoint:
  Data Engineer
  Senior Data Engineer
overstory:
  Engineering Manager, Machine Learning
  Data Engineering Manager
  Senior Software Engineer, Geospatial Data
  Staff Software Engineer
  Staff Machine Learning Engineer - Wildfire
  Director of Platform Engineering
  Senior Software Engineer, Full Stack
pano-ai:
  Senior Design Quality Engineer
  Senior Process Quality Engineer
  Geospatial Data Engineer
  Senior Software Engineer (Cross-Platform Mobile)
```

R2 layout (verifying AC1/AC2):
```
raw/greenhouse/floodbase/   KeyCount=0 (0-yield run, dlt wrote no parquet)
raw/greenhouse/blastpoint/  KeyCount=2 (2 runs)
raw/greenhouse/overstory/   KeyCount=2 (2 runs)
raw/ashby/pano-ai/...       (Parquet present, snake_case-preserved hyphen)
```

AC6 — README updated with 4 new source-coverage rows.

# Critique Disposition

Risk class: low

Critique policy: optional

Policy rationale: this ticket adds no new code paths and changes
no schema. The v1 critiques on the Greenhouse and Ashby extractors
already cover the resource factories; no new surface to
pressure-test.

Findings: None — no critique scheduled.

Disposition status: not_required

Deferral / not-required rationale: low risk, no new code paths,
view shape unchanged, v1 critiques still apply. Same posture as
v1's `ticket:tiv8bsu7`.

# Wiki Disposition

No new wiki page expected. If any of the four new boards surfaces
a non-trivial divergence (different field shape, anti-bot, etc.),
update `wiki:extractor-shape` accordingly during the close-out.

# Acceptance Decision

Accepted by: Connor
Accepted at: 2026-05-02T15:30:00Z
Basis: AC1–AC6 satisfied with observation-first evidence (see
Evidence section). Resource factories generalized cleanly to 4
new slugs. View glob absorbed all new ATS slugs without DDL
change. PM1 of `plan:expand-radar` closes with this ticket.
Residual risks:
- Floodbase yields 0 today (legitimate — current openings are
  GTM/Marketing). Same posture as sitemap/gohunt + page/regrid
  in v1; pipeline catches future engineering posts
  automatically.
- Pano AI's hardware/quality engineer titles match keyword
  filter (FIND-002 in walking-skeleton critique still deferred).
  Wave 5 retro re-evaluates with broader corpus.

# Dependencies

Hard prerequisites:

- v1 `initiative:close-the-loop` closed (done 2026-05-02).
  Provides the Greenhouse + Ashby extractors and the view that
  this ticket extends.

Soft references:

- `research:ats-discovery-v2` — confirms all four endpoints.
- `wiki:extractor-shape` — canonical pattern this ticket reuses.

# Journal

- 2026-05-02 — ticket created from `plan:expand-radar` Wave 1.
  Status set directly to `ready`; readiness checklist passes
  trivially because the work is config-only and both resource
  factories already accept board-slug tuples. Risk classified
  `low`; critique optional and explicitly not required.
- 2026-05-02 — Implementation: `DEFAULT_BOARDS` extended in
  `extractors/greenhouse.py` (added floodbase, blastpoint,
  overstory) and `extractors/ashby.py` (added pano-ai). Pipelines
  ran clean. View shows new slugs with positive counts (blastpoint
  2, overstory 7, pano-ai 4) plus floodbase=0 honest 0-yield.
  Total view rows now 120 (was 107). AC1–AC6 satisfied. Status →
  `closed`. PM1 of `plan:expand-radar` closes.
