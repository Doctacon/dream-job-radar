---
id: ticket:usz502u5
kind: ticket
status: closed
change_class: code-behavior
risk_class: high
created_at: 2026-04-30T03:06:26Z
updated_at: 2026-05-02T12:56:43Z
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
  predecessor:
    - ticket:gjkpkpum
    - ticket:tiv8bsu7
    - ticket:oy172mt9
    - ticket:xwfvoj4o
    - ticket:k0ftbmsi
external_refs: {}
depends_on:
  - ticket:k0ftbmsi
---

# Summary

Wave 3 / PM3: schedule the radar pipeline on GitHub Actions cron
with per-source error isolation, an idempotent view-apply step, and
basic N→0 health detection. Goal: one full week of clean
unattended scheduled runs, then PM3 closes.

# Context

PM2 of `plan:v1-radar` is closed (2026-04-30). All four v1 source
kinds run end-to-end via the meta-runner; per-source entry points
exist for every source kind. The pipeline has been exercised
manually multiple times across the four kinds. View row counts
today: greenhouse/onxmaps=8, greenhouse/planetlabs=36,
ashby/Mapbox=59, sitemap/gohunt=0, page/regrid=0, page/felt=1.

Per W0 acceptance, GitHub Actions secrets are already configured
on the repo: `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`,
`R2_ACCOUNT_ID`, `R2_BUCKET`, `MOTHERDUCK_TOKEN`.

This ticket inherits two explicit Wave 2 critique inputs:

- **Page-monitor regex fragility** (FIND-001 in
  `critique:page-monitor-iter1`). Webflow / Tailwind regenerations
  on Felt or Regrid silently produce 0 matches. Wave 3 must alert
  on per-(source_kind, ats_slug) N→0 transitions, not just on
  pipeline failure.
- **Per-source-kind health checks** (FIND-007 same critique). 4
  source kinds × 7 ATS slugs × 2 distinct role_id semantics ⇒ a
  single binary "is it working" alert is too coarse.

Plus one carried Wave 1 deferral:

- **Scripted view-apply** (FIND-008 in
  `critique:walking-skeleton-iter1`). The README's shell-quoted
  Python one-liner that materializes `motherduck/views.sql` is too
  brittle for cron. Wave 3 owns replacing it with a real Python
  runner.

# Why Now

PM2 just closed and the pipeline is stable enough to schedule.
Without a scheduled refresh:

- the Dive shows snapshot data that drifts as roles open and close
- the operator must manually run `pipelines.radar` to refresh
- nothing detects when an upstream HTML change quietly breaks a
  page-monitor parser

Scheduling closes that gap and produces one of the initiative's
explicit success metrics: "data freshness measured in hours, not
weeks".

# Scope

- Add `scripts/apply_views.py` (replaces the README one-liner):
  - `load_dotenv()`, read `motherduck/views.sql`, substitute
    `${R2_BUCKET}`, execute against `md:?motherduck_token=...`.
  - Idempotent (`CREATE OR REPLACE VIEW`).
  - Print "view materialized" on success; non-zero exit on
    failure.
  - Invocation: `uv run python scripts/apply_views.py`.

- Add `scripts/health_check.py`:
  - Connect to MotherDuck via `MOTHERDUCK_TOKEN`.
  - For each `(source_kind, ats_slug)` ever observed in the parquet
    (i.e., looking across the full R2 history, not just the
    current view), compute the latest-fetch row count.
  - Compare against the row count from the prior fetch.
  - If any slug went from `prior > 0` to `current == 0`, exit
    non-zero (workflow step fails). Print which slug, prior count,
    current count.
  - If no prior fetch exists for a slug, it is a new slug — report
    informationally but do not fail.
  - Must work against the R2 raw zone directly (DuckDB
    `read_parquet` glob), not just the deduped view.
  - Invocation: `uv run python scripts/health_check.py`.

- Add `.github/workflows/refresh.yml`:
  - Trigger: `schedule: cron: "0 12 * * *"` (daily at 12:00 UTC —
    safely after most timezone-shifted upstream cron updates) plus
    `workflow_dispatch` for manual runs.
  - Single job on `ubuntu-latest`. Sets up `uv` (the official
    `astral-sh/setup-uv` action) and Python.
  - `uv sync` to install deps.
  - One step per source kind, calling the per-source entry point.
    Each step uses `continue-on-error: true` so one source failing
    does not block the others. The job records each step's outcome.
  - After the four source steps, run `apply_views.py` (always —
    even if a source failed, the view DDL is idempotent and
    re-running it is safe).
  - Run `health_check.py` as a final required step (no
    `continue-on-error`). Failure here fails the job and surfaces
    via GitHub's normal email-on-failure.
  - Concurrency: `concurrency: { group: refresh, cancel-in-progress:
    false }` so two runs do not stomp on each other.
  - Permissions: minimal (`contents: read` only — no GITHUB_TOKEN
    usage needed).
  - Secrets: pull all five from GitHub Actions secrets into env.

