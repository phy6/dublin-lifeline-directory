# 02: Add live region for filter results

**What to build:** A polite live region that announces filter/search result count changes to screen readers on the Home and Search pages.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Add `<div role="status" aria-live="polite" id="results-announcer" class="sr-only">` to `src/routes/+page.svelte` and `src/routes/search/+page.svelte`
- [ ] Update announcer text when `filtered.length` changes (via reactive statement or effect)
- [ ] Announcement should say: `"{count} services found"` or `"{count} services found open on {day}"`
- [ ] Ensure existing stats text remains visible for sighted users
- [ ] Test with screen reader: filter by category, day, and search — each change should announce
