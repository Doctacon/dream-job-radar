---
id: ticket:9mtt9h6j
kind: ticket
status: closed
change_class: code-behavior
risk_class: low
created_at: 2026-04-29T14:17:56Z
updated_at: 2026-04-29T14:17:56Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:close-the-loop
  plan: plan:v1-radar
  constitution: constitution:main
  decision: decision:0001-storage-backend-r2
  research: research:storage-backend
external_refs: {}
depends_on: []
---

# Summary

Provision the v1-radar infrastructure baseline: a Cloudflare R2 bucket
for pipeline output, an R2 API token scoped to that bucket, a MotherDuck
workspace authorized to read the bucket via a `TYPE R2` secret, a
`pyproject.toml`-based Python project managed with `uv`, and a GitHub
repo with the secrets the later wave will need. This is Wave 0 of
`plan:v1-radar`.

# Context

The repo currently contains only `.loom/`. No code, no R2 resources, no
MotherDuck workspace, no CI. Wave 1 (the walking skeleton) cannot begin
until each of those credentials and resources is live and proven to talk
to the next service in the chain.

Storage backend is Cloudflare R2 per `decision:0001-storage-backend-r2`,
not AWS S3. R2 exposes an S3-compatible API at
`https://<ACCOUNT_ID>.r2.cloudflarestorage.com`, so dlt's filesystem
destination configures with the same `aws_access_key_id` /
`aws_secret_access_key` shape plus `endpoint_url`.

# Why Now

Every later wave depends on this. The plan's whole strategy is "walking
skeleton first," and the skeleton cannot be walked without these surfaces
existing.

# Scope

- create a personal Cloudflare R2 bucket for pipeline output (private,
  Standard storage class)
- create an R2 API token scoped to read/write that bucket only; capture
  the access key id, secret access key, and account id
- create a MotherDuck workspace
- inside MotherDuck, create the R2 secret:
  ```sql
  CREATE SECRET IN MOTHERDUCK (
    TYPE R2,
    KEY_ID  '<access_key_id>',
    SECRET  '<secret_access_key>',
    ACCOUNT_ID '<cloudflare_account_id>'
  );
  ```
- initialize a Python project at the repo root with `uv` (`pyproject.toml`,
  `uv.lock`, `.python-version`)
- add `dlt` (with the `filesystem` extra), `boto3`, and `python-dotenv`
  as project dependencies
- add a `.gitignore` that excludes `.env`, `__pycache__`, `.venv`, dlt
  working directories, and any local credential file
- create a GitHub repo for this project and push the existing `.loom/`
  plus the new project skeleton
- store the following as GitHub Actions secrets on that repo:
  `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`,
  `R2_BUCKET`, `MOTHERDUCK_TOKEN`
