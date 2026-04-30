---
id: critique:sitemap-gohunt-iter1
kind: critique
status: final
created_at: 2026-04-30T02:33:54Z
updated_at: 2026-04-30T02:33:54Z
scope:
  kind: repository
  repositories:
    - repo:root
review_target: ticket:xwfvoj4o (Ralph iteration 1)
links:
  ticket: ticket:xwfvoj4o
  packet: packet:ralph-sitemap-gohunt-20260430T022113Z
  plan: plan:v1-radar
  wiki: wiki:extractor-shape
  predecessor_critique: critique:ashby-mapbox-iter1
external_refs: {}
---

# Summary

Direct artifact + code review of Wave 2 #4 (sitemap monitor →
GoHunt). Profiles per ticket Critique Disposition: code-quality,
schema-fitness. Predecessor critiques cover the resource-factory
shape and the Wave 2 schema-fitness lessons; this pass focuses on
what is genuinely new: sitemap parsing, JSON-LD extraction, role_id
derivation, and the 0-match honesty contract.

# Review Target

- Ticket: `ticket:xwfvoj4o`
- Packet: `.loom/packets/ralph/sitemap-gohunt-20260430T022113Z.md`
- Working tree at parent reconciliation time:
  - `src/dream_job_radar/extractors/sitemap.py` (new)
  - `src/dream_job_radar/pipelines/sitemap.py` (new)
  - `src/dream_job_radar/pipelines/radar.py` (extended)
  - `README.md` (extended)
- Evidence: ticket Evidence section + packet Child Output.

# Verdict

`pass_with_findings`.

The sitemap slice meets AC1–AC5 with truthful observation-first
evidence including a 0-match outcome that the pipeline handled
cleanly. The implementation makes the right tradeoffs (regex-based
JSON-LD parsing instead of a new dep; sitemap-index escalation
instead of silent recursion). Findings are inheritance/hardening
notes, not blockers.

# Findings

## FIND-001: `role_id` is fragile under upstream slug rename

Severity: medium
Confidence: high
Disposition: open

Observation:

`_role_id_from_url` returns the last path segment of the article's
canonical URL. If GoHunt renames a slug (typo fix, SEO change,
title rewording), the next pipeline run sees a "new" role with a
new `first_seen_at`, and the old observation stops appearing in the
view (no fresh `fetched_at` to win the dedup partition).

Why it matters:

For sitemap-derived sources, the URL slug IS the de-facto identity.
There is no upstream UUID. The tradeoff is real and likely
unavoidable in v1, but downstream consumers (the Dive in
particular) may show ghost duplicates if a role gets renamed.

Follow-up:

Document the constraint in `wiki:extractor-shape` during the
retrospective: "for sitemap-monitor sources, role_id is derived
from URL slug; upstream slug renames break identity continuity."
If/when this becomes a real problem, consider hashing
`headline + canonical URL host` as a secondary id; defer.

Challenges: None - not claim-specific.

## FIND-002: JSON-LD extraction by regex is fragile in theory

Severity: low
Confidence: medium
Disposition: open

Observation:

`JSONLD_BLOCK_RE` matches `<script type="application/ld+json">...</script>`
spans with a non-greedy DOTALL regex. A nested `</script>` literal
inside a JSON string would prematurely terminate the match. The
JSON spec disallows literal `</script>` (it would have to be
escaped, e.g., `"<\/script>"`), so in practice this never bites,
but it is technically not bulletproof.

Why it matters:

If a future source kind embeds odd content inside JSON-LD (rich
descriptions, escaped HTML, etc.), debugging would be painful.
BeautifulSoup or lxml would be more robust, at the cost of a new
dep.

Follow-up:

Defer. If a real source kind breaks the regex, switch to
`lxml.html` (already a transitive dep through pyarrow / dlt) or
add `beautifulsoup4` then. Track in retrospective.

Challenges: None - not claim-specific.

## FIND-003: No `isListed`-equivalent for sitemap sources

Severity: low
Confidence: high
Disposition: open

Observation:

The Ashby extractor defensively filters `isListed=True` before the
keyword filter. Sitemap-monitor has no such flag — sitemap presence
itself is the publishedness signal. The wiki's "defensive
listed/published checks" pattern (added in Wave 2 #2 retro) does
not apply identically here.

Why it matters:

Wave 2 #3 (page monitor for Regrid + Felt) and any future sitemap
or HTML-driven source will face the same question. Worth a note in
the wiki so authors understand why the pattern is omitted, not
forgotten.

Follow-up:

Update `wiki:extractor-shape` during the retrospective: under
"Defensive listed/published checks", add a note that sitemap- or
page-derived sources rely on the upstream listing surface itself
as the published signal — there is no separate flag to check.

Challenges: None - not claim-specific.

## FIND-004: dlt 0-yield handling is friendlier than expected — worth noting

