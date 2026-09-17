# Ticket: Output locations

**Blocked by:** scraper-hybrid-data-source (closed)
**Blocks:** scraper-version-bumping, scraper-github-actions
**Assigned to:** agent (claimed)
**Status:** Closed — 2026-09-17 (implementation verified, bugs found)

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

**Resolution:** ✅ Implementation exists in `pipeline.py`: `write_services()` writes to both paths with identical data, metadata includes all required fields, `bump_version()` implements semver logic. **BUT bugs found in the actual output:**

1. **Files are NOT identical** — `static/services.json` is stale; it's missing tags (`water`, `meal`, `GP`, `caring`) that exist in `src/lib/data/services.json`. The `static/services.json` was not regenerated in the last pipeline run.
2. **Version not bumped** — `src/lib/data/services.json` shows `version: 3.1.0` with `metadata.updates: 9`, but should be `3.2.0` per the semver rules (updates > 0 → minor bump). The pipeline was apparently not run after the services changed, or `bump_version` wasn't called in a prior run.

**Action needed:** Re-run the pipeline to regenerate both output files identically, or manually sync `static/services.json` from `src/lib/data/services.json`.

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