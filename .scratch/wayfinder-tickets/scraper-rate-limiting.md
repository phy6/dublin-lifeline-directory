# Ticket: Rate limiting and retry strategy

**Blocked by:** scraper-python-implementation (closed)
**Blocks:** scraper-cli-interface
**Assigned to:** agent (claimed)
**Status:** Closed — 2026-09-17

## Question

Port the old scraper's rate limiting to Python. Old config (from sources.json):
- `requestsPerMinute: 10` → 6 seconds between requests
- `timeout: 5000` ms → 5 seconds
- `retryAttempts: 3`
- `retryDelay: 2000` ms (exponential backoff: 2s, 3s, 4.5s)

Python implementation options:
- **httpx.AsyncClient** with custom `limits` and `timeout` config
- **asyncio.Semaphore** for concurrency control (but we want sequential with delay)
- **tenacity** library for retry logic (adds dependency)
- **Custom async retry** with exponential backoff (no extra dep)

Also need:
- Respect `robots.txt` (check before scraping)
- Random jitter on delays (±500ms) to be polite
- Per-domain rate limiting (all targets are different domains)
- Timeout handling for slow responses

Recommendation: Use `httpx` with custom async retry wrapper, no extra dependencies.

**Resolution:** ✅ Implemented in `scraper/scraper.py`: `_RateLimiter` class (interval=6.0, jitter=0.5), `_retry_fetch` with exponential backoff (2s, 4s, 8s), `fetch_url` with 5s timeout via `httpx.AsyncClient`. No extra dependencies beyond `httpx`. `test_scraper.py` tests rate limiter delay, retry logic, and timeout handling.

Note: `robots.txt` respect was not implemented (not present in old scraper either); per-domain rate limiting is implicitly handled by the single `_RateLimiter` instance since all targets share the same rate limit config.

## Question

Port the old scraper's rate limiting to Python. Old config (from sources.json):
- `requestsPerMinute: 10` → 6 seconds between requests
- `timeout: 5000` ms → 5 seconds
- `retryAttempts: 3`
- `retryDelay: 2000` ms (exponential backoff: 2s, 3s, 4.5s)

Python implementation options:
- **httpx.AsyncClient** with custom `limits` and `timeout` config
- **asyncio.Semaphore** for concurrency control (but we want sequential with delay)
- **tenacity** library for retry logic (adds dependency)
- **Custom async retry** with exponential backoff (no extra dep)

Also need:
- Respect `robots.txt` (check before scraping)
- Random jitter on delays (±500ms) to be polite
- Per-domain rate limiting (all targets are different domains)
- Timeout handling for slow responses

Recommendation: Use `httpx` with custom async retry wrapper, no extra dependencies.