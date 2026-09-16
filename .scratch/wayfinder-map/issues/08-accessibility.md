# 08: Implement accessibility features

**Label:** `wayfinder:task`
**Assigned to:** phy6 (claimed)
**Status:** closed
**Resolution date:** 2026-09-14

**Resolution:** ✅ Full implementation complete. All 5 acceptance criteria met:
- Offline mode: Service Worker (CacheFirst/StaleWhileRevalidate/NetworkFirst) + accessible offline fallback page with emergency contacts
- Large text mode: `TextScaleToggle.svelte` (100%–200%, localStorage persistence, `clamp()` typography)
- Low-data mode: `LowDataToggle.svelte` (auto-detect via Network Information API, manual toggle, signals SW via `postMessage`, compact JSON)
- Screen reader support: ARIA live regions (`#status-announcer`, `#status-assertive`), skip links, semantic HTML, 44×44px touch targets
- Intuitive navigation: Emergency FAB, persistent bottom nav, high contrast, reduced motion, coach marks ready

Testing: 19 unit/integration tests + 6 E2E tests passing. GitHub Actions CI. See `research/accessibility-implementation-plan.md`.
**Blocked by:** 05-define-data-model (closed), 04-research-accessibility (closed)
**Resolution date:** 2026-09-14 — Research complete. Detailed implementation plan created at `.scratch/wayfinder-map/research/accessibility-implementation-plan.md`. Plan covers all 5 acceptance criteria with specific SvelteKit code patterns, CSS approaches, service worker configurations, and integration with the existing offline strategy and PWA framework. Ready for agent to begin implementation in Phase 1 (P0: critical MVP items).

**Question:** Implement the accessibility features: offline mode, large text, low-data mode, screen reader support, and intuitive navigation for users with limited tech experience.

**Acceptance criteria:**

- Offline mode with cached data display
- Large text mode (configurable font sizes)
- Low-data mode (minimal network usage, cached-first)
- Screen reader support
- Intuitive navigation (minimal gestures, clear labels)
- Output: accessible mobile app interface

**Research outputs:**

- Implementation plan: `.scratch/wayfinder-map/research/accessibility-implementation-plan.md`
- Accessibility spec: `.scratch/wayfinder-map/research/accessibility-spec.md`
- Offline strategy: `.scratch/wayfinder-map/research/offline-strategy.md`
- PWA framework recommendation: `.scratch/wayfinder-map/research/pwa-framework-recommendation.md`

**Key decisions made during research:**

- Continue with SvelteKit (no framework switch needed — `@vite-pwa/sveltekit` provides built-in accessibility features like route announcements and focus management)
- Expand existing `vite.config.ts` `runtimeCaching` to include services.json (StaleWhileRevalidate) and navigation (NetworkFirst)
- Create compact JSON (`services-compact.json`) for low-data mode
- Use `localStorage` for accessibility preference persistence (text scale, low-data mode, high contrast)
- Create accessible offline fallback page with emergency contacts

**Implementation priority:**

- Phase 1 (P0 — Critical): Service worker caching, offline page, screen reader semantics, tab bar, emergency button
- Phase 2 (P1 — High): Text scale toggle, low-data mode, high contrast, network detection
- Phase 3 (P2 — Medium): Map marker accessibility, data update broadcasts, coach marks
- Phase 4 (P3 — Low): Voice search, haptic feedback, data budget controls
