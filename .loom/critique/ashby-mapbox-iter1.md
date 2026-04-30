---
id: critique:ashby-mapbox-iter1
kind: critique
status: final
created_at: 2026-04-30T01:11:35Z
updated_at: 2026-04-30T01:11:35Z
scope:
  kind: repository
  repositories:
    - repo:root
review_target: ticket:oy172mt9 (Ralph iteration 1)
links:
  ticket: ticket:oy172mt9
  packet: packet:ralph-ashby-mapbox-20260430T004920Z
  plan: plan:v1-radar
  wiki: wiki:extractor-shape
  predecessor_critique: critique:walking-skeleton-iter1
external_refs: {}
---

# Summary

Direct artifact + code review of Wave 2 #2 (Ashby → Mapbox). Review
profiles per ticket Critique Disposition: code-quality,
schema-fitness. Predecessor critique
`critique:walking-skeleton-iter1` covered the resource factory
shape; this pass focuses on what is genuinely new in this iteration:
the second source kind, the cross-extractor refactor (`_r2.py`,
meta-runner `radar.py`), and the two schema-fitness deviations the
child surfaced.

# Review Target

- Ticket: `ticket:oy172mt9`
- Packet: `.loom/packets/ralph/ashby-mapbox-20260430T004920Z.md`
- Working tree (uncommitted) at parent reconciliation time:
  - `src/dream_job_radar/extractors/ashby.py` (new)
  - `src/dream_job_radar/extractors/greenhouse.py` (modified — drops
    `departments`)
  - `src/dream_job_radar/pipelines/_r2.py` (new)
  - `src/dream_job_radar/pipelines/ashby.py` (new)
  - `src/dream_job_radar/pipelines/radar.py` (rewritten as
    meta-runner)
  - `README.md` (extended)
- Evidence: ticket Evidence section + packet Child Output.

# Verdict

`pass_with_findings`.

The Ashby slice meets AC1–AC7 with truthful observation-first
evidence after the in-flight fix. Both deviations the child
surfaced are real schema-fitness lessons that need to land in
`wiki:extractor-shape` so Wave 2 #3 and #4 inherit them. Refactor
shape (`_r2.py` helper, meta-runner `radar.py`) is clean and
inheritable.

# Findings

## FIND-001: `departments` dropped from canonical shape — wiki must follow

Severity: medium
Confidence: high
Disposition: open

Observation:

The Ralph iteration removed `departments` from the canonical row in
both extractors. `wiki:extractor-shape` still lists `departments`
under the `current_open_roles` column table even though the column
was never view-exposed and is now never extractor-emitted.

Why it matters:

Wave 2 #3 (page monitor) and #4 (sitemap monitor) authors will read
`wiki:extractor-shape` to learn the canonical contract. If the wiki
still names `departments`, those authors will reproduce the
nested-table bug. The wiki must be updated as part of this
retrospective; it is not safe to defer.

Follow-up:

Update `wiki:extractor-shape` during the post-closure retrospective:
remove `departments` from the canonical shape table; add a
non-list-fields rule ("the canonical row must not contain Python
list values; multi-valued source fields stay in `raw_json` for v1").

Challenges: None - not claim-specific.

## FIND-002: dlt snake_case normalization lowercases the slug — document the policy

Severity: medium
Confidence: high
Disposition: open

Observation:

dlt's default `snake_case` naming convention rewrites the
table-directory name. With `Mapbox` as the resource name, R2
receives `raw/ashby/mapbox/...parquet`. The data column `ats_slug`
preserves `Mapbox`. Net behavior: view groups correctly by data
column; path-vs-data divergence is invisible to the view but visible
to anyone listing R2 directly.

Why it matters:

This will recur on every Wave 2 source kind that uses mixed-case
slugs (Ashby is the obvious one; sitemap monitor for GoHunt and
page monitor for Regrid/Felt are unlikely to). The current behavior
is a known dlt quirk, not a defect, but it must be documented so
future agents do not "fix" it by reaching for `direct` naming
convention without understanding the tradeoff.

Follow-up:

Update `wiki:extractor-shape` during the retrospective: add a
section on slug-case policy. Specifically: data-column casing
follows the source; R2 path follows dlt's default normalization;
view groups by data column; do not change `naming_convention`
without weighing the blast radius across all source kinds.

Challenges: None - not claim-specific.

## FIND-003: View should harden against non-canonical rows leaking through `union_by_name`

Severity: medium
Confidence: medium
Disposition: open

Observation:

The first Ashby run wrote `raw/ashby/mapbox__departments/...parquet`,
which the view's
`read_parquet(..., union_by_name=true)` slurped. After dedup, this
produced one `(null, null, null, ...)` row in the view. The child
fixed this by removing the offending data shape; the view's defense
is still only `WHERE filename NOT LIKE '%/_dlt_%'`, which would not
catch a future child-table named `<slug>__<field>`.

Why it matters:

Wave 2 #3 (HTML parsing) and #4 (sitemap parsing) will be more
likely to produce odd column shapes (parsed strings that don't fit
the canonical row). A defensive `WHERE source_kind IS NOT NULL`
(or equivalent) would catch these without changing the v1 happy
path.

Follow-up:

Either (a) add `WHERE source_kind IS NOT NULL` to
`motherduck/views.sql`, or (b) explicitly project the canonical
columns and rely on the dedup partition keys being NOT NULL by
construction. Option (a) is cheaper. Open follow-up note for the
retrospective.

Challenges: None - not claim-specific.

## FIND-004: `r2_destination()` factored to `_r2.py` is a clean inheritable improvement

Severity: low
Confidence: high
Disposition: resolved

Observation:

The packet flagged the refactor as optional. Child chose to factor
the helper to `pipelines/_r2.py`. Clean diff; no duplication;
imports are unambiguous; no shared mutable state. Wave 2 #3 and #4
will reuse this helper.

Why it matters:

This is a foundational refactor for the rest of Wave 2 — it's
worth confirming explicitly that the shape is correct (no per-source
config bleed, etc.).

Follow-up:

None. Resolved by inspection.

Challenges: None - not claim-specific.

## FIND-005: `radar.py` rewrite is acceptable but worth flagging

Severity: low
Confidence: high
Disposition: resolved

Observation:

Old `radar.py` had a `run()` function specific to Greenhouse. New
`radar.py` is a meta-runner with `run_greenhouse()` and `run_all()`,
calling into `ashby_pipeline.run()`. No external caller depends on
the old `run()` signature (no scheduler exists yet; README is the
only invocation surface and was updated in the same iteration).

Why it matters:

This is a quiet API change. Worth being explicit so that Wave 3
(scheduling) can rely on `run_all()` as the canonical "run
everything" entry point.

Follow-up:

None. Wave 3 ticket will choose between `pipelines.radar` and
per-source entry points based on per-source error-isolation needs.

Challenges: None - not claim-specific.

## FIND-006: Ashby duplicate-by-title roles all survive dedup

Severity: low
Confidence: high
Disposition: open

Observation:

Mapbox publishes the same role title under multiple region-specific
listings, each with a distinct UUID. The view dedup keys on
`(source_kind, ats_slug, role_id)` so all 59 entries survive. This
is the same pattern Planet Labs surfaced (Wave 2 #1 acceptance
captured it as a residual risk).

Why it matters:

Two source kinds in a row exhibit the duplicate-by-title pattern.
Worth promoting to a wiki note rather than re-discovering on every
new source.

Follow-up:

Update `wiki:extractor-shape` during the retrospective: add a
"duplicate-by-title is upstream behavior, not a defect" note. The
Dive consumes the view as-is; if duplicate suppression becomes a
Dive concern later, do it at the Dive layer, not in the view.

Challenges: None - not claim-specific.

## FIND-007: `isListed` defensive filter is good practice, document it

Severity: low
Confidence: high
Disposition: open

Observation:

The Ashby extractor filters `job.get("isListed", True)` before the
title-keyword filter. The probe found all 84 jobs `isListed=True`,
so the filter is currently a no-op, but it defends against unlisted
drafts appearing in the public response.

Why it matters:

Other source kinds may have similar "publicly fetched but not
listed" flags. Worth noting the pattern in the wiki so authors do
not skip it.

Follow-up:

Update `wiki:extractor-shape` during the retrospective: add a
"defensive listed/published checks" note.

Challenges: None - not claim-specific.

# Evidence Reviewed

- `ticket:oy172mt9` — full Acceptance Criteria, Evidence section
  including before/after observations and the 10-row Mapbox sample,
  Critique Disposition profiles, Journal entries describing the
  in-flight fix.
- `packet:ralph-ashby-mapbox-20260430T004920Z` — Child Output and
  Parent Merge Notes.
- Working-tree files listed under Review Target.
- Live observation outputs (radar end-to-end run, R2 listing, view
  count + sample).
- Predecessor critique `critique:walking-skeleton-iter1` for
  inherited posture and finding format.

# Residual Risks

- Wave 2 #3 and #4 inheriting `wiki:extractor-shape` without
  FIND-001/002/003/006/007 updates. Mitigated by promoting all
  five to the wiki page during the post-closure retrospective.
- View hardening against non-canonical rows (FIND-003) deferred to
  retrospective; if Wave 2 #3 (page monitor) lands a free-form HTML
  parser before the wiki is updated, parents must inspect that
  iteration's R2 output before declaring success.

# Required Follow-up

Before ticket closure:

- Parent confirms the two schema-fitness deviations are accepted
  (already done in Parent Merge Notes; this critique just records
  the verdict).

After ticket closure (retrospective inputs):

- Update `wiki:extractor-shape`:
  - drop `departments` from canonical column table (FIND-001)
  - add slug-case policy section (FIND-002)
  - add duplicate-by-title note (FIND-006)
  - add defensive listed/published flag note (FIND-007)
- Decide on view hardening (FIND-003); update
  `motherduck/views.sql` if (a) is chosen.

# Acceptance Recommendation

`complete_pending_acceptance`.

This critique pass found no `changes_required` findings. All
findings are `low` or `medium` severity; FIND-001/002 are accepted
as deferred follow-up to the retrospective rather than blockers
because the implementation is already correct — only the wiki
inheritance contract needs to catch up. Ticket may advance from
`review_required` to `complete_pending_acceptance`; parent
acceptance closes it.
