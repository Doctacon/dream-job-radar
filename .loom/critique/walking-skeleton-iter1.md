---
id: critique:walking-skeleton-iter1
kind: critique
status: final
created_at: 2026-04-29T23:43:59Z
updated_at: 2026-04-29T23:43:59Z
scope:
  kind: repository
  repositories:
    - repo:root
review_target: ticket:gjkpkpum (Ralph iteration 1)
links:
  ticket: ticket:gjkpkpum
  packet: packet:ralph-walking-skeleton-20260429T231616Z
  plan: plan:v1-radar
external_refs: {}
---

# Summary

Direct artifact + code review of the walking-skeleton Ralph iteration: the
Greenhouse extractor, the dlt pipeline, the MotherDuck `current_open_roles`
view DDL, and the supporting `pyproject.toml` / `README.md` changes. Review
profiles per `ticket:gjkpkpum` Critique Disposition: code-quality,
schema-fitness.

# Review Target

- Ticket: `ticket:gjkpkpum`
- Packet: `.loom/packets/ralph/walking-skeleton-20260429T231616Z.md`
- Working tree (uncommitted) at parent reconciliation time:
  - `src/dream_job_radar/__init__.py`
  - `src/dream_job_radar/extractors/__init__.py`
  - `src/dream_job_radar/extractors/greenhouse.py`
  - `src/dream_job_radar/pipelines/__init__.py`
  - `src/dream_job_radar/pipelines/radar.py`
  - `motherduck/views.sql`
  - `pyproject.toml`
  - `README.md`
- Evidence: ticket Evidence section + packet Child Output.

# Verdict

`pass_with_findings`.

The walking skeleton meets AC1–AC5 and AC8 with truthful observation-first
evidence. The dataset_name deviation is accepted — observable path won
over the packet's literal value. Remaining findings are non-blocking but
some should be addressed before Wave 2 multiplies the schema choices.

# Findings

## FIND-001: View shape diverges from `open_roles` naming used in initiative / plan

Severity: low
Confidence: high
Disposition: open

Observation:

Implementation names the view `current_open_roles` (as the ticket and the
packet specified). The initiative and the plan's "Surface" section refer to
an `open_roles` shape. The ticket Acceptance section also uses
`current_open_roles` consistently. Only the upstream initiative/plan prose
is slightly inconsistent.

Why it matters:

Future agents reading the plan first will look for `open_roles` and not find
it. Cheap to align.

Follow-up:

Either (a) update plan/initiative prose to say `current_open_roles`, or
(b) wrap the view with an `open_roles` alias. Prefer (a). Defer to retro.

Challenges: None - not claim-specific.

## FIND-002: Title-keyword filter is plain substring; `data` matches "Database Administrator"

Severity: low
Confidence: high
Disposition: open

Observation:

`extractors/greenhouse.py:_title_matches` lowercases the title and checks
substring containment. "Database Administrator" would match `data`. None of
the 27 onX roles trip this today (none match `data` substring without being
a data role).

Why it matters:

Wave 2 boards (Mapbox, Planet Labs, etc.) may include DBA/devops roles that
slip through. The initiative explicitly chose substring match, so this is a
known tradeoff, not a defect. Worth re-evaluating once Wave 2 corpus exists.

Follow-up:

Open follow-up note for Wave 2 retrospective: review false-positive rate
across all six v1 boards before deciding whether to upgrade the keyword
model.

Challenges: None - not claim-specific.

## FIND-003: View filter `WHERE filename NOT LIKE '%/_dlt_%'` defends against future format changes

Severity: low
Confidence: medium
Disposition: open

Observation:

`motherduck/views.sql` filters on `filename` to exclude dlt system tables.
Today those system tables write JSONL, so the `*.parquet` glob already
excludes them; the WHERE clause is belt-and-suspenders. dlt could change
defaults in a future minor version.

Why it matters:

Defensive. Costs nothing.

Follow-up:

Keep the filter. If dlt 2.x writes parquet system tables, the WHERE clause
saves the view.

Challenges: None - not claim-specific.

## FIND-004: `raw_json` column emitted but not surfaced in the view

Severity: low
Confidence: high
Disposition: open

Observation:

Extractor writes `raw_json` (json-serialized full Greenhouse payload) into
Parquet. The view does not select it. Useful for re-derivation.

Why it matters:

If Wave 2 needs richer fields (departments, offices, metadata), the raw is
already in R2 and a sibling view can expose it without re-running extracts.

Follow-up:

None now. Add a `raw_open_roles` view in Wave 2 if needed.

Challenges: None - not claim-specific.

## FIND-005: `posted_at` derives from Greenhouse `updated_at`

Severity: medium
Confidence: high
Disposition: open

Observation:

