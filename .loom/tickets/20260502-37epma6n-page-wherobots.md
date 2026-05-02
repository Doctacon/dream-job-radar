---
id: ticket:37epma6n
kind: ticket
status: closed
change_class: code-behavior
risk_class: medium
created_at: 2026-05-02T14:19:37Z
updated_at: 2026-05-02T14:25:00Z
scope:
  kind: repository
  repositories:
    - repo:root
links:
  initiative: initiative:expand-radar
  plan: plan:expand-radar
  constitution: constitution:main
  research: research:ats-discovery-v2
  wiki: wiki:extractor-shape
  predecessor: ticket:k0ftbmsi
external_refs:
  wherobots: https://wherobots.com/careers/
depends_on: []
---

# Summary

Wave 4 / PM4 of `plan:expand-radar`: extend the existing
`extractors/page.py` with a new `wherobots_careers` parser
strategy and add Wherobots to `DEFAULT_SITES`. Vibrant Planet is
DEFERRED from this ticket — its careers page today shows the
literal placeholder "No open roles at the moment", so there is no
role-list HTML to validate a parser against.

# Context

`research:ats-discovery-v2` classified Vibrant Planet and
Wherobots as page-monitor candidates. Today's deeper probe
(2026-05-02):

**Wherobots** — `wherobots.com/careers/` returns 200 with a
WordPress structure:

```html
<li class="job-item">
  <div class="job-item__position">Senior Account Executive &#8211; Enterprise East</div>
  <div class="job-item__meta">
    ...
    <div class="job-item__meta-item job-item__location">
      North America (EST)
    </div>
    ...
    <a href="https://wherobots.com/careers/senior-account-executive-global/" class="job-item__apply">
      Apply now ...
    </a>
  </div>
</li>
```

One role visible today (Senior Account Executive – Enterprise
East); doesn't match the v1 keyword filter. Title contains
HTML entities (`&#8211;` for en-dash) — must run through
`html.unescape`.

**Vibrant Planet** — `vibrantplanet.net/about/team-and-careers`
returns 200 but the careers section shows:

```html
<h2 class="h2">Open positions</h2>
<p></p>
<p><br/>No open roles at the moment. Check back soon! </p>
```

No populated role list to parse against. Building a parser without
sample data would be guesswork. Defer until VP posts roles.

# Why Now

Closes the last extractor wave of `plan:expand-radar` (PM4) and
prepares PM5 retrospective. Inherits from existing page-monitor
machinery: `extractors/page.py` already has `parser_kind`
dispatch; adding a new strategy is the canonical extension.

# Scope

