# Accessibility Specification: Wayfinder Map — Dublin City Support Services

**Version:** 1.0
**Date:** 2026-09-14
**Status:** Draft
**Author:** Research Agent

---

## 1. Overview

This specification defines the accessibility requirements for the Wayfinder Map mobile application, which serves people experiencing homelessness, drug-related issues, and other hardships in Dublin City. The app must be usable by individuals with limited tech experience, disabilities, intermittent connectivity, and constrained data plans. Accessibility is a first-class requirement — not a feature add-on — alongside offline mode, large text, and low-data mode.

**Platform:** iOS and Android (cross-platform)
**Target users:** People experiencing homelessness, drug-related issues, low digital literacy, varying disabilities, and limited connectivity

---

## 2. Essential Accessibility Features for the Target User Base

### 2.1 Visual Accessibility

| Feature            | Requirement                                                                 | Rationale                                                             |
| ------------------ | --------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Large text mode    | Configurable font scaling up to 200% system default; minimum 18sp body text | Users with vision impairment, aging users, users reading under stress |
| High contrast mode | WCAG AAA contrast ratios (7:1); black-on-white toggle option                | Low vision, outdoor glare, stressed or fatigued users                 |
| Bold text support  | Respect system bold-text preference                                         | Users with low vision who benefit from heavier type weights           |
| Color independence | Never encode meaning by color alone; use icons + labels + color             | Color blindness, grayscale mode users                                 |
| Reduced motion     | Respect `reduceMotion` system setting; disable animations                   | Users with vestibular disorders, epilepsy, or cognitive sensitivities |
| Dark mode          | System-aware dark/light theme support                                       | Low-light environments (sleeping rough), battery saving on OLED       |

### 2.2 Cognitive & Literacy Accessibility

| Feature                           | Requirement                                                                                | Rationale                                                                                                        |
| --------------------------------- | ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| Plain language                    | Read at ≤6th-grade reading level; avoid jargon and domain-specific terms                   | Users with limited literacy, cognitive load in crisis situations                                                 |
| Icon + text labeling              | Every interactive element has visible text label; icons never used alone                   | Low-literacy users; screen reader users                                                                          |
| Linear navigation                 | Flat, linear information architecture; no nested hierarchies deeper than 2 levels          | Users unfamiliar with hierarchical menus; research confirms linear navigation is preferred by low-literate users |
| Consistent layout                 | Same navigation structure on every screen; predictable placement of key actions            | Cognitive load reduction; users build mental models faster                                                       |
| Contextual help                   | Help/coach marks available from every screen; audio/video tutorials over text instructions | Users who need guided onboarding; low-literacy users                                                             |
| Single-purpose screens            | Each screen delivers one primary action or question                                        | Reduces cognitive overwhelm in urgent situations                                                                 |
| Confirmation for critical actions | Explicit confirmation dialogs before actions like calling emergency services               | Prevents accidental activation in stressful moments                                                              |

### 2.3 Hardware & Device Accessibility

| Feature                | Requirement                                                                      | Rationale                                                        |
| ---------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Low-end device support | App must run on 2GB RAM devices; test on budget hardware (Android 7+, iPhone SE) | Many users rely on older, lower-spec phones                      |
| Offline voice output   | Text-to-speech works fully offline                                               | Users who cannot read; hands-free use while moving               |
| Haptic feedback        | Vibration confirmation on all actions                                            | Deaf/hard-of-hearing users; confirmation without sound           |
| Large touch targets    | Minimum 48dp on Android, 44pt on iOS; recommended 56dp for high-stress use       | Users with motor impairments, tremor, arthritis, or gloved hands |
| Voice control          | App operable via voice commands (system-level integration)                       | Users with limited fine motor control                            |

---

## 3. Accessible UI Patterns for Service Directories

### 3.1 Service List & Card Patterns

