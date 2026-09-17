# Ticket: Version bumping strategy

**Blocked by:** scraper-output-locations (closed), scraper-hybrid-data-source (closed)
**Blocks:** None
**Assigned to:** agent (claimed)
**Status:** Closed — 2026-09-17

## Question

The `services.json` has a semver `version` field (currently `3.1.0`) and metadata tracking pipeline runs. Define when to bump each version component:

- **Patch (3.1.0 → 3.1.1)**: Only metadata changes — timestamps updated, `nextSync` recalculated, no service data changes
- **Minor (3.1.0 → 3.2.0)**: Additions or updates to existing services (new locations, changed hours, phone, coordinates, services list)
- **Major (3.1.0 → 4.0.0)**: Schema changes (field added/removed/renamed), or deletions of services

The pipeline (mergeData.js) already computes `differencesDetected`, `additions`, `updates`, `deletions`. Use these to decide:
- If `deletions > 0` → major
- Else if `additions > 0` or `updates > 0` → minor
- Else → patch

Also update `metadata.nextSync = pipelineRun + 7 days` (or configurable cadence).

**Resolution:** ✅ Fully implemented in `pipeline.py`: `bump_version()` implements all three semver rules using `compute_diff()` output. `nextSync` is set to `pipelineRun + 7 days` in `run_pipeline`. `test_pipeline.py` has 4 tests covering patch/minor/major bumps and the compute_diff tests cover additions/updates/deletions detection.

Note: The current `services.json` shows `version: 3.1.0` with `updates: 9` — this indicates the pipeline hasn't been re-run since the services changed (see `scraper-output-locations` ticket for details).

## Question

The `services.json` has a semver `version` field (currently `3.1.0`) and metadata tracking pipeline runs. Define when to bump each version component:

- **Patch (3.1.0 → 3.1.1)**: Only metadata changes — timestamps updated, `nextSync` recalculated, no service data changes
- **Minor (3.1.0 → 3.2.0)**: Additions or updates to existing services (new locations, changed hours, phone, coordinates, services list)
- **Major (3.1.0 → 4.0.0)**: Schema changes (field added/removed/renamed), or deletions of services

The pipeline (mergeData.js) already computes `differencesDetected`, `additions`, `updates`, `deletions`. Use these to decide:
- If `deletions > 0` → major
- Else if `additions > 0` or `updates > 0` → minor
- Else → patch

Also update `metadata.nextSync = pipelineRun + 7 days` (or configurable cadence).