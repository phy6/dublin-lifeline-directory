# Ticket: Python implementation

**Blocked by:** scraper-configurable-targets
**Blocks:** scraper-cli-interface, scraper-rate-limiting, scraper-local-archive-fallback, scraper-provider-discovery, scraper-test-strategy, scraper-scrape-failure-handling

## Question

Port the scraper logic from Node.js (`/home/martin/Dublin Services/scripts/scraper.js`) to Python 3.10. Key components to port:

1. **DublinLifelineScraper class** → Python class with async support
2. **HTTP fetching** with rate limiting, retries, timeouts → use `httpx` or `requests` with `asyncio`
3. **HTML parsing** with Cheerio → use `beautifulsoup4` + `lxml`
4. **Selector extraction** (phone, address, hours, email, website, description) → replicate selector lists
5. **Activity extraction** (taxonomy keyword matching on full text + specific selectors) → port `ACTIVITY_TAXONOMY` and `ACTIVITY_SELECTORS`
6. **Tag extraction** → port `tagPatterns`
7. **Category detection** → port `categoryMap`
8. **Local HTML archive fallback** → check `scraper/docs/` for saved HTML
9. **Provider discovery** → port discovery logic (optional, can defer)
10. **Output** → write `scraped_output.json` with same schema as old scraper

Dependencies: `httpx`, `beautifulsoup4`, `lxml`, `python-dotenv` (for config)