---
id: critique:page-monitor-iter1
kind: critique
status: final
created_at: 2026-04-30T03:00:59Z
updated_at: 2026-04-30T03:00:59Z
scope:
  kind: repository
  repositories:
    - repo:root
review_target: ticket:k0ftbmsi (Ralph iteration 1)
links:
  ticket: ticket:k0ftbmsi
  packet: packet:ralph-page-monitor-20260430T025403Z
  plan: plan:v1-radar
  wiki: wiki:extractor-shape
  predecessor_critique: critique:sitemap-gohunt-iter1
external_refs: {}
---

# Summary

Direct artifact + code review of Wave 2 #3 (page monitor → Regrid +
Felt). Profiles per ticket Critique Disposition: code-quality,
schema-fitness. Predecessor critiques cover the resource-factory
shape, the canonical-row contract, and the sitemap-monitor
no-API precedent; this pass focuses on what is genuinely new:
per-site parser strategies, regex fragility against HTML,
divergent role_id strategies inside one source kind, and Felt's
careers-page-as-url quirk.

# Review Target

- Ticket: `ticket:k0ftbmsi`
- Packet: `.loom/packets/ralph/page-monitor-20260430T025403Z.md`
- Working tree at parent reconciliation time:
  - `src/dream_job_radar/extractors/page.py` (new)
  - `src/dream_job_radar/pipelines/page.py` (new)
  - `src/dream_job_radar/pipelines/radar.py` (extended)
  - `README.md` (extended)
- Evidence: ticket Evidence section + packet Child Output.

# Verdict

`pass_with_findings`.

The page-monitor slice meets AC1–AC6 with truthful
observation-first evidence including the Felt match
("Sales/Solution Engineer") and Regrid's honest 0-match outcome.
The two-parser-strategy approach is appropriate given the
structural divergence between Regrid (Gusto board) and Felt
(Webflow page). All findings are inheritance / hardening notes for
the wiki and Wave 3 considerations, not blockers.

# Findings

## FIND-001: Regex parsers are fragile to upstream markup change

Severity: medium
Confidence: high
Disposition: open

Observation:

Both parsers depend on exact class-name matches:
- Felt: `<div class="h4 careers">TITLE</div>` (`FELT_ROW_RE`)
- Gusto: `<a class="block hover:bg-gray-50" href="...">` +
  `<h3 class="text-lg">TITLE</h3>` (`GUSTO_ROW_RE`)

Webflow regenerations or Tailwind class re-shuffling on either
host can silently produce 0 matches even when humans see roles on
the page. The MATCH/skip log makes the failure visible at run time,
but no automated alert exists.

Why it matters:

This is the fundamental fragility of page-monitor sources without
JSON-LD. The `parsed N role(s) from page` log is the only signal a
parser is broken. Wave 3 (cron) needs a way to detect N→0 silent
breakage.

Follow-up:

- Update `wiki:extractor-shape` during the retrospective: add a
  page-monitor section that explicitly calls out this fragility
  and the per-site parser dispatch pattern.
- Future Wave 3 ticket should consider an alert / metric:
  "parsed 0 roles from a page that previously yielded N>0" → loud
  failure.

Challenges: None - not claim-specific.

## FIND-002: role_id strategies divergent inside one source kind

Severity: medium
Confidence: high
Disposition: open

Observation:

`source_kind="page"` covers both Regrid (UUID-tail from Gusto
posting URL) and Felt (sha1 of slug + title). Two stability
properties:

- Regrid Gusto UUIDs are stable across title/slug rewrites because
  the UUID is server-generated.
- Felt sha1(slug+title) is stable only while the title is unchanged.
  A title rename creates a new logical role with fresh
  `first_seen_at`; the old observation drops out of the view.

Two extractors, one source kind, two identity contracts. The view
has no way to know.

Why it matters:

Wave 2 #4 (sitemap → GoHunt) had the same property locally (URL
slug = identity); this ticket extends the inconsistency across two
sites in one source kind. Future page-monitor authors must decide
on the spot which strategy a new site needs.

Follow-up:

Update `wiki:extractor-shape` during the retrospective: add a
section explicitly comparing role_id strategies across source
kinds (Greenhouse int id, Ashby UUID, sitemap URL-slug, page-Gusto
UUID, page-Felt content-hash). Document the rule: "if the
upstream provides a stable id, use it; otherwise hash a stable
content-derived key and accept that renames break identity."

Challenges: None - not claim-specific.

## FIND-003: Felt `url` is the careers page itself, not a per-role link

Severity: low
Confidence: high
Disposition: open

Observation:

The Felt parser stores `url = spec.url = "https://felt.com/careers"`
because Felt has no per-role URL — apply is via `mailto:hello@felt.com`.
All Felt rows in the view share the same URL. The Dive will show
multiple Felt roles all linking to the same destination.

Why it matters:

Future Dive consumers may surface `url` as a click target. Multiple
rows linking to the same URL is unusual and may be confusing
without a hint. The mailto-as-apply path is invisible in the
canonical row.

Follow-up:

