# Offline-First Architecture Research Report
## Dublin City Support Services — Wayfinder Map

**Date:** 2026-09-14  
**Author:** Research Agent  
**Status:** Recommendation — SQLite + Sync Queue with Delta Sync

---

## 1. Executive Summary

This report evaluates three offline-first mobile architectures for the Dublin City Support Services app, which serves people experiencing homelessness. The app must function reliably without internet, cache service data from primarycaresafetynet.ie, support large text and low-data mode, and work on both iOS and Android.

**Recommendation:** A **SQLite-based offline-first architecture** with a queued sync engine, delta sync, and timestamp-based data freshness validation. For a Flutter cross-platform implementation, this means `sqflite` or `drift` (SQLite ORM) as the local persistence layer, paired with a custom sync queue and WorkManager/BGTasks for background synchronization.

---

## 2. Project Context

The app's core data consists of service locations (Day Support Centres, GP Clinics, Mobile Health Units) with attributes like address, hours, contact info, and service categories. Data originates from a scraper pulling from primarycaresafetynet.ie. Key constraints:

- **Users:** People experiencing homelessness — likely on low-end devices, with limited/unreliable data plans
- **Data profile:** Relatively small (hundreds of locations), mostly read-heavy, infrequent updates (scraper runs periodically)
- **Accessibility:** First-class requirement — offline-compatible large text, low-data mode
- **Platforms:** iOS and Android (cross-platform Flutter is the likely implementation)
- **Data flow:** Scraper → server → app cache (additive updates, never remove without confirmation)

---

## 3. Offline-First Architectures Evaluated

### 3.1 Architecture A: SQLite + Sync Queue (Recommended)

**Stack:** SQLite (via `sqflite` or `drift` for Flutter) + custom sync queue + WorkManager/BGTasks

**How it works:**
- Local SQLite database is the **source of truth** for all reads
- Writes go to SQLite first, then a sync queue persists pending operations
- When connectivity is detected, a background worker processes the queue
- Delta sync: only changed records since last sync are transferred
- Conflict resolution via last-write-wins with timestamp metadata

**Strengths:**
- **Mature and battle-tested:** SQLite is the most widely used embedded database in mobile (Android ships with it, iOS uses it via FMDB or GRDB)
- **ACID compliance:** Transactions guarantee data integrity even if the app crashes mid-write
- **Complex queries:** SQL enables filtering, sorting, and joining service categories, locations, and hours efficiently
- **Small footprint:** SQLite databases are compact — ideal for low-end devices
- **Flutter ecosystem:** `sqflite`, `drift`, `floor`, and `sqlite_async` all provide strong Flutter support
- **No vendor lock-in:** Self-contained, no cloud service dependency
- **Encryption:** SQLCipher provides AES-256 encryption for local data
- **Proven in similar domains:** Health services, field work apps, and community services apps all use this pattern

**Weaknesses:**
- Requires building custom sync logic (though patterns are well-documented)
- Schema migrations need manual management
- More initial development effort than an all-in-one solution

**Trade-off assessment:** The custom sync engine is the main cost, but the scraper-based data model (periodic, additive updates) makes sync relatively simple compared to multi-user collaborative scenarios. The investment pays off in reliability and long-term maintainability.

---

### 3.2 Architecture B: Hive (NoSQL Key-Value)

**Stack:** Hive (Dart-native NoSQL) + custom sync layer

**How it works:**
- Hive stores data as key-value "boxes" in a binary format
- All data is deserialized into memory on open — extremely fast reads
- Type-safe via code-generated adapters
- Sync handled by custom logic pushing/pulling serialized records

**Strengths:**
- **Fastest read performance** among Flutter-local options (10x faster than SQLite for simple operations)
- **Zero configuration:** No schemas, no migrations, pure Dart
- **Smallest storage footprint** for structured data
- **Reactive:** Built-in listeners for reactive UI updates
- **Flutter-first:** Written in Dart, no native bridge overhead
- **AES encryption** available via separate package

**Weaknesses:**
- **No relational queries:** Cannot JOIN or do complex filtering across service types and locations
- **Schema rigidity:** Changing data structures requires manual migration scripts
- **Memory-bound:** All data loads into memory on box open — problematic if dataset grows significantly
- **No built-in sync:** Must build everything from scratch
- **Limited query patterns:** Good for exact-key lookups, poor for "find all clinics within 5km" or "filter by service category AND hours"
- **Community concerns:** The `Hive` package has had maintenance issues, with the author pivoting to `Isar` as a successor