- **List-first approach:** Service directories render as simple vertical lists, not grids or maps-first interfaces. Lists are sequentially navigable and screen-reader friendly.
- **Card layout per service:** Each service card contains: title (service name), category icon, distance/proximity, status indicator (open/closed), and a single "Get Directions" or "Call" CTA button.
- **Category filtering by visible tabs:** Use horizontal tab bar with color-coded category icons (Food, Hygiene, Healthcare, Connectivity, Employment). Tabs must have text labels beneath icons.
- **Status badges:** Use high-contrast badges with text ("Open Now," "Closed," "Today Only") — never rely on color alone to indicate status.

### 3.2 Map Accessibility Pattern

- **Map is secondary to list:** The primary interaction is a scrollable list of services; the map view is an optional visual enhancement. Users can toggle between list and map views.
- **Map pins with accessible labels:** Each pin must have a semantic label including service name, category, distance, and current status. Screen readers announce all this information on tap/focus.
- **Tap-to-expand, not pinch-to-zoom:** Avoid pinch gestures as primary map interaction. Use visible zoom controls (+/- buttons) alongside any gesture support.
- **Accessibility traversal on map:** Ensure screen readers can move between map markers sequentially, not just explore by touch.

### 3.3 Search & Filter Patterns

- **Voice search first:** Primary search input should have a microphone button for voice input; text input is secondary. This serves users with low literacy.
- **Category-based filtering over keyword search:** For this user base, category tabs (Food, Shelter, Healthcare) are more discoverable than a search bar. Research with homeless users shows search bars are confusing when the query is broad.
- **Filters as visible toggles:** Active filters show as clear, removable chips above results. Use "Clear all" button.
- **Results sorted by proximity and urgency:** Default sort by distance; allow sorting by "Open Now" or "Today." Announce sort order to screen readers.

### 3.4 Crisis/Emergency Pattern

- **Persistent emergency button:** A fixed, high-contrast button visible on every screen (bottom navigation or floating action button) that calls emergency services (911, 988, ambulance). Must be the largest touch target on screen.
- **Crisis mode:** A dedicated mode (activatable from emergency button or app settings) that simplifies the interface to essential information only, with large text, high contrast, and screen-reader-optimized announcements.
- **Speed dial:** Quick-access shortcuts to frequently needed services (shelter, food, medical) accessible from any screen with a single tap.

### 3.5 Service Detail Screen Pattern

- **Single-column layout:** No side panels or multi-column layouts.
- **Information in priority order:** Service name → Status → Hours → Address → Phone → Website → Directions. Each item is a tappable element where appropriate.
- **One action per screen:** Directions, Call, or Save — never more than one primary action per detail card.
- **Offline availability indicator:** Clear badge showing whether service details are available offline.

---

## 4. Offline-Compatible Accessibility Solutions

### 4.1 Architecture Approach

Offline accessibility requires a **cache-first, offline-first architecture** where all essential content and UI are available without network connectivity.

| Layer        | Strategy                                            | Technology                                                                |
| ------------ | --------------------------------------------------- | ------------------------------------------------------------------------- |
| App shell    | Precached at install time                           | Service Worker (PWA) or framework-specific caching (Flutter/React Native) |
| Service data | Full dataset cached locally on first online session | SQLite / IndexedDB / Hive (Flutter) / WatermelonDB (React Native)         |
| Map tiles    | Critical area map tiles precached for Dublin City   | Offline tile cache with configurable area                                 |
| AI/TTS       | Voice models cached on-device after first download  | On-device TTS (iOS AVSpeechSynthesizer, Android TextToSpeech)             |
| Images       | Compressed, WebP format; low-res fallback cached    | Local asset cache with size-appropriate variants                          |

### 4.2 Offline-First Data Strategy

