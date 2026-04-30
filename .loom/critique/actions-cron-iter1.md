---
id: critique:actions-cron-iter1
kind: critique
status: final
created_at: 2026-04-30T03:23:14Z
updated_at: 2026-04-30T03:23:14Z
scope:
  kind: repository
  repositories:
    - repo:root
review_target: ticket:usz502u5 (Ralph iteration 1)
links:
  ticket: ticket:usz502u5
  packet: packet:ralph-actions-cron-20260430T031009Z
  plan: plan:v1-radar
  wiki: wiki:extractor-shape
  predecessor_critique: critique:page-monitor-iter1
external_refs: {}
---

# Summary

Mandatory critique of Wave 3 / PM3 (GitHub Actions cron + scripts +
health check). Profiles per ticket Critique Disposition:
code-quality, ops-fitness. This is the first ticket that ships
production-shaped automation; the critique posture is
deliberately stricter than Wave 2.

# Review Target

- Ticket: `ticket:usz502u5`
- Packet: `.loom/packets/ralph/actions-cron-20260430T031009Z.md`
- Working tree at parent reconciliation:
  - `scripts/apply_views.py` (new)
  - `scripts/health_check.py` (new)
  - `.github/workflows/refresh.yml` (new)
  - `README.md` (extended)
  - `src/dream_job_radar/pipelines/greenhouse.py` (new)
  - `src/dream_job_radar/pipelines/radar.py` (rewritten as thin
    meta-runner)
- Evidence: ticket Evidence section + packet Child Output.

# Verdict

`pass_with_findings`.

The implementation meets AC1–AC3 and AC7 with truthful
observation-first evidence. AC4–AC6 are parent-acceptance work
post-merge. The health-check pivot (row-count → freshness) is the
right call given dlt's 0-yield behavior; the workflow shape is
correct and minimal. Findings are calibration / hardening notes
for the one-week observation window and follow-up tickets, not
blockers.

# Findings

## FIND-001: 36h staleness threshold is conservative; tighten after observation window

Severity: medium
Confidence: high
Disposition: open

Observation:

`scripts/health_check.py` uses `STALE_THRESHOLD_HOURS = 36`. Cron
runs every 24h, so a normal sequence is: T0 cron, T+24h cron,
T+48h cron. A slug's `latest_fetched` ages from 0h to ~24h between
cron runs and back to ~0h after each successful fetch. The 36h
threshold tolerates one missed cron before alerting — generous
buffer for the first weeks.

Why it matters:

Once the AC6 one-week observation window passes cleanly, the
threshold should tighten to ~26h (1.08× cron interval) so a
single missed run produces an alert instead of being silently
absorbed.

Follow-up:

After AC6 passes (one week of green runs), open a small follow-up
ticket OR direct edit to drop `STALE_THRESHOLD_HOURS` to 26.
Defer until the one-week data exists.

Challenges: None - not claim-specific.

## FIND-002: Health-check pivot from row-count to freshness — algorithm choice deserves wiki capture

Severity: medium
Confidence: high
Disposition: open

Observation:

The packet specified a row-count "prior > 0, latest == 0" check.
The child correctly identified that this is unimplementable
because dlt does not write parquet for 0-yield runs — there is no
"latest == 0" parquet row to detect. The freshness check
("prior parquet existed, but the most-recent fetched_at is older
than threshold") captures the same FIND-001 page-monitor regex-
fragility scenario without false positives on 0-match-honest
sources.

Why it matters:

This is a non-obvious dlt property worth preserving. Future
authors who try to add a per-row health check will hit the same
wall.

Follow-up:

Update `wiki:extractor-shape` (or open a sibling
`wiki:scheduled-refresh` page) during the post-closure
retrospective: document that dlt 0-yield does not produce
parquet, and that freshness is the load-bearing signal for
"extractor silently broke".

Challenges: None - not claim-specific.

## FIND-003: Workflow has no per-source-step `outputs` for downstream visibility

Severity: low
Confidence: medium
Disposition: open

Observation:

Each per-source step has a stable `id:` (greenhouse, ashby,
sitemap, page) but does not export `outputs`. Downstream steps
(view-apply, health-check) cannot inspect which source steps
failed, only check global `success()` / `failure()`.

Why it matters:

Today health-check is the load-bearing failure detector — it
catches the staleness regardless of which source step failed. So
the missing outputs are not a defect today. But if future
iterations want a per-source GitHub status badge, or want to skip
view-apply when ALL sources failed (so as not to mask the failure
behind a healthy view), they will need step outputs.

Follow-up:

Defer. Add when concrete downstream logic needs them.

Challenges: None - not claim-specific.

## FIND-004: View-apply runs on `if: always()` even if every source failed

Severity: low
Confidence: high
Disposition: open

Observation:

`scripts/apply_views.py` is `if: always()` so the view DDL is
re-applied even if all four source steps failed. The view DDL is
idempotent; re-applying changes nothing. The view does NOT
re-fetch parquet — it just re-defines the SELECT. So this is
safe.

Why it matters:

Confirming the safety: `CREATE OR REPLACE VIEW` does not touch
data; only the view definition. Even with stale or zero parquet,
the view continues to read whatever is in R2.

Follow-up:

None. Resolved by inspection.

Challenges: None - not claim-specific.

## FIND-005: Concurrency group ungated by ref/branch

Severity: low
Confidence: high
Disposition: open

Observation:

`concurrency: { group: refresh, cancel-in-progress: false }`.
Single global group across all branches. If the workflow ever
runs on a feature branch (it cannot today — only `schedule` and
`workflow_dispatch` triggers fire), it would queue behind main's
schedule.

Why it matters:

Today only main runs the workflow (no `pull_request` or `push`
triggers). Concurrency design is fine for v1.

Follow-up:

If Wave 4+ adds branch-based triggers, group becomes
`refresh-${{ github.ref }}` then.

Challenges: None - not claim-specific.

## FIND-006: Setup-uv `@v3` major-pin keeps automatic upgrades; acceptable

Severity: low
Confidence: high
Disposition: resolved

Observation:

`astral-sh/setup-uv@v3` and `actions/checkout@v4` are major-pinned.
Both vendors maintain semver-clean major lines; auto-updating
within a major is the right tradeoff for a personal-scale repo.

Why it matters:

Confirming: this is what the packet asked for and what the
implementation delivered.

Follow-up:

None.

Challenges: None - not claim-specific.

## FIND-007: Secrets are job-level env; visible to every step including third-party actions

Severity: medium
Confidence: high
Disposition: open

Observation:

All five secrets are exposed at job-level `env:`. The
`actions/checkout@v4` and `astral-sh/setup-uv@v3` actions
therefore receive them in their own process environment. Both are
trusted publishers (GitHub, Astral) but technically have access.

Why it matters:

The cleaner posture is to set `env:` on the specific steps that
need each secret — checkout needs none, setup-uv needs none, only
the per-source steps + apply_views + health_check need them.
Step-level `env:` would minimize the secret surface.

The current shape is the standard Actions idiom and acceptable for
v1. But this is a worthwhile hardening for a future iteration.

Follow-up:

Open a follow-up note for retrospective: consider per-step `env:`
to minimize secret exposure to third-party actions. Defer until
the workflow stabilizes.

Challenges: None - not claim-specific.

## FIND-008: No retry-with-backoff on transient HTTP failures

Severity: low
Confidence: medium
Disposition: open

Observation:

Per packet non-goals: no retry-with-backoff on transient HTTP
failures. A flaky upstream causes one source step to fail; next
cron run picks it up. AC6 (one-week window) is the test.

Why it matters:

Acceptable for v1 personal scale. Five upstream sources × 1
fetch/day = ~5 fetches/day. Failure rate on any single fetch is
likely < 5%. Tolerable.

Follow-up:

If the one-week observation window shows a recurring transient
failure pattern on a specific source, add retry then.

Challenges: None - not claim-specific.

## FIND-009: Sitemap polite sleep is hard-coded; same module-level constant as v1

Severity: low
Confidence: high
Disposition: open

Observation:

`extractors/sitemap.py` `PAGE_FETCH_DELAY_S = 0.5` (carried from
Wave 2 #4). On daily cron, total sleep ~2s for 4 GoHunt URLs —
trivial. On a future scale-up (more URLs per source), this
becomes meaningful.

Why it matters:

Already noted in FIND-005 of `critique:sitemap-gohunt-iter1`.
Carried forward but not promoted to a ticket. Wave 3 cron does
not change this either way.

Follow-up:

Defer to the same retrospective trigger as the original FIND. No
new follow-up.

Challenges: None - not claim-specific.

## FIND-010: AC6 one-week observation window depends on the user, not the implementation

Severity: low
Confidence: high
Disposition: open

Observation:

AC6 explicitly requires seven scheduled-run URLs covering one
week of clean unattended runs. This Ralph iteration cannot satisfy
it; only time can. The ticket Acceptance Decision should record
this with a target date.

Why it matters:

The ticket cannot legitimately move from `review_required` to
`complete_pending_acceptance` until AC4 succeeds (manual
dispatch); it cannot move from `complete_pending_acceptance` to
`closed` until AC5 + AC6 are satisfied with evidence URLs.

Follow-up:

After parent merges + the manual workflow_dispatch run completes:
advance ticket from `review_required` to
`complete_pending_acceptance`. Record the manual-dispatch run URL
in Evidence. Schedule a follow-up agent to revisit after the
one-week window passes.

Challenges: None - not claim-specific.

# Evidence Reviewed

- `ticket:usz502u5` — full Acceptance + Evidence + Critique
  Disposition.
- `packet:ralph-actions-cron-20260430T031009Z` — Child Output and
  Parent Merge Notes.
- Working-tree files listed under Review Target.
- Live observation outputs (apply_views.py x2, health_check.py,
  greenhouse standalone, radar all-sources).
- Predecessor critiques `critique:walking-skeleton-iter1` (FIND-008
  scripted view-apply) and `critique:page-monitor-iter1`
  (FIND-001 + FIND-007 carried into this ticket's design).

# Residual Risks

- Threshold value (36h) may produce false positives or false
  negatives at the edge cases; AC6's one-week window is the test
  (FIND-001).
- Job-level `env:` exposes secrets to third-party actions
  (FIND-007); standard idiom but worth tightening later.
- AC6 cannot be satisfied today (FIND-010); time-dependent
  acceptance is a property of the ticket, not a defect.
- No alert fan-out beyond GitHub email-on-failure (per packet
  non-goals); acceptable for v1.

# Required Follow-up

Before AC4:

- Parent merges this work, then runs `gh workflow run refresh.yml`
  (or UI button) to verify the dispatch path. Record run URL in
  ticket Evidence.

Before AC5:

- Wait for first scheduled cron firing after merge. Record run
  URL in ticket Evidence.

Before AC6:

- Wait for one full week of cron firings. Record all seven URLs.
- Critique recommends scheduling a `loom-schedule` agent or
  calendar reminder to verify after 7 days.

After AC6 (retrospective inputs):

- Update `wiki:extractor-shape` (or new
  `wiki:scheduled-refresh`): dlt 0-yield → no parquet → freshness
  is the load-bearing signal (FIND-002).
- Tighten `STALE_THRESHOLD_HOURS` to 26 (FIND-001).
- Consider per-step `env:` for secret minimization (FIND-007).

# Acceptance Recommendation

`active follow-up required`.

This iteration's artifacts are correct and verified locally. AC4–
AC6 are gated on parent acceptance work that requires push +
merge + GitHub-side runs. Ticket should remain in
`review_required` until AC4 succeeds, then advance to
`complete_pending_acceptance` while AC5 + AC6 accrue evidence.

Do NOT close this ticket today.