**Trade-off assessment:** Hive's speed advantage is compelling, but the lack of relational querying is a significant drawback for a service directory app that needs to filter, sort, and combine categories. As the dataset grows (new locations added by scraper), the all-in-memory model becomes a liability.

---

### 3.3 Architecture C: Couchbase Lite + Sync Gateway

**Stack:** Couchbase Lite (embedded NoSQL) + Couchbase Sync Gateway + Capella (cloud)

**How it works:**
- Couchbase Lite is an embedded NoSQL database with built-in peer-to-peer sync
- Sync Gateway handles bidirectional replication between devices and cloud
- Change-based sync replicates only document changes
- Built-in conflict resolution with multiple strategies (last-write-wins, custom)
- Supports channels and access control for data partitioning

**Strengths:**
- **Built-in sync:** No custom sync engine needed — the hardest problem is solved
- **Bi-directional replication:** Automatic conflict resolution
- **Delta sync:** Only changed documents are transmitted
- **Mature platform:** Used in enterprise field-service and healthcare apps
- **Offline-first by design:** First-class offline support with automatic re-sync
- **Peer-to-peer:** Devices can sync directly without going through the cloud
- **Channels/access control:** Natural fit for partitioning service data by category or region

**Weaknesses:**
- **Heavy dependency:** Requires a Couchbase Sync Gateway server (or Capella cloud service)
- **Complex infrastructure:** Even for simple deployments, running Sync Gateway adds operational burden
- **Large binary size:** Couchbase Lite SDK is significantly larger than SQLite
- **Over-engineering:** The scraper-based data model is a one-directional push (server → app), not a multi-device collaboration scenario
- **Vendor dependency:** Tied to Couchbase ecosystem
- **Flutter support:** Less mature than SQLite options for Flutter
- **Cost:** Capella cloud service has pricing — self-hosting requires infrastructure management

**Trade-off assessment:** Couchbase Lite solves the sync problem elegantly but introduces significant infrastructure complexity that is disproportionate to the app's needs. The data model is simple (server pushes scraper data to app), making a lightweight sync queue more appropriate than a full replication system.

---

### 3.4 Comparison Matrix

| Criterion | SQLite + Sync Queue | Hive | Couchbase Lite |
|---|---|---|---|
| **Offline reliability** | Excellent | Excellent | Excellent |
| **Query flexibility** | Excellent (SQL) | Poor (key-value only) | Good (N1QL-like) |
| **Sync complexity** | Medium (build own) | High (build own) | Low (built-in) |
| **Storage footprint** | Small | Smallest | Largest |
| **Performance (reads)** | Good | Excellent | Good |
| **Flutter ecosystem** | Strong | Strong | Moderate |
| **Encryption** | Via SQLCipher | Built-in | Built-in |
| **Operational overhead** | Low | Low | High |
| **Scalability** | Excellent | Limited | Excellent |
| **Data integrity** | ACID | Eventual | ACID (within DB) |
| **Best fit for this app** | ✅ **Yes** | ❌ No | ❌ Overkill |

---

## 4. Recommended Architecture: SQLite + Sync Queue

### 4.1 Data Layer Design

```
┌─────────────────────────────────────────────┐
│                  App UI Layer                │
│  (Service list, map, detail, accessibility) │
├─────────────────────────────────────────────┤
│              Repository Layer                │
│  (Reads from local first, falls back to cache│
│   freshness checks, sync state management)   │
├─────────────────────────────────────────────┤
│           Local SQLite Database              │
│  ┌─────────────┐ ┌──────────┐ ┌──────────┐ │
│  │ locations   │ │categories│ │sync_queue│ │
│  │ (main data) │ │(metadata)│ │(pending) │ │
│  └─────────────┘ └──────────┘ └──────────┘ │
├─────────────────────────────────────────────┤
│         Sync Engine + Network Monitor        │
│  (WorkManager / BGTasks, connectivity      │
│   detection, retry with exponential backoff) │
├─────────────────────────────────────────────┤
│              Remote API Layer                │
│  (Scraper data endpoint, ETag/version check) │
└─────────────────────────────────────────────┘
```

### 4.2 Database Schema