- **Precache the app shell** at install time: HTML, CSS, JS bundles, fonts, and always-visible UI elements. Users can launch the app and navigate the interface entirely offline.
- **Full service dataset sync:** On first online connection, download the complete dataset of all Dublin City support services (locations, hours, categories, contact info) to local SQLite/IndexedDB. This is a one-time download (~5-10MB).
- **Background sync queue:** User actions (favorites, searches) performed offline are queued locally and synced when connectivity returns. The user sees a clear sync status indicator.
- **Stale-while-revalidate for service updates:** When online, serve cached data immediately while silently fetching updates in the background. When offline, serve cached data with an "Updated: [date]" timestamp so users know how current the information is.

### 4.3 Offline Accessibility Guarantees

- All text content available offline
- TTS voices available offline (system voices, not cloud-based)
- Map tiles for Dublin City core area available offline
- Service search and filtering work offline against cached data
- Directions (pre-downloaded routing data) available offline
- Emergency contacts always accessible (hardcoded local resources)

### 4.4 Offline Indicators & Feedback

- **Persistent connectivity badge:** Visible on every screen showing online/offline status. Use high-contrast icon + text label (e.g., "Online," "Offline — showing cached data").
- **Staleness warning:** When offline, show a banner: "Showing cached data from [date]. Some information may be outdated."
- **Graceful degradation:** Features requiring network (real-time availability, booking) show a clear message: "This feature requires internet. Essential services are still available."

---

## 5. Low-Data Mode Implementation Strategy

### 5.1 Android Data Saver Integration

The app must detect and respond to Android's **Data Saver** mode (API 24+) and Apple's **Low Data Mode** (iOS 13+), implementing the following adaptive behaviors:

| Trigger                                             | Action                                                                        |
| --------------------------------------------------- | ----------------------------------------------------------------------------- |
| Data Saver ON / Low Data Mode ON                    | Block all image loading; show text-only content with placeholders             |
| Constrained/expensive network detected              | Reduce image resolution to thumbnail; disable prefetching; disable animations |
| 2G/3G detected                                      | Serve text-only; disable all media; use compressed WebP at 50% quality        |
| User manually enables low-data mode in app settings | Apply all above + disable background sync + reduce polling frequency          |

### 5.2 Image Optimization Strategy

- **WebP format:** All images served as WebP (30% smaller than JPEG/PNG at equivalent quality). Android supports lossy WebP since API 14; iOS supports WebP natively.
- **Adaptive image loading:** Serve different image resolutions based on network type:
  - WiFi/4G/5G: Full resolution
  - 3G: Medium resolution (thumbnail)
  - 2G/constrained: No images; text-only with color-coded placeholders
- **Dynamic image sizing:** Request server-served images at the exact display size needed, not larger.
- **Lazy loading:** Images load only when they enter the viewport; never prefetch off-screen content.
- **Placeholder strategy:** Generate placeholder colors from images using palette analysis; show colored placeholder blocks while loading.

### 5.3 Data Budget Controls

- **User-configurable data budget:** Settings allow users to set a monthly data limit. The app warns before exceeding and switches to text-only mode near the limit.
- **WiFi-only mode toggle:** Option to download updates, sync data, and load images only when on WiFi.
- **Batching:** Network requests batched (not one-by-one) to minimize connection overhead.
- **Compression:** All JSON API payloads compressed with gzip/deflate. Text-based data (service listings) compressed to <50KB for full Dublin dataset.

### 5.4 Low-Data Testing Benchmarks

- App must load core service list in <3 seconds on 3G (500KB/s)
- Full dataset sync must complete in <60 seconds on 3G
- App shell must load in <2 seconds on 2G (50KB/s)
- Zero images in text-only mode; all screens functional without imagery

---

## 6. Screen Reader & Gesture Navigation Support

### 6.1 Screen Reader Compatibility

The app must be fully navigable with **VoiceOver** (iOS) and **TalkBack** (Android). All accessibility testing must be done with screen readers enabled.

**Core requirements:**

