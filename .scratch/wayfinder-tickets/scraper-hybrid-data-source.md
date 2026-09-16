# Ticket: Hybrid data source

**Blocked by:** scraper-python-implementation
**Blocks:** scraper-dynamic-activities-merge, scraper-scrape-failure-handling, scraper-data-validation, scraper-version-bumping

## Question

Define the merge strategy between scraper output and `flyer-data.json` enrichments. The flyer data (in `.scratch/wayfinder-map/research/flyer-data.json`) has human-researched:
- Coordinates for all 10 flyer locations
- Phone numbers for all 10 locations
- GP clinic schedules (3 of 5 confirmed)
- MHU schedule (Tue/Thu at Mendicity, Wed at Lighthouse)

The scraper will produce fresh data from live sites. Merge rules:
- **Human-verified fields win**: If flyer-data.json has a non-null value for phone, coordinates, email, website, hours → use it
- **Scraper fills gaps**: For locations not in flyer-data.json, or fields missing in flyer-data.json, use scraper result
- **Dynamic activities**: Scraper discovers activities from live pages; merge with flyer's static services
- **scrapeSuccess tracking**: Track whether each location came from live scrape, local archive, fallback, or flyer data
- **lastScraped timestamp**: Update when scraper runs; flyer data has its own `extracted_date`

The merge should happen in the pipeline (separate from scraper), producing final `services.json`.