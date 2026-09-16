# 03: Make map markers keyboard accessible

**What to build:** Leaflet markers on the Map page that can be focused and activated via keyboard (Enter/Space), with proper ARIA roles.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] In `src/routes/map/+page.svelte`, add `tabindex="0"` and `role="button"` to each marker
- [ ] Add keyboard event handler for `Enter` and `Space` to open popup
- [ ] Ensure popup content is accessible (focus moves to popup, Escape closes it)
- [ ] Add `aria-label` to each marker with service name
- [ ] Test: Tab through markers, press Enter to open popup, Escape to close
