---
id: critique:polymer-upstream-iter1
kind: critique
status: final
created_at: 2026-05-02T13:59:59Z
updated_at: 2026-05-02T13:59:59Z
scope:
  kind: repository
  repositories:
    - repo:root
review_target: ticket:7n0yj21k (Ralph iteration 1)
links:
  ticket: ticket:7n0yj21k
  packet: packet:ralph-polymer-upstream-20260502T135222Z
  plan: plan:expand-radar
  wiki: wiki:extractor-shape
  predecessor_critique: critique:rippling-kalkomey-iter1
external_refs: {}
---

# Summary

Direct artifact + code review of Wave 3 / PM3 of
`plan:expand-radar` (Polymer → Upstream Tech). Profiles per
ticket Critique Disposition: code-quality, schema-fitness.
Predecessor critiques cover sitemap-monitor + page-monitor +
Rippling lessons; this pass focuses on what is genuinely new:
the index-then-per-role hybrid pattern, non-ISO datePosted
reformatting, list-typed jobLocation flattening, and the
polite→browser UA fallback.

# Review Target

- Ticket: `ticket:7n0yj21k`
- Packet:
  `.loom/packets/ralph/polymer-upstream-20260502T135222Z.md`
- Working tree at parent reconciliation:
  - `src/dream_job_radar/extractors/polymer.py` (new)
  - `src/dream_job_radar/pipelines/polymer.py` (new)
  - `src/dream_job_radar/pipelines/radar.py` (extended chain)
  - `.github/workflows/refresh.yml` (new step)
  - `README.md` (extended)
- Evidence: ticket Evidence section + packet Child Output.

# Verdict

`pass_with_findings`.

The slice meets AC1–AC7 with truthful observation-first evidence.
Today's 0-yield matches established v1 / v2 patterns (floodbase,
gohunt, regrid, kalkomey). The hybrid index-then-per-role pattern
is correctly modeled; SiteSpec generalizes for hypothetical future
Polymer-hosted companies. Findings are inheritance / hardening
notes for PM5 retro, not blockers.

# Findings

## FIND-001: Polite→browser UA fallback is reasonable but worth flagging

Severity: medium
Confidence: medium
Disposition: open

Observation:

`_get(url, accept=...)` issues a polite UA first, then retries
with a browser UA on 403 / 503. Today's Upstream Tech surfaces
returned 200 to the polite UA at probe time and at run time, so
the fallback was not exercised. The fallback exists because:
(a) `www.alltrails.com/careers` returned 403 to both UAs during
v2 research (dropped from scope), and (b) Cloudflare-fronted sites
sometimes 503 polite scripts during high traffic.

Why it matters:

The fallback is a soft anti-bot evasion. Constitutional posture
explicitly says "no anti-bot evasion". The line is fuzzy here —
the browser UA is not a JS execution or cookie dance, just a
header swap. Pragmatic for v1; worth documenting so future agents
don't normalize it into more aggressive evasion.

Follow-up:

Update `wiki:extractor-shape` during PM5 retro: document the
polite→browser UA fallback as the v1 ceiling on UA tactics.
Anything beyond that (cookies, JS, headless browsers) requires a
research loopback and explicit constitutional discussion.

Challenges: None - not claim-specific.

## FIND-002: Index discovery via regex against parent careers page is fragile

Severity: medium
Confidence: high
Disposition: open

Observation:

`_fetch_index_ids(spec)` runs `re.findall(spec.id_pattern, html)`
against the parent careers page HTML. For Upstream Tech this works
because the role IDs appear in cleartext URLs. But the parent
careers page is a rich Webflow site (~84KB HTML, mostly
non-careers content); a future re-skin could move the role-ID
links into a JS-rendered section, breaking the regex silently
(0 IDs discovered → 0 yield → indistinguishable from honest
0-match without the
`[polymer:<slug>] index discovered N role(s)` log).

Why it matters:

Same operator-visibility constraint as page-monitor regex (FIND-001
of `critique:page-monitor-iter1`). The
`index discovered N role(s)` log line gives run-time visibility,
but Wave 3 cron has no automated alert on N→0 transitions for
index discovery (only for parquet freshness).

Follow-up:

