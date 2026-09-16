# Ticket: Scraper CLI interface

**Blocked by:** scraper-configurable-targets, scraper-python-implementation
**Blocks:** None

## Question

Design the CLI interface for `scraper/main.py`. Required flags:

- `--targets <csv>` — comma-separated list of target IDs to scrape (default: all)
- `--flyer-only` — scrape only the 10 flyer targets (5 Day Support Centres + 5 GP Clinics/MHU)
- `--dry-run` — show targets and selectors without fetching
- `--output <path>` — output file for scraped_output.json (default: `scraper/output/scraped_output.json`)
- `--config <path>` — path to sources.json (default: `scraper/config/sources.json`)
- `--no-fallback` — fail if live fetch fails (don't use local archive or fallback data)
- `--verbose` / `-v` — detailed logging
- `--help` — show usage

Also support environment variables for sensitive config (none currently needed).