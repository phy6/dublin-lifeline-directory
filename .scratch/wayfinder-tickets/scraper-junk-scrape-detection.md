# Ticket: Junk scrape detection (false "live" / scrapeSuccess)

**Blocked by:** scraper-scrape-failure-handling (closed), scraper-data-validation (closed)
**Blocks:** None
**Assigned to:** unassigned
**Status:** Open
**Label:** needs-triage

## Question

The pipeline marks a scrape `dataSource: "live", scrapeSuccess: true` whenever the HTTP fetch succeeds — even when the extracted fields are site chrome, not listing data. Current `services.json` (3.3.0) contains entries with `website: "HOME"`, `"Campaigns"`, `"Donate now"`, `"View Report >"`, `description: null`, and `latitude/longitude: 0`, all marked live/success. This is the same failure mode the discovery follow-up already called out once ("selectors match site chrome, not listings").

How should the pipeline distinguish a genuinely successful scrape from a fetch that succeeded but extracted junk?

Options:
1. **Field-sanity gate**: after extraction, validate fields (e.g. `website` must look like a URL/domain, `address` non-null, at least one of `phone`/`address`/`description` present); failures downgrade `source` to `"fallback"`/`"none"` so existing `scrapeSuccess`/`dataSource` tracking handles it.
2. **Confidence score**: `extract_field()` returns (value, confidence); low-confidence results mark `needsReview: true` but keep data.
3. **Diff-based detection**: if a run's extracted values differ wildly from the previous run (e.g. address disappears, website changes to a single word), quarantine the new values and keep the old ones pending review.
4. **Per-target required fields**: extend `sources.json` targets with `required: ["address", "phone"]`; missing required fields after a live fetch count as failure.

Also consider: option 1 changes `scrapeSuccess` semantics for currently-"live" entries, which will surface as version-bump diffs (see scraper-version-bump-semantics). The validator (`scraper/validate.py`) already flags these shapes as errors — 34 pre-existing errors on 3.3.0 output — so the detection rules should align with validation rules rather than inventing a second definition of "good data".

## Acceptance criteria

- [ ] Detection rule implemented in `scraper/` (pipeline or scraper module, not a one-off script)
- [ ] Junk-shaped live results no longer recorded as `dataSource: "live", scrapeSuccess: true`
- [ ] Rules consistent with `scraper/validate.py` error definitions
- [ ] Tests covering: chrome-text website, null address with 0-coordinates, empty services
- [ ] Full suite green (`python3 -m pytest scraper/tests/ -q`)
