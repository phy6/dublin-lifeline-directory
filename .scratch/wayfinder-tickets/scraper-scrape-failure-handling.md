# Ticket: Handling scrapeSuccess: false entries

**Blocked by:** scraper-hybrid-data-source, scraper-python-implementation
**Blocks:** None

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