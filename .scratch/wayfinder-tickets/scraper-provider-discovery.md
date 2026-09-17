# Ticket: Provider discovery feature

**Blocked by:** scraper-python-implementation
**Blocks:** None
**Status:** Implemented — code + tests done, live sources need refresh

> **Reopened per user request to "rethink scraping":** ported discovery from old `scraper.js` to Python. `discovery` section added to `scraper/config/sources.json` (7 URLs + selectors from old config), `DublinLifelineScraper.discover_providers()` in `scraper/scraper.py`, `--discover` CLI in `scraper/main.py`, 4 tests in `scraper/tests/test_discovery.py` (69 total passing).

## Question

The old scraper has a "discovery" feature that crawls directory sites (Dublin City Council, Charity Navigator, etc.) to find new provider URLs. Config in sources.json includes:
- 7 discovery URLs
- Selectors for name, url, description, phone, category, address
- 60 second interval between discovery requests
- Max 50 results

Should we port this?
- **Yes**: Keeps the scraper extensible; can discover new services automatically
- **No**: Out of scope for MVP; current 14 targets are sufficient; discovery adds complexity and maintenance
- **Defer**: Build core scraper first; add discovery in a follow-up ticket

Recommendation: **Defer**. The current target list is stable. Discovery can be added later if needed.

## Follow-up (live run 2026-09-17)

- `python -m pytest scraper/tests/ -q`: 69 passed (65 existing + 4 new discovery tests, mocked — no network).
- Live discovery full run (sleep mocked for speed): 5/7 URLs fail (dublincity.ie 404, `chaarities.ie`/siara/dublincare/corkcitycommunity DNS dead). charitynavigator + alone.ie fetch OK but selectors match site chrome, not listings — 3 junk results (2x "Nonprofit Resources" nav links, 1x referral-form button text). Effectively 0 usable providers.
- (Earlier "0 providers" reading was a timeout artifact: real 60s sleeps between URLs killed the run early.)
- Fixes applied: `follow_redirects=True` on httpx clients, multi-selector matching, link-is-element handling (`h2 a` returns `<a>`), mailto/tel/# filtering, `urljoin` for relative URLs, slugify via regex, `getattr(args,"discover",False)` for backward-compat mocks.
- Remaining: refresh `discovery.urls` with live directory sources before `--discover` is useful in production.

## Live sources wired (2026-09-17, per user pointers)

- **Focus Ireland useful-organisations** (`focusireland.ie/get-help/useful-organisations/`): 200, static HTML. All 35 external org links live in `.two-col-content__row li a` (verified against live DOM). `discover_providers()` now returns **35 providers with categories** (20 advice/homelessness, 7 legal, 3 state services, 5 gov departments) — Threshold, SVP, Simon, Crosscare, PMVT, MABS, Women's Aid, DRHE, etc.
- **Charities Regulator**: HTML pages behind Cloudflare 403, but the published **register XLSX downloads directly** (38MB, verified 200). New `scraper/fetch_register.py` downloads/parses/filters it: 14,469 rows → 11,475 Registered → 3,152 Dublin → **998 candidates** (homeless classification / poverty / community-welfare purpose). Overlap check: 12/14 existing targets match a candidate by name (missing: Samaritans — national org, non-Dublin address; Crosscare — different registered legal name). Run: `python3 scraper/fetch_register.py --download`.
- Config changes: `discovery.urls` replaced (5 dead + 2 junk-yielding URLs dropped, reasons above); entries support `{url, name_selectors?, capture_category?}` dicts, plain strings still work. `register_xlsx` URL stored in config. Same-domain links excluded (a directory no longer "discovers" itself).
- 80 tests passing (69 + 11 new: discovery dict-entry/category/self-link-exclusion, register filter + end-to-end on generated workbook).