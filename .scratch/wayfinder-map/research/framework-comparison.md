# Framework Comparison: Flutter, React Native, and Kotlin Multiplatform

**Project:** Dublin City Support Services — Wayfinder Map
**Date:** September 2026
**Purpose:** Evaluate cross-platform mobile frameworks for building an iOS + Android app serving Dublin residents experiencing homelessness/hardship

---

## Executive Summary

**Recommendation: Flutter**

For this project — an offline-first, accessibility-critical service directory with map rendering targeting users with limited connectivity — **Flutter** is the recommended framework. It offers the strongest combination of mature offline storage options (Hive, sqflite), a well-established map ecosystem (google_maps_flutter, mapbox_maps_flutter), robust built-in accessibility support (Semantics framework, ScreenReaderOptimizer package, Android 14 nonlinear text scaling), and the fastest development cycle for a small team. React Native is a close second if the team already has JavaScript/TypeScript expertise. Kotlin Multiplatform is compelling for performance and native UX but is a higher-risk choice for this specific project due to its younger ecosystem and the accessibility challenges inherent in Compose Multiplatform on iOS.

---

## 1. Offline Storage Capabilities

### Flutter

Flutter offers three well-established offline storage options:

| Solution | Type | Best For | Encryption | Maturity |
|---|---|---|---|---|
| `hive_ce` | NoSQL key-value | Object caching, offline lists | Built-in AES-256 | High (use community fork) |
| `sqflite` | Relational SQL | Complex queries, structured data | Via SQLCipher | High |
| `shared_preferences` | Key-value | Settings, flags | No | High |

For the Wayfinder app, **Hive (hive_ce)** is the best fit for caching service directory data — it is extremely fast, pure Dart (no native bridge overhead), supports custom objects via TypeAdapters, and works offline with built-in encryption for sensitive data. For relational queries (e.g., filtering services by category and district), **sqflite** is available. The 2026 maintenance warning for the original `hive` package means the project should use `hive_ce` (Community Edition), which is actively maintained.

**Offline-first architecture:** Flutter's local-first design means the app is fully functional without internet. Caching strategies are well-documented. The `workmanager` package supports background sync when connectivity returns.

### React Native

React Native's offline storage ecosystem is mature but fragmented:

| Solution | Type | Best For | Encryption | Maturity |
|---|---|---|---|---|
| `WatermelonDB` | Reactive SQL | Large offline lists, sync | SQLCipher | High (but maintenance concerns) |
| `MMKV` | Key-value | Fast state, session | Built-in | High |
| `AsyncStorage` | Key-value | Legacy compat | Community fork | Declining |
| `Realm` | Object DB | Cross-device sync | Yes | Medium (MongoDB licensing concerns) |
| `expo-sqlite` | SQL | Simple structured data | SQLCipher | High |

**WatermelonDB** is the standout option for offline-first apps. It is built on SQLite, supports lazy loading, reactive queries, and has a first-class sync protocol (pull/push with conflict resolution). However, in 2026 there are significant concerns: WatermelonDB's last stable release was over a year old (0.28.0, April 2025), it requires community plugins for Expo SDK 54, has React 19 peer dependency issues, and needs native patches to work with the new architecture. **PowerSync** and **ElectricSQL** are emerging alternatives with better Expo SDK 54 support.

**Key risk:** WatermelonDB's maintenance uncertainty and the complexity of getting it running on Expo SDK 54 (the current standard) make React Native's offline storage story less straightforward than Flutter's.

### Kotlin Multiplatform

KMP offers two database options, both now fully multiplatform:

| Solution | Type | Best For | Maturity |
|---|---|---|---|
| `SQLDelight` | Schema-first SQL | Greenfield multiplatform | Very High (since 2018) |
| `Room Multiplatform` | Annotation-based | Migrating Android apps | High (stable 2025, Room 3.0 2026) |

