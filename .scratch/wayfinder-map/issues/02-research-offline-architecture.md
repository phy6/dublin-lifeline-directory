# 02: Research offline-first mobile architecture

**Label:** `wayfinder:research`
**Type:** Research (AFK)
**Blocked by:** None (can start immediately)

**Question:** What offline-first architecture works best for a mobile app serving people experiencing homelessness? The app must work without reliable internet, support large text and low-data mode, and cache service data locally.

**Acceptance criteria:**

- Evaluation of offline-first mobile architectures (local SQLite, Realm, Hive, etc.)
- Strategy for syncing flyer data updates from scraper to local cache
- Approach for handling data freshness (how to know if cached data is stale)
- Accessibility implementation strategy (offline-compatible large text, low-data)
- Output: architecture recommendation with trade-offs

---

**Resolution:** ✅ Complete. Recommended architecture: SQLite + Sync Queue with Delta Sync. Flutter with sqflite/drift. ETag-based pull sync. Report at `research/offline-architecture.md`.

**Resolution date:** 2026-09-14

---

**Status:** closed
