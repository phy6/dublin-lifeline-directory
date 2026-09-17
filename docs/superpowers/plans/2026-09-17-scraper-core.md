# Scraper Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python scraper + pipeline system that replaces the Node.js scraper, fetches 14 service targets, merges with flyer enrichments, and writes `services.json` for the SvelteKit PWA.

**Architecture:** Python 3.10 with httpx/beautifulsoup4/lxml. The scraper fetches HTML, falls back to local archive, and outputs scraped_output.json. The pipeline merges scraped output with flyer-data.json and writes services.json to both src/lib/data/ and static/.

**Tech Stack:** Python 3.10, httpx, beautifulsoup4, lxml, python-dotenv, argparse

**Spec:** `docs/superpowers/specs/2026-09-17-scraper-core-design.md`

---

## Global Constraints

- Python 3.10 (matches GitHub Actions runner)
- `httpx` for HTTP, `beautifulsoup4` + `lxml` for parsing
- No extra deps for retry logic (custom async wrapper)
- Replace `services.json` entirely on each pipeline run
- Local HTML archive fallback for offline support
- 14 targets from `sources.json` with selectors + fallback data
- Rate limiting: 6s between requests, 5s timeout, 3 retries exponential backoff
- Output to `src/lib/data/services.json` AND `static/services.json`
- `npm run build` must still work after pipeline writes updated JSON
- `npm test` must still pass

---

## File Map

### New files (to create)

- `scraper/config/sources.json` — 14 target configs with selectors and fallback data
- `scraper/scraper.py` — Core DublinLifelineScraper class
- `scraper/pipeline.py` — Merge + output pipeline
- `scraper/main.py` — CLI entry point
- `scraper/requirements.txt` — Python dependencies
- `scraper/output/scraped_output.json` — Intermediate output (generated)
- `scraper/docs/` — Local HTML archive (copied from old docs)
- `scraper/tests/test_scraper.py` — Unit tests
- `scraper/tests/test_pipeline.py` — Pipeline tests
- `docs/superpowers/plans/2026-09-17-scraper-core.md` — This plan

### Modified files

- `.github/workflows/scraper.yml` — Updated to use new structure
- `src/lib/data/services.json` — Will be overwritten by pipeline (no code changes needed)

---

## Task 1: Configurable Targets

**Files:** Create `scraper/config/sources.json`

This is the foundation — all other tasks depend on it. Copy the existing 14-target config from the old project.

- [ ] **Step 1: Copy sources.json from old project**
      Read `/home/martin/Dublin Services/config/sources.json` and copy the full JSON to `scraper/config/sources.json`. Preserve all 14 targets, their URLs, selectors, and fallback data.

  Command: `cp /home/martin/Dublin\ Services/config/sources.json scraper/config/sources.json`

- [ ] **Step 2: Verify the JSON is valid**
      Run: `python3 -c "import json; d=json.load(open('scraper/config/sources.json')); print(f'{len(d[\"targets\"])} targets, version={d[\"version\"]}')"`
      Expected: `14 targets, version=3.1.0`

- [ ] **Step 3: Verify all targets have selectors and fallback**
      Run: `python3 -c "import json; d=json.load(open('scraper/config/sources.json')); assert all('selectors' in t and 'fallback' in t for t in d['targets']); print('All targets have selectors and fallback')"`
      Expected: `All targets have selectors and fallback`

- [ ] **Step 4: Commit**
  ```bash
  git add scraper/config/sources.json
  git commit -m "feat(scraper): add configurable target sources"
  ```

---

## Task 2: Python Scraper

**Files:** Create `scraper/scraper.py`, `scraper/tests/test_scraper.py`

Core scraper that fetches HTML, parses with selectors, falls back to local archive.

- [ ] **Step 1: Create requirements.txt**
      Write `scraper/requirements.txt`:

  ```
  httpx>=0.27.0
  beautifulsoup4>=4.12.0
  lxml>=5.0.0
  python-dotenv>=1.0.0
  ```