Per ticket Execution Notes (line 165–166 of the ticket): "`posted_at`
should come from Greenhouse's `updated_at` for v1; rename later if a
Wave 2 extractor uses a different shape." Implementation does this. The
column is therefore "last-modified at the source", not "first-posted at
the source", which is what the column name implies.

Why it matters:

If Wave 2 (Ashby) exposes a true `created_at` or `published_at`,
keeping `posted_at` as a wrapper field is fine but the semantic mismatch
should be documented.

Follow-up:

Document `posted_at` semantic in `wiki:extractor-shape` when promoted in
the retrospective. Consider renaming to `source_updated_at` if Wave 2
shows divergence.

Challenges: None - not claim-specific.

## FIND-006: One pipeline per source_kind is the load-bearing pattern, not a workaround

Severity: medium
Confidence: high
Disposition: open

Observation:

The dataset_name = source_kind pattern (recorded in plan Wave 2) is the
only way to make the path contract `r2://<bucket>/raw/<source_kind>/<ats_slug>/`
hold given dlt's unconditional dataset prefix.

Why it matters:

Wave 2 will copy this pattern four times. If a future change re-evaluates
this (e.g. one pipeline with `extra_placeholders` controlling layout), the
schema and view do not change but the dlt internals do. Worth a wiki page
during the retrospective so Wave 2 inherits the pattern intentionally.

Follow-up:

Promote `wiki:extractor-shape` during the post-closure retrospective. Cite
this critique.

Challenges: None - not claim-specific.

## FIND-007: No unit coverage for `_title_matches` or `_normalize`

Severity: low
Confidence: high
Disposition: open

Observation:

Verification posture was observation-first; integration evidence covers
behavior. Unit tests would catch keyword-list regressions and field
normalization regressions cheaply.

Why it matters:

Wave 2 extractor authors will copy this shape. A small `tests/` skeleton
gives them a place to add cheap unit coverage without a separate decision.

Follow-up:

Optional Wave 1.5 ticket: add `tests/extractors/test_greenhouse.py`. Defer
to retrospective; not blocking ticket closure.

Challenges: None - not claim-specific.

## FIND-008: View materialization is a manual one-liner, not idempotent automation

Severity: low
Confidence: high
Disposition: open

Observation:

`motherduck/views.sql` is run via a shell-quoted Python one-liner in the
README. `CREATE OR REPLACE VIEW` is idempotent so re-running is safe, but
the one-liner is brittle (escaping `${R2_BUCKET}`).

Why it matters:

Wave 3 (GitHub Actions) will need a non-shell-escaped path. A small
`scripts/apply_views.py` runner is the natural shape.

Follow-up:

Wave 3 ticket should add `scripts/apply_views.py` or fold view-apply into
the pipeline run. Not blocking now.

Challenges: None - not claim-specific.

# Evidence Reviewed

- `ticket:gjkpkpum` (especially Acceptance Criteria, Evidence section,
  Critique Disposition).
- `packet:ralph-walking-skeleton-20260429T231616Z` (Child Output, Parent
  Merge Notes, Output Contract).
- `plan:v1-radar` (Wave 1 + Wave 2 sequencing, including the new
  inherited-pattern note).
- Working-tree files listed in Review Target above.
- Live observation outputs:
  - dlt run summary (8 records, 1 load package LOADED, no failed jobs)
  - `boto3 list_objects_v2` against `raw/greenhouse/onxmaps/` returning 1
    Parquet
  - MotherDuck `count(*)` returning 8
  - 8 sampled titles, all matching the keyword filter
  - Upstream Greenhouse cross-check: 27 total roles, 8 matched, no false
    positives in matched set, no obviously-missed roles in unmatched set.

# Residual Risks

- Wave 2 inheriting the dataset_name = source_kind pattern without a wiki
  page may rediscover the reasoning. Mitigated by promoting
  `wiki:extractor-shape` during the retrospective.
- Title-keyword filter false-positive rate is unknown across the full
  six-board v1 corpus. Mitigated by Wave 2 retrospective re-check.
- `posted_at` semantic mismatch will widen if Wave 2 sources expose a
  true creation timestamp.

# Required Follow-up

Before ticket closure:

- Parent decides whether AC6 (Dive renders) and AC7 (iframe embed
  attempt) are gated by this critique or are independent local edits.
  Recommendation: independent — they do not change the data shape.

After ticket closure (retrospective inputs):

- Promote `wiki:extractor-shape` page citing FIND-005, FIND-006, FIND-007.
- Reconcile initiative/plan `open_roles` vs `current_open_roles` naming.
- Optional: open follow-up ticket for `tests/extractors/test_greenhouse.py`.

# Acceptance Recommendation

`complete_pending_acceptance` once AC6 and AC7 are recorded.

This critique pass found no `changes_required` findings. All findings are
`low` or `medium` severity, all are open as deferred follow-up rather than
blockers. Ticket may advance from `review_required` to
`complete_pending_acceptance` when the parent records AC6 and AC7
outcomes.
