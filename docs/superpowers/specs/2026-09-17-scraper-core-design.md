# Scraper Core Infrastructure — Design Spec

**Date:** 2026-09-17
**Status:** Draft
**Scope:** Tickets 1-3 (configurable targets, Python implementation, CLI interface)
**Author:** Dublin City Support Services team

---

## 1. Architecture Overview

A Python-based scraper + pipeline system that replaces the existing Node.js scraper. It fetches service data from 14 configured targets, merges with flyer enrichments, and writes the final `services.json` for the SvelteKit PWA.

```
┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  scraper/config/    │────▶│  scraper/scraper │────▶│  scraped_output │
│  sources.json       │     │  .py (fetch +    │     │  _json          │
│  (14 targets)       │     │   parse)         │     │                 │
└─────────────────────┘     └──────────────────┘     └────────┬────────┘
                                                                │
                    ┌──────────────────┐                        │
                    │  scraper/docs/   │                        │
                    │  (HTML archive)  │                        │
                    └──────────────────┘                        │
                                                                ▼
┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  scraper/pipeline  │◀────│  scraped_output  │────▶│  src/lib/data/  │
│  .py (merge +      │     │  _json           │     │  services.json  │
│   validate +       │     │                  │     │  (SvelteKit SSR)│
│   version bump)    │     └──────────────────┘     └────────┬────────┘
└─────────────────────┘                                        │
                                                               ▼
                                                    ┌─────────────────┐
                                                    │  static/        │
                                                    │  services.json  │
                                                    │  (GitHub Pages) │
                                                    └─────────────────┘
```

### Integration Points

- **SvelteKit build**: `+page.server.ts` imports `services.json` at build time. Pipeline writes to `src/lib/data/services.json` before `npm run build`.
- **Static adapter**: `static/services.json` is served directly by GitHub Pages for client-side fetch and service worker caching.
- **GitHub Actions**: `scraper.yml` runs the pipeline, commits updated data files, and deploys.
- **Existing workflows**: `test.yml` builds with whatever `services.json` is present on push/PR.

---

## 2. Target Configuration (Ticket 1)

### File: `scraper/config/sources.json`

Mirrors the existing `/home/martin/Dublin Services/config/sources.json` structure with 14 targets. Each target has:

```json
{
  "id": "capuchin-day-centre",
  "name": "Capuchin Day Centre",
  "url": "https://capuchindaycentre.ie/",
  "selectors": {
    "phone": ["a[href^=\"tel\"]", ".phone", ...],
    "address": [".address", ".location-address", ...],
    "hours": [".opening-hours", ".hours", ...],
    "email": ["a[href^=\"mailto\"]", ".contact-email", ...],
    "website": [".website-link", "a[href^=\"http\"]:not([href^=\"mailto\"])", ...],
    "description": [".services-description", ".about-text", ...]
  },
  "fallback": {
    "name": "...", "address": "...", "phone": "...",
    "hours": {...}, "email": "...", "website": "...",
    "services": [...], "tags": [...], "category": "...",
    "latitude": 53.3481, "longitude": -6.2758,
    "description": "..."
  }
}
```

**Config loading**: The scraper reads `sources.json` at startup. Supports `--config <path>` flag (default: `scraper/config/sources.json`).

---

## 3. Python Scraper (Ticket 2)

### File: `scraper/scraper.py`

Core class `DublinLifelineScraper` that:

1. **Loads config** from `sources.json`
2. **Fetches HTML** for each target using `httpx.AsyncClient`
   - Rate limiting: 6 seconds between requests (10 req/min)
   - Timeout: 5 seconds
   - Retry: 3 attempts with exponential backoff (2s, 3s, 4.5s)
   - Random jitter: ±500ms on delays
3. **Falls back to local HTML archive** (`scraper/docs/`) if live fetch fails
4. **Parses HTML** using `beautifulsoup4` + `lxml`
5. **Extracts fields** using configured selectors (phone, address, hours, email, website, description)
6. **Outputs** `scraper/output/scraped_output.json` with the same schema as the old scraper

### Class Structure

```python
class DublinLifelineScraper:
    def __init__(self, config_path: str) -> None:
        self.config = load_json(config_path)
        self.results: list[dict] = []
        self.errors: list[dict] = []

    async def fetch_target(self, target: dict) -> dict | None:
        """Fetch and parse a single target. Returns result or None."""

    async def run(self, targets: list[str] | None = None) -> None:
        """Run scraper for specified targets (or all)."""

    def _extract_field(self, soup: BeautifulSoup, selectors: list[str]) -> str | None:
        """Try each selector until one returns a match."""
```

