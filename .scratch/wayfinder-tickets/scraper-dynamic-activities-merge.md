# Ticket: Merge strategy for dynamicActivities vs static services

**Blocked by:** scraper-hybrid-data-source
**Blocks:** scraper-data-validation

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