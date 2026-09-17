# 07: Prototype UI for service finder

**Label:** `wayfinder:prototype`
**Assigned to:** phy6 (claimed)
**Status:** awaiting-human-review

**Next step:** Open `research/prototype-ui.html` in browser to review. See ticket description for feedback checklist.
**Resolution date:** 2026-09-14
**Prototype:** [prototype-ui.html](prototype-ui.html)

**Question:** Build a throwaway prototype showing how the service finder UI works — searching, filtering by category, viewing hours, and displaying locations on a map. Test with real flyer data.

**Acceptance criteria:**

- Working UI prototype with search and filter
- Service list view with locations, categories, hours
- Map view showing all locations
- Day-based filtering (what's open now)
- Large text and accessibility preview
- Output: shareable prototype artifact (HTML or app screen)

**What was built:**

Single-file HTML prototype at `research/prototype-ui.html` containing:

- Searchable/filterable service list (5 day support centres from flyer-data.json)
- Leaflet map with color-coded markers (green = open now, red = closed)
- Day-based filtering via day-of-week buttons (highlights what's open now)
- Detail panel with full hours table, services list, categories, and special notes
- Accessibility panel: text size slider (100%–200%), high contrast mode, reduced motion
- WCAG 2.2 AA: skip links, ARIA live regions, keyboard navigation, 44×44px touch targets, relative units

**Human feedback needed:**

- Review the visual layout and information architecture
- Confirm category tags and hour display format are clear
- Verify map markers and "open now" indicators are intuitive
- Check that the accessibility controls work as expected
- Provide any UX improvements before proceeding to implementation
