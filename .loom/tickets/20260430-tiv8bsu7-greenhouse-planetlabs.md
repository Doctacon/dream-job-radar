---
id: ticket:tiv8bsu7
kind: ticket
status: closed
change_class: code-behavior
risk_class: low
created_at: 2026-04-30T00:37:08Z
updated_at: 2026-04-30T00:42:00Z
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
  greenhouse: https://boards-api.greenhouse.io/v1/boards/planetlabs/jobs
depends_on:
  - ticket:gjkpkpum
---

# Summary

Wave 2 #1: extend the Greenhouse extractor to `planetlabs` (Planet
Labs). Config-only addition; reuses the resource factory shipped in
Wave 1 with no new code paths. Lands Parquet at
`r2://<bucket>/raw/greenhouse/planetlabs/` and exposes Planet Labs
roles through the existing `current_open_roles` view.

# Context

Wave 1 (`ticket:gjkpkpum`) settled the extractor shape:
`wiki:extractor-shape` documents the dataset_name = source_kind
pattern, the `current_open_roles` column shape, and the v1 keyword
filter. The Greenhouse extractor (`src/dream_job_radar/extractors/greenhouse.py`)
already exposes `board_resources(boards: tuple[str, ...])` so adding
a new slug requires no new resource code.

Per `research:ats-discovery`, Planet Labs hosts on Greenhouse with
slug `planetlabs`. Verified 2026-04-30:
`GET https://boards-api.greenhouse.io/v1/boards/planetlabs/jobs`
returns 102 total roles, of which 36 match the v1 keyword filter
(`data | engineer | gis | geospatial`, case-insensitive substring).

# Why Now

Planet Labs is the cheapest Wave 2 slice. Shipping it first proves
the resource factory generalizes before #2 (Ashby) introduces a new
source kind. If a hidden onX-specific assumption lurks in the Wave 1
code, this ticket surfaces it.

# Scope

- Add `planetlabs` to the default board list. The cheapest landing
  is to change `DEFAULT_BOARDS` in
  `src/dream_job_radar/extractors/greenhouse.py` from `("onxmaps",)`
  to `("onxmaps", "planetlabs")`. Pipeline already iterates the
  tuple.
- Run the pipeline once locally to produce real Parquet at
  `r2://<bucket>/raw/greenhouse/planetlabs/`.
- Verify the view picks up the new ATS slug without any DDL change
  (the glob already matches `raw/*/*/*.parquet`).
- Update `README.md` "Run the pipeline" section if any wording is
  now stale (e.g., references to "onX only").

# Non-goals

