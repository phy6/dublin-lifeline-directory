# Ticket: Local HTML archive fallback

**Blocked by:** scraper-python-implementation
**Blocks:** None

## Question

The old scraper checks `docs/` for saved HTML files when live fetch fails (e.g., `capuchin-day-centre.html`, `dublin_lifeline_capuchin-day-centre.html`, etc.). Should we keep this?

Options:
- **Keep**: Copy `docs/` from old project; scraper checks for local archives before using fallback data
- **Remove**: Rely only on live fetch + fallback data in config; simpler, no archive maintenance
- **Optional**: Support `SCRAPER_ARCHIVE_DIR` env var; if set and file exists, use it

The old `generate-scraped.js` also used this to regenerate scraped_output.json from archives without live fetching.

If kept, need to:
1. Copy `/home/martin/Dublin Services/docs/` to `scraper/docs/`
2. Port `findLocalArchive(id)` logic
3. Add `dataSource: 'local-archive'` to output