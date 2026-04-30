---
id: plan:v1-radar
kind: plan
status: active
created_at: 2026-04-29T14:17:56Z
updated_at: 2026-04-29T23:35:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:close-the-loop
  constitution: constitution:main
  research:
    - research:ats-discovery
    - research:storage-backend
  decisions:
    - decision:0001-storage-backend-r2
---

# Purpose

Sequence the execution of `initiative:close-the-loop` v1: a dlt pipeline
landing data in a personal Cloudflare R2 bucket, queried by MotherDuck,
surfaced as a Dive, refreshed on a GitHub Actions schedule.

This plan owns the route from "Loom records exist" to "the Dive is live and
refreshing on schedule." It does not own live execution truth — that lives
in the tickets it spawns.

# Strategy

Walking-skeleton first. Build one end-to-end vertical (Greenhouse extractor
for onX → R2 → MotherDuck view → Dive) before adding any other extractor
kind. Once the skeleton works manually, add the remaining three extractor
kinds in parallel because they each write to independent R2 prefixes and
contribute independent dlt resources. Then wire the GitHub Actions
schedule. Blog post lands last.

This ordering keeps the highest-uncertainty integration risks (R2 perms,
MotherDuck R2 read, Dive over MotherDuck view, iframe vs link surface) in
front. Once those are settled, the remaining work is incremental
extractor-by-extractor.

# Strategy Snapshot

Repo is empty. No code yet. Loom records exist (constitution, initiative,
research, decision, this plan). Personal Cloudflare account (R2 enabled)
and MotherDuck personal-plan account are assumed available; explicit
verification is the first slice.

# Workstreams

## Infra

R2 bucket, R2 API token (S3-compatible access key + secret), MotherDuck
workspace with R2 secret configured, GitHub repo with Actions secrets.

## Extractors

Per source kind:

- Greenhouse API (covers onX, Planet Labs)
- Ashby API (covers Mapbox)
- Page monitor (covers Regrid, Felt)
- Sitemap monitor (covers GoHunt)

Each extractor is one dlt resource family, reading from a config-driven
list of companies for that kind.

## Storage layout

R2 prefix per source kind, dlt-managed schema, append semantics with a
`first_seen_at` / `last_seen_at` derivation in MotherDuck.

## Surface

MotherDuck view that unions across R2 prefixes into a single
`current_open_roles` shape, then a Dive over that view.

## Scheduling

GitHub Actions cron + R2 creds + dlt run. Failure isolation per
company.

## Documentation

Part-two blog post on `loughondata.com`.

# Milestones

## PM1 — Walking skeleton ships

One Greenhouse extractor (onX) lands data in R2, MotherDuck reads it, a
Dive renders the title-keyword-filtered open roles. Reachable at a stable
MotherDuck Dive URL.

## PM2 — All four extractor kinds running

Greenhouse, Ashby, page monitor, sitemap monitor each write to R2 for
their assigned companies. MotherDuck view unions them. Dive covers all
six companies.

## PM3 — Scheduled refresh

GitHub Actions runs the pipeline on cron. One full week of clean
unattended runs.

## PM4 — Part-two post live

Blog post on `loughondata.com` links to the Dive. (Iframe embed is a
business-plan-only MotherDuck feature; this project is on the free
plan, so embed is closed by policy.)

These map onto initiative milestones as: PM1 ⊆ M1+M2+M3 (for one source);
PM2 = M1+M2+M3 broadened; PM3 = M4; PM4 = M5.

# Sequencing

PM1 first because every later step depends on having a working
R2-to-Dive path. The walking skeleton answers the four high-uncertainty
questions in one slice:

1. Does R2 + dlt write what we expect?
2. Does MotherDuck read our R2 prefix natively?
3. Does a Dive over a MotherDuck view render usefully?
4. Is iframe embed available, or do we link?

Once PM1 is true, PM2's three remaining extractor kinds are independent
(separate companies, separate R2 prefixes, separate dlt resources, no
shared lockfiles beyond `pyproject.toml`/`uv.lock`). They run in parallel.