| Requirement            | Details                                                                                                                |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Semantic labels        | Every interactive element has a meaningful label (e.g., "Shelter at 5 Main Street, open until 8pm" not "Button 1")     |
| Heading hierarchy      | Content structured with proper heading levels (H1 → H2 → H3) so screen readers can jump between sections               |
| Focus order            | Logical sequential focus order matching visual layout; no focus traps                                                  |
| Live regions           | Dynamic content updates (search results, status changes) announced via `aria-live` regions                             |
| Grouping               | Related elements (image + title + status) grouped into a single semantic unit so screen readers announce them together |
| Skip navigation        | "Skip to content" link available for bypassing repetitive navigation                                                   |
| No touch-only gestures | All custom gestures have tap/button alternatives. Never use a double-tap or swipe as the only way to trigger an action |

**Key guidelines from WCAG 2.2 / Mobile Accessibility Extension:**

- Do not override platform gestures. VoiceOver's swipe-left/right for navigation and double-tap for activation must remain intact.
- All functions available by touch when screen reader is off must still be available when screen reader is on.
- Infinite scroll is incompatible with screen readers — use "Load more" button instead.
- Custom gestures require a single-pointer alternative (per WCAG 2.5.1 Pointer Gestures).

### 6.2 Screen Reader Optimization for Service Discovery

- **Service cards announced as groups:** Title + category + status + distance in a single announcement.
- **Search results navigation:** Screen reader users can swipe through results sequentially; each result announced with full context.
- **Map marker navigation:** Markers focusable via screen reader swipe; each announces name and status.
- **"What's nearby" mode:** A dedicated screen reader mode that reads out all services within a radius, in order of proximity, with one swipe per service.

### 6.3 Gesture Navigation for Limited Tech Experience Users

- **Minimize gestures:** Use only tap and swipe-down-to-refresh. Avoid pinch, long-press, two-finger scroll, or any complex gesture.
- **Tap targets:** All interactive elements ≥48dp/44pt. Increase to 56dp for emergency buttons.
- **No horizontal-only navigation:** Never require horizontal swiping as the sole navigation method. All content must be accessible vertically.
- **Back gesture:** Use standard system back button/gesture; do not implement custom swipe-to-go-back patterns.
- **Confirm before navigation away:** If a user navigates away with unsaved data, show a simple confirmation dialog.

### 6.4 Alternative Input Methods

| Method                 | Support         | Use Case                                                        |
| ---------------------- | --------------- | --------------------------------------------------------------- |
| Switch control         | Full support    | Motor-impaired users using external switches                    |
| Voice control (system) | Full support    | Hands-free navigation; users with limited dexterity             |
| Keyboard navigation    | Full support    | External keyboards, Bluetooth keyboards                         |
| Assistive touch        | No interference | App must work with iOS AssistiveTouch and Android switch access |

---

## 7. Intuitive Navigation Patterns for Users with Limited Tech Experience

### 7.1 Navigation Architecture

```
┌─────────────────────────────┐
│  TAB BAR (persistent, fixed) │
├─────────────────────────────┤
│                              │
│  EMERGENCY BUTTON (floating) │
│  (visible on all screens)    │
│                              │
├─────────────────────────────┤
│  SCREEN CONTENT              │
│  (one primary action)        │
│                              │
└─────────────────────────────┘
```

**Tab bar (4 tabs max):**

1. **Nearby** — Map + list of services near current location (default)
2. **Categories** — Filter by service type (Food, Shelter, Healthcare, etc.)
3. **Help** — Emergency contacts, crisis mode, audio help tutorials
4. **Settings** — Accessibility settings, low-data mode, connectivity status

### 7.2 Navigation Principles

