---
id: critique:rippling-kalkomey-iter1
kind: critique
status: final
created_at: 2026-05-02T13:42:48Z
updated_at: 2026-05-02T13:42:48Z
scope:
  kind: repository
  repositories:
    - repo:root
review_target: ticket:vr6iel5o (Ralph iteration 1)
links:
  ticket: ticket:vr6iel5o
  packet: packet:ralph-rippling-kalkomey-20260502T133231Z
  plan: plan:expand-radar
  wiki: wiki:extractor-shape
  predecessor_critique: critique:ashby-mapbox-iter1
external_refs: {}
---

# Summary

Direct artifact + code review of Wave 2 / PM2 of
`plan:expand-radar` (Rippling → Kalkomey). Profiles per ticket
Critique Disposition: code-quality, schema-fitness. Predecessor
critiques cover the resource-factory shape and the Wave 2 v1
schema-fitness lessons; this pass focuses on what is genuinely
new: the Rippling list shape, the no-`isListed` posture, and the
workflow extension.

# Review Target

- Ticket: `ticket:vr6iel5o`
- Packet:
  `.loom/packets/ralph/rippling-kalkomey-20260502T133231Z.md`
- Working tree at parent reconciliation:
  - `src/dream_job_radar/extractors/rippling.py` (new)
  - `src/dream_job_radar/pipelines/rippling.py` (new)
  - `src/dream_job_radar/pipelines/radar.py` (extended chain)
  - `.github/workflows/refresh.yml` (new step)
  - `README.md` (extended)
- Evidence: ticket Evidence section + packet Child Output.

# Verdict

`pass_with_findings`.

The slice meets AC1–AC7 with truthful observation-first evidence.
Today's Kalkomey 0-yield is honest and matches established v1
0-match patterns (floodbase, gohunt, regrid). All findings are
inheritance / hardening notes for the wiki and Wave 5 retro, not
blockers.

# Findings

## FIND-001: Rippling row enters role_id strategies table as the cleanest API surface so far

Severity: low
Confidence: high
Disposition: open

Observation:

`role_id = str(job["uuid"])` is the most rename-stable identity
strategy in the project. Rippling's UUID is server-generated and
opaque — title or slug rewrites at the company's end do not change
it. Same property as Greenhouse integer ids and Ashby UUIDs.

Why it matters:

Wiki retrospective should add a `rippling` row to the role_id
strategies table in `wiki:extractor-shape` so future Rippling-
hosted boards inherit it without re-deriving.

Follow-up:

Update wiki during PM5 retro alongside Polymer + page-monitor
additions.

Challenges: None - not claim-specific.

## FIND-002: Defensive listed/published posture diverges by source kind; document the rule

Severity: medium
Confidence: high
Disposition: open

Observation:

Rippling has no `isListed`-equivalent flag. Extractor uses
"presence in the response is the published signal" (sitemap-
monitor / page-monitor posture). Greenhouse and Ashby have flags
(or `/jobs` only returns published). Two distinct postures across
five source kinds:

- **flag-based** — Ashby's `isListed=True`
- **presence-based** — sitemap (gohunt), page (regrid + felt),
  Rippling (kalkomey)
- **API-implicit** — Greenhouse's `/jobs` only returns published

Why it matters:

Wave 4 page-monitor adds (Vibrant Planet, Wherobots) and PM3 Polymer
add (Upstream Tech) will face the same question. Worth captured
explicitly in `wiki:extractor-shape` so authors don't re-derive.

Follow-up:

Update `wiki:extractor-shape` "Defensive listed/published checks"
section with a per-source-kind table.

Challenges: None - not claim-specific.

## FIND-003: posted_at = "" — same convention as page-monitor; widens the per-source-kind divergence

Severity: low
Confidence: high
Disposition: open

Observation:

Rippling's list endpoint returns no posting timestamp. Extractor
sets `posted_at = ""`; view's `TRY_CAST(posted_at AS TIMESTAMP)`
(added 2026-05-01) converts to NULL — correct behavior, no DDL
change needed.

Why it matters:

The `posted_at` semantic table in `wiki:extractor-shape` already
documents 4 source-kind variants (greenhouse=updated_at,
ashby=publishedAt, sitemap=datePublished/dateModified, page="").
Rippling adds a 5th row (rippling=""). Future consumers are likely
to use `first_seen_at` (view-derived) for unified recency.

Follow-up:

Update wiki posted_at table during PM5 retro.

Challenges: None - not claim-specific.

## FIND-004: Workflow `concurrency` group still ungated by ref/branch

