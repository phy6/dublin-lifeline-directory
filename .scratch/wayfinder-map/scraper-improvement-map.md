# Wayfinder Map: Scraper Improvement

## Destination

Build a **Python scraper + data pipeline** in this repo that: (1) scrapes configurable targets from `sources.json`, (2) merges with `flyer-data.json` enrichments (human-verified data takes precedence), (3) outputs `services.json` for the SvelteKit PWA, (4) runs daily via GitHub Actions cron.

## Notes

- Domain: Dublin City social services directory data pipeline
- Skills to consult: `grilling`, `domain-modeling`, `implement`, `tdd`
- Standing preferences: Python 3.10 (matches GitHub Actions), configurable target list, hybrid data source (scraper + flyer-data.json), output to `src/lib/data/services.json` + `static/services.json`
- Existing assets: Old scraper at `/home/martin/Dublin Services/scripts/scraper.js`, merger at `mergeData.js`, config at `config/sources.json` (14 targets), flyer data at `.scratch/wayfinder-map/research/flyer-data.json`
- Tracker: local markdown under `.scratch/wayfinder-map/`

## Decisions so far

- [Configurable target list](scraper-configurable-targets.md): Target list driven by `sources.json`; can run subset via CLI flag
- [Python implementation](scraper-python-implementation.md): Port scraper logic to Python 3.10; use `requests`, `beautifulsoup4`, `lxml`
- [Hybrid data source](scraper-hybrid-data-source.md): Scraper output merges with flyer-data.json; human-verified enrichments (coordinates, phones, hours) take precedence
- [Output locations](scraper-output-locations.md): Write to both `src/lib/data/services.json` (for SSR) and `static/services.json` (for client fetch)
- [GitHub Actions integration](scraper-github-actions.md): Update `.github/workflows/scraper.yml` to run `python scraper/main.py` daily at 06:00 UTC

## Not yet specified

- Scraper CLI interface (flags for target subset, dry-run, output path)
- Rate limiting and retry strategy in Python
- Local HTML archive fallback (like old scraper's `docs/` fallback)
- Provider discovery feature (from old scraper's discovery config)
- Data validation schema (reuse from pipeline spec)
- Merge strategy for dynamicActivities vs static services
- Version bumping strategy (semver in services.json metadata)
- Test strategy (unit tests for scraper, integration for pipeline)
- Handling of `scrapeSuccess: false` entries (COPE Ireland pattern)

## Out of scope

- Changing the SvelteKit PWA frontend
- Adding new service categories beyond existing 7
- Real-time/background sync (PWA uses StaleWhileRevalidate)
- Provider submission forms (Web3Forms - separate feature)
- Native app builds