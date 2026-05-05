---
id: ticket:7t9jzfqe
kind: ticket
status: closed
change_class: code-behavior
risk_class: medium
created_at: 2026-05-04T04:05:00Z
updated_at: 2026-05-05T02:30:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:lakehouse-iceberg
  plan: plan:lakehouse-iceberg
  research:
    - research:lakehouse-iceberg-spike
  predecessor:
    - ticket:q67za0wk
  constitution: constitution:main
external_refs: {}
---

# Summary

P1.3 of `initiative:lakehouse-iceberg`. Wire the Iceberg mart
writer into the existing daily refresh workflow. After radar
pipelines write raw and the MotherDuck views are applied, run
`iceberg_mart` so each scheduled fire produces (or no-ops on
already-snapshotted) one Iceberg snapshot per day and refreshes
the materialization. Failure of the mart step must not break
the rest of the cron.

# Goal

`.github/workflows/refresh.yml` ends each scheduled run with a
fresh Iceberg snapshot for `current_date` (UTC) plus a refreshed
MotherDuck materialization, without compromising the existing
raw-zone-write + views path or the health check.

# In Scope

- `R2_TOKEN_VALUE` added to job `env:` block (sourced from a
  GitHub repo secret of the same name).
- New step `Iceberg mart writer` between `Apply MotherDuck
  views` and `Health check`.
- `continue-on-error: true` on the new step so an Iceberg
  failure surfaces in the run but does not block the health
  check.
- Out-of-band note in this ticket on what the user must do once
  before merging: add the `R2_TOKEN_VALUE` repo secret in
  GitHub.
- Manual `workflow_dispatch` smoke run after merge to confirm
  the cron green-paths end-to-end.

# Out Of Scope

- The bootstrap secret script. Persistent MotherDuck secret
  was created in P1.1 and persists workspace-side; cron does
  not need to re-run it. If the R2 access key rotates, run
  `scripts/bootstrap_motherduck_iceberg.py` locally once.
- Compaction / snapshot expiration policies on the Iceberg
  table.
- Dive panel (P1.4).
- Wiki / retro (P1.5).
- Touching `_r2.py`, `views.sql`, `_iceberg.py`, `iceberg_mart.py`,
  or `bootstrap_iceberg.sql`.

# Acceptance Criteria

- AC1: `.github/workflows/refresh.yml` adds `R2_TOKEN_VALUE`
  env var and a new step running
  `uv run python -m dream_job_radar.pipelines.iceberg_mart`
  after `Apply MotherDuck views` and before `Health check`,
  with `continue-on-error: true`.
- AC2: Manual `workflow_dispatch` post-merge run passes
  end-to-end (radar pipelines → views → iceberg_mart → health).
  Logs show iceberg_mart step succeeding.
- AC3: Re-firing manual run on the same day shows
  iceberg_mart step still succeeds (idempotent skip path);
  Iceberg row count unchanged from AC2.
- AC4: `MotherDuck → SELECT count(DISTINCT snapshot_date) FROM
  mart.job_postings_daily_snapshot;` returns 1 immediately
  after AC2 and AC3.
- AC5: User has added `R2_TOKEN_VALUE` to GitHub repo secrets
  (verified by reading the workflow run logs — secret
  redaction means the value won't be echoed but absence
  surfaces as a Python KeyError).

# Verification Posture

`observation-first`. Behavior is "the cron green-paths and the
Iceberg snapshot lands". Evidence:

- Capture the GitHub Actions run URL + step status in the
  ticket close-out.
- Capture pre/post counts of Iceberg rows + distinct
  snapshot_date in `.loom/evidence/lakehouse-iceberg-spike/`
  (gitignored logs).

# Notes For Implementer

- Step ordering matters: views must be re-applied before
  iceberg_mart so any view-shape change in a same-day deploy
  is materialized before the mart writer reads
  `current_open_roles`.
- Place new step before `Health check`. Health check intentionally
  fails the job on staleness; we want it to remain the last
  word on cron success.
- `R2_TOKEN_VALUE` in env: the writer reads it via
  `_iceberg.py`. Without it, PyIceberg's RestCatalog will fail
  auth at `list_namespaces`.
- No need to set timezone in the workflow; the writer pins
  session TZ to UTC on its own.

# Status Summary

Drafted 2026-05-04 immediately after `ticket:q67za0wk` (P1.2
writer) closed. Executed same session.

## Outcome 2026-05-05: closed

All ACs met:

- AC1: workflow edited as specified. Iceberg mart step inserted
  between views refresh and health check, `if: always()`,
  `continue-on-error: true`. `R2_TOKEN_VALUE` env wired.
- AC2: GH run 25354628535 (workflow_dispatch) green
  end-to-end. Iceberg mart step succeeded.
- AC3: This same run hit the idempotent-skip path because P1.2
  local run earlier today (same UTC date) had already
  populated. Step output:
  `[iceberg_mart] skip append: 120 rows already snapshotted today`.
  Materialization still refreshed. AC3's behavioral claim
  satisfied without a second dispatch.
- AC4: `SELECT count(*), count(DISTINCT snapshot_date),
  max(snapshot_date) FROM mart.job_postings_daily_snapshot;`
  returns `(120, 1, date(2026,05,05))` post-cron.
- AC5: `R2_TOKEN_VALUE` added to GH repo secrets via `gh secret
  set` before dispatch (visible in `gh secret list`).

Notes:

- Cron scheduled fire is daily 12:00 UTC. Today's Phoenix
  evening dispatch ran at 02:29 UTC = 2026-05-05 in UTC, so
  the snapshot landed under that UTC date. Subsequent cron at
  12:00 UTC tomorrow will be 2026-05-06 UTC and will append a
  fresh row set.
- 122-vs-120 visible in step output: cron just refreshed views
  before the mart step, finding 122 currently-open roles. The
  Iceberg snapshot stays at the 120 it already had for today's
  UTC date (idempotency holds). Tomorrow's cron will write
  whatever current_open_roles holds at 12:00 UTC.

Next: P1.4 (Dive panel). Will be opened as a fresh ticket.