Severity: low
Confidence: high
Disposition: open

Observation:

`concurrency: { group: refresh, cancel-in-progress: false }` is
unchanged from v1 Wave 3. Single global group across all branches.
Today only `schedule` and `workflow_dispatch` triggers fire; no
risk. Adding the Rippling step did not change this.

Why it matters:

Same as FIND-005 in `critique:actions-cron-iter1`. Carried forward.

Follow-up:

If branch-based triggers ever land, group becomes
`refresh-${{ github.ref }}`. Defer.

Challenges: None - not claim-specific.

## FIND-005: STALE_THRESHOLD_HOURS not yet tightened from v1 close-out

Severity: low
Confidence: high
Disposition: open

Observation:

`scripts/health_check.py` `STALE_THRESHOLD_HOURS = 36`. Carried
from v1 Wave 3. The v1 close-out left the tightening (→ 26h) as a
deferred follow-up. Wave 2 expansion adds two new slugs that
produce parquet today (blastpoint, overstory, pano-ai from PM1)
plus rippling/kalkomey which today produces no parquet.

Why it matters:

The threshold is conservative; not blocking PM2. Wave 5 retro is
the natural moment to tighten.

Follow-up:

Same disposition as `critique:actions-cron-iter1` FIND-001.
No change.

Challenges: None - not claim-specific.

## FIND-006: 0-yield Kalkomey doesn't write parquet; health-check freshness rule is unaffected

Severity: low
Confidence: high
Disposition: resolved

Observation:

Kalkomey produced 0 yielded records today, so no
`raw/rippling/kalkomey/` parquet was written. `health_check.py`
queries the R2 zone for slugs that have ever produced parquet;
kalkomey will not appear in that result set until a future run
yields a match. This is the same edge case as page/regrid +
sitemap/gohunt + greenhouse/floodbase. The freshness rule is
designed to handle it (FIND-002 of v1 actions-cron critique
already documents this).

Why it matters:

Confirming: no false-positive risk from adding a 0-yield slug.

Follow-up:

None.

Challenges: None - not claim-specific.

## FIND-007: Workflow now runs 5 source kinds; cron HTTP volume + duration acceptable

Severity: low
Confidence: medium
Disposition: open

Observation:

Workflow runs 5 per-source steps + apply_views + health_check.
Total wall-clock per cron firing has grown but stays well under 1
minute (per recent run evidence: ~12s extract phase + ~3s view
apply + ~2s health). Rippling adds one more API request per cron
(currently 6 jobs scope; trivial volume).

Why it matters:

No throttling concern at this scale. If the watch list grows past
~20 boards or any single board crosses 1k roles, revisit.

Follow-up:

Defer. PM5 retro re-evaluates.

Challenges: None - not claim-specific.

# Evidence Reviewed

- `ticket:vr6iel5o` — Acceptance + Evidence + Critique Disposition.
- `packet:ralph-rippling-kalkomey-20260502T133231Z` — Child Output
  + Parent Merge Notes.
- Working-tree files listed under Review Target.
- Live observation outputs (standalone + chained run, R2 layout,
  view counts).
- Predecessor critiques: `critique:ashby-mapbox-iter1` (Wave 2 v1
  schema-fitness lessons), `critique:actions-cron-iter1` (Wave 3
  v1 workflow lessons), `critique:sitemap-gohunt-iter1` +
  `critique:page-monitor-iter1` (0-yield posture precedents).

# Residual Risks

- Wiki currently does NOT have a Rippling-specific section
  (FIND-001/002/003); future Rippling-hosted boards or critique
  passes will re-derive without it. Mitigated by promoting during
  PM5 retro.
- The `STALE_THRESHOLD_HOURS=36` carryover (FIND-005) does not
  yet flag this iteration as risky; tightening waits for the
  initiative close-out.

# Required Follow-up

Before AC4 (manual workflow_dispatch on the new shape):

- Parent commits + pushes; runs `gh workflow run refresh.yml`;
  records run URL.

After PM5 retro:

- Update `wiki:extractor-shape` with Rippling additions to:
  - role_id strategies table (FIND-001)
  - Defensive listed/published checks per-source-kind table
    (FIND-002)
  - posted_at semantic table (FIND-003)

# Acceptance Recommendation

`active follow-up required`.

This iteration's artifacts are correct and verified locally. AC1–
AC7 satisfied; only post-merge AC validation (manual workflow
dispatch on the new shape, then natural cron firings) remains.
Ticket may close after the manual dispatch succeeds; the wiki
updates land at PM5 retro per established initiative pattern.