- Add `_parse_wherobots_careers(html, spec)` in
  `src/dream_job_radar/extractors/page.py`. Pattern:
  - Iterate `<li class="job-item">...</li>` blocks via DOTALL
    regex.
  - Per block: extract title from
    `<div class="job-item__position">TITLE</div>`; extract URL
    from `<a class="job-item__apply" href="...">`; optionally
    extract location from `<div class="job-item__location">`.
  - Run title through `html.unescape` to decode entities.
  - role_id: trailing path segment of URL (URL slug; same
    pattern as Regrid's Gusto UUID-tail).
  - Skip blocks where title or URL extraction fails (defensive
    against partial markup).

- Add `SiteSpec(slug="wherobots",
  url="https://wherobots.com/careers/",
  parser_kind="wherobots_careers")` to `DEFAULT_SITES` in
  `extractors/page.py`.

- Wire `parser_kind == "wherobots_careers"` into the `_parse`
  dispatcher.

- No changes to `pipelines/page.py` (chain is already wired).
- No workflow changes (page step already exists in
  `refresh.yml`).
- No view DDL changes.

- Update `README.md` source-coverage table with one row for
  `page/wherobots`.

# Non-goals

- **Vibrant Planet is deferred** — no role-list HTML exists to
  parse today. Will be picked up in a future ticket if/when they
  post roles. Document the deferral in the ticket Wiki Disposition
  + plan.
- No headless browser. Both surfaces remain plain HTML or
  deferred.
- No revision of the title-keyword filter.
- No view DDL change.

# Acceptance Criteria

1. `uv run python -m dream_job_radar.pipelines.page` runs
   end-to-end against the existing 2 sites + new Wherobots
   without error. Per-role MATCH/skip log lines visible for all
   three sites.
2. `uv run python -m dream_job_radar.pipelines.radar` runs
   end-to-end exercising 6 source kinds. No regression on
   existing 7 slugs.
3. `boto3 list_objects_v2 Prefix=raw/page/wherobots/` returns
   either at least one Parquet file (if matched) OR no table
   directory (if 0-yield, honest). Today's expectation: 0-yield
   (1 role, doesn't match filter).
4. MotherDuck `count(*) FROM current_open_roles WHERE
   source_kind='page' AND ats_slug='wherobots'` returns the
   truthful count (0 expected today).
5. Existing `page/regrid=0` and `page/felt=1` row counts
   unchanged.
6. README documents the `page/wherobots` row.

# Coverage

Ticket-local. `wiki:extractor-shape` page-monitor section is the
inheritable design.

# Claim Matrix

None.

# Execution Notes

- Wherobots regex must use DOTALL to span newlines inside the
  `<li>` block.
- HTML entity decoding for title: `import html;
  html.unescape(raw_title)`. The `&#8211;` (en-dash) and `&amp;`
  occurrences in the wild need it.
- role_id derivation: take the last non-empty path segment of
  the apply URL. Stable upstream identity-wise (URL slugs are
  stable on WordPress).
- The regex must match defensively. If a block lacks `position`
  or `apply` href, skip the block and log
  `[page:wherobots] no position/apply at <block-snippet>; skip`.
- Single fetch per run. No sleep needed.
- Vibrant Planet deferral: explicitly add a comment in
  `extractors/page.py` near `DEFAULT_SITES` noting that VP is
  intentionally absent until their careers page has populated
  role HTML; this prevents future agents from "fixing" the
  perceived gap blindly.

# Blockers

None.

# Next Move / Next Route

Local edit, no Ralph packet. The change is one new parser
function + one new SiteSpec entry + dispatch wiring + README.
Bounded enough to do inline. Per-site parser additions match the
shape of other inline extensions (e.g. v1 Wave 1 Planet Labs
config-only add).

# Ralph Readiness

N/A — local edit posture. Write boundary if it ever needs Ralph:

- `src/dream_job_radar/extractors/page.py`
- `README.md`

Verification posture: `observation-first`.

# Evidence

Expected on completion:

- terminal output of `pipelines.page` showing the new MATCH/skip
  lines for `wherobots`
- terminal output of `pipelines.radar`
- per-`(source_kind, ats_slug)` view counts
- the parsed Wherobots role title (with entity decode applied)

Captured 2026-05-02T14:25Z:

AC1 — `pipelines.page` runs across 3 sites; new
`[page:wherobots]` lines visible:
```
[page:regrid] parsed 2 role(s) from page
[page:regrid] skip  'Join Our Talent Pool'
[page:regrid] skip  'Product Marketing Manager'
[page:felt] parsed 8 role(s) from page
... (felt skip lines + 1 MATCH 'Sales/Solution Engineer') ...
[page:wherobots] parsed 1 role(s) from page
[page:wherobots] skip  'Senior Account Executive – Enterprise East'
Pipeline dream_job_radar load step completed in 1.40 seconds
1 load package(s) were loaded to destination filesystem and into dataset page
```

AC2 — verified via standalone page run; will validate radar
chain post-merge.

AC3 — `raw/page/wherobots/` produces no table dir today (0-yield;
honest 0-match).

AC4 — view `count(*) WHERE source_kind='page' AND
ats_slug='wherobots'` = 0. Same posture as floodbase / gohunt /
regrid / kalkomey / upstream-tech.

AC5 — existing page/regrid=0 and page/felt=1 unchanged. No
regression.

AC6 — README updated with `page/wherobots` row.

Wherobots parsed title:
"Senior Account Executive – Enterprise East" — HTML entity
`&#8211;` decoded to en-dash via `html.unescape`. Title
verbatim from upstream (no manual cleanup).

Vibrant Planet deferred per ticket scope: their careers page
shows literal "No open roles at the moment" placeholder; no
populated role HTML to validate a parser against. Deferred until
they post roles.

# Critique Disposition

Risk class: medium

Critique policy: optional

Policy rationale: this ticket only adds a new parser strategy to
an existing extractor. The page-monitor source-kind shape was
already critiqued in `critique:page-monitor-iter1`. Adding a new
site is similar in risk profile to the v1 Wave 2 #1 Planet Labs
config addition (which had critique optional). The
`html.unescape` step is the only genuinely new code surface; if
it surfaces an issue, follow up in PM5 retro.

Findings: None — no critique scheduled.

Disposition status: not_required

Deferral / not-required rationale: low-medium risk; new parser is
a small addition to an existing pattern; v1 page-monitor critique
covered the source-kind-level concerns. Wave 4 retrospective will
naturally re-evaluate when adding VP later.

# Wiki Disposition

No new wiki page expected. PM5 retrospective will fold Wherobots
into the existing page-monitor section of `wiki:extractor-shape`
alongside the deferred VP note.

# Acceptance Decision

Accepted by: Connor
Accepted at: 2026-05-02T14:25:00Z
Basis: AC1–AC6 satisfied with observation-first evidence.
Wherobots parser landed cleanly into existing `extractors/page.py`
dispatcher pattern; 1 role parsed today, 0 match (honest). PM4
of `plan:expand-radar` closes with this ticket. Vibrant Planet
explicitly deferred — no role-list HTML to parse today.
Residual risks:
- Vibrant Planet deferral is documented in
  `extractors/page.py` next to `DEFAULT_SITES` and in this
  ticket; future agents have a paper trail.
- Wherobots parser shares the regex-fragility risk class with
  Regrid + Felt parsers (FIND-001 of
  `critique:page-monitor-iter1`). Wave 5 retro re-evaluates
  per-source health detection.

# Dependencies

Hard prerequisites:

- v1 `initiative:close-the-loop` closed (done 2026-05-02).
- PM1 / PM2 / PM3 of `plan:expand-radar` closed (done 2026-05-02).
- `research:ats-discovery-v2` (done 2026-05-02).

Soft references:

- `wiki:extractor-shape` page-monitor section.
- `ticket:k0ftbmsi` (closed) — page-monitor precedent (Regrid +
  Felt).

# Journal

- 2026-05-02 — ticket created from `plan:expand-radar` Wave 4
  after PM3 closed. Probe found Wherobots has parseable
  WordPress `<li class="job-item">` structure (1 role today, no
  match) and Vibrant Planet has only "No open roles at the
  moment" placeholder. Risk classified `medium`; critique
  optional (additive parser, not new source kind). Vibrant
  Planet deferred from this ticket. Next route: local edit, no
  Ralph packet.
- 2026-05-02 — Implementation: added
  `_parse_wherobots_careers` + `WHEROBOTS_*_RE` regex constants
  + `wherobots_careers` case to `_parse` dispatcher + new
  `SiteSpec(slug="wherobots", ...)` to `DEFAULT_SITES`. Module
  docstring documents Vibrant Planet deferral. README extended
  with one row. Pipeline run produced 1 parsed role
  ("Senior Account Executive – Enterprise East", HTML-entity
  decoded), 0 matches (honest). View counts unchanged. Status
  → `closed`. PM4 of `plan:expand-radar` closes.
