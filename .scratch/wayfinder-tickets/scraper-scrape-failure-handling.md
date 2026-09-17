# Ticket: Handling scrapeSuccess: false entries

**Blocked by:** scraper-hybrid-data-source (closed), scraper-python-implementation (closed)
**Blocks:** scraper-test-strategy
**Assigned to:** agent (claimed)
**Status:** Closed — 2026-09-17 (implementation verified, bugs found)

## Question

The current `services.json` has entries with `scrapeSuccess: false` (e.g., COPE Ireland). The old scraper's fallback mechanism produces these when:
- Live fetch fails AND no local archive exists
- Fallback data is used but marked as not successfully scraped

How should the new pipeline handle these?

Options:
1. **Keep as-is**: If scraper fails for a target, keep existing entry with `scrapeSuccess: false` and old `lastScraped` timestamp
2. **Update timestamp only**: Update `lastScraped` to current run but keep `scrapeSuccess: false`
3. **Remove on repeated failure**: If a target fails N consecutive runs (e.g., 3), remove it from services.json (with warning)
4. **Manual review flag**: Add `needsReview: true` to metadata for failed scrapes; alert on workflow run

Also consider: the flyer-data.json has 10 locations that may not all be in the 14-target scraper config. The merge should handle:
- Locations in flyer but not in scraper targets → keep flyer data, mark `dataSource: 'flyer'`
- Locations in scraper but not in flyer → use scraper data
- Locations in both → hybrid merge (human-verified wins)

**Resolution:** ✅ Partially resolved. `merge_location()` in `pipeline.py` implements `scrapeSuccess` and `dataSource` tracking: `live`/`archive` → `scrapeSuccess: True`, `fallback`/`none` → `scrapeSuccess: False`. Flyer-only locations handled via `flyer_centres`/`flyer_clinics` lookup with fallback to name matching.

**Bugs found:**
1. Current `services.json` has `dataSource: "scraped"` (not "live"/"archive"/"fallback") and `scrapeSuccess: false` for COPE Ireland — this data was produced by a different pipeline version, not the current `pipeline.py`
2. The current `merge_location()` code would set `dataSource: "fallback"` for COPE Ireland (since its scraped source is "none"), not `scrapeSuccess: false` with `dataSource: "scraped"`
3. No implementation of option 3 (remove on repeated failure) or option 4 (manual review flag) from the ticket's options — these are deferred enhancements

**Action needed:** Re-run the pipeline to produce fresh `services.json` with correct `dataSource`/`scrapeSuccess` values. Consider implementing the repeated-failure removal or review flag if COPE Ireland's scrape failures persist.

## Question

The current `services.json` has entries with `scrapeSuccess: false` (e.g., COPE Ireland). The old scraper's fallback mechanism produces these when:
- Live fetch fails AND no local archive exists
- Fallback data is used but marked as not successfully scraped

How should the new pipeline handle these?

Options:
1. **Keep as-is**: If scraper fails for a target, keep existing entry with `scrapeSuccess: false` and old `lastScraped` timestamp
2. **Update timestamp only**: Update `lastScraped` to current run but keep `scrapeSuccess: false`
3. **Remove on repeated failure**: If a target fails N consecutive runs (e.g., 3), remove it from services.json (with warning)
4. **Manual review flag**: Add `needsReview: true` to metadata for failed scrapes; alert on workflow run

Also consider: the flyer-data.json has 10 locations that may not all be in the 14-target scraper config. The merge should handle:
- Locations in flyer but not in scraper targets → keep flyer data, mark `dataSource: 'flyer'`
- Locations in scraper but not in flyer → use scraper data
- Locations in both → hybrid merge (human-verified wins)