**Locations table:**
- `id` (TEXT, primary key) — unique identifier from scraper
- `name` (TEXT) — service location name
- `category` (TEXT) — Food, Hygiene, Healthcare, Connectivity, Employment
- `address` (TEXT)
- `latitude` (REAL), `longitude` (REAL)
- `hours` (TEXT) — opening hours
- `phone` (TEXT)
- `website` (TEXT)
- `notes` (TEXT) — additional accessibility info
- `last_updated` (INTEGER) — Unix timestamp of last scraper update
- `is_active` (INTEGER) — additive updates only (never removed without confirmation)

**Sync metadata table:**
- `last_sync_timestamp` (INTEGER)
- `last_sync_etag` (TEXT) — for conditional requests
- `data_version` (INTEGER) — incrementing version counter
- `pending_sync_count` (INTEGER)

### 4.3 Why SQLite Wins for This Specific Use Case

1. **Scraper data is relational:** Locations have categories, hours, contact info — SQL queries like "find all food services open now within 5km" are natural
2. **Additive updates only:** The scraper never removes locations, so sync is simpler — just INSERT or UPDATE, no complex delete reconciliation
3. **Read-heavy:** Users browse locations far more than they create data — SQLite's read performance is more than adequate
4. **Low-end device friendly:** SQLite's storage footprint and memory usage are the lowest among the options
5. **No server infrastructure needed:** The scraper pushes to a server; the app just pulls. No sync gateway required
6. **Proven in similar domains:** The 6B health services research specifically notes that SQLite-based offline-first is the standard for community health and social services apps

---

## 5. Sync Strategy Recommendation

### 5.1 Approach: Pull-Based Delta Sync with Queued Writes

Given the data flow (scraper → server → app), the primary sync direction is **server → app** (pull). User-generated data is minimal or nonexistent.