- Document in `wiki:extractor-shape` retrospective.
- If a future Dive iteration needs to expose apply-actions
  distinctly (mailto vs URL), add a column then. Defer.

Challenges: None - not claim-specific.

## FIND-004: `posted_at = ""` for page-monitor sources

Severity: low
Confidence: high
Disposition: open

Observation:

Neither Gusto board nor Felt careers exposes a posting timestamp.
Both sites use the empty string. The view's `first_seen_at`
derivation provides a usable proxy (when did the pipeline first
observe this role).

Why it matters:

Sorting roles by recency in the Dive cannot use `posted_at` for
page-monitor rows; downstream consumers must use `first_seen_at`
instead. Mixed `posted_at` semantics across source kinds (Greenhouse
`updated_at`, Ashby `publishedAt`, sitemap `datePublished`,
page="") need to be documented.

Follow-up:

Update `wiki:extractor-shape` during the retrospective: extend the
existing `posted_at` semantic section with a per-source-kind table
including the empty-string convention for page monitor.

Challenges: None - not claim-specific.

## FIND-005: Felt apply-path is mailto; not surfaced in canonical row

Severity: low
Confidence: medium
Disposition: open

Observation:

`raw_json` on Felt rows contains only the parsed dict (`title`,
`role_id`, `url`); the `mailto:hello@felt.com` apply path lives
only in the upstream HTML, not in any view-accessible column. A
Dive consumer cannot today render an "Apply" button for Felt.

Why it matters:

Dives can show `url` as a click target, but for Felt that opens
the careers page, not the apply flow. For all other source kinds,
`url` IS the canonical surface. Mild semantic inconsistency.

Follow-up:

Defer. If future Dive iterations want a structured apply field,
add a per-source-kind capture in `_normalize` and a column in the
canonical row. Today's surface (`url`) is acceptable.

Challenges: None - not claim-specific.

## FIND-006: Gusto UUID-tail regex assumes 36-char canonical UUID

Severity: low
Confidence: high
Disposition: resolved

Observation:

`GUSTO_UUID_TAIL_RE` matches the canonical hyphenated UUID format.
Gusto's posting slugs all use that format today. The fallback
(use the entire posting slug if no UUID match) is loud — a
non-canonical id would be a hex-readable slug rather than a UUID,
which a human reader would notice.

Why it matters:

Defensive fallback is correct. Resolved by inspection.

Follow-up:

None.

Challenges: None - not claim-specific.

## FIND-007: 4 source kinds × 2 role_id semantics = future Wave 3 alert design space

Severity: low
Confidence: medium
Disposition: open

Observation:

Wave 3 (scheduled refresh) will run all four source kinds on cron.
With 4 source kinds, 7 distinct ATS slugs, and 2 distinct role_id
semantics (stable upstream id vs content-hash), the failure modes
multiply. A single "0 matches across all sources" alert would be
too coarse.

Why it matters:

Anticipatory: Wave 3 ticket should think in terms of per-source-kind
or per-slug health checks rather than a single binary "is it
working" signal.

Follow-up:

Note in retrospective. Wave 3 ticket should explicitly carry this
constraint into its design.

Challenges: None - not claim-specific.

# Evidence Reviewed

- `ticket:k0ftbmsi` Acceptance + Evidence sections.
- `packet:ralph-page-monitor-20260430T025403Z` Child Output.
- Working-tree files listed under Review Target.
- Live observation outputs (page stand-alone run, all-sources
  radar run, R2 listing, view count + sample row).
- Predecessor critiques `critique:walking-skeleton-iter1`,
  `critique:ashby-mapbox-iter1`, `critique:sitemap-gohunt-iter1`
  for inherited posture.

# Residual Risks

- HTML parser fragility (FIND-001) is the highest-impact long-tail
  risk; tracked for wiki promotion + Wave 3 alert design.
- role_id strategy divergence (FIND-002) is now real across 4
  source kinds; tracked for wiki.
- Felt-url-equals-careers-page (FIND-003) and mailto apply
  (FIND-005) are surface concerns the Dive can address later if
  needed.

# Required Follow-up

Before ticket closure:

- Parent confirms the 1-match outcome (Felt) + 0-match outcome
  (Regrid) is acceptable as v1 delivery (already done in packet
  Parent Merge Notes).

After ticket closure (retrospective inputs):

- Update `wiki:extractor-shape`:
  - add page-monitor section: per-site parser dispatch, regex
    fragility, MATCH/skip logging convention (FIND-001)
  - add role_id strategies comparison across all 4 source kinds
    (FIND-002)
  - add `posted_at` per-source-kind table (FIND-004)
  - add Felt-as-careers-page note (FIND-003)
- Note FIND-001 + FIND-007 as Wave 3 alert-design considerations.

# Acceptance Recommendation

`complete_pending_acceptance`.

This critique pass found no `changes_required` findings. All
findings are `low` or `medium` severity, all are deferred follow-up
or already resolved. Ticket may advance from `review_required` to
`complete_pending_acceptance`; parent acceptance closes it. PM2 of
`plan:v1-radar` then closes — all four source kinds shipped.