- [ ] **Step 2: Create the scraper module structure**
      Write `scraper/scraper.py` with:
  - `load_config(config_path: str) -> dict` — loads sources.json
  - `extract_field(soup: BeautifulSoup, selectors: list[str]) -> str | None` — tries each selector in order, returns first match
  - `async fetch_url(client: httpx.AsyncClient, url: str, timeout: float = 5.0) -> str` — fetches HTML with timeout
  - `async fetch_with_fallback(target: dict, docs_dir: str) -> tuple[str | None, str]` — tries live fetch, falls back to local archive
  - `class DublinLifelineScraper` with `__init__`, `async run()`, `async fetch_target()` methods
  - Custom async retry wrapper with exponential backoff (2s, 3s, 4.5s)
  - Rate limiting: 6s between requests, ±500ms jitter
  - Output: `scraped_output.json` with list of results

- [ ] **Step 3: Copy HTML archive from old project**

  ```bash
  mkdir -p scraper/docs
  cp /home/martin/Dublin\ Services/docs/*.html scraper/docs/
  ```

  Verify: `ls scraper/docs/*.html | wc -l` should be 20+ HTML files

- [ ] **Step 4: Write failing unit tests**
      Write `scraper/tests/test_scraper.py`:
  - Test `extract_field` returns first matching selector
  - Test `extract_field` returns None when no selector matches
  - Test `load_config` returns dict with 14 targets
  - Test retry logic with mocked failure
  - Test local archive fallback when fetch fails
  - Use `httpx.MockTransport` for HTTP mocking

- [ ] **Step 5: Run tests to verify they fail**
      Run: `cd scraper && python -m pytest tests/test_scraper.py -v`
      Expected: FAIL (module not found or tests not yet passing)

- [ ] **Step 6: Implement minimal code to pass tests**
      Implement just enough in `scraper/scraper.py` to pass all tests.

- [ ] **Step 7: Run tests to verify they pass**
      Run: `cd scraper && python -m pytest tests/test_scraper.py -v`
      Expected: All PASS

- [ ] **Step 8: Install dependencies and do a smoke test**

  ```bash
  pip install -r scraper/requirements.txt
  python scraper/main.py --dry-run --flyer-only
  ```

  Expected: Prints target list and exits without fetching

- [ ] **Step 9: Commit**
  ```bash
  git add scraper/scraper.py scraper/requirements.txt scraper/docs/ scraper/tests/test_scraper.py
  git commit -m "feat(scraper): add Python scraper with archive fallback"
  ```

---

## Task 3: Pipeline

**Files:** Create `scraper/pipeline.py`, `scraper/tests/test_pipeline.py`

Reads scraped_output.json + flyer-data.json, produces final services.json.

- [ ] **Step 1: Load flyer-data.json reference**
      Read `.scratch/wayfinder-map/research/flyer-data.json` to understand the structure. The pipeline needs to know the fields available in flyer data.

- [ ] **Step 2: Write pipeline module**
      Write `scraper/pipeline.py` with:
  - `load_flyer_data(path: str) -> dict` — loads flyer-data.json
  - `merge_location(scraped: dict, flyer: dict, fallback: dict) -> dict` — human-verified wins (flyer non-null overrides scraped)
  - `normalize_services(services: list[str]) -> list[str]` — convert display names to slugs
  - `compute_diff(old: dict, new: dict) -> dict` — additions, updates, deletions
  - `bump_version(old_version: str, diffs: dict) -> str` — patch/minor/major
  - `write_services(data: dict) -> None` — writes to src/lib/data/services.json AND static/services.json
  - `run_pipeline(scraped_path: str, flyer_path: str, output_dir: str) -> dict` — orchestrates the full pipeline

- [ ] **Step 3: Write failing pipeline tests**
      Write `scraper/tests/test_pipeline.py`:
  - Test `merge_location` prefers flyer data over scraped data
  - Test `normalize_services` converts "Hot Meals" to "food"
  - Test `bump_version` increments patch for metadata-only changes
  - Test `bump_version` increments minor for additions
  - Test `bump_version` increments major for deletions
  - Test `compute_diff` detects additions, updates, deletions

- [ ] **Step 4: Run tests to verify they fail**
      Run: `cd scraper && python -m pytest tests/test_pipeline.py -v`
      Expected: FAIL

- [ ] **Step 5: Implement pipeline to pass tests**
      Implement `scraper/pipeline.py` with enough logic to pass all tests.

- [ ] **Step 6: Run tests to verify they pass**
      Run: `cd scraper && python -m pytest tests/test_pipeline.py -v`
      Expected: All PASS

