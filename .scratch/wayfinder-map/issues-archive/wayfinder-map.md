# Wayfinder Map: Dublin City Support Services PWA

## Destination

A **Progressive Web App (PWA)** that helps Dublin City residents experiencing homelessness, drug-related issues, and other hardships find nearby support services — locations, hours, and how to access them. Users install it by scanning a QR code on flyers, adding it to their home screen from the web. Hosted on GitHub Pages (static hosting). MVP covers the 5 Day Support Centres + 5 Free Doctor Clinics + Mobile Health Unit from the flyer.

## Notes

- Domain: Dublin City social services directory for people experiencing homelessness/hardship
- Skills to consult: `grilling`, `domain-modeling`, `prototype`, `tdd`, `implement`
- Standing preferences: accessibility-first (offline mode, large text, low-data), any device with browser, flyer data as initial dataset
- Data source: flyer dataset (12/02/2026), scraper for updates (written, not fully tested)
- Tracker: local markdown under `.scratch/wayfinder-map/`
- Triage labels: default five canonical roles
- **No backend services** — all static files on GitHub Pages
- **Installation**: PWA manifest + service worker → QR codes on flyers → "Add to Home Screen"

## Decisions so far

- Purpose: service directory/map. Features like booking, favorites, etc. come later.
- Target user: people experiencing homelessness, drug-related issues, and other hardships.
- Platform: **any device with a browser** (PWA). No native app stores. Install via QR code on flyers → "Add to Home Screen".
- Backend: **None**. No server, no API, no hosting costs. All static files on GitHub Pages.
- Data: Static JSON hosted alongside the PWA on GitHub Pages. Scraper produces static JSON files.
- Installation: PWA manifest + service worker → scan QR code on flyers → "Add to Home Screen"
- Offline: Service Worker caching (Cache API), not SQLite. Static-first architecture.

### Research resolutions

- **Data model (01)**: ✅ Flyer data extracted to `research/flyer-data.json`. All 5 Day Support Centres + 5 GP clinics documented. Gap analysis at `research/gap-analysis.md`.
- **Offline architecture (02)**: ⚠️ **SUPERSEDED by PWA pivot.** SQLite + Sync Queue was researched for native apps. Now replaced by Service Worker + Cache API for static PWA architecture.
- **Framework (03)**: ⚠️ **SUPERSEDED by PWA pivot.** Flutter was researched for native apps. Now re-evaluated → **Continue with SvelteKit** (`@vite-pwa/sveltekit` + `@sveltejs/adapter-static`). Zero-friction GitHub Pages deployment, built-in accessibility platform, PWA plugin already configured. See [→ 03-pwa-framework.md](03-pwa-framework.md) and `research/pwa-framework-recommendation.md`
- **Accessibility (04)**: ✅ Full spec at `research/accessibility-spec.md`. WCAG 2.2 / Mobile Accessibility Extension compliance. Principles framework-agnostic. [→ 04-research-accessibility.md](04-research-accessibility.md)
- **PWA offline strategy (02-pwa-offline-strategy)**: ✅ Service Worker architecture and caching strategy documented at `research/offline-strategy.md`. CacheFirst for app shell, StaleWhileRevalidate for JSON, NetworkFirst for navigation, CacheOnly for offline fallback. Version-based freshness detection. Low-data mode with CacheOnly + Network Information API. WCAG 2.2 AA for offline page. [→ 02-pwa-offline-strategy.md](02-pwa-offline-strategy.md)
- **Data gap fill**: ✅ Coordinates and phone numbers filled for all 5 locations from web research. GP clinic schedules obtained for 3/5 locations. MHU schedule obtained (Tues/Wed/Thu 7pm-10pm). See `research/data-gap-fill.md` and updated `research/flyer-data.json`
- **Framework (03)**: ⚠️ **SUPERSEDED by PWA pivot → re-evaluated → Continue with SvelteKit** (`@vite-pwa/sveltekit` + `@sveltejs/adapter-static`). Zero-friction GH Pages deployment, built-in accessibility platform, PWA plugin already configured. See [→ 03-pwa-framework.md](03-pwa-framework.md)

### Implementation resolutions

- **PWA accessibility (08-accessibility)**: ✅ Full implementation complete. Service Worker caching, offline fallback page, ARIA live regions, skip links, text scale toggle (100%–200%), low-data mode toggle (auto-detect + manual), emergency FAB, high contrast, reduced motion. 25 tests passing (unit/integration/E2E). See `research/accessibility-implementation-plan.md` and `src/lib/components/`.
- **PWA icons**: ✅ 7 icon sizes (72→512) generated from SVG (Dublin castle + medical cross), updated manifest in `vite.config.ts`.
- **QR code generation**: ✅ Build-time script (`npm run qr:generate`), outputs `static/qr-code.svg` (SVG, error correction H, URL: `https://dublin-city-support.github.io/`).
- **Testing infrastructure**: ✅ Vitest + Playwright + axe-core configured. 19 unit/integration tests + 6 E2E tests passing. GitHub Actions CI workflow. CI scripts: `test`, `test:unit`, `test:e2e`, `lint`, `check`, `build` all passing.

## Not yet specified

- 07-prototype-ui — **awaiting human review** of `research/prototype-ui.html`

## Out of scope

- Booking/appointment features (MVP is directory-only)
- Favorites/saved locations (can be added later)
- Social features, sharing, community forums
- Non-Dublin City services
- Native app stores (iOS App Store, Google Play)
- Administrative dashboard for service providers
- Payment or transaction features
- Integration with other city systems beyond the flyer/scraper
- Backend services, APIs, databases, server-side rendering
