# 02-offline-architecture: PWA offline strategy update

**Label:** `wayfinder:research`
**Type:** Research (AFK)
**Blocked by:** None (can start immediately)
**Supersedes:** 02-research-offline-architecture (SQLite research — superseded by PWA pivot)
**Assigned to:** phy6 (claimed)
**Status:** closed
**Resolution date:** 2026-09-14

**Resolution:** ✅ Complete. Full strategy document at `research/offline-strategy.md`. Key decisions: CacheFirst for app shell, StaleWhileRevalidate for JSON data, NetworkFirst for navigation pages, CacheOnly for offline fallback. Version-based freshness detection via `services.json` version field. Low-data mode uses CacheOnly + Network Information API auto-detection + user toggle. WCAG 2.2 AA compliance for offline page. P0 priority: precaching + offline fallback + JSON caching + freshness indicators.

---

**Question:** What is the offline strategy for a static PWA hosted on GitHub Pages? The app must work without internet, cache service data locally, and support large text and low-data mode. All data is static JSON served alongside the PWA.

**Acceptance criteria:**

- Service Worker caching strategy (Cache API, stale-while-revalidate, network-first vs cache-first)
- Static JSON data caching approach
- Offline fallback page design
- Data freshness strategy (how to know if cached data is stale without a backend)
- Low-data mode implementation (minimal service worker footprint, cached-only mode)
- Accessibility considerations for offline mode (large text, screen reader)
- Output: service worker architecture and caching strategy document