- [ ] **Step 7: Full pipeline smoke test**

  ```bash
  python scraper/main.py --flyer-only --dry-run
  ```

  Then run the full pipeline with a small subset to verify output:

  ```bash
  python -c "from scraper.pipeline import run_pipeline; result = run_pipeline('scraper/output/scraped_output.json', '.scratch/wayfinder-map/research/flyer-data.json', 'scraper/output'); print(result)"
  ```

  Verify `src/lib/data/services.json` is valid JSON with `services` array and `metadata` block.

- [ ] **Step 8: Commit**
  ```bash
  git add scraper/pipeline.py scraper/tests/test_pipeline.py
  git commit -m "feat(scraper): add pipeline with merge, validation, and version bumping"
  ```

---

## Task 4: CLI Interface

**Files:** Create `scraper/main.py`

The entry point that ties scraper + pipeline together with argparse.

- [ ] **Step 1: Write failing CLI tests**
      Write `scraper/tests/test_cli.py`:
  - Test `--help` exits with usage info
  - Test `--dry-run` prints targets and exits
  - Test `--flyer-only` limits to 10 targets
  - Test `--targets` filters to specified subset
  - Test `--no-fallback` raises on fetch failure
  - Test `--verbose` enables detailed logging

- [ ] **Step 2: Write main.py with argparse**
      Write `scraper/main.py`:
  - `argparse` with flags: `--targets`, `--flyer-only`, `--dry-run`, `--no-fallback`, `--verbose`, `--config`, `--output`
  - Load config
  - If `--dry-run`, print targets and exit
  - Run scraper (with/without fallback)
  - Run pipeline (merge + validate + write)
  - Print summary (targets scraped, errors, version bump)
  - Exit code 0 on success, 1 on critical failure

- [ ] **Step 3: Run tests to verify they pass**
      Run: `cd scraper && python -m pytest tests/test_cli.py -v`
      Expected: All PASS

- [ ] **Step 4: End-to-end test**

  ```bash
  python scraper/main.py --flyer-only --dry-run
  ```

  Expected: Prints list of 10 flyer targets and exits cleanly.

- [ ] **Step 5: Commit**
  ```bash
  git add scraper/main.py scraper/tests/test_cli.py
  git commit -m "feat(scraper): add CLI interface with argparse"
  ```

---

## Task 5: GitHub Actions + Archive

**Files:** Modify `.github/workflows/scraper.yml`, copy archive docs

Update the workflow to use the new scraper structure and copy HTML archive.

- [ ] **Step 1: Copy HTML archive to scraper/docs**

  ```bash
  cp /home/martin/Dublin\ Services/docs/*.html scraper/docs/
  ls scraper/docs/*.html | wc -l
  ```

  Expected: 20+ HTML files copied

- [ ] **Step 2: Update scraper.yml**
      Modify `.github/workflows/scraper.yml`:
  - `pip install` reads from `scraper/requirements.txt`
  - Run command: `python scraper/main.py --flyer-only` (or `python scraper/main.py`)
  - `git add src/lib/data/services.json static/services.json`
  - Keep existing deploy step
  - Add `continue-on-error: false` for the scraper step

- [ ] **Step 3: Verify the workflow YAML is valid**
      Run: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/scraper.yml')); print('Valid YAML')"`
      Expected: `Valid YAML`

- [ ] **Step 4: Commit**
  ```bash
  git add scraper/docs/ .github/workflows/scraper.yml
  git commit -m "feat(scraper): update GitHub Actions workflow with archive and new structure"
  ```

---

## Task 6: Integration Verification

Verify everything works end-to-end with the SvelteKit app.

- [ ] **Step 1: Verify npm run build still works**
      Run: `npm run build`
      Expected: Build succeeds with updated services.json

- [ ] **Step 2: Verify npm test still passes**
      Run: `npm run test`
      Expected: All 35 tests pass

- [ ] **Step 3: Verify npm run lint passes**
      Run: `npx eslint src/`
      Expected: No errors

- [ ] **Step 4: Verify npm run check passes**
      Run: `npm run check`
      Expected: 0 errors (6 warnings are expected Svelte 5 patterns)

- [ ] **Step 5: Final commit**
  ```bash
  git add -A
  git commit -m "feat(scraper): complete scraper core infrastructure implementation"
  ```
