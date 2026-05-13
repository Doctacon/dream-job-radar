# General Board Source Selection

ID: research:20260513-general-board-source-selection
Type: Research
Status: completed
Created: 2026-05-13
Updated: 2026-05-13

## Summary

Investigated public broad job-board sources for the first non-curated Dream Job Radar source. RemoteOK is the recommended MVP source because it is public, unauthenticated, structured, and has explicit location strings that can be gated by `relevant_open_roles`; The Muse, Remotive, and Arbeitnow were rejected for the first implementation due to precision or access/semantics issues.

## Question

Which broad public job-board source should be the first MVP for `plan:20260513-general-job-board-discovery`, given the operator's constraints: broad aggregators first, avoid high-friction/login/anti-bot sources, and prefer high precision over recall?

## Scope

Covered lightweight public-source probes for The Muse public jobs API, RemoteOK API, Remotive API, and Arbeitnow job-board API. Excluded LinkedIn, Indeed, Glassdoor, login-heavy, anti-bot-heavy, credential-required, and CAPTCHA-bypassing paths by operator constraint. This research selects one MVP source; it does not implement the extractor or decide future source expansion.

Freshness: probes were run on 2026-05-13. Recheck before implementation if any endpoint starts requiring credentials, changes response shape, blocks the project user agent, or materially changes terms/access posture.

## Method And Sources

- `ticket:20260513-general-board-source-research` - source-selection acceptance criteria and constraints.
- `plan:20260513-general-job-board-discovery` - broad discovery strategy and dependence on relevance filtering.
- `.loom/wiki/extractor-shape.md` - canonical raw row shape the source must map into.
- `https://www.themuse.com/api/public/jobs` - probed with `category=Data and Analytics&location=Remote` and `category=Data and Analytics&location=Phoenix, AZ`.
- `https://remoteok.com/api` - probed with project user agent; returned JSON with job IDs, company, position, URL, location, date, tags.
- `https://remotive.com/api/remote-jobs?search=data engineer` - probed as a remote-job API alternative.
- `https://www.arbeitnow.com/api/job-board-api?search=data engineer&remote=true` - probed as a public job-board API alternative.

## Findings

- The Muse public API is accessible without credentials and has structured fields: `id`, `name`, `locations`, `categories`, `refs`, and `company`. However, location filtering was not high precision for this use case. A Phoenix/Data probe returned many `Flexible / Remote` rows and remote/multi-location rows rather than clearly Arizona-local roles. A Remote/Data probe returned many vague `Flexible / Remote` locations, which the relevance contract would exclude unless a future source-specific classifier inspected job descriptions.
- RemoteOK API is accessible without credentials at `https://remoteok.com/api` and returned a JSON array. A probe returned 98 jobs; 23 had titles containing current broad keywords. Sample fields included `id`, `position`, `company`, `url`, `location`, `tags`, and date fields. Location examples included `Remote - US`, `Remote, United States`, `US Remote`, blank locations, Canada, and other countries. This gives the relevance view enough explicit location text to include US remote and exclude vague/foreign rows.
- Remotive API is accessible and structured, but the `search=data engineer` probe returned only 19 jobs with weak title precision: examples included Office Assistant, Inside Sales Contractor, Freelance Writer, and Customer Support Manager. It also includes a legal notice warning not to submit Remotive jobs to third-party websites. It may be acceptable for private personal use later, but it is not the best first high-precision source.
- Arbeitnow API is accessible and structured, but the `search=data engineer&remote=true` probe returned 100 jobs with poor relevance for this radar; the first result was a German finance/administration role in Hamburg. It appears EU-heavy and weakly aligned with the operator's explicit US/worldwide remote and Arizona relevance contract.
- Adzuna and similar broad aggregators may be relevant later, but credential/API-key setup makes them a worse first source under the current avoid-friction constraint.

## Tradeoffs

- RemoteOK - strongest first implementation fit. Public unauthenticated JSON, simple single endpoint, stable-looking job IDs, explicit enough location text for `relevant_open_roles`, and broad enough to discover companies outside the curated board list. Weakness: remote-first rather than all-job broad aggregation, and title filtering must be stricter than the existing simple `engineer` keyword to avoid support/sales/non-target roles.
- The Muse - broad public jobs API and strong field structure. Weakness: remote/location semantics are too vague for the current high-precision relevance contract; using it first would likely yield many rows hidden by `relevant_open_roles` or require description-level inference.
- Remotive - structured remote API. Weakness: poor search precision in the probe and legal/redistribution warning create avoidable risk for a first source.
- Arbeitnow - structured public API. Weakness: poor precision and location fit for this operator's target market.

## Rejected Paths And Null Results

- LinkedIn, Indeed, Glassdoor - rejected by operator constraint for first plan because they are high-friction/login/anti-bot-heavy sources.
- The Muse as first MVP - rejected for now because `Flexible / Remote` and loose location results conflict with the high-precision relevance contract.
- Remotive as first MVP - rejected for now because query precision was poor and the API response includes a legal warning against third-party job submission.
- Arbeitnow as first MVP - rejected for now because probe results were location- and title-noisy for this radar.

## Conclusions

RemoteOK is the recommended MVP source for the first general-board extractor. Confidence is medium: the endpoint was reachable and source fields map cleanly, but implementation should re-probe immediately before coding and should use a stricter source-specific title filter to preserve high precision.

Suggested source mapping:

- `company`: RemoteOK `company`
- `source_kind`: `remoteok`
- `ats_slug`: `remoteok`
- `role_id`: RemoteOK `id`
- `title`: RemoteOK `position`
- `url`: RemoteOK `url`
- `location`: RemoteOK `location`
- `posted_at`: RemoteOK date/publication field, normalized if present
- `fetched_at`: pipeline fetch timestamp
- `raw_json`: full source job JSON

## Recommendations

- `ticket:20260513-general-board-mvp-extractor` should implement RemoteOK as one source kind, with a stricter source-specific title allowlist and existing relevance gating downstream.
- Do not add The Muse, Remotive, Arbeitnow, Adzuna, LinkedIn, Indeed, or Glassdoor in the MVP extractor ticket.
- If RemoteOK blocks access or changes response shape before implementation, return to `ticket:20260513-general-board-source-research` or create a follow-up research ticket instead of guessing a substitute.

## Open Questions

- The exact RemoteOK title allowlist should be finalized inside the MVP extractor ticket after one fresh probe of current jobs.
- If broad non-remote aggregators become important later, revisit API-key-based sources such as Adzuna as a separate source-selection pass.

## Related Records

- `plan:20260513-general-job-board-discovery` - consumes this research for the first implementation source.
- `ticket:20260513-general-board-source-research` - closed from this research conclusion.
- `ticket:20260513-general-board-mvp-extractor` - should execute the RemoteOK MVP from this conclusion.
- `plan:20260513-personalized-relevance-filter` - provides the relevance gate that keeps RemoteOK noise out of the user-facing Dive.
