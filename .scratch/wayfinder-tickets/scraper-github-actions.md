# Ticket: GitHub Actions integration

**Blocked by:** scraper-python-implementation, scraper-output-locations
**Blocks:** None

## Question

Update `.github/workflows/scraper.yml` to run the new Python scraper + pipeline. Current workflow expects `scraper/main.py` but it doesn't exist. New workflow should:

1. **Checkout** repo
2. **Setup Python 3.10** (already in workflow)
3. **Install dependencies** from `scraper/requirements.txt` (`httpx`, `beautifulsoup4`, `lxml`)
4. **Run scraper** → `python scraper/main.py` (outputs `scraper/output/scraped_output.json`)
5. **Run pipeline** → `python scraper/pipeline.py` (reads scraped_output.json + flyer-data.json, writes services.json)
6. **Commit updated data** if changed (already in workflow)
7. **Deploy to GitHub Pages** (already in workflow)

The workflow runs daily at 06:00 UTC (`cron: '0 6 * * *'`). Should also support `workflow_dispatch` for manual runs.

Consider: run scraper and pipeline as separate steps for better logging/debugging, or combine into one script?