### Dependencies (`scraper/requirements.txt`)

```
httpx>=0.27.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
python-dotenv>=1.0.0
```

No extra dependencies for retry logic — custom async retry wrapper with exponential backoff.

---

## 4. Pipeline (Ticket 2)

### File: `scraper/pipeline.py`

Reads `scraped_output.json` + `flyer-data.json`, produces final `services.json`.

**Steps:**

1. Load `scraped_output.json`
2. Load `flyer-data.json` (human-verified enrichments: coordinates, phone numbers)
3. For each target in scraped output:
   - Start with fallback data from `sources.json`
   - Override with scraped data (live fetch results)
   - Override with flyer data where non-null (human-verified wins)
   - Set `dataSource`, `lastScraped`, `scrapeSuccess`
4. Normalize services to slugs, deduplicate
5. Build metadata (version, timestamps, diffs)
6. Write to `src/lib/data/services.json` and `static/services.json`

**Merge rules (human-verified wins):**

- If flyer-data.json has non-null value for phone, coordinates, email, website, hours → use it
- Scraper fills gaps for locations not in flyer-data.json or fields missing in flyer

**Version bumping:**

- Patch (x.y.Z+1): only metadata changes (timestamps, nextSync)
- Minor (x.Y+1.0): additions or updates to service data
- Major ((X+1).0.0): schema changes or deletions

---

## 5. CLI Interface (Ticket 3)

### File: `scraper/main.py`

Entry point with `argparse`:

```bash
python scraper/main.py                          # Run all targets
python scraper/main.py --targets capuchin-day-centre,merchants-quay-ireland  # Subset
python scraper/main.py --flyer-only             # Only 10 flyer targets
python scraper/main.py --dry-run                # Show targets without fetching
python scraper/main.py --no-fallback            # Fail if live fetch fails
python scraper/main.py --verbose                # Detailed logging
python scraper/main.py --config path/to/sources.json
python scraper/main.py --output path/to/output.json
```

**Flow:**

1. Parse CLI args
2. Load config
3. If `--dry-run`, print targets and exit
4. Run scraper (with or without fallback based on `--no-fallback`)
5. Run pipeline (merge + validate + write services.json)
6. Print summary (targets scraped, errors, version bump)

---

## 6. Offline Support

### File: `scraper/docs/`

Local HTML archive directory. Contains saved HTML files from each target (copied from `/home/martin/Dublin Services/docs/`).

**Fallback strategy:**

1. Try live fetch with `httpx`
2. If fetch fails, check `scraper/docs/<id>.html` or `scraper/docs/dublin_lifeline_<id>.html`
3. If archive exists, parse it and mark `dataSource: 'local-archive'`
4. If no archive, use fallback data from `sources.json` and mark `scrapeSuccess: false`

---

## 7. GitHub Actions Integration

### Updated `scraper.yml`

```yaml
- Install dependencies: pip install -r scraper/requirements.txt
- Run scraper: python scraper/main.py
- Commit updated data: git add src/lib/data/services.json static/services.json
- Deploy to GitHub Pages
```

Changes from current workflow:

- `pip install` reads from `scraper/requirements.txt` instead of installing packages inline
- `git add` includes both `src/lib/data/services.json` and `static/services.json`
- `--flyer-only` flag optional for faster runs

---

## 8. Non-Goals

- **Provider discovery**: Deferred to follow-up ticket
- **Dynamic activities merge**: Deferred — scraper outputs raw data, pipeline normalizes
- **Data validation schema**: Deferred to follow-up ticket (pipeline does basic validation)
- **Test strategy**: Deferred to follow-up ticket
- **Rate limiting library**: Custom async retry wrapper, no `tenacity` dependency
- **Local archive copy**: Copy from old project, not re-implement archive discovery

---

## 9. Acceptance Criteria

For the first 3 tickets:

1. **scraper/config/sources.json** exists with all 14 targets and their selectors/fallbacks
2. **scraper/scraper.py** fetches a target, parses HTML, handles failures gracefully
3. **scraper/pipeline.py** merges scraped output with flyer data and writes valid `services.json`
4. **scraper/main.py** runs with `--targets`, `--flyer-only`, `--dry-run`, `--no-fallback`, `--verbose`
5. **scraper/requirements.txt** lists all dependencies
6. **scraper/output/scraped_output.json** is produced after a run
7. **src/lib/data/services.json** and **static/services.json** are updated after pipeline runs
8. **scraper.yml** is updated to use the new structure
9. `npm run build` still works after pipeline writes updated JSON
10. `npm test` still passes