Note in PM5 retro: page-monitor + polymer-monitor sources share
the regex-fragility risk class. Health-check enhancement
(distinguish "index returned 0 IDs" from "index returned N IDs but
0 matched") is a future ticket if Wave 4 wants it.

Challenges: None - not claim-specific.

## FIND-003: `_parse_date_posted` accepts only one Polymer-specific format

Severity: low
Confidence: high
Disposition: open

Observation:

`_parse_date_posted(s)` accepts ISO (passthrough) or Polymer's
`'YYYY-MM-DD HH:MM:SS UTC'`. Other formats fall through to `""`
(NULL after view TRY_CAST). Today's 3 Upstream Tech roles all use
the Polymer format; if a hypothetical second Polymer-hosted site
serves dates in (say) `'YYYY-MM-DDTHH:MM:SSZ'` or
`'YYYY-MM-DD HH:MM:SS GMT'`, the fall-through silently NULLs.

Why it matters:

NULL `posted_at` is honest and matches Felt's `posted_at = ""`
posture. But PM5 retro should add a generic `dateutil.parser`
fallback OR explicitly document that Polymer-hosted companies
must conform to the supported date format.

Follow-up:

Defer. If a second Polymer site lands, expand the parser then.
Track via PM5 retro `posted_at` table update.

Challenges: None - not claim-specific.

## FIND-004: `_extract_location` flattens addressLocality + addressRegion + addressCountry

Severity: low
Confidence: high
Disposition: resolved

Observation:

Builds the location string from
`addressLocality, addressRegion, addressCountry` joined by `, `,
skipping empty parts. Today all 3 Upstream roles return only
`addressCountry: "US"`, so the `location` column reads `"US"`.
This is a thinner location signal than Greenhouse / Ashby provide,
but accurately reflects what the upstream JSON-LD exposes.

Why it matters:

Confirming: shape is correct. Future polymer sites that include
locality / region will produce richer strings naturally.

Follow-up:

None.

Challenges: None - not claim-specific.

## FIND-005: SiteSpec's id_pattern is a str, not a compiled regex

Severity: low
Confidence: high
Disposition: open

Observation:

`SiteSpec.id_pattern` is a `str`; `_fetch_index_ids` compiles it
each call. For 1 site / 1 cron firing per day this is trivial; if
the Polymer kind grows to many sites + many runs, pre-compiling at
module load would shave microseconds.

Why it matters:

Premature optimization for v1. Storing a string is also more
serializable / loggable.

Follow-up:

None unless Polymer scales to many sites.

Challenges: None - not claim-specific.

## FIND-006: Polymer adds a sixth source kind to the cron; per-step env: not yet tightened

Severity: low
Confidence: high
Disposition: open

Observation:

The workflow now has 6 per-source steps, each with
`continue-on-error: true`, all sharing the job-level `env:` (5
secrets). FIND-007 of `critique:actions-cron-iter1` flagged
per-step `env:` as a future hardening; this iteration does not
adopt it.

Why it matters:

Scaling per-step `env:` to 6 source steps + 2 final steps will
make the workflow YAML noisier; current shape is acceptable for
v1.

Follow-up:

Same disposition as `critique:actions-cron-iter1` FIND-007.
Defer to a future hardening pass.

Challenges: None - not claim-specific.

## FIND-007: Wiki updates compounding — PM5 retro must promote a non-trivial set

Severity: medium
Confidence: high
Disposition: open

Observation:

`wiki:extractor-shape` does not yet have:
- a Rippling section (FIND-001/002/003 of
  `critique:rippling-kalkomey-iter1`)
- a Polymer section (FIND-001/002/003 of this critique)
- updated role_id strategies table (Rippling UUID + Polymer
  numeric ID rows)
- updated `posted_at` semantic table (rippling="" +
  polymer reformatted-from-Polymer-format)
- updated defensive listed/published table (rippling
  presence-as-signal + polymer presence-as-signal)

Why it matters:

Two source kinds shipped without wiki updates. Wave 4 (page-monitor
adds Vibrant Planet + Wherobots) will be the third. Wave 5 retro
becomes load-bearing for keeping the wiki accurate.

Follow-up:

PM5 retro is now a multi-section wiki update. Plan accordingly.

Challenges: None - not claim-specific.

# Evidence Reviewed

- `ticket:7n0yj21k` Acceptance + Evidence + Critique Disposition.
- `packet:ralph-polymer-upstream-20260502T135222Z` Child Output +
  Parent Merge Notes.
- Working-tree files listed under Review Target.
- Live observation outputs (standalone + chained run).
- Predecessor critiques (full v1 + v2 chain).

# Residual Risks

- Index regex fragility (FIND-002) — operator-visibility via
  `index discovered N role(s)` log line.
- UA fallback boundary (FIND-001) — could erode constitutional
  posture if not documented.
- Wiki gap accumulating (FIND-007) — promote at PM5 retro.

# Required Follow-up

Before AC closure:

- Parent commits + pushes; runs `gh workflow run refresh.yml`;
  records run URL in ticket Evidence.

After PM5 retro:

- Update `wiki:extractor-shape`:
  - new Rippling section
  - new Polymer section (incl. UA-fallback boundary, index-regex
    fragility, datePosted reformat convention)
  - role_id strategies table (5 → 7 rows; add rippling, polymer)
  - posted_at semantic table (5 → 7 rows; add rippling="",
    polymer-reformatted)
  - defensive listed/published table (consolidated per source
    kind)

# Acceptance Recommendation

`active follow-up required`.

This iteration's artifacts are correct and verified locally.
AC1–AC7 satisfied. Close after manual workflow dispatch on the
new shape succeeds. Wiki updates land at PM5 retro per the
established initiative pattern.