- No new extractor kind (#2 Ashby owns that).
- No view DDL change. The view glob is invariant under new ATS slugs
  inside the same source kind. If something forces a DDL change,
  loop back into a Wave 1 fix; do not silently widen scope here.
- No GitHub Actions schedule (Wave 3).
- No revision of the title-keyword filter, even though Planet Labs
  surfaces lots of hardware "engineer" hits. FIND-002 in
  `critique:walking-skeleton-iter1` already flagged the substring
  posture; revisit during the Wave 2 retrospective once all four
  source kinds have data.

# Acceptance Criteria

1. `uv run python -m dream_job_radar.pipelines.radar` runs end-to-end
   without error and writes Parquet to both
   `r2://pipelines/raw/greenhouse/onxmaps/` and
   `r2://pipelines/raw/greenhouse/planetlabs/`.
2. `boto3 list_objects_v2 Prefix=raw/greenhouse/planetlabs/` returns
   at least one Parquet object key after the run.
3. MotherDuck query
   `SELECT count(*) FROM current_open_roles
    WHERE source_kind='greenhouse' AND ats_slug='planetlabs'`
   returns a positive integer.
4. All Planet Labs rows in the view satisfy the title-keyword filter
   (substring match against `data | engineer | gis | geospatial`).
   Verify by sampling at least 10 returned titles.
5. The onX row count is unchanged (or higher; new roles may appear
   between runs) — i.e., this ticket does not regress the Wave 1
   data.

# Coverage

Ticket-local acceptance criteria above. No spec contract. Patterns
inherited from `wiki:extractor-shape`.

# Claim Matrix

None — no spec contract; ticket-local acceptance criteria only.

# Execution Notes

- The extractor's filter is per-title; Planet Labs has 102 roles, ~36
  match. Running this will roughly 5× the row count in
  `current_open_roles`. That is expected.
- Hardware/manufacturing roles will match `engineer`. That is a known
  v1 keyword tradeoff (FIND-002), not a defect.
- dlt's `_dlt_loads/`, `_dlt_pipeline_state/`, `_dlt_version/`
  metadata under `raw/greenhouse/` will be appended to in this run.
  No cleanup needed; the view already filters via
  `WHERE filename NOT LIKE '%/_dlt_%'`.

# Blockers

None.

# Next Move / Next Route

Local edit, no Ralph packet. The change is one tuple plus a verifying
run. Ralph's bounded-handoff overhead would be larger than the work.
If the run surfaces an unexpected schema mismatch (e.g., Planet Labs
returns a field shape we did not see at onX), loop back to extractor
revision; otherwise commit and close.

# Ralph Readiness

N/A — local edit posture. Write boundary if it ever needs Ralph:

- `src/dream_job_radar/extractors/greenhouse.py`
- `README.md`

Verification posture: `observation-first` (Parquet appears, view
returns rows).

# Evidence

Expected on completion:

- terminal output of the pipeline run, including the dlt summary
- `boto3 list_objects_v2` output for
  `s3://pipelines/raw/greenhouse/planetlabs/`
- MotherDuck `count(*)` for the new ats_slug
- 10-row title sample confirming the keyword filter holds

Captured 2026-04-30T00:42Z:

AC1 — pipeline runs end-to-end across both boards:
```
... onxmaps: 8 ...
... planetlabs: 36 ...
Pipeline dream_job_radar load step completed in 2.65 seconds
1 load package(s) were loaded to destination filesystem and into dataset greenhouse
Load package 1777509715.123391 is LOADED and contains no failed jobs
```

AC2 — Parquet under both prefixes:
```
raw/greenhouse/onxmaps/   KeyCount=2
  1777505542.5649621.8c17618d4c.parquet  8373
  1777509715.123391.0834eec6fd.parquet   8369
raw/greenhouse/planetlabs/ KeyCount=1
  1777509715.123391.7cdd5c76d6.parquet  12201
```

AC3 — view rows per slug:
```
md: SELECT ats_slug, count(*) FROM current_open_roles GROUP BY ats_slug
-> ('onxmaps', 8), ('planetlabs', 36)
```

AC4 — keyword filter holds for Planet Labs sample (all 10 contain
`engineer`):
```
Senior Mechanical Engineer, Deployable Solar Arrays
Senior Software Engineer, Strategic Customer Engagements
Mechanical Engineer, Harness Design
Satellite Tasking Engineer, Collection Planning
Intern, Mission Optimization Engineer
Space Systems Engineer, Space Operations
AI Engineer, Marketing
AI Engineer, Marketing
Flight Software Engineer
Senior Software Engineer
```

AC5 — onX row count unchanged at 8 (matches Wave 1). No regression.

# Critique Disposition

Risk class: low

Critique policy: optional

Policy rationale: this ticket adds no new code paths and changes no
schema. The Wave 1 critique already covered the resource factory and
the view. A repeat critique pass would be ceremony.

Findings: None — no critique scheduled.

Disposition status: not_required

Deferral / not-required rationale: low risk, no new code paths, view
shape unchanged, Wave 1 critique still applies.

# Wiki Disposition

No new wiki page expected. If Planet Labs surfaces a non-trivial
divergence (different field shape, anti-bot, etc.), update
`wiki:extractor-shape` accordingly during the close-out.

# Acceptance Decision

Accepted by: Connor
Accepted at: 2026-04-30T00:42:00Z
Basis: AC1–AC5 satisfied with observation-first evidence (see Evidence
section). View shape unchanged; no regression on onX. Resource factory
generalized cleanly to the new slug — confirms the
`wiki:extractor-shape` pattern. Critique not required (low risk, no
new code paths).
Residual risks:
- Two duplicate "AI Engineer, Marketing" rows from Planet Labs survive
  the (source_kind, ats_slug, role_id) dedup because Greenhouse
  exposes them under distinct role_ids. Not a defect; reflects
  upstream board reality. Re-evaluate during the Wave 2 retrospective
  if the duplicate-by-title pattern appears across other source
  kinds.
- Hardware/manufacturing roles match `engineer` per FIND-002 in
  `critique:walking-skeleton-iter1`. Known v1 keyword tradeoff.

# Dependencies

Hard prerequisites:

- `ticket:gjkpkpum` (closed) — provides the Greenhouse extractor,
  the dlt pipeline, and the `current_open_roles` view.

Soft references:

- `wiki:extractor-shape` — the canonical pattern this ticket reuses.
- `research:ats-discovery` — confirms `planetlabs` as the slug.

# Journal

- 2026-04-30 — ticket created from `plan:v1-radar` Wave 2 #1.
  Status set directly to `ready`; readiness checklist passes
  trivially because the work is config-only and the resource
  factory already accepts a tuple of board slugs. Risk classified
  `low`; critique optional and explicitly not required.
- 2026-04-30 — Implementation: `DEFAULT_BOARDS` in
  `extractors/greenhouse.py` extended to
  `("onxmaps", "planetlabs")`. Pipeline run produced 36 Planet Labs
  records + 8 onX records (unchanged); Parquet landed at both R2
  prefixes; view returns the new ats_slug without DDL change.
  AC1–AC5 satisfied. Status → `closed`.