- set Cloudflare billing email notifications at $1 and $5 thresholds
  (compensating control for the absent hard spend cap; expected to never
  fire given the workload is well inside R2's free tier)
- prove end-to-end credential reachability:
  - `uv run python -c "import boto3, os; s3 = boto3.client('s3',
    endpoint_url=f'https://{os.environ[\"R2_ACCOUNT_ID\"]}.r2.cloudflarestorage.com',
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY']);
    s3.head_bucket(Bucket=os.environ['R2_BUCKET'])"` succeeds locally
  - upload a one-row Parquet placeholder to the bucket and read it from a
    MotherDuck query using the R2 secret (evidence: query output)

# Non-goals

- no AWS account, no AWS S3 bucket, no IAM user — R2 only
- no extractor code (Wave 1)
- no MotherDuck view DDL beyond the credential proof query (Wave 1)
- no Dive (Wave 1)
- no GitHub Actions workflow file yet — only the secrets configuration
  (Wave 3 owns the workflow)
- no decisions about R2 prefix layout beyond "the bucket exists"; the
  walking-skeleton ticket will choose the prefix shape
- no DuckLake — `decision:0001-storage-backend-r2` keeps it out of v1
- no blog post infrastructure (Wave 4)

# Acceptance Criteria

1. R2 bucket exists, private, Standard storage class.
2. R2 API token exists, scoped to read/write that bucket.
3. Local `boto3.head_bucket` against the R2 bucket succeeds with the R2
   credentials and `endpoint_url` (evidence: terminal output).
4. MotherDuck workspace exists; R2 secret is created in MotherDuck;
   a query reads the placeholder Parquet from the bucket (evidence:
   query output).
5. `uv`-managed Python project committed to the repo with `dlt`
   (filesystem extra), `boto3`, and `python-dotenv` as dependencies.
   `uv sync` succeeds on a fresh clone.
6. `.gitignore` excludes credentials, virtualenv, and dlt scratch dirs.
7. Code is pushed to a GitHub repo, and required secrets
   (`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`,
   `R2_BUCKET`, `MOTHERDUCK_TOKEN`) are stored as Actions secrets.
8. Cloudflare billing notifications configured at $1 and $5 thresholds.

# Coverage

Covers: ticket-local acceptance criteria above. No spec exists yet for
this work.

# Claim Matrix

None — no spec contract; ticket-local acceptance criteria only.

# Execution Notes

- Per `CLAUDE.md`, `uv` is the package manager. Do not use `pip` or
  `poetry` here.
- R2 endpoint URL pattern:
  `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`. The `ACCOUNT_ID` comes
  from the Cloudflare dashboard, not the bucket name.
- R2 API token: create from Cloudflare dashboard → R2 → Manage R2 API
  Tokens. Choose "Object Read & Write" permission scoped to the one
  bucket.
- MotherDuck R2 secret syntax is `CREATE SECRET IN MOTHERDUCK (TYPE R2,
  KEY_ID, SECRET, ACCOUNT_ID)`. The UI path is Settings → Integrations
  → Secrets if SQL is inconvenient.
- The placeholder Parquet used to prove the MotherDuck read can be a
  one-row file generated locally with pyarrow or pandas; delete it
  after Wave 1 lands real data.
- Region: R2 is region-light; pick automatic placement unless data
  residency demands otherwise.

# Blockers

None.

# Next Move / Next Route

Local edit driven by the user. This ticket is mostly external account
setup (Cloudflare console / MotherDuck console / GitHub UI) plus a small
repo bootstrap commit. A Ralph packet would not help — too many
out-of-repo clicks. Move to `active` when the user begins.

# Ralph Readiness

Not applicable. Next route is local edit, not Ralph.

# Evidence

Expected on completion:

- terminal output of `boto3.head_bucket` succeeding against the R2
  endpoint
- terminal output (or screenshot) of a MotherDuck query reading the
  placeholder Parquet via the R2 secret
- `git log --oneline` showing the bootstrap commit on the new GitHub
  repo
- screenshot or `gh secret list` output confirming Actions secrets
  exist
- screenshot of Cloudflare billing notification thresholds

Captured:

- `uv run python scripts/smoke_r2.py` →
  `OK head_bucket pipelines via https://<account>.r2.cloudflarestorage.com`
  + `OK put_object s3://pipelines/smoke/placeholder.parquet`
- `uv run python scripts/smoke_motherduck.py` →
  `OK read r2://pipelines/smoke/placeholder.parquet` +
  `(1, 'dream-job-radar smoke')`
- `gh secret list` shows: `MOTHERDUCK_TOKEN`, `R2_ACCESS_KEY_ID`,
  `R2_ACCOUNT_ID`, `R2_BUCKET`, `R2_SECRET_ACCESS_KEY` (all set
  2026-04-29T22:53:27Z–22:53:30Z).
- Cloudflare billing notifications configured (two thresholds, user
  confirmed).
- GitHub repo: `Doctacon/dream-job-radar`.

# Critique Disposition

Risk class: low

Critique policy: optional

Policy rationale: configuration setup with no behavior surface. The
credentials and bucket scope are easy to verify directly; nothing
adversarial review would catch that direct verification would miss.

Required critique profiles: None - low risk, no behavior contract.

Findings: None - no critique yet.

Disposition status: not_required

Deferral / not-required rationale: optional critique with no expected
findings; user can request critique later if a security or scope concern
emerges.

# Wiki Disposition

No wiki promotion expected. Setup steps are one-time and well covered by
Cloudflare R2 / MotherDuck / GitHub vendor docs.

# Acceptance Decision

Accepted by: Connor
Accepted at: 2026-04-29
Basis: All 8 acceptance criteria met with evidence captured above
(R2 bucket `pipelines`, R/W token, head_bucket green, MotherDuck reads
R2 placeholder via secret, uv project + 5 deps, .gitignore correct,
GitHub repo + 5 Actions secrets set, Cloudflare billing notifications
configured).
Residual risks:
- R2 API token has no IP restriction (deliberate; CI will need
  unrestricted access in W3). User accepted this trade-off.
- One earlier credential set was exposed during a `grep` on `.env` and
  has been rotated; only the rotated values are in use and stored.

# Dependencies

- Personal Cloudflare account with R2 enabled
- Personal MotherDuck account
- GitHub account

# Journal

- 2026-04-29 — ticket created from `plan:v1-radar` Wave 0 (originally
  scoped against AWS S3).
- 2026-04-29 — ticket rewritten to swap AWS S3 for Cloudflare R2 per
  `decision:0001-storage-backend-r2`. Eight acceptance criteria, all
  ticket-local. Status remains `ready`; readiness checklist still
  passes.
- 2026-04-29 — ticket executed. uv project initialized, deps added
  (dlt[filesystem], boto3, duckdb, pyarrow, python-dotenv); .gitignore
  + .env.example + smoke scripts written; R2 bucket + token created
  by user; MotherDuck R2 secret created by user; both smoke scripts
  green; GitHub Actions secrets set via `gh secret set`; Cloudflare
  billing notifications configured. Status →
  `complete_pending_acceptance`.
- 2026-04-29 — bootstrap committed and pushed to
  `Doctacon/dream-job-radar` (commits c718c70, 29e1b17). Status →
  `closed`. W0 done.
