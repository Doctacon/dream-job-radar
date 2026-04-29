---
id: constitution:main
kind: constitution
status: active
created_at: 2026-04-29T14:17:56Z
updated_at: 2026-04-29T14:17:56Z
scope:
  kind: workspace
links: {}
---

# Vision

Dream-Job Radar closes the loop between "a top-fit role exists somewhere on
the public web" and "I noticed it before it closed."

The product is a small, durable, mostly-automated pipeline that watches a
curated set of companies for data-shaped roles and surfaces them on a page the
author actually checks: a webpage on a phone, often on a Forest Service road
with one bar of LTE.

The point is not a job-board scraper. The point is closing the loop on
`found role → tracked role → applied to role` so the next dream job does not
slip past on a dog walk.

# Principles

## The Dive is the destination

The end-state surface is a MotherDuck Dive over the S3-backed dataset. The
Dive itself is the product, not a consolation prize. Whether the Dive can
also be iframe-embedded on `loughondata.com` is a bonus surface, not a
gating requirement. A Dive accessed directly via its MotherDuck URL still
satisfies the project.

## Author works data; weekends and weekdays should overlap

This project is biased toward companies whose product the author already uses
hard on weekends — hunting, mapping, outdoor, geospatial. GoHunt and onX are
the anchor examples, not the only ones. Industry fit is a first-class filter,
not a nice-to-have.

## Open source first

Inherit the parent CLAUDE.md principle: when a viable open-source option
exists, choose it. Proprietary tools are allowed only when no usable
open-source equivalent exists, and the integration surface stays small enough
to swap later. This applies to the dashboard layer, the storage layer, the
pipeline orchestrator, and the front end.

## Public accountability over private intent

This project is being built in public on `loughondata.com`. The embarrassment
of an unfinished public artifact is part of the design. Build artifacts and
the live radar surface should remain visible even when ugly.

## Pipelines do pipeline things; humans get a webpage

Resist mixing pipeline ergonomics with consumption ergonomics. The pipeline's
job ends when fresh data is queryable. The consumption surface's job is to be
glanceable on a phone. Do not collapse the two.

# Constraints

## S3 is the system of record; MotherDuck reads it natively

Pipeline output lands in personal AWS S3. MotherDuck reads from S3 directly
— no intermediate DuckDB file, no separate warehouse load step. This keeps
the data layer portable: S3 survives any swap of compute or dashboard.

## Greenhouse-only ingestion at v1

Initial ingestion uses the Greenhouse public API against a curated company
list. Other ATS providers (Lever, Workday, Ashby, etc.) are out of scope for
v1. Reconsider only after the loop is closed end-to-end.

## Curated companies, not crawled internet

The radar watches a hand-picked list. It does not try to enumerate every
company posting data jobs. Scope is bounded by the author's interest set; new
entries require explicit add, not heuristic discovery.

## No public exposure of application intent

The radar surface lists roles seen, not roles applied to. Application status,
cover letter content, and personal candidacy details stay off the public
surface.

## Iframe embed is a bonus, not a gate

A Dive embedded in `loughondata.com` is the preferred surface, but the Dive
itself — accessed directly on MotherDuck — is the canonical product.
Embeddability is not a Plan-B trigger. If embedding is unavailable on a
personal plan, ship the Dive as the destination and link to it from the
blog post. Do not upgrade plans for embed support.

## Offline-tolerance is a north star, not a v1 requirement

The author has been burned by "offline" apps (GoHunt, onX) that cold-start
badly with no service. The radar should aspire to degrade gracefully on poor
connections, but v1 is allowed to be a normal web page.

# Strategic Direction

## Phase 1 — Ship the Dive

```
dlt (Greenhouse API, curated companies, title keywords)
  → personal AWS S3
  → MotherDuck (reads from S3)
  → Dive (canonical surface)
GitHub Actions runs the pipeline on a schedule.
```

Stop when a role is observable on the live Dive within one schedule cycle of
posting.

## Phase 2 — Embed the Dive on loughondata.com (bonus)

Iframe-embed the Phase 1 Dive into the blog post if a personal-plan Dive
supports it. If not, link to the Dive directly from the post. Either way,
Phase 1 is already shipped.

## Phase 3 — Closing the apply loop

After the radar surface is live, extend the loop into observed application
state — privately. Public surface still shows roles seen; private surface
tracks application status. Out of scope until Phase 1 ships.

# Current Focus

- Bootstrap Loom (done)
- Pick the curated v1 company list (anchors: GoHunt, onX)
- Stand up the dlt → S3 → MotherDuck → Dive path
- Resolve iframe embed question opportunistically — does not block Phase 1

# Open Constitutional Questions

- Can a MotherDuck Dive on a personal plan be iframe-embedded on a
  third-party site? Bonus question; does not gate Phase 1.
- What is the v1 curated company list beyond GoHunt and onX? Needs an
  explicit seed set.

# Change History

- 2026-04-29 — initial constitution drafted from `Building a Dream-Job Radar`
  (loughondata.com, 2026-04-28).
- 2026-04-29 — corrected dashboard risk: cost is not the blocker on a
  personal plan; iframe embeddability of a Dive on a third-party site is the
  real open question.
- 2026-04-29 — codified S3-as-system-of-record: MotherDuck reads S3
  natively, no intermediate DuckDB layer. Removed the MotherDuck-vs-DuckDB
  open question.
- 2026-04-29 — reframed Dive as the destination: the Dive itself is the
  product, iframe embed on loughondata.com is bonus surface only. Removed
  Plan-B-on-embed-failure framing.
