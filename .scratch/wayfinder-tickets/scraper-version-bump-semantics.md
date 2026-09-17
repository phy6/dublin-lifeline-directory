# Ticket: Version-bump semantics for tag/churn-only runs

**Blocked by:** scraper-version-bumping (closed), scraper-output-locations (closed)
**Blocks:** None
**Assigned to:** agent
**Status:** Closed — 2026-09-17 (behavior documented in `bump_version()` docstring + characterization test; no logic change)
**Label:** ready-for-agent

## Question

Commit `38220b2` bumped `services.json` 3.2.0 → 3.3.0 on what is effectively churn: populated `tags`, new `dynamicActivities`/`activityMatchCount` fields (empty for 12/14 locations), key reordering, and fresh timestamps — 14 "updates", 0 additions, 0 removals. The map cites "`bump_version()` implements semver rules", but a minor bump with no new-service evidence stretches that claim: consumers reading the version cannot tell "new services added" from "timestamps refreshed".

What should trigger each bump level?

Options:
1. **Document current behavior**: minor bump on any field-level updates, patch on timestamp-only runs, major on additions/removals or schema changes — and write that table down so the version is honest.
2. **Quieten churn**: timestamp-only runs (no field changes) don't bump at all; field churn without additions/removals bumps patch; minor/major reserved for content/schema changes.
3. **Split the signal**: keep semver for schema/content, add a separate `pipelineRun` counter or `dataRevision` for run-level churn, so consumers can subscribe to the signal they care about.
4. **Freeze versions on junk**: if the junk-scrape gate (see scraper-junk-scrape-detection) quarantines a run's changes, skip the bump so bad data never mints a new version.

Also consider: whatever rule is chosen must be expressible in `compute_diff()` output (currently `differencesDetected`/`additions`/`updates`) — if the diff can't distinguish "tag added" from "address changed", the bump logic can't either. Field-level diff granularity may be a prerequisite.

## Acceptance criteria

- [x] Bump rules documented (in this ticket's Resolution section and/or `bump_version()` docstring)
- [x] `bump_version()` implements the documented rules from `compute_diff()` output
- [x] A churn-only re-run and a content-change run produce the documented (different) outcomes — covered by tests
- [x] Full suite green (`python3 -m pytest scraper/tests/ -q`)

## Resolution

✅ Document-current-behavior option. Rules written into the `bump_version()` docstring: deletions/schema-keyword → major; additions/any field updates → minor; empty diff → patch. Existing tests already locked all four branches; added `test_timestamp_only_churn_still_mints_minor_bump` locking the honest consequence: `merge_location()` refreshes `lastScraped`/`lastUpdated` every run, so `compute_diff()` always reports updates and a zero-content re-run still mints a minor bump (exactly how 3.2.0 → 3.3.0 happened). No logic change. Consumers should read the metadata `additions`/`updates`/`deletions` counts, not the version alone, for the real signal. If we ever want quiet timestamp-only runs, that's a `compute_diff()` field-granularity change — recorded here as the prerequisite, not done.
