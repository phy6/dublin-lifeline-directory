# Ticket: Merge Charities Register candidates into pipeline

**Blocked by:** scraper-provider-discovery (closed)
**Blocks:** None
**Assigned to:** agent
**Status:** Closed — 2026-09-17 (proposal-list generator implemented; promotion via separate bot-comms project)
**Label:** ready-for-agent

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

- [x] Chosen option implemented and documented (in this ticket's Resolution section)
- [x] Samaritans / Crosscare mismatch cases handled by the chosen approach (alias list, RCN anchoring, or documented wontfix)
- [x] No pipeline behavior change unless a human explicitly promotes a candidate
- [x] Tests for the new logic; full suite green (`python3 -m pytest scraper/tests/ -q`)

## Resolution

✅ Proposal-list option implemented. `scraper/register_proposals.py` (`--candidates` or `--xlsx`) diffs register candidates against `sources.json` targets and emits `register_proposals.json` with four sections: `matched` (exact, incl. AKA + RCN), `near_matches` (token-containment or difflib ≥ 0.8, shaped as yes/no confirm questions), `new_orgs`, `unmatched_targets`. Matching normalizes case/punctuation/legal-form words (Limited, CLG, Trust, ...).

Live run on the 998 candidates: **9 matched, 4 to confirm, 985 new, 3 targets missing**. Notably it surfaced Crosscare's real registered name — 'St. Laurence O'Toole Catholic Social Care CLG' — as a confirm item, resolving that open question pending a yes. Samaritans is confirmed out of the cut (non-Dublin registered address); `simon-community-employment` and `inner-city-helping-homeless` are also missing from the cut (likely trade names without separate registration). Near-matches deliberately over-trigger ('Cps Trust Ireland' vs COPE, 'Doras Buí...' vs ALONE) — they're questions, not merges.

Promotion stays manual per the plan: `summarize()` prints a sub-1000-char chat-ready summary (counts + numbered yes/no questions) for confirmation via the separate bot-comms project. Nothing in the pipeline changes until a human adds a target to `sources.json`. 5 tests in `test_proposals.py`; 95 passing overall.
