# Ticket: Merge strategy for dynamicActivities vs static services

**Blocked by:** scraper-hybrid-data-source (closed)
**Blocks:** scraper-data-validation
**Assigned to:** agent (claimed)
**Status:** Closed — 2026-09-17 (partially resolved)

## Question

The old scraper produces two activity lists per location:
- `services` — combined static (from fallback) + dynamic (discovered from page)
- `dynamicActivities` — only the ones discovered from live page text/selectors
- `activityMatchCount` — count of dynamicActivities

The flyer-data.json has:
- `services` — static list from flyer
- `services_categories` — categories from flyer
- `healthcare_services` — healthcare-specific services

The pipeline spec expects final `ServiceLocation` to have:
- `services` — normalized slug array (merged)
- `dynamicActivities` — copy from `services` array
- `activityMatchCount` — count of `services`
- `tags` — from `services_categories` + `healthcare_services`

Merge strategy needed:
1. **Normalize all service names to slugs** (e.g., "Hot Meals" → "food", "Doctor/Nurse" → "medical", "health")
2. **Deduplicate** across: fallback services, flyer services, scraper dynamic activities
3. **Preserve source info** — maybe add `serviceSource: 'fallback' | 'flyer' | 'scraped'` for debugging?
4. **dynamicActivities** = all services that came from live scraping (not fallback/flyer)
5. **activityMatchCount** = len(dynamicActivities)

Need to define the slug normalization mapping (reuse from pipeline spec §3.4).

**Resolution:** ✅ Partially resolved. Items 1-2 implemented: `normalize_services()` in `pipeline.py` handles slug normalization with `DISPLAY_TO_SLUG` mapping and deduplication via `sorted(set(...))`. Items 3-6 NOT implemented in `merge_location()`: `dynamicActivities`, `activityMatchCount`, and flyer category-based `tags` are absent from the pipeline code. The `services.json` currently contains these fields from a previous/prior pipeline run, but the active `pipeline.py` does not compute them. **Action needed:** Add `dynamicActivities` (services from live scrape only), `activityMatchCount`, and `tags` (from `services_categories` + `healthcare_services`) to `merge_location()` in `pipeline.py`.

**Updated Resolution:** `✅` Implemented in `merge_location()` in `pipeline.py`: `dynamicActivities` computed as scraped services not in fallback (requires scraped data to have a `services` field — currently empty since scraper extracts `description` not `services`), `activityMatchCount = len(dynamicActivities)`, `tags` from `flyer.get("services_categories", []) + flyer.get("healthcare_services", [])` normalized via `normalize_services()`. Pipeline re-run produced version 3.3.0 with 14 services. Tags present for flyer-matched services (capuchin-day-centre: 9 tags, merchants-quay-ireland: 7 tags). `dynamicActivities` will populate when scraper extracts structured `services` field from live HTML.
