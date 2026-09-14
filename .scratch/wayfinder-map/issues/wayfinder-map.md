# Wayfinder Map: Dublin City Support Services Mobile App

## Destination

A mobile app (iOS + Android) that helps Dublin City residents experiencing homelessness, drug-related issues, and other hardships find nearby support services — locations, hours, and how to access them. MVP covers the 5 Day Support Centres + 5 Free Doctor Clinics + Mobile Health Unit from the flyer.

## Notes

- Domain: Dublin City social services directory for people experiencing homelessness/hardship
- Skills to consult: `grilling`, `domain-modeling`, `prototype`, `tdd`, `implement`
- Standing preferences: accessibility-first (offline mode, large text, low-data), both platforms, flyer data as initial dataset
- Data source: flyer dataset (12/02/2026), scraper for updates (written, not fully tested)
- Tracker: local markdown under `.scratch/wayfinder-map/`
- Triage labels: default five canonical roles

## Decisions so far

- Purpose: service directory/map. Features like booking, favorites, etc. come later.
- Target user: people experiencing homelessness, drug-related issues, and other hardships.
- Platform: both iOS and Android. Web version is a future consideration.
- Tracker: local markdown (`.scratch/`). No GitHub repo yet.
- MVP scope: flyer services only — 5 day centers + 5 GP clinics + 1 MHU.
- Data maintenance: flyer dataset as initial data, scraper for updates (community contributions later).
- Accessibility: offline mode, large text, low-data mode are first-class requirements.
- Project initialized: git repo, CLAUDE.md, CONTEXT.md, docs/agents/ configured.

### Research resolutions

- **Data model (01)**: Flyer data extracted to `research/flyer-data.json`. All 5 Day Support Centres + 5 GP clinics documented. Gap analysis: missing phone numbers, coordinates, websites, detailed GP clinic hours, MHU schedule. [→ 01-research-flyer-data.md](01-research-flyer-data.md)
- **Offline architecture (02)**: **SQLite + Sync Queue with Delta Sync** recommended (over Hive and Couchbase Lite). Flutter with `sqflite`/`drift`. Pull-based delta sync with ETag validation, freshness indicators (<1h green, 6-24h amber, >24h red). [→ 02-research-offline-architecture.md](02-research-offline-architecture.md)
- **Framework (03)**: **Flutter** recommended (strongest accessibility framework `Semantics`/`TextScaler`, mature offline storage `hive_ce`/`sqflite`, Mapbox offline caching, 780ms hot reload). React Native rejected (`react-native-maps` accessibility bug), KMP rejected (immature map ecosystem, no hot reload). Mapbox instead of Google Maps for marker accessibility. [→ 03-research-framework.md](03-research-framework.md)
- **Accessibility (04)**: Full spec at `research/accessibility-spec.md`. WCAG 2.2 / Mobile Accessibility Extension compliance. Visual: large text, high contrast, bold text. Cognitive: plain language, linear navigation, single-purpose screens. Hardware: low-end device support, haptics, voice control. UI: list-first layout, accessible map pins, voice search, crisis button, max 3 taps to any service. [→ 04-research-accessibility.md](04-research-accessibility.md)

## Not yet specified

- Data model schema — how are locations, services, hours structured? (research done, needs final definition)
- Scraper architecture — how does the scraper fetch and transform the flyer data? (needs integration with SQLite)
- Map rendering — Mapbox confirmed. How are locations displayed? What clustering/zoom behavior?
- Search and filtering — how do users find services by category, proximity, or day?
- Notification system — are hours changes pushed to users?
- Testing strategy — how to verify data accuracy and app reliability?
- Data gap resolution — how to fill missing fields (phone numbers, coordinates, GP clinic hours, MHU schedule)?

## Out of scope

- Booking/appointment features (MVP is directory-only)
- Favorites/saved locations (can be added later)
- Social features, sharing, community forums
- Non-Dublin City services
- Web version (mobile-only first)
- Administrative dashboard for service providers
- Payment or transaction features
- Integration with other city systems beyond the flyer/scraper
