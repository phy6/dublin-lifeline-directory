# Ticket: Merge Charities Register candidates into pipeline

**Blocked by:** scraper-provider-discovery (closed)
**Blocks:** None
**Assigned to:** unassigned
**Status:** Open
**Label:** needs-triage

## Question

`scraper/fetch_register.py` downloads the Charities Regulator XLSX and filters it to 998 Dublin candidates (`register_candidates.json`), but the output stops there — nothing consumes it. The pipeline still scrapes only the 14 fixed targets in `sources.json`, and the 12/14 overlap check was a manual one-off (Samaritans has a non-Dublin registered address; Crosscare is registered under a different legal name, both unresolved).

How should register candidates flow into the directory?

Options:
1. **Discovery input**: feed candidate names/websites into the discovery flow as seed URLs for `--discover` runs, with human review before any target is added to `sources.json`.
2. **New-target proposals**: a script that diffs candidates against existing target names/RCNs and emits a review list (new orgs, name mismatches like Crosscare, address mismatches like Samaritans); a human promotes entries to `sources.json` targets.
3. **RCN-anchored merge**: store each target's RCN in `sources.json`; on each register refresh, flag targets whose status/address/name drifted (deregistered, moved out of Dublin, renamed).
4. **Do nothing automated**: keep `fetch_register.py` as a manual research tool (current state); document the review workflow instead of building merge logic.

Also consider: 998 candidates is a review pool, not pipeline input — blindly scraping all of them would swamp the 14-location directory and break the version-bump semantics (see scraper-version-bump-semantics). Any automated path needs the junk-scrape gate (see scraper-junk-scrape-detection) first, or every new target risks landing as chrome-text junk marked live. The register XLSX URL (`/media/5rrnldzg/...`) may rot; the HTML pages are Cloudflare-walled, so there is no fallback source if the direct download breaks.

## Acceptance criteria

- [ ] Chosen option implemented and documented (in this ticket's Resolution section)
- [ ] Samaritans / Crosscare mismatch cases handled by the chosen approach (alias list, RCN anchoring, or documented wontfix)
- [ ] No pipeline behavior change unless a human explicitly promotes a candidate
- [ ] Tests for the new logic; full suite green (`python3 -m pytest scraper/tests/ -q`)
