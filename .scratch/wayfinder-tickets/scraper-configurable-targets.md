# Ticket: Configurable target list

**Blocked by:** None
**Blocks:** scraper-cli-interface, scraper-python-implementation
**Assigned to:** agent (claimed)
**Status:** Closed — 2026-09-17

## Question

How should the scraper's target list be configured and selected at runtime? The old `sources.json` has 14 targets with detailed selectors and fallbacks. The new scraper should support:
- Running all targets (default)
- Running a subset via CLI flag (e.g., `--targets capuchin-day-centre,merchants-quay-ireland`)
- Running only flyer targets (5 Day Support Centres + 5 GP Clinics + MHU)
- Dry-run mode that shows what would be scraped without fetching

The config should live in `scraper/config/sources.json` (mirroring old structure) and be loaded by the scraper.

**Boundary note:** This ticket defines the *config structure and runtime selection logic*. The `scraper-cli-interface` ticket defines the *CLI flag design and user-facing arguments*. Configurable-targets is the data model; CLI-interface is the interface to it.