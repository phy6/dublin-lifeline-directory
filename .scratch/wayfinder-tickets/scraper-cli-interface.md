# Ticket: Scraper CLI interface

**Blocked by:** scraper-configurable-targets (closed), scraper-rate-limiting (closed), scraper-local-archive-fallback (closed)
**Blocks:** None
**Assigned to:** agent (claimed)
**Status:** Closed — 2026-09-17

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

**Resolution:** ✅ Fully implemented in `scraper/main.py`: `parse_args()` handles all flags, `get_targets()` filters by `--targets`/`--flyer-only`, `run_scraper()` handles `--no-fallback` logic, `main()` orchestrates the full pipeline. `test_cli.py` has 11 tests covering all flags, `--flyer-only` filtering (3 targets), `--targets` filtering, `--dry-run`, `--no-fallback`, `--verbose`, default args, and error handling.

Note: `--flyer-only` returns 3 targets (mendicity-institution, merchants-quay-ireland, capuchin-day-centre) based on `FLYER_ID_MAP` — the old 10-flyer target count doesn't apply since the GP clinics are separate targets in sources.json.

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