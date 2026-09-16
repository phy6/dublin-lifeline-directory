# Ticket: Output locations

**Blocked by:** scraper-hybrid-data-source
**Blocks:** scraper-version-bumping, scraper-github-actions

## Question

The pipeline must write the final `services.json` to TWO locations:

1. **`src/lib/data/services.json`** — imported by SvelteKit server routes (`+page.server.ts`) at build time
2. **`static/services.json`** — served by GitHub Pages for client-side fetch (service worker caching)

Both files must be identical. The pipeline should:
- Write to `src/lib/data/services.json` first
- Copy to `static/services.json` (or write both in one step)
- Ensure the `metadata` block includes: `version`, `lastUpdated`, `generatedBy`, `nextSync`, `pipelineRun`, `differencesDetected`, `additions`, `updates`, `deletions`

The version should be incremented semantically:
- Patch: only metadata changes (timestamps, nextSync)
- Minor: additions or updates to services
- Major: schema changes or deletions