| Principle                         | Implementation                                                                 |
| --------------------------------- | ------------------------------------------------------------------------------ |
| **Maximum 3 taps to any service** | Home → Category → Service detail = 3 taps max                                  |
| **No login required**             | Zero account creation, zero personal data                                      |
| **No hidden menus**               | All navigation visible; no hamburger menus or drawer navigation                |
| **Breadcrumb-less**               | Do not show path breadcrumbs; use clear tab labels instead                     |
| **Persistent emergency button**   | Always-visible, always-accessible from any screen                              |
| **One question per screen**       | Never ask multiple questions on one screen                                     |
| **Visual progress indicators**    | When a flow has steps (e.g., getting directions), show a simple step indicator |

### 7.3 Onboarding & First-Run Experience

- **No tutorial screen at launch.** Users can skip onboarding entirely.
- **Contextual coach marks:** Small, dismissible hints appear next to key features on first use (e.g., "Tap this to see services near you").
- **Audio walkthrough option:** A "Listen to how this works" button that uses TTS to describe the app's main features.
- **"Start without reading" option:** A prominent button to bypass all help content and go directly to the service list.

### 7.4 Error Handling & Recovery

| Situation             | Behavior                                                                              |
| --------------------- | ------------------------------------------------------------------------------------- |
| No network            | Show cached data + "Offline" badge; never show blank screen or error-only state       |
| Empty search results  | Show "No services found for this category. Try a different category or check nearby." |
| Location unavailable  | Prompt with "Enable location?" → link to settings; fall back to manual area selection |
| App crash on relaunch | Resume to home screen, not error screen; restore previous scroll position             |
| Data sync failure     | Show "Will sync when online" badge; queue operations; never lose user data            |

---

## 8. Framework Recommendations & Accessibility Tooling

### 8.1 Framework Considerations

For cross-platform iOS + Android development, the framework must provide:

- Built-in accessibility semantics support
- Dynamic type / text scaling
- Screen reader integration
- Offline storage capabilities

**Recommended approaches:**

| Framework                | Accessibility Strengths                                                                          | Offline Storage                  | Notes                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------ | -------------------------------- | ---------------------------------------------------- |
| **Flutter**              | Built-in Semantics widget, Material Design accessibility, `flutter_accessibility_helper` package | Hive, SQLite, Isar               | Strong accessibility API, single codebase            |
| **React Native**         | `AccessibilityInfo` API, `expo-accessibility-plus` (Expo), `react-native-accessibility-toolkit`  | WatermelonDB, AsyncStorage, MMKV | Rich ecosystem of accessibility packages             |
| **Kotlin Multiplatform** | Native Android accessibility; iOS via Swift interop                                              | SQLDelight, Realm                | Best native performance; more platform-specific code |

### 8.2 Essential Accessibility Plugins/Libraries

| Platform       | Package                                                   | Purpose                                                                                   |
| -------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Flutter        | `flutter_accessibility_helper`                            | Screen reader optimization, focus management, semantic support                            |
| Flutter        | `accessibility_tools`                                     | Debug checker for tap targets, font overflow, image labels                                |
| Flutter        | `flutter_adaptive_assist`                                 | Unified API for platform accessibility settings (bold text, high contrast, reduce motion) |
| React Native   | `expo-accessibility-plus`                                 | Extended accessibility flags beyond stock `AccessibilityInfo`                             |
| React Native   | `@accessibility-rn-js/react-native-accessibility-toolkit` | TTS, screen reader, color adjustments, accessibility profiles                             |
| React Native   | `react-native-voice`                                      | Voice input for search and commands                                                       |
| Cross-platform | Workbox (PWA) or equivalent                               | Service worker caching strategies                                                         |

### 8.3 Testing & QA Requirements

- **Screen reader testing:** Every screen tested with VoiceOver and TalkBack enabled
- **Automated accessibility checks:** `accessibility_tools` (Flutter) or `eslint-plugin-jsx-a11y` (React Native) in CI pipeline
- **Color contrast validation:** Automated contrast checking against WCAG AAA (7:1) standards
- **Touch target validation:** Automated checks ensuring all interactive elements ≥48dp/44pt
- **Offline testing:** Cold-start offline testing on every release; automated test suite simulating offline conditions
- **Low-data testing:** Network throttling tests (2G, 3G) verifying app functionality and data usage
- **Real user testing:** Testing with actual users experiencing homelessness, low literacy, and disabilities — not just automated checks