Severity: low
Confidence: high
Disposition: resolved

Observation:

dlt's filesystem destination handled the 0-yielded-records path
cleanly: pipeline ran, wrote `_dlt_loads/`, `_dlt_pipeline_state/`,
`_dlt_version/`, `init`, did NOT write a `gohunt/` table directory,
did NOT raise. This is a pleasant property of dlt 1.x not
guaranteed by the docs. The view glob `raw/*/*/*.parquet` requires
at least one matching file — DuckDB raises "no files found" if zero
parquet files match the glob. Today the existing greenhouse + ashby
parquet keeps the glob populated; a hypothetical "all sources yield
zero" run would re-introduce a view-render failure.

Why it matters:

Wave 3 (scheduling) might run sitemap alone for testing. The view
will continue to work because greenhouse and ashby parquet exists,
but the failure mode is worth knowing.

Follow-up:

None for v1. Document in retrospective if Wave 3 surfaces it.

Challenges: None - not claim-specific.

## FIND-005: `time.sleep(0.5)` is a hard-coded courtesy

Severity: low
Confidence: high
Disposition: open

Observation:

`PAGE_FETCH_DELAY_S = 0.5` is module-level constant. Runs against
~4 URLs today; would be ~30s if GoHunt scaled to 60 roles. Not
configurable per source.

Why it matters:

Wave 3 cron will call into this code; if a site adds 100 roles, the
fetch loop dominates run time. Per-spec sleep override would let
each source tune politeness independently.

Follow-up:

Make `delay_s` a `SiteSpec` field with default 0.5 the next time
sitemap.py is touched. Defer; not blocking.

Challenges: None - not claim-specific.

## FIND-006: Sitemap-index escalation choice is correct

Severity: low
Confidence: high
Disposition: resolved

Observation:

`_fetch_sitemap_urls` raises `ValueError` if root tag is
`sitemapindex`. Right call — silent recursion would invite either
unbounded fetch or wrong-shape filter.

Why it matters:

Wave 3 cron failure mode is loud (raises) instead of silent (wrong
data). Healthy posture.

Follow-up:

None.

Challenges: None - not claim-specific.

## FIND-007: 0-row honesty — flag for Wave 2 retrospective

Severity: low
Confidence: high
Disposition: open

Observation:

GoHunt produces 0 matches today. View has no sitemap rows. The
Dive's KPI row currently shows 3 distinct companies (onxmaps,
planetlabs, Mapbox). When a future run produces a GoHunt match, the
KPI would jump to 4. The Dive does not currently advertise that it
is monitoring sources beyond what currently appears.

Why it matters:

Future Dive iterations might want a "sources monitored" line
distinct from "sources with current matches" — useful for trust
("we are watching GoHunt, the count is 0") vs raw ("there are 3
companies hiring"). Defer to retrospective; not a defect.

Follow-up:

Note in retrospective. Consider during PM3 (scheduled refresh) or
PM4 (blog post) revisions to the Dive.

Challenges: None - not claim-specific.

# Evidence Reviewed

- `ticket:xwfvoj4o` Acceptance + Evidence sections.
- `packet:ralph-sitemap-gohunt-20260430T022113Z` Child Output.
- Working-tree files listed under Review Target.
- Live observation outputs (sitemap stand-alone run, all-sources
  radar run, R2 listing, view count).
- Predecessor critiques `critique:walking-skeleton-iter1` and
  `critique:ashby-mapbox-iter1` for inherited posture.

# Residual Risks

- `role_id` slug-rename fragility (FIND-001) is the highest-impact
  long-tail risk; tracked for wiki promotion.
- 0-match outcome handling depends on at least one other source
  kind producing parquet so the view glob has matches (FIND-004).
- Hard-coded sleep (FIND-005) becomes meaningful only at
  scale; defer.

# Required Follow-up

Before ticket closure:

- Parent confirms the 0-match outcome is acceptable as v1 delivery
  (already done — see plan + ticket Acceptance Decision).

After ticket closure (retrospective inputs):

- Update `wiki:extractor-shape`:
  - add sitemap-monitor section (URL-as-identity, slug-rename
    fragility, regex JSON-LD parsing tradeoff) (FIND-001, FIND-002)
  - extend "Defensive listed/published checks" with the
    sitemap-presence-is-the-signal note (FIND-003)
- Note FIND-005 (per-spec sleep override) and FIND-007
  ("sources monitored" vs "sources with matches" Dive distinction)
  as future Wave-3/PM4 considerations.

# Acceptance Recommendation

`complete_pending_acceptance`.

This critique pass found no `changes_required` findings. All
findings are `low` or `medium` severity, all are deferred follow-up
or already resolved by inspection. Ticket may advance from
`review_required` to `complete_pending_acceptance`; parent
acceptance closes it.
