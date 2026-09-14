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

## Not yet specified

- Data model schema — how are locations, services, hours structured? Need to define before coding.
- Scraper architecture — how does the scraper fetch and transform the flyer data?
- Offline storage strategy — what local database/cache for mobile?
- UI framework — what stack for iOS + Android cross-platform?
- Map rendering — how are locations displayed on a map? What map library?
- Search and filtering — how do users find services by category, proximity, or day?
- Notification system — are hours changes pushed to users?
- Testing strategy — how to verify data accuracy and app reliability?

## Out of scope

- Booking/appointment features (MVP is directory-only)
- Favorites/saved locations (can be added later)
- Social features, sharing, community forums
- Non-Dublin City services
- Web version (mobile-only first)
- Administrative dashboard for service providers
- Payment or transaction features
- Integration with other city systems beyond the flyer/scraper