PM3 is deferred until PM2 is stable because scheduling a broken pipeline
just produces scheduled noise.

PM4 is last because the post is documentation of a working thing, not a
forcing function for the work itself.

# Execution Waves

## Wave 0 — Infra prep

Sequential, single ticket.

- `ticket:9mtt9h6j` — Provision R2 bucket, R2 API token, MotherDuck
  workspace with R2 secret, uv-managed Python project, GitHub repo,
  Actions secrets. Verifies all
  credentials end-to-end. Likely write scope: new repo bootstrap files
  only; no extractor code yet. Status: `closed` (2026-04-29).

## Wave 1 — Walking skeleton (Greenhouse: onX)

Sequential, single ticket.

- `ticket:gjkpkpum` — dlt Greenhouse extractor for onX → R2 → MotherDuck
  view → Dive. Title-keyword filter applied in dlt. Manual run only.
  Posture: observation-first (proves data lands, view queries, Dive
  renders). Closes PM1. Status: `closed` (2026-04-29). Dive at
  `https://app.motherduck.com/dives/391d1329-70d7-4223-89c8-d0dfde66ef7f`.

## Wave 2 — Remaining extractor kinds (parallel)

Three independent tickets. No shared write scope beyond `pyproject.toml`
and `uv.lock`. Coordinate by sequencing dependency adds, not by
sequencing the extractor code.

**Inherited pattern from Wave 1 (accepted 2026-04-29):** each
extractor kind runs as its own dlt pipeline with
`dataset_name = <source_kind>` and
`bucket_url = s3://<bucket>/raw`. dlt's filesystem destination always
prefixes `<dataset_name>/` under `bucket_url`, so this is what makes
the observable layout `r2://<bucket>/raw/<source_kind>/<ats_slug>/`
true. The `current_open_roles` view globs
`r2://<bucket>/raw/*/*/*.parquet` and is invariant under new
source kinds. dlt system tables (`_dlt_loads`, `_dlt_pipeline_state`,
`_dlt_version`) live at `raw/<source_kind>/` and are excluded by the
view's `WHERE filename NOT LIKE '%/_dlt_%'` filter.

- `ticket:tiv8bsu7` — Greenhouse extractor extended to Planet Labs
  (config-only addition; trivial reuse of Wave 1 resource). Status:
  `closed` (2026-04-30). 36 roles landed at
  `r2://pipelines/raw/greenhouse/planetlabs/`.
- `ticket:oy172mt9` — Ashby extractor for Mapbox. Status: `closed`
  (2026-04-30). 59 roles landed at `r2://pipelines/raw/ashby/mapbox/`
  (dlt lowercased the path; ats_slug data preserves `Mapbox`).
  Iteration surfaced a list-fields-create-child-table bug; canonical
  shape now forbids Python list values. View hardened with
  NOT NULL guards on dedup partition keys.
- `ticket:<TBD>` — Page monitor extractor for Regrid + Felt (one dlt
  resource that polls HTML and emits role records).
- `ticket:xwfvoj4o` — Sitemap monitor extractor for GoHunt
  (sitemap.xml + per-URL JSON-LD parse). Status: `closed`
  (2026-04-30). 4 sitemap URLs fetched, all skipped by keyword
  filter (truthful 0-match outcome — retail/media roles only
  today). Pipeline catches future data/engineer/GIS/geospatial
  posts automatically.

After Wave 2 returns, parent reconciles: integration test that the
MotherDuck view unions all four prefixes correctly. Closes PM2.

## Wave 3 — Schedule

Sequential, single ticket.

- `ticket:<TBD>` — GitHub Actions cron + R2 creds + dlt run, with
  per-company error isolation so one broken board does not fail the
  run. One-week observation period. Closes PM3.

## Wave 4 — Blog post

Sequential, single ticket.

