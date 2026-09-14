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
- **Framework (03)**: ⚠️ **SUPERSEDED by PWA pivot.** Flutter was researched for native apps. Now needs re-evaluation for PWA — SvelteKit, Next.js, or Nuxt.js for static PWA generation.
- **Accessibility (04)**: ✅ Full spec at `research/accessibility-spec.md`. WCAG 2.2 / Mobile Accessibility Extension compliance. Principles framework-agnostic. [→ 04-research-accessibility.md](04-research-accessibility.md)

## Not yet specified

- PWA framework selection — SvelteKit vs Next.js vs Nuxt.js for static PWA generation
- Data model schema — how are locations, services, hours structured?
- Scraper architecture — how does the scraper fetch and transform flyer data into static JSON?
- Service Worker strategy — what caching patterns for offline support?
- Map rendering — what library for map rendering in a PWA? Mapbox GL JS? Leaflet?
- Search and filtering — how do users find services by category, proximity, or day?
- PWA manifest — app name, icons, theme colors, display mode
- QR code generation — how to generate and distribute QR codes on flyers?
- Testing strategy — how to verify data accuracy and PWA reliability?
- Data gap resolution — how to fill missing fields (phone numbers, coordinates, GP clinic hours, MHU schedule)?

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