- Update `README.md`:
  - Replace the materialize one-liner with a pointer to
    `scripts/apply_views.py`.
  - Add a "Scheduled refresh" section pointing at the workflow
    file.
  - Document the daily cron schedule and the
    `workflow_dispatch` manual-run path.

# Non-goals

- No alerting via Slack / email / webhook beyond GitHub's built-in
  email-on-failure (which fires when any required step fails). If
  alert fan-out is needed later, a future ticket can wire it.
- No pipeline reorganization. Per-source entry points already
  exist; this ticket consumes them.
- No retry-with-backoff on transient HTTP failures inside an
  extractor — one failed step in one cron run is acceptable; the
  next run picks it up. Reconsider only if a real failure pattern
  emerges across the one-week observation window.
- No metric storage table. Health-check is a per-run computation;
  a long-tail metrics table is future work.
- No view shape changes.

# Acceptance Criteria

1. `uv run python scripts/apply_views.py` runs locally, materializes
   the view server-side, and prints `view materialized`. Subsequent
   runs are idempotent.
2. `uv run python scripts/health_check.py` runs locally and
   succeeds against the current R2 + MotherDuck state. Exits 0
   when no slug regressed.
3. `.github/workflows/refresh.yml` validates locally with
   `gh workflow view` (or simply parses cleanly via `actionlint` if
   available) and is recognized by GitHub once pushed.
4. A manual `gh workflow run refresh.yml` (or the GitHub UI's
   "Run workflow" button) succeeds end-to-end. All four
   per-source steps complete; view-apply succeeds; health-check
   passes.
5. The first scheduled cron run that fires after the merge
   succeeds end-to-end with no failed steps.
6. After one week of scheduled runs, every cron firing has either
   succeeded or failed only on a single per-source step that the
   `continue-on-error: true` flag caught (no health-check failures
   that should have been transient). One-week observation period
   is acceptance, not deferred to a separate ticket.
7. README documents the scheduled refresh and the new scripts.

# Coverage

Ticket-local. No spec contract. `wiki:extractor-shape` covers
extractor shape; this ticket is purely infra.

# Claim Matrix

None — no spec contract; ticket-local acceptance criteria only.

# Execution Notes

- Cron timing: `0 12 * * *` (daily at 12:00 UTC = 5am Pacific /
  8am Eastern). Most upstream ATS daily-cron-job updates land in
  US business hours, so a noon-UTC fire reads after they settle.
  Adjustable later.
- `health_check.py` algorithm:
  - DuckDB `read_parquet('r2://<bucket>/raw/*/*/*.parquet',
    filename=true, union_by_name=true)`.
  - WHERE `filename NOT LIKE '%/_dlt_%'` and `source_kind`,
    `ats_slug`, `role_id` IS NOT NULL (mirror view guards).
  - Group by `source_kind, ats_slug, fetched_at` to get
    per-fetch counts.
  - For each `(source_kind, ats_slug)`, sort by `fetched_at` desc,
    pick top 2. If prior > 0 and latest == 0, alert.
  - Edge case: only one fetch ever (new slug). Report, do not
    fail.
- The workflow's per-source steps should each cite the specific
  entry point: `pipelines.greenhouse` (NB: greenhouse currently
  runs through `pipelines.radar`'s `run_greenhouse()`; the cleanest
  Wave 3 step calls it via the meta-runner with a flag, OR the
  greenhouse logic is split into `pipelines/greenhouse.py` for
  symmetry). Decide during implementation; the cleanest API for
  Wave 3 isolation is one entry point per source kind.
- `actionlint` is the standard linter for GitHub Actions YAML.
  Optional but recommended.

# Blockers

None.

# Next Move / Next Route

Ralph implementation packet. New code (two scripts), new YAML
file, README update. Bounded write boundary. High risk
(automation + production-shaped + secrets), so critique is
mandatory.

# Ralph Readiness

Bounded iteration: two new Python scripts + one new YAML workflow
+ README extension. Possibly a small split of `pipelines/radar.py`
into `pipelines/greenhouse.py` for per-source step symmetry.

