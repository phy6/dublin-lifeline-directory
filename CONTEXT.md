# Dublin City Support Services

## Domain Glossary

- **Day Support Centre**: A physical location offering daily services (food, showers, healthcare, etc.) to people experiencing homelessness or hardship.
- **Service Category**: A type of support offered — Food, Hygiene (shower/clothing), Connectivity (WiFi/charging), Healthcare, Employment.
- **Location**: A Day Support Centre or clinic with a physical address, hours, and contact information.
- **GP Clinic**: A general practitioner clinic offering free or low-cost medical services, often with walk-in hours and appointment slots.
- **Mobile Health Unit (MHU)**: A travelling healthcare service that visits different locations on scheduled days.
- **Service Directory**: The PWA's core data — locations, services, hours, and access information.

## Standing Preferences

- All service data originates from the flyer dataset. Scraper updates are additive — never remove a location without confirmation.
- The app targets users experiencing homelessness, drug-related issues, and other hardships.
- Accessibility is a first-class requirement: offline mode, large text, low-data mode.
- **Platform**: PWA (any device with a browser). No native app stores.
- **Installation**: QR codes on flyers → "Add to Home Screen". Hosted on GitHub Pages.
- **Backend**: None. All static files on GitHub Pages. No server, no API.
- **Offline**: Service Worker + Cache API. Static-first architecture.