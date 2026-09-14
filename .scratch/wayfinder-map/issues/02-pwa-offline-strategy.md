# 02-offline-architecture: PWA offline strategy update

**Label:** `wayfinder:research`
**Type:** Research (AFK)
**Blocked by:** None (can start immediately)
**Supersedes:** 02-research-offline-architecture (SQLite research — superseded by PWA pivot)

**Question:** What is the offline strategy for a static PWA hosted on GitHub Pages? The app must work without internet, cache service data locally, and support large text and low-data mode. All data is static JSON served alongside the PWA.

**Acceptance criteria:**

- Service Worker caching strategy (Cache API, stale-while-revalidate, network-first vs cache-first)
- Static JSON data caching approach
- Offline fallback page design
- Data freshness strategy (how to know if cached data is stale without a backend)
- Low-data mode implementation (minimal service worker footprint, cached-only mode)
- Accessibility considerations for offline mode (large text, screen reader)
- Output: service worker architecture and caching strategy document