Write boundary:
- `scripts/apply_views.py`
- `scripts/health_check.py`
- `.github/workflows/refresh.yml`
- `README.md`
- `src/dream_job_radar/pipelines/greenhouse.py` (only if the
  implementer decides per-source step symmetry warrants it; the
  alternative is to call `pipelines.radar` with a `--source` flag
  but that's a wider refactor)
- `src/dream_job_radar/pipelines/radar.py` (only if needed for the
  greenhouse split)

Verification posture: `observation-first`. Evidence is the local
runs of both scripts plus a manual `gh workflow run` (or its
GitHub UI equivalent).

Expected output contract:
- working `scripts/apply_views.py` and `scripts/health_check.py`
- a passing `actionlint` (or hand-validated) workflow file
- the manual workflow-dispatch run completes green
- the first scheduled run completes green
- the one-week observation window is parent work after the child
  returns; not a Ralph iteration scope

# Evidence

Expected on completion (initial Ralph + acceptance window):

- terminal output of `scripts/apply_views.py` (idempotent re-run).
- terminal output of `scripts/health_check.py` (current state).
- the workflow YAML (full file inline OR linked) plus its first
  successful manual-dispatch run URL on GitHub.
- the first scheduled-run URL after merge.
- the seven scheduled-run URLs covering the one-week window.

Captured 2026-04-30T03:25Z (Ralph iteration 1):

AC1 — `apply_views.py` runs idempotently:
```
$ uv run python scripts/apply_views.py
view materialized
$ uv run python scripts/apply_views.py
view materialized
```

AC2 — `health_check.py` runs locally and exits 0:
```
[health] checking 4 observed slug(s); stale threshold = 36h
[health] ok    ashby/Mapbox latest=...-07:00 (0.4h old) latest_count=59
[health] ok    greenhouse/onxmaps latest=...-07:00 (0.4h old) latest_count=8
[health] ok    greenhouse/planetlabs latest=...-07:00 (0.4h old) latest_count=36
[health] ok    page/felt latest=...-07:00 (0.4h old) latest_count=1
[health] PASS
```

AC3 — workflow YAML written; hand-validated against the packet
contract. Verified: triggers (cron + workflow_dispatch),
concurrency, permissions, env-from-secrets at job level,
per-source `continue-on-error: true` with stable step ids,
view-apply with `if: always()`, health-check required.
`actionlint` not on PATH locally; GitHub's parser will be the
final validator on push.

Greenhouse split verified — per-source entry point works
end-to-end and the all-sources radar meta-runner still chains
all four pipelines without row-count regression.

AC4 — satisfied 2026-04-30T03:40:14Z. Manual workflow_dispatch
run completed in 41s, conclusion `success`. All steps green:
checkout, setup-uv, uv sync, greenhouse, ashby, sitemap, page,
apply_views, health_check.
Run URL:
`https://github.com/Doctacon/dream-job-radar/actions/runs/25146099357`.
Cosmetic warnings (Node.js 20 deprecation notice, transient
GitHub cache-service failure) noted but not load-bearing.

AC5 — closed by parent acceptance 2026-05-02. First scheduled
cron firings (runs `25244430806`, `25244696172`) initially failed
because the MotherDuck-side R2 SECRET held stale keys after a
Cloudflare R2 token rotation. Fix landed: drop+recreate the
MotherDuck `dream-job-radar` SECRET with the working keys (now in
GH Actions secrets + local `.env`). Subsequent runs are expected
to be green; parent accepts the AC without waiting for the next
cron firing.

AC6 — closed by parent acceptance 2026-05-02. One-week
observation window dropped from acceptance scope; the workflow
will keep running but is no longer a gate for this ticket. If
issues surface, they will be picked up in a follow-up initiative.

AC7 — README updated: pointer to `apply_views.py`, pointer to
`health_check.py`, "Scheduled refresh" section documenting the
workflow shape + cron schedule + manual dispatch path + the
five required secrets.

# Critique Disposition

Risk class: high

Critique policy: mandatory

Policy rationale: this is the first ticket that ships automation.
Cron + secrets + per-source error handling + alert-on-regression
are all production-shaped surfaces. A subtly wrong workflow could
silently miss broken sources for a week; a subtly wrong
health-check could flap on routine 0-match outcomes (sitemap/gohunt
is `0` today legitimately) and erode trust in the alert.

Required critique profiles:
- code-quality (workflow shape, error handling, secret hygiene,
  health-check algorithm)
- ops-fitness (cron timing, per-source isolation correctness,
  health-check false-positive rate, behavior under transient
  upstream failures)

Findings: see `critique:actions-cron-iter1` (10 findings; 3
medium, 7 low; none `changes_required`). Verdict:
`pass_with_findings`.

Disposition status: resolved-with-followup. FIND-001 (tighten
threshold to 26h after AC6 passes), FIND-002 (wiki the
freshness-vs-row-count rationale), FIND-007 (per-step env: to
minimize secret exposure to third-party actions), FIND-010
(time-dependent acceptance) all deferred to retrospective + AC6
window. FIND-004 / FIND-006 resolved by inspection. None block
ticket closure conceptually; AC4–AC6 are time/parent-gated.

Deferral / not-required rationale: N/A — mandatory critique
performed.

# Wiki Disposition

Likely a new wiki page: `wiki:scheduled-refresh` — covers the
workflow shape, the health-check algorithm, the operator-facing
"what to do when the alert fires" runbook. Decide during
post-closure retrospective.

# Acceptance Decision

Accepted by: Connor
Accepted at: 2026-05-02T12:56:43Z
Basis: AC1–AC4 + AC7 satisfied with observation-first evidence
(see Evidence section). AC5 (first scheduled cron firing) hit a
real-world incident — the user rotated the Cloudflare R2 API
token; GH Actions + `.env` were updated, but the MotherDuck
server-side R2 SECRET was not. Two cron firings failed at
`Apply MotherDuck views` until the SECRET was dropped and
recreated. Parent accepts the AC after the SECRET fix; subsequent
cron firings are expected green. AC6 (one-week observation
window) explicitly dropped from acceptance scope to unblock the
initiative close-out.
Residual risks:
- AC6 not gathered. If a future failure pattern emerges, will be
  picked up in a follow-up initiative.
- FIND-001 (tighten `STALE_THRESHOLD_HOURS` to 26) deferred.
- FIND-002 (wiki-promote the freshness-vs-row-count rationale)
  deferred.
- FIND-007 (per-step `env:` for secret minimization) deferred.
- The R2-rotation incident is a useful surfaceable lesson; not
  promoted to wiki today (initiative is closing).

# Dependencies

Hard prerequisites:
- All Wave 2 tickets (`tiv8bsu7`, `oy172mt9`, `xwfvoj4o`,
  `k0ftbmsi`) closed. Done as of 2026-04-30.
- Wave 0 (`9mtt9h6j`) provided GitHub Actions secrets. Done.

Soft references:
- `wiki:extractor-shape` — describes per-source-kind shape.
- All Wave 1+2 critiques — encode the inheritance constraints
  this ticket must honor.

# Journal

- 2026-04-30 — ticket created from `plan:v1-radar` Wave 3 after
  PM2 closed. Risk classified `high`; critique `mandatory` with
  two named profiles (code-quality, ops-fitness). Inherits FIND-001
  + FIND-007 from `critique:page-monitor-iter1` and FIND-008 from
  `critique:walking-skeleton-iter1`. Next route: Ralph
  implementation packet.
- 2026-04-30 — Ralph packet compiled at
  `.loom/packets/ralph/actions-cron-20260430T031009Z.md` (style:
  reference-first, posture: observation-first, source SHA
  `91b174d`). Awaiting child execution. Note: child ships the
  artifacts (scripts + workflow); AC5 (first scheduled run) and
  AC6 (one-week window) are explicit parent acceptance work after
  the child returns.
- 2026-04-30 — Ralph iteration 1 returned `continue`. Two scripts
  + workflow YAML + greenhouse split shipped. Health-check
  algorithm pivoted from row-count "N→0" to freshness staleness
  because dlt does not write parquet for 0-yield runs (the
  packet's literal check was unimplementable; the freshness check
  captures the same FIND-001 scenario without false positives on
  0-match-honest sources). Both scripts run locally; greenhouse
  per-source entry point verified; radar meta-runner still chains
  all four pipelines. Status → `review_required`. Critique pass
  next.
- 2026-04-30 — Mandatory critique landed at
  `.loom/critique/actions-cron-iter1.md`. Verdict
  `pass_with_findings`; 10 findings (3 medium, 7 low), none
  `changes_required`. Acceptance recommendation: "active
  follow-up required" — do not close today; AC4 (manual dispatch),
  AC5 (first scheduled run), AC6 (one-week window) require
  parent + time. Ticket stays `review_required` until parent
  merges and exercises the workflow.
- 2026-04-30 — Parent pushed; manual `gh workflow run refresh.yml`
  completed end-to-end in 41s. Run URL
  `https://github.com/Doctacon/dream-job-radar/actions/runs/25146099357`,
  conclusion `success`. AC4 satisfied. Status →
  `complete_pending_acceptance`. AC5 + AC6 still gated on time
  (first scheduled firing + one-week window).
- 2026-05-02 — R2 token rotation incident. Cloudflare R2 API token
  rotated (proactive); GH Actions secrets + local `.env` updated,
  but MotherDuck server-side R2 SECRET held the stale credentials.
  Cron runs `25244430806` and `25244696172` failed at
  `Apply MotherDuck views` with
  `_duckdb.HTTPException: HTTP Error: Permission error: Missing or
  invalid credentials`. Fix: drop+recreate
  `CREATE OR REPLACE SECRET dream-job-radar IN MOTHERDUCK (TYPE R2,
  ...)` from the new keys. Local `apply_views.py` confirmed green
  after fix.
- 2026-05-02 — Parent closed `initiative:close-the-loop` and all
  underlying records to free up bandwidth for new work. AC5 + AC6
  dropped from acceptance scope; the workflow continues to run on
  cron but is no longer a gate. Status → `closed`.
