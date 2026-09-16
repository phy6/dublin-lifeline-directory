# 07: Fix FilterBar accessibility

**What to build:** Search input with proper label, filter buttons with `aria-controls` linking to results, and proper focus management.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Search input (`src/lib/components/FilterBar.svelte:23-28`): Add `<label for="search-input">Search services</label>` visually hidden; `id="search-input"` on input
- [ ] Category filter buttons: Add `aria-controls="service-list"` pointing to ServiceList container
- [ ] Day filter buttons: Add `aria-controls="service-list"`
- [ ] Ensure `ServiceList` has `id="service-list"`
- [ ] Test: Screen reader announces filter changes via live region (ticket 02)
