# Ticket: GitHub Actions integration

**Blocked by:** scraper-python-implementation (closed), scraper-output-locations (closed)
**Blocks:** None
**Assigned to:** agent (claimed)
**Status:** Closed — 2026-09-17

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

**Resolution:** ✅ Fully implemented in `.github/workflows/scraper.yml`: checkout, setup-python@v5 with Python 3.10, `pip install -r scraper/requirements.txt`, `python scraper/main.py` (which internally calls `run_pipeline()`), commit updated data to `src/lib/data/services.json` and `static/services.json`, deploy to GitHub Pages via `peaceiris/actions-gh-pages@v3`. Cron `0 6 * * *` and `workflow_dispatch` both configured. Scraper and pipeline are combined into one step via `main.py` calling `run_pipeline()`.

Note: The `main.py` also runs the pipeline as part of its execution, so the scraper+pipeline are effectively combined. This was the "combine into one script" option from the ticket's consideration. The separate `scraper/pipeline.py` can still be run standalone via `python scraper/pipeline.py`.

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