# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

## [0.1.0] — 2026-05-02

First public release. The radar watches a curated list of mission-aligned
companies (outdoor / geospatial / forestry / hunting / climate) for new
data-engineering, GIS, and geospatial-shaped roles, and surfaces them in a
mobile-friendly MotherDuck Dive.

### Pipeline

- **Six source kinds** ingest open roles into Cloudflare R2 as Parquet:
  - `greenhouse` — public job-board API (`onxmaps`, `planetlabs`,
    `floodbase`, `blastpoint`, `overstory`).
  - `ashby` — public job-board API (`Mapbox`, `pano-ai`).
  - `sitemap` — `sitemap.xml` + per-URL JSON-LD `Article` scrape (`gohunt`).
  - `page` — per-site HTML parsers for sources without an API
    (`regrid` via Gusto board, `felt` via Webflow careers, `wherobots` via
    WordPress careers).
  - `rippling` — public job-board API (`kalkomey` /
    HuntStand+HuntWise).
  - `polymer` — parent careers index + per-role JSON-LD `JobPosting` on
    `jobs.<company>.<tld>` (`upstream-tech`).
- Title keyword filter applied at extract time:
  `data | engineer | gis | geospatial`, case-insensitive substring.
- Each extractor follows the canonical row contract documented in
  `.loom/wiki/extractor-shape.md`.

### Storage

- **Hive-partitioned R2 layout:**
  `raw/<source_kind>/<ats_slug>/year=YYYY/month=MM/day=DD/<file>.parquet`.
- Dlt's filesystem destination (shared `pipelines/_r2.py` factory) writes
  one parquet per source-kind per cron firing. Append-only.
- One-time backfill of 89 historical flat parquets into hive paths via
  `s3.copy_object` + `delete` (server-side; no data rewritten).

### Query layer

- **`current_open_roles` view in MotherDuck** unions all source kinds,
  dedupes on `(source_kind, ats_slug, role_id)` with `qualify
  ROW_NUMBER() OVER (... ORDER BY fetched_at DESC) = 1`, and exposes
  derived `first_seen_at` / `last_seen_at` columns.
- View CTE filters parquet partitions to the last 30 days *before* the
  dedupe window function runs, so scan size stays roughly constant as
  history accumulates.
- View hardened with `WHERE filename NOT LIKE '%/_dlt_%'` and
  NOT-NULL guards on the dedupe partition keys.
- `posted_at` cast to `TIMESTAMP WITH TIME ZONE` via `TRY_CAST` so
  consumers can use `strftime` / `EXTRACT` directly. Empty strings →
  `NULL` honestly.

### Dive

- **Mobile-friendly Dive** at
  `https://app.motherduck.com/dives/391d1329-70d7-4223-89c8-d0dfde66ef7f`.
- Filters to roles whose `coalesce(posted_at, first_seen_at) >=
  current_date - INTERVAL 6 DAY` (last 7 calendar days inclusive).
- Title cells are hyperlinked to the upstream apply URL.
- Light theme matched to [loughondata.com](https://loughondata.com)'s
  palette (Hugo Blowfish, neutral-on-white with deep-teal links) for
  legibility in direct sunlight.

### Scheduled refresh

- **GitHub Actions cron** (`.github/workflows/refresh.yml`) at
  `0 12 * * *` UTC.
- Per-source extractor steps run with `continue-on-error: true` so one
  source failing does not block the others.
- View-apply step uses `if: always()` and is idempotent
  (`CREATE OR REPLACE VIEW`).
- Final per-`(source_kind, ats_slug)` freshness health check fails the
  job if any previously-observed slug has gone stale; failure surfaces
  via GitHub's email-on-failure.
- Concurrency-grouped to prevent overlapping runs from racing on dlt
  state.

### Loom records

The project ships with a `.loom/` tree documenting the build:

- `constitution:main` — durable identity, principles, hard constraints.
- Closed initiatives: `close-the-loop` (v1 pipeline + Dive),
  `expand-radar` (v2 source-kind + company expansion),
  `partition-r2-layout` (hive partitioning), `bound-view-window`
  (view-side scan bound).
- `wiki:extractor-shape` — canonical reference for all six source kinds:
  the dataset_name pattern, role_id strategies, posted_at semantics,
  defensive listed/published checks, R2 layout, and view-bound rules.
- Per-ticket research / packets / critique records preserve the design
  audit trail.

### Out of v0.1 scope

- Iceberg / DuckLake / Polaris catalog managed table format.
- Incremental dlt ingest (full refresh + read-time bound is honest at
  this scale).
- Apply-loop tracking (private surface for application status).
- Per-step `env:` minimization in the workflow.
- Vibrant Planet page-monitor parser (their careers page shows "No
  open roles at the moment" — defer until populated).
- AllTrails / Pachama / CalTopo / BaseMap — dropped permanently per
  `research:ats-discovery-v2` (anti-bot, acquired, no public surface).