---

## 9. Compliance Standards

This specification aligns with:

| Standard                                    | Level                           | Application                                                   |
| ------------------------------------------- | ------------------------------- | ------------------------------------------------------------- |
| WCAG 2.2                                    | AA minimum, AAA where possible  | All UI content, color, navigation, input                      |
| W3C Mobile Accessibility Extension          | All applicable success criteria | Touch gestures, screen reader compatibility                   |
| W3C Guidance on Applying WCAG 2.2 to Mobile | All applicable guidance         | Mobile-specific patterns                                      |
| Section 508 (where applicable)              | —                               | Government service requirements                               |
| GDPR / Data Protection                      | —                               | No personal data collected; anonymity is a design requirement |

---

## 10. Priority Matrix

| Feature                                          | Priority          | Phase    |
| ------------------------------------------------ | ----------------- | -------- |
| Offline-first data caching (full dataset)        | **P0 — Critical** | MVP      |
| Large text / dynamic type                        | **P0 — Critical** | MVP      |
| Screen reader support (VoiceOver/TalkBack)       | **P0 — Critical** | MVP      |
| High contrast mode                               | **P0 — Critical** | MVP      |
| Emergency button (always visible)                | **P0 — Critical** | MVP      |
| Low-data mode (image blocking, adaptive loading) | **P1 — High**     | MVP+1    |
| Voice search                                     | **P1 — High**     | MVP+1    |
| Linear navigation (flat hierarchy)               | **P1 — High**     | MVP      |
| Category-based filtering                         | **P1 — High**     | MVP      |
| Haptic feedback                                  | **P2 — Medium**   | Post-MVP |
| Switch control / external input                  | **P2 — Medium**   | Post-MVP |
| Audio/video help tutorials                       | **P2 — Medium**   | Post-MVP |
| Data budget controls                             | **P2 — Medium**   | Post-MVP |
| Onboarding coach marks                           | **P3 — Low**      | Post-MVP |
| Advanced offline map tiles                       | **P3 — Low**      | Post-MVP |

---

## 11. References

- [W3C Guidance on Applying WCAG 2.2 to Mobile Applications](https://www.w3.org/TR/wcag2mobile-22/)
- [W3C Mobile Accessibility Extension](https://w3c.github.io/Mobile-A11y-Extension/)
- [WCAG 2.2 Success Criterion 2.5.1: Pointer Gestures](https://www.w3.org/WAI/WCAG22/Understanding/pointer-gestures.html)
- [NN/G: Challenges for Screen-Reader Users on Mobile](https://www.nngroup.com/articles/screen-reader-users-on-mobile/)
- [Android Data Saver Documentation](https://source.android.com/docs/core/data/data-saver)
- [Apple Low Data Mode Documentation](https://support.apple.com/en-us/102433)
- [Flutter Accessibility Documentation](https://docs.flutter.dev/ui/accessibility/assistive-technologies)
- [MDN: Service Workers & Offline Caching](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Caching)
- [Google Android Accessibility Best Practices](https://android.googlesource.com/platform/frameworks/base/+/c6c45d225cba9ecc4521de61c3af49cc038d685a/docs/html/distribute/essentials/quality/billions.jd)
- [Turning Point / Arch — Harm Reduction App Design](https://wearearch.com/our-work/turning-point)
- [Actionable UI Design Guidelines for Low-Literate Users](https://www.shivanikapania.com/assets/cscw2021paper.pdf)
- [No-D NYC App — Accessibility Case Study](https://no-d-nyc.appstor.io/)
