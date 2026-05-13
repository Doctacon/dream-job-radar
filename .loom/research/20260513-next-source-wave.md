# Next Source Wave

ID: research:20260513-next-source-wave
Type: Research
Status: completed
Created: 2026-05-13
Updated: 2026-05-13

## Summary

Evaluated GIS Jobs Clearinghouse, Climatebase, and USAJobs as follow-up source candidates after Tech Jobs for Good. GIS Jobs Clearinghouse is the best next implementation candidate because it exposes a simple public RSS feed and is intrinsically geospatial, but expected user-facing yield may be low due to onsite/non-AZ roles. Climatebase is mission-fit but direct public fetch returned blocked/SPA behavior and should not be implemented without a separate access strategy. USAJobs public website is accessible but the data API returned 401 without required API credentials, so it is not a low-friction next source unless the operator wants to configure USAJobs API access.

## Question

Which source should follow Tech Jobs for Good to increase high-signal roles without reintroducing broad-board noise?

## Scope

Covered lightweight public probes for GIS Jobs Clearinghouse, Climatebase, and USAJobs. Excluded login, premium, credential-only, CAPTCHA, anti-bot bypassing, and paid access paths. This research does not implement any extractor.

## Method And Sources

- `plan:20260513-broaden-mission-source-discovery` - source expansion strategy.
- `https://www.gjc.org/cgi-bin/rssjobs.pl` - public GIS Jobs Clearinghouse RSS feed.
- `https://jobs.climatebase.org/jobs?l=Remote` and `https://climatebase.org/jobs` - public Climatebase pages.
- `https://www.usajobs.gov/Search/Results?...` and `https://data.usajobs.gov/api/search` - public USAJobs search and API probes.

## Findings

- GIS Jobs Clearinghouse exposes RSS at `https://www.gjc.org/cgi-bin/rssjobs.pl`. The feed includes stable job links like `showjob.pl?id=...`, title, description text containing company/location, and `pubDate`. It is highly geospatial/GIS relevant. Current feed examples include GIS Technician roles, GIS Data Supervisor, GIS Architect, GIS Strategic Planning Manager, and GIS Web Developer. Weakness: many roles are onsite and not Arizona; several current entries are older than the high-value recent window.
- Climatebase is strong mission fit for climate/environment jobs, but `https://jobs.climatebase.org/jobs?l=Remote` returned 403 and the public `https://climatebase.org/jobs` page appears SPA-heavy from fetch output. It may be feasible with a documented API or legitimate export, but it is not ready for a simple public HTML/RSS extractor.
- USAJobs website search is publicly viewable, but the data API probe at `https://data.usajobs.gov/api/search` returned 401 without API credentials. A browser-search scrape is not attractive because USAJobs has official API semantics and government-specific filters that should be used if configured.

## Tradeoffs

- GIS Jobs Clearinghouse - easiest next implementation, strong geospatial signal, low engineering risk. Likely low immediate relevant yield due to location constraints.
- Climatebase - strong mission signal and likely higher volume for climate roles, but access feasibility is unresolved and may require a separate legitimate API/research path.
- USAJobs - potentially useful for public-sector GIS/data/civic roles, but official API requires configured credentials; HTML search results are less suitable than the API.

## Recommendation

If adding another source immediately, implement GIS Jobs Clearinghouse RSS as a small source-kind pipeline. It should write raw/current inventory and rely on the existing location gate for user-facing relevance. In parallel or later, research legitimate Climatebase access and USAJobs API setup if the operator wants higher-volume climate/government sourcing.

## Rejected Or Deferred Paths

- Climatebase direct public scraping - deferred because direct fetch is blocked/SPA-heavy.
- USAJobs API implementation - deferred until API credentials/access are configured intentionally.
- USAJobs HTML scraping - rejected for now because an official API exists and should be preferred.

## Related Records

- `ticket:20260513-next-source-research-gjc-climatebase-usajobs` - closed from this research.
- `plan:20260513-broaden-mission-source-discovery` - consumes the recommendation.