**Sync model:**

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Server      │     │  Sync Engine │     │  Local DB    │
│  (Scraper)   │     │  (Scheduler) │     │  (SQLite)    │
│              │     │              │     │              │
│  Data + ETag │────▶│  1. Check    │────▶│  2. Compare  │
│              │     │     ETag     │     │     ETag     │
│              │     │  3. If       │────▶│  3. Apply    │
│              │     │     changed  │     │     delta    │
│              │     │  4. Update   │────▶│  4. Store    │
│              │     │     ETag     │     │     + meta   │
└──────────────┘     └──────────────┘     └──────────────┘
```

**Sync triggers:**
1. **App launch** — check if data is stale (last sync > 6 hours)
2. **Connectivity change** — when network becomes available after being offline
3. **Manual refresh** — user pulls-to-refresh
4. **Scheduled background sync** — WorkManager (Android) / BGProcessingTask (iOS), every 6 hours minimum

**Delta sync implementation:**
- Server responds with `ETag` header representing current data version
- App sends `If-None-Match` header with last known ETag
- If data unchanged (304 Not Modified): skip sync, save bandwidth
- If data changed (200 OK): receive only changed records, merge into local DB

**Conflict resolution:** Not a concern for this data model. The scraper is the sole writer; app users are read-only consumers. Last-write-wins is sufficient since the server is always authoritative.

**Offline queue:** If the app has any user-generated data (favorites, notes), these are queued locally with timestamps and synced when connectivity returns. Each queue entry has a status: `pending`, `synced`, `failed`.

**Retry strategy:** Exponential backoff (1min → 2min → 4min → 8min) with a maximum of 24 hours. Failed syncs are retried on next connectivity event.

### 5.2 Why Not Push-Based Sync

Push-based sync (like Couchbase's WebSocket replication) assumes bidirectional data flow. Since this app is primarily read-only for users, push sync adds unnecessary complexity. A simple pull-based delta sync is sufficient and more bandwidth-efficient.

---

## 6. Data Freshness Approach

### 6.1 Strategy: ETag + Timestamp Hybrid

**Primary mechanism — ETag validation:**
- Server includes an `ETag` header on all API responses, computed from the scraper's last run timestamp
- App stores the ETag alongside cached data
- On sync, app sends `If-None-Match` with stored ETag
- 304 response = data is fresh; 200 response = data has changed, fetch new data

**Secondary mechanism — Last-updated timestamps:**
- Each location record includes `last_updated` (Unix timestamp from scraper)
- App displays freshness indicator: "Last updated: 2 hours ago"
- If `last_updated` > 24 hours, show a "Data may be outdated" warning

**Freshness thresholds:**

| Age of data | Display behavior |
|---|---|
| < 1 hour | ✅ "Data is current" (green indicator) |
| 1–6 hours | ⚠️ "Updated X hours ago" (yellow indicator) |
| 6–24 hours | ⚠️ "Updated X hours ago — refresh when online" (amber indicator) |
| > 24 hours | ❌ "Data may be outdated" (red indicator, auto-sync attempted) |

**Why this matters for the user base:** People experiencing homelessness need reliable information about shelter hours, meal times, and clinic availability. Stale data could mean arriving at a closed facility. The freshness indicators ensure users can make informed decisions.

### 6.2 Staleness Detection for User-Generated Content

Any user-created content (favorites, notes) uses a separate `isSynced` boolean flag:
- `isSynced = false` → data exists only locally, not yet pushed to server
- `isSynced = true` → data confirmed on server

This prevents confusion between "I haven't synced my notes" and "the service data is outdated."

---

## 7. Accessibility Strategy

### 7.1 Offline-Compatible Large Text

The accessibility requirement is that large text must work **without internet**. This means text sizes, layouts, and content must be self-contained in the app bundle and local database — not fetched from a server on demand.

**Implementation approach:**

1. **Scalable Dimensional Units:** Use `sp` (scale-independent pixels) on Android and Dynamic Type on iOS. All text sizes must use platform-native scalable units, never fixed pixels.

2. **System Font Scaling Support:**
   - Android: Use `android:fontScale` compatible layouts; text must reflow without truncation at 200% scaling
   - iOS: Support Dynamic Type categories from `Body` to `Accessibility XXXL`; use `.font(.system(.body, design:.rounded))` with relative sizing

3. **Flexible Layouts:**
   - Scrollable containers for all text-heavy screens (service details, notes)
   - `wrap_content` / `flexible` height constraints — never fixed heights that clip text
   - Test at 200% system font scale to verify no content is lost

4. **Offline Content Guarantee:**
   - All service descriptions, hours, and notes are stored locally in SQLite — no text is fetched from network on demand
   - Large text variants of content are pre-rendered or stored as-is (the scraper provides the full text; no truncation for offline mode)

5. **Contrast Requirements:**
   - WCAG AA minimum: 4.5:1 for body text, 3:1 for large text
   - Must work in bright outdoor conditions (homeless services users often outdoors)
   - Dark mode and light mode support with verified contrast ratios in both

6. **Screen Reader Support:**
   - Semantic labels for all service cards (`accessibilityLabel` on iOS, `contentDescription` on Android)
   - Focus order follows logical reading order
   - Dynamic content changes (new service loaded, sync status) announced via accessibility events

### 7.2 Offline Accessibility Guarantees

| Feature | Online | Offline |
|---|---|---|
| Large text (system setting) | ✅ | ✅ (data is local) |
| Screen reader navigation | ✅ | ✅ (labels are local) |
| High contrast mode | ✅ | ✅ (theme is local) |
| Service search/filter | ✅ | ✅ (queries against local DB) |
| Map rendering | ✅ (online tiles) | ⚠️ (cached tiles only) |
| Service directions | ⚠️ (requires network) | ❌ (cached addresses only) |

**Key insight:** The offline accessibility gap is primarily **map tiles and directions**. The fix: cache map tiles for the Dublin area and provide text-only directions (street address + distance) as a fallback when offline.

---

## 8. Low-Data Mode Strategy

### 8.1 Platform-Native Low Data Mode Integration

Both iOS and Android have built-in **Low Data Mode** settings. The app should respect these:

- **iOS:** `NWPathMonitor` detects `constrained` or `expensive` network states
- **Android:** `ConnectivityManager` detects `NET_CAPABILITY_NOT_CONGESTED` and `NetworkCapabilities.TRANSPORT_CELLULAR` with `IS_NOT_ROAMING` checks

When low-data mode is active, the app should:

### 8.2 Data Reduction Strategies

**1. Text-Only Mode (Primary Strategy):**
- Disable map image loading; show text-only service list
- Replace thumbnails/icons with text labels
- Use lightweight vector icons (SVG/FontAwesome) instead of bitmap images
- This reduces data usage by ~80% compared to full map mode

**2. Progressive Data Loading:**
- **Tier 1 (always cached):** Service name, category, address, phone, hours — essential info stored in local SQLite
- **Tier 2 (conditional download):** Detailed descriptions, notes, accessibility features — only downloaded on Wi-Fi or when user explicitly requests
- **Tier 3 (never auto-download):** Map tiles, photos, large media — only on Wi-Fi or explicit user action

**3. Aggressive Caching:**
- Cache all API responses with `Cache-Control: max-age=21600` (6 hours)
- Use HTTP 304 Not Modified responses for ETag validation (saves full payload)
- Pre-cache the full service directory on first Wi-Fi connection
- Store cached data with no expiry for the core directory (stale-while-revalidate)

**4. Sync Optimization:**
- Delta sync only (already recommended in Section 5)
- Sync throttling: In low-data mode, delay background sync until Wi-Fi
- Batch all pending writes into a single request when connectivity returns
- Compress sync payloads (gzip)

**5. Data Usage Indicators:**
- Show data usage in settings: "This session used X MB"
- Warn before downloading large content: "This will use ~500KB of data"
- Default to low-data mode on cellular connections

### 8.3 Low-Data Mode Configuration

```
Low Data Mode Active:
  ├── Map: Text-only list (no tiles)
  ├── Images: Disabled
  ├── Sync: Wi-Fi only
  ├── Background refresh: Disabled
  ├── Tier 2/3 data: Not downloaded
  └── Cache: Aggressive (max age 24h)