- `ticket:<TBD>` — Part-two post on `loughondata.com`, link or embed
  the Dive. Closes PM4.

# Risks

- **Sitemap monitor is heavier than other extractors.** GoHunt requires
  fetching each new sitemap URL and parsing the resulting blog post for
  title and posting date. Mitigation: keep it isolated in Wave 2 so it
  cannot block the other three extractor tickets, and accept that this
  ticket may need to spawn sub-iterations.
- **dlt + R2 + MotherDuck integration may have quirks.** Mitigation: Wave
  1 walking skeleton exists specifically to surface them early.
- **Page monitor on Felt may be too dynamic.** Felt's careers page had
  one "Open role" block; if listings move to a JS-rendered surface, the
  page monitor needs a headless browser. Mitigation: try plain HTML
  first; escalate to research if it fails.
- **Iframe embed unavailable on free plan (confirmed 2026-04-29).**
  Business-plan-only feature. Per constitution, this is a bonus
  surface, not a blocker. PM4 links to the Dive instead of embedding.
- **Scheduled run hits a rate limit or anti-bot heuristic.** Mitigation:
  conservative cron interval; per-source error isolation; backoff in
  page/sitemap monitors.

# Evidence Strategy

- Wave 0: observation-first. Evidence is "credentials work end-to-end,
  echoed back from each service."
- Wave 1: observation-first. Evidence is the live Dive URL plus a
  snapshot of the rendered roles list.
- Wave 2: observation-first per ticket. Evidence is the unioned Dive
  showing roles from each newly added source.
- Wave 3: observation-first. Evidence is one week of green GitHub
  Actions runs plus a Dive that reflects fresh data each cycle.
- Wave 4: observation-first. Evidence is the published post URL.

No `test-first` posture is required for v1; the work is integration-
shaped and the Dive itself is the acceptance surface.

Critique disposition: `recommended` for Wave 1 (walking skeleton sets
patterns the rest of the plan inherits) and Wave 3 (scheduling and error
isolation are easy to get subtly wrong). `optional` elsewhere unless
findings emerge.

# Plan Readiness Review

Spec / acceptance coverage:
- No separate spec exists. Acceptance criteria are ticket-local, derived
  from initiative success metrics. Promote to a spec only if v2 work
  needs a reusable contract.

Placeholder scan:
- Ticket IDs are `<TBD>` because tickets do not exist yet. They will be
  filled when each ticket is created.
- No `TODO` or "handle edge cases" placeholders in the work itself.

Ticket-sized slices:
- Wave 0, 1, 3, 4 are each one ticket. Wave 2 is four independent
  tickets. Sitemap monitor (GoHunt) may legitimately need sub-iterations
  but starts as one ticket.

Likely write scopes:
- Wave 0: repo bootstrap files only.
- Wave 1: `extractors/greenhouse/`, dlt config, MotherDuck view DDL,
  Dive definition.
- Wave 2: extractor-kind-specific subdirectories; shared
  `pyproject.toml`/`uv.lock` adds.
- Wave 3: `.github/workflows/` only.
- Wave 4: nothing in this repo; the post lives in the
  `loughondata.com` Hugo repo.

Likely verification posture:
- observation-first throughout.

Evidence and critique route:
- Critique recommended on Wave 1 and Wave 3.
- Evidence captured per wave per the strategy above.

Stop / loopback conditions:
- If Wave 1 reveals MotherDuck cannot read the chosen R2 layout, route
  back to plan revision before doing Wave 2.
- If Felt page monitor needs a headless browser, route to research
  before committing the page-monitor ticket.
- If Ashby's API shape diverges meaningfully from Greenhouse's (it
  does — different field names), do not try to share extractor code;
  ship a parallel resource.

# Exit Criteria

- All six confirmed v1 companies have data flowing through the
  pipeline.
- Dive is live at a stable URL.
- GitHub Actions has run cleanly for at least seven consecutive
  scheduled cycles.
- Part-two blog post is published.
- Initiative milestones M1–M5 are closed.
