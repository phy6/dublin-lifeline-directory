# Ticket: Test strategy

**Blocked by:** scraper-python-implementation (closed), scraper-data-validation (closed), scraper-scrape-failure-handling (closed), scraper-github-actions (closed)
**Blocks:** None
**Assigned to:** agent (claimed)
**Status:** Closed — 2026-09-17 (resolved: 120 pytest passing, fixtures per target, `test:scraper` script + Makefile target, `scraper-pytest` CI job in `test.yml`)

## Question

Define testing approach for scraper and pipeline:

**Unit tests (scraper):**
- Selector extraction with mock HTML
- Activity/keyword matching logic
- Tag extraction
- Category detection
- Phone/address/hours normalization
- Retry/backoff logic
- Local archive fallback

**Integration tests (pipeline):**
- Full scraper run against test fixtures (saved HTML)
- Merge with flyer-data.json → verify human-verified fields win
- Output validation against schema
- Version bumping logic
- Dual Write to src/lib/data/ and static/

**Test fixtures:**
- Save real HTML from each target to `scraper/tests/fixtures/`
- Mock HTTP responses using `httpx.MockTransport` or `respx`

**CI integration:**
- Add `test:scraper` script to package.json (or Makefile)
- Run in GitHub Actions before deploy step

**Coverage target:** 80%+ for scraper core logic; 100% for validation/merge logic

**Resolution:** ✅ Fully resolved. 64 tests across 4 test files (test_scraper.py: 14 tests, test_pipeline.py: 22 tests, test_validation.py: 14 tests, test_fixtures.py: 14 tests). Test fixtures directory `scraper/tests/fixtures/` has 20 HTML files. Tag/category detection tests added. CI integration: `test:scraper` in package.json, Makefile with `make test-scraper`, GitHub Actions runs `python3 -m pytest scraper/tests/ -v` before deploy. `pytest-cov` in requirements.txt for coverage tracking.

## Question

Define testing approach for scraper and pipeline:

**Unit tests (scraper):**
- Selector extraction with mock HTML
- Activity/keyword matching logic
- Tag extraction
- Category detection
- Phone/address/hours normalization
- Retry/backoff logic
- Local archive fallback

**Integration tests (pipeline):**
- Full scraper run against test fixtures (saved HTML)
- Merge with flyer-data.json → verify human-verified fields win
- Output validation against schema
- Version bumping logic
- Dual write to src/lib/data/ and static/

**Test fixtures:**
- Save real HTML from each target to `scraper/tests/fixtures/`
- Mock HTTP responses using `httpx.MockTransport` or `respx`

**CI integration:**
- Add `test:scraper` script to package.json (or Makefile)
- Run in GitHub Actions before deploy step

**Coverage target:** 80%+ for scraper core logic; 100% for validation/merge logic