**SQLDelight** is the most mature multiplatform database — it generates type-safe Kotlin code from `.sq` SQL files, compiles for Android, iOS, JVM, JS, and WASM, and has been production-proven since 2019. **Room Multiplatform** gained full KMP support with Room 2.7+ and Room 3.0 (March 2026), making Google's annotation-based approach available across platforms. Both use `BundledSQLiteDriver` for cross-platform consistency (~2-3 MB size increase).

Offline sync patterns are well-established: use `Flow`-based reactive queries to observe database changes, write a sync worker that pulls/pushes changes, and use `WorkManager` on Android and background tasks on iOS for scheduled sync. The sync logic lives entirely in `commonMain` — written once, tested once, shared across platforms.

**Advantage:** KMP's offline storage is the most architecturally elegant — shared database schema and sync logic in one place, with no platform-specific duplication.

---

## 2. Map Rendering Support

### Flutter

Flutter has two robust map options:

- **`google_maps_flutter`**: Official Google Maps plugin. Well-maintained, widely used. However, there is a known accessibility bug (GitHub issue #163392) where markers are not recognized by Android's "Select to Speak" accessibility tool on Google APIs emulator images. The Flutter team has classified it as a P2 accessibility issue. This is a **significant concern** for this project where accessibility is a first-class requirement.
- **`mapbox_maps_flutter`**: Official Mapbox SDK for Flutter. Supports all major map features (styles, annotations, user location, offline maps, GeoJSON layers). Mapbox offers more customization and better offline map capabilities. However, the Flutter Mapbox plugin is still in pre-release for some features (web support is in public preview as alpha).

**Mapbox is the recommended choice for Flutter** due to its superior offline map support and customization, though it requires a Mapbox access token and the offline map download feature is essential for this project.

### React Native

- **`react-native-maps`**: The dominant map library (15,945 GitHub stars, MIT license, actively maintained). Supports Google Maps on both platforms and Apple Maps on iOS natively. Requires a Google Maps API key for Google Maps usage.

**Critical accessibility issues:** There is an open bug (GitHub issue #3500, since 2020) where accessibility properties on `<Marker />` and `<Callout />` are ignored by screen readers on Android. The workaround is limited — only the `title` prop is announced. Additionally, issue #5743 reports map flickering when `importantForAccessibility` changes. The New Architecture (iOS with Google Maps provider) has a separate bug where markers fail to render (issue #5908).

**This is a major red flag.** For an app where screen reader accessibility is critical for users experiencing homelessness, React Native's map accessibility issues are a significant barrier.

### Kotlin Multiplatform

KMP's map ecosystem is growing but less mature:

- **`kmp-maps`** (Software Mansion): Universal map component for Compose Multiplatform. Supports Google Maps on Android and iOS, Apple Maps on iOS, and Google Maps JS on desktop. Features custom markers, GeoJSON layers, location services, and native gesture handling. Active development.
- **`kmp-maps-compose`** (yankeppey): Google Maps integration specifically for Compose Multiplatform, designed as a multiplatform replacement for `android-maps-compose`. Uses Google Maps iOS SDK via Swift Package Manager. Some features have platform-specific limitations (e.g., polyline patterns, terrain view on iOS falls back to normal).

**Limitation:** KMP map libraries are still maturing. Feature parity with native map SDKs is incomplete, and some advanced features (StreetView, clustering utilities, scale bars) are missing or platform-specific. The ecosystem has fewer community resources and tutorials than Flutter or React Native.

---

## 3. Accessibility Feature Support

### Flutter

Flutter has the strongest built-in accessibility story of the three frameworks:

- **Semantics framework**: Every widget automatically generates an accessibility tree. The `Semantics` widget allows custom labeling. Screen readers (TalkBack, VoiceOver) work out of the box.
- **`flutter_accessibility_helper`** package: Provides `ScreenReaderOptimizer`, focus management, accessibility testing tools, and native platform integration for detecting bold text, high contrast, invert colors, reduce motion, font scale, and screen reader detection on Android.
- **Android 14 nonlinear font scaling**: Supported since Flutter 3.14 (stable in 3.16). Text scaling up to 200% is handled correctly with `TextScaler`.
- **`MaterialApp` locale and `Localizations`**: Affect screen reader voices starting from Flutter 3.38.
- **Built-in large text support**: `MediaQuery.textScaleFactor` / `TextScaler` is a first-class concept in Flutter's rendering system.
- **Known gap**: The `google_maps_flutter` marker accessibility issue (mentioned above) affects the map specifically, but the rest of the app benefits from Flutter's comprehensive accessibility infrastructure.

### React Native

React Native has basic accessibility support but significant gaps:

- **`accessibilityLabel`, `accessibilityRole`, `accessible`** props are available on most components.
- **`importantForAccessibility`** prop exists but causes map flickering bugs (issue #5743).
- **The `react-native-maps` accessibility issues are a deal-breaker**: markers are not announced by screen readers on Android, and the workaround is incomplete.
- **No built-in large text scaling equivalent**: React Native does not have a first-class text scaling system comparable to Flutter's `TextScaler`. Developers must implement custom scaling, which is error-prone.
- **`react-native-accessibility`** and similar community packages exist but are fragmented.
- **No equivalent to Flutter's `flutter_accessibility_helper`** with native feature detection for bold text, high contrast, etc.

### Kotlin Multiplatform

KMP's accessibility approach is fundamentally different — and both an advantage and a challenge:

- **When using native UI (SwiftUI + Jetpack Compose)**: Accessibility is handled by the platform's native APIs. iOS has `UIAccessibility`, Android has `ViewCompat` accessibility delegates. These are the most mature and complete accessibility systems available. **This is the strongest accessibility path** — you get Apple's and Google's native accessibility support directly.
- **When using Compose Multiplatform for shared UI**: Accessibility support improved significantly with CMP 1.8.0 (May 2025) and 1.12.0 (2026). Compose Multiplatform now exposes accessibility trees to iOS tooling reliably. However, the accessibility support is still catching up to native SwiftUI/UIKit levels. Pre-1.8.0, apps "failed audits" due to unreliable accessibility trees.
- **Key advantage of native UI approach**: The platform-specific accessibility implementation means full access to VoiceOver, TalkBack, Switch Control, and all platform-specific accessibility features without any framework limitations.

**Critical nuance:** KMP's accessibility is strongest when the team commits to native UI with shared business logic. Shared UI via Compose Multiplatform is more accessible than it was in 2024 but is not yet indistinguishable from native.

---

## 4. Performance and Data Usage

### App Size Comparison (2026 benchmarks)

| Framework | Android APK | iOS IPA |
|---|---|---|
| **Kotlin Multiplatform** | **14.2 MB** | **16.8 MB** |
| Flutter 4 | 18.4 MB | 21.3 MB |
| React Native 0.78 | 22.1 MB | 28.9 MB |
| Expo Router 4 | 23.7 MB | 31.2 MB |

**KMP has the smallest binaries**, followed by Flutter. React Native/Expo produce the largest bundles — a significant concern for users on limited data plans who must download the app over cellular connections.

### Memory Usage

| Framework | Idle Memory | Under Load (10K items) |
|---|---|---|
| **KMP** | **64 MB** | **187 MB** |
| Flutter | 87 MB | 243 MB |
| React Native | 142 MB | 312 MB |

**KMP has the lowest memory footprint** due to native compilation and no rendering engine overhead. Flutter's Impeller engine adds 30-50 MB of baseline memory. React Native's JavaScript heap adds significant overhead. For this project — targeting users with potentially older, lower-memory devices — KMP's memory efficiency is a meaningful advantage.

### Startup Time

| Framework | Android Cold Start | iOS Cold Start |
|---|---|---|
| **KMP** | **276 ms** | **298 ms** |
| Flutter | 298 ms | 310 ms |
| React Native | ~500 ms | 487 ms |

All three frameworks are acceptably fast. KMP and Flutter are very close. React Native's JavaScript engine initialization adds overhead.

### Data Usage (Offline-First Context)

Since this app is designed to be offline-first, initial data usage for downloading the app is the primary data concern. After installation, the app caches service data locally.

- **Flutter**: Initial download is moderate (18-22 MB). Map tiles can be pre-cached via Mapbox's offline map feature.
- **React Native**: Larger initial download (22-29 MB) means higher data cost for users downloading over cellular. Map caching works but the larger base size is a disadvantage.
- **KMP**: Smallest initial download (14-17 MB). This is the lowest-barrier option for users with limited data.

**Battery impact:** KMP has the lowest battery consumption (~10%/hr idle), Flutter is moderate (~11%/hr), and React Native is highest (~15%/hr) due to JavaScript engine overhead.

---

## 5. Framework Maturity and Ecosystem

| Factor | Flutter | React Native | Kotlin Multiplatform |
|---|---|---|---|
| **Stability** | Stable since 2018 | Stable (New Arch since 0.76) | KMP stable since Nov 2023; CMP iOS stable since May 2025 |
| **Community size** | Large | Largest (npm ecosystem) | Growing rapidly (7% → 18% adoption in one year) |
| **Production adopters** | Alibaba, BMW, eBay | Meta, Microsoft, Shopify | Netflix, McDonald's, Cash App, Airbnb (95% sharing) |
| **Talent availability** | Dart is niche | JavaScript/TS is abundant | Kotlin is growing but scarce |
| **Hot reload** | Excellent (780ms avg) | Good (Fast Refresh ~1,140ms) | Poor — full recompile required (2-4 min) |
| **CI cost** | Low (Linux runners) | Low (Linux runners) | High (macOS runners required for iOS builds) |
| **Google support** | Google owns Flutter | Meta (community) | Google officially recommends KMP |
| **Web support** | Available | React Native Web | Beta (Kotlin/Wasm) |

### Key Considerations for This Project

- **Team size**: Small team → Flutter's fast development cycle is advantageous
- **CI cost**: KMP requires macOS runners for iOS builds, which significantly increases CI costs (one team with 150 devs reported doubled CI costs)
- **Maintenance**: KMP has lower 3-year total cost of ownership according to industry analysis
- **KMP CI bottleneck**: Every iOS build requires macOS. This is a real operational cost consideration

---

## 6. Detailed Risk Assessment

### Flutter Risks

1. **Map accessibility bug**: The `google_maps_flutter` marker accessibility issue on Android is unresolved. Using Mapbox may mitigate this, but Mapbox's Flutter plugin is less mature for accessibility.
2. **Dart talent scarcity**: Finding Flutter developers is harder than finding React Native developers.
3. **Larger binary than KMP**: The Impeller engine adds ~4 MB to the APK compared to KMP.
4. **Non-native look and feel**: Flutter renders its own widgets, which may not feel identical to native iOS/Android. For a service directory app, this is acceptable but notable.

### React Native Risks

1. **Map accessibility**: The `react-native-maps` accessibility bug on Android is a **critical risk** for this project. Screen reader users cannot reliably access map markers.
2. **WatermelonDB maintenance uncertainty**: The core offline database library has not had a stable release in over a year and requires community patches for current Expo SDK.
3. **Largest bundle size**: 22-29 MB is the largest download, creating a barrier for users on limited data.
4. **Bridge overhead**: Even with the New Architecture, JavaScript-to-native bridge calls add latency and memory pressure.
5. **High 3-year maintenance cost**: Frequent breaking updates and dependency churn.

### Kotlin Multiplatform Risks

1. **Map ecosystem immaturity**: `kmp-maps` and `kmp-maps-compose` are active but not as battle-tested as Flutter's or React Native's map libraries. Feature parity gaps exist.
2. **Accessibility in shared UI**: While native UI provides the best accessibility, Compose Multiplatform's accessibility is still maturing. The team must commit to native UI to guarantee accessibility standards.
3. **No hot reload**: Development speed is slower — every change requires a full recompile (2-4 minutes). This significantly impacts productivity for a small team iterating on UI.
4. **macOS CI requirement**: Every iOS build requires a macOS runner. This is a hard operational constraint with real cost implications.
5. **Team skill gap**: The team needs Kotlin expertise and iOS development knowledge (SwiftUI, Xcode). If the team lacks these, onboarding costs are significant.
6. **Swift interop**: Still experimental. Swift Export is Alpha. Production interop today requires tools like SKIE.

---

## 7. Recommendation: Flutter

**Primary recommendation: Flutter**, with **React Native as a fallback** if the team has strong JavaScript/TypeScript skills.

### Rationale

1. **Accessibility is a first-class requirement**: Flutter has the most comprehensive built-in accessibility framework of the three options. The `Semantics` system, `flutter_accessibility_helper` package, `TextScaler` for large text, and `ScreenReaderOptimizer` provide a complete accessibility toolkit. The one gap (map marker accessibility) can be mitigated by using Mapbox instead of Google Maps.

2. **Offline support is mature and well-documented**: Hive (`hive_ce`) and `sqflite` are battle-tested, well-maintained, and have excellent documentation. The offline-first architecture pattern is well-understood in the Flutter ecosystem.

3. **Map rendering has two solid options**: Both `google_maps_flutter` and `mapbox_maps_flutter` are production-ready. Mapbox specifically offers offline map download — essential for this app's offline-first design.

4. **Fastest development cycle**: Flutter's hot reload (780ms average) enables rapid iteration, which matters for a small team building and refining UI for a vulnerable user population. The widget library covers 94% of platform APIs out of the box.

5. **App size is acceptable**: At 18-22 MB, Flutter's bundle is larger than KMP but significantly smaller than React Native's 22-29 MB. Mapbox offline map caching can be managed independently of app size.

6. **Single codebase, single team**: Flutter requires one team with Dart skills, not the Kotlin + Swift + Android + iOS expertise that KMP demands. For a project with accessibility as a core requirement, having one team focused on one codebase reduces the risk of accessibility regressions.

### Why not React Native?

The `react-native-maps` accessibility bug (markers not announced by screen readers on Android since 2020) is a critical risk for a project where accessibility is a first-class requirement. WatermelonDB's maintenance uncertainty compounds the risk. The largest bundle size (22-29 MB) is also a disadvantage for users on limited data plans. React Native is a viable fallback if the team has existing JavaScript expertise and can invest in custom accessibility solutions for maps.

### Why not Kotlin Multiplatform?

KMP offers the best performance characteristics (smallest bundle, lowest memory, fastest startup) and the strongest native accessibility when using platform-specific UI. However, the risks for this specific project are significant:
- The map ecosystem is not mature enough for a production accessibility-critical app
- No hot reload severely impacts development velocity for a small team
- macOS CI requirement adds ongoing operational cost
- The team would need Kotlin, SwiftUI, and Android Compose expertise
- Shared UI via Compose Multiplatform has improved but is not yet indistinguishable from native for accessibility

KMP is recommended if the team is already Kotlin-proficient, has dedicated iOS and Android developers, and can invest in building the map and accessibility layers carefully.

---

## 8. Implementation Notes

If Flutter is selected, the recommended architecture for the Wayfinder app:

- **Offline storage**: `hive_ce` for service directory caching, `sqflite` for relational queries (filtering by category, district, hours)
- **Map rendering**: `mapbox_maps_flutter` with offline map caching
- **Accessibility**: `flutter_accessibility_helper` package, `Semantics` widgets throughout, `TextScaler` for large text mode
- **Low-data mode**: Implement data-saving preferences in `shared_preferences`, disable map tile pre-fetching, use compressed data formats
- **Sync**: Background sync via `workmanager` when connectivity returns, using the scraper's JSON output
- **State management**: Riverpod or Flutter Bloc for reactive state

---

*This report is based on research conducted in September 2026 using publicly available documentation, GitHub issues, benchmark data, and community analysis.*