Normal Mode:
  ├── Map: Standard tiles
  ├── Images: Enabled
  ├── Sync: On connectivity change + scheduled
  ├── Background refresh: Enabled (6h interval)
  ├── Tier 2/3 data: Downloaded on Wi-Fi
  └── Cache: Standard (max age 6h)
```

---

## 9. Implementation Recommendations

### 9.1 Technology Stack (Flutter)

| Layer | Technology | Rationale |
|---|---|---|
| Local Database | `drift` (SQLite ORM) or `sqflite` | `drift` provides compile-time SQL validation, type-safe queries, and better Dart integration than raw `sqflite` |
| State Management | Riverpod or Provider | Reactive state that observes local DB changes |
| Sync Scheduler | `workmanager` (Android) + `bg_tasks` (iOS) | Platform-native background processing |
| Network Monitoring | `connectivity_plus` | Detects connectivity changes to trigger sync |
| Encryption | `sqflite_sqlcipher` or `drift_sqlcipher` | AES-256 encryption for local database |
| HTTP Client | `dio` with interceptors | Interceptors for ETag handling, retry logic, compression |
| Accessibility | Platform-native | `MediaQuery` (Android), `Dynamic Type` (iOS) |
| Map | `flutter_map` + offline tile caching | OpenStreetMap tiles cached locally |

### 9.2 Migration Path

1. **Phase 1:** Build local SQLite database with all service data, offline-first reads
2. **Phase 2:** Implement sync engine with ETag validation and delta sync
3. **Phase 3:** Add accessibility features (large text, screen reader support)
4. **Phase 4:** Implement low-data mode with text-only map and sync throttling
5. **Phase 5:** Add map tile caching and offline directions

### 9.3 Testing Strategy

- **Offline simulation:** Use Android Emulator network throttling and iOS Network Link Conditioner
- **Sync testing:** Verify data integrity after extended offline periods (24h+), then reconnect
- **Accessibility testing:** Test with system font at 200%, screen readers (TalkBack/VoiceOver), high contrast mode
- **Low-data testing:** Verify data usage under 1MB for a full session with low-data mode active
- **Staleness testing:** Verify freshness indicators update correctly after sync

---

## 10. Risks and Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| SQLite migration complexity | Medium | Use `drift` for automated migration support; keep schema simple |
| Sync engine bugs | High | Thorough testing with offline/online cycling; exponential backoff prevents server overload |
| Data grows too large for low-end devices | Low | Service directory is small (hundreds of records); SQLite is compact |
| Scraper changes API format | Medium | Abstract API layer; versioned data model; migration scripts |
| Map tiles expire on device storage | Low | Cache management with LRU eviction; text-only fallback |

---

## 11. Conclusion

For the Dublin City Support Services app, **SQLite-based offline-first architecture** is the clear recommendation. It provides the right balance of reliability, query flexibility, low storage footprint, and Flutter ecosystem maturity. The scraper-based data model makes sync straightforward (pull-based delta sync), and the additive-only data policy eliminates complex conflict resolution.

The key differentiator from other architectures is that SQLite's relational model naturally fits the service directory data structure (locations, categories, hours), while the custom sync queue is simple to implement given the one-directional data flow. Hive lacks the query capabilities needed, and Couchbase Lite introduces infrastructure overhead that is unjustified for this use case.

Accessibility and low-data mode are not afterthoughts — they are architectural constraints that shape the data layer design. By storing all service text locally, the app guarantees offline accessibility. By implementing tiered data loading and platform-native low-data mode integration, the app respects users' limited data plans without sacrificing core functionality.
