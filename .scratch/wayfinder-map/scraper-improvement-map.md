# Wayfinder Map: Scraper Improvement

## Destination

Build a **Python scraper + data pipeline** in this repo that: (1) scrapes configurable targets from `sources.json`, (2) merges with `flyer-data.json` enrichments (human-verified data takes precedence), (3) outputs `services.json` for the SvelteKit PWA, (4) runs daily via GitHub Actions cron.

## Notes

- Domain: Dublin City social services directory data pipeline
- Skills to consult: `grilling`, `domain-modeling`, `implement`, `tdd`
- Standing preferences: Python 3.10 (matches GitHub Actions), configurable target list, hybrid data source (scraper + flyer-data.json), output to `src/lib/data/services.json` + `static/services.json`
- Existing assets: Old scraper at `/home/martin/Dublin Services/scripts/scraper.js`, merger at `mergeData.js`, config at `config/sources.json` (14 targets), flyer data at `.scratch/wayfinder-map/research/flyer-data.json`
- Tracker: local markdown under `.scratch/wayfinder-tickets/`

## Decisions so far

- [Configurable target list](scraper-configurable-targets.md): ✅ Closed — 14 targets in `sources.json` with selectors, fallbacks, coordinates. Runtime selection via `--targets`/`--flyer-only`/`--dry-run`
- [Python implementation](scraper-python-implementation.md): ✅ Closed — `scraper/scraper.py` with async httpx, rate limiter, retry/backoff, archive fallback; `scraper/pipeline.py` with merge, normalization, diff, version bumping, dual-write; `scraper/tests/` with 3 test files
- [Hybrid data source](scraper-hybrid-data-source.md): ✅ Closed — `merge_location()` in `pipeline.py` implements all rules: flyer fields win when non-null, scraper fills gaps, `dataSource`/`scrapeSuccess` tracking, `lastScraped` timestamps, service normalization via `DISPLAY_TO_SLUG` mapping
- [Output locations](scraper-output-locations.md): ✅ Closed — `write_services()` writes to both `src/lib/data/services.json` and `static/services.json` identically; metadata includes all required fields; `bump_version()` implements semver. **Bugs found:** `static/services.json` was stale (synced now), and version wasn't bumped despite 9 updates (pipeline needs re-run)
- [GitHub Actions integration](scraper-github-actions.md): ✅ Closed — `.github/workflows/scraper.yml` has checkout, setup-python@v5 3.10, pip install requirements, `python scraper/main.py` (which calls `run_pipeline()`), commit, deploy to GitHub Pages. Cron `0 6 * * *` + `workflow_dispatch` configured
- [Scraper CLI interface](scraper-cli-interface.md): CLI flags for `--targets`, `--flyer-only`, `--dry-run`, `--output`, `--config`, `--no-fallback`, `--verbose`
- [Rate limiting and retry strategy](scraper-rate-limiting.md): ✅ Closed — `_RateLimiter` (6s interval, ±0.5 jitter), `_retry_fetch` with exponential backoff, 5s httpx timeout, all in `scraper/scraper.py`; no extra deps
- [Local HTML archive fallback](scraper-local-archive-fallback.md): ✅ Closed — `scraper/docs/` with 20+ HTML archives; `fetch_with_fallback()` checks `{id}.html` and `dublin_lifeline_{id}.html`; `--no-fallback` flag raises on archive/none sources
- [Provider discovery feature](scraper-provider-discovery.md): ✅ Implemented — Focus Ireland page yields 35 categorized providers; regulator XLSX via `fetch_register.py` yields 998 Dublin candidates (12/14 targets overlap); 80 tests passing
- [Merge strategy for dynamicActivities vs static services](scraper-dynamic-activities-merge.md): ✅ Closed — `merge_location()` implements `dynamicActivities` (scraped services not in fallback), `activityMatchCount`, `tags` from `services_categories` + `healthcare_services` via `normalize_services()`. Pipeline 3.3.0, 14 services. Tags present for flyer-matched (capuchin-day-centre: 9, merchants-quay-ireland: 7). `dynamicActivities` empty because scraper extracts `description` not structured `services` field
- [Scrape failure handling](scraper-scrape-failure-handling.md): ✅ Closed (partial) — `merge_location()` implements `scrapeSuccess`/`dataSource` tracking; flyer-only locations handled via lookup; **bugs:** `services.json` has stale `dataSource: "scraped"` values from old pipeline run; no repeated-failure removal or review flag
- [Data validation schema](scraper-data-validation.md): ✅ Closed — `scraper/validate.py` with custom validators (no pydantic): location errors/warnings, hours format/ordering, service slug validation, clinic location_id check. `scraper/tests/test_validation.py` with 14 tests. CLI: `python3 scraper/validate.py src/lib/data/services.json`
- [Version bumping strategy](scraper-version-bumping.md): ✅ Closed — `bump_version()` implements all semver rules using `compute_diff()` output; `nextSync` set to `pipelineRun + 7 days`; 4 tests in `test_pipeline.py`
- [Test strategy](scraper-test-strategy.md): ✅ Closed — 64 tests across 4 test files (test_scraper.py, test_pipeline.py, test_validation.py, test_fixtures.py). `tests/fixtures/` with 20 HTML files. `test:scraper` in package.json, Makefile, CI runs pytest before deploy. `pytest-cov` in requirements.txt
- [Junk scrape detection](scraper-junk-scrape-detection.md): Open — live fetch + chrome-text extraction still recorded as `live`/`scrapeSuccess: true`; needs a field-sanity gate aligned with validate.py
- [Register merge](scraper-register-merge.md): Open — `fetch_register.py` yields 998 candidates but nothing consumes them; Samaritans/Crosscare mismatches unresolved
- [Version-bump semantics](scraper-version-bump-semantics.md): Open — 3.3.0 minted a minor bump on tag churn + timestamps; bump rules vs diff granularity undecided

## Not yet specified

- Pipeline orchestration as a distinct module (currently embedded in `scraper/pipeline.py`; may need separate extraction)

## Out of scope

- Changing the SvelteKit PWA frontend
- Adding new service categories beyond existing 7
- Real-time/background sync (PWA uses StaleWhileRevalidate)
- Provider submission forms (Web3Forms - separate feature)
- Native app builds
- ~~Provider discovery feature — deferred as out of scope for MVP~~ → implemented; live URL refresh still out of scope
