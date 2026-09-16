# Ticket: Test strategy

**Blocked by:** scraper-python-implementation, scraper-data-validation
**Blocks:** None

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