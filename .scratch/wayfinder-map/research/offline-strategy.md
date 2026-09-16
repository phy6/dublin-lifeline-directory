# Dublin City Support Services — PWA Offline Strategy

**Document Version:** 1.0
**Date:** 2026-09-14
**Project:** Dublin City Support Services (SvelteKit PWA, `@sveltejs/adapter-static`, `@vite-pwa/sveltekit`, GitHub Pages)

---

## Table of Contents

1. [Service Worker Caching Strategy](#1-service-worker-caching-strategy)
2. [Static JSON Data Caching Approach](#2-static-json-data-caching-approach)
3. [Offline Fallback Page Design](#3-offline-fallback-page-design)
4. [Data Freshness Strategy](#4-data-freshness-strategy)
5. [Low-Data Mode Implementation](#5-low-data-mode-implementation)
6. [Accessibility Considerations for Offline Mode](#6-accessibility-considerations-for-offline-mode)

---

## 1. Service Worker Caching Strategy

### 1.1 Architecture Context

The app uses `@vite-pwa/sveltekit` (Workbox-based) with `@sveltejs/adapter-static`. The service worker is generated automatically. The current `vite.config.ts` defines two `runtimeCaching` rules for OpenStreetMap resources (`CacheFirst` for tiles, `StaleWhileRevalidate` for the API). All app data is static JSON served from the same origin as the SPA shell.

### 1.2 Recommended Strategy Matrix

| Resource Type                              | Strategy                            | Rationale                                                        | Source                                                                                                                         |
| ------------------------------------------ | ----------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| App shell (JS, CSS, HTML, icons, manifest) | **CacheFirst** (precache)           | Never changes between deployments; served instantly              | [web.dev: Service worker caching strategies](https://web.dev/articles/service-worker-caching-and-http-caching)                 |
| Static JSON (`services.json`)              | **StaleWhileRevalidate**            | Show cached data immediately, update in background on next visit | [Workbox: StaleWhileRevalidate](https://developer.chrome.com/docs/workbox/caching-strategies-overview/#stale-while-revalidate) |
| Navigation requests (route pages)          | **NetworkFirst**                    | Fresh HTML is important; fall back to cache when offline         | [MDN: PWA Caching](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Caching)                           |
| OpenStreetMap tiles                        | **CacheFirst** (existing)           | Large, rarely changing, expensive to re-fetch                    | [Existing config](vite.config.ts:39)                                                                                           |
| OpenStreetMap API                          | **StaleWhileRevalidate** (existing) | Balance freshness with performance                               | [Existing config](vite.config.ts:45)                                                                                           |
| Offline fallback page                      | **CacheOnly** (precached)           | Must always be available; self-contained HTML                    | [web.dev: Offline fallback page](https://web.dev/articles/offline-fallback-page)                                               |

### 1.3 Workbox Configuration via `@vite-pwa/sveltekit`

The `runtimeCaching` array in `vite.config.ts` should be expanded:

```typescript
workbox: {
  globPatterns: ['**/*.{js,css,html,ico,png,svg,webmanifest,ttf,woff,woff2,json}'],
  runtimeCaching: [
    // App shell — precache all build + static assets
    {
      urlPattern: /^https:\/\/dublin-city-support\.github\.io\//,
      handler: 'CacheFirst',
      options: {
        cacheName: 'app-shell',
        expiration: {
          maxEntries: 50,
          maxAgeSeconds: 30 * 24 * 60 * 60 // 30 days
        },
        cacheableResponse: {
          statuses: [0, 200]
        }
      }
    },
    // Static JSON data — stale-while-revalidate
    {
      urlPattern: /\/services\.json/,
      handler: 'StaleWhileRevalidate',
      options: {
        cacheName: 'data-json',
        expiration: {
          maxEntries: 10,
          maxAgeSeconds: 7 * 24 * 60 * 60 // 7 days
        }
      }
    },
    // Navigation — network first, cache fallback
    {
      urlPattern: ({ request }) => request.mode === 'navigate',
      handler: 'NetworkFirst',
      options: {
        cacheName: 'pages',
        networkTimeoutSeconds: 3,
        expiration: {
          maxEntries: 20,
          maxAgeSeconds: 1 * 24 * 60 * 60 // 1 day
        }
      }
    },
    // Existing OpenStreetMap rules
    {
      urlPattern: /^https:\/\/tile\.openstreetmap\.org\//,
      handler: 'CacheFirst'
    },
    {
      urlPattern: /^https:\/\/api\.openstreetmap\.org\//,
      handler: 'StaleWhileRevalidate'
    }
  ]
}
```

### 1.4 Precaching Strategy

The `@sveltejs/adapter-static` prerenders all pages as static HTML. The `@vite-pwa/sveltekit` plugin generates a precache manifest from the build output. Key configuration:

- Enable `kit.includeVersionFile: true` so the SvelteKit `_app/version.json` is included in the precache manifest, enabling cache invalidation on deployment [SvelteKit docs](https://svelte.dev/docs/kit/service-workers).
- The `prerender.entries: ['*']` in `svelte.config.js` ensures all routes are prerendered, making them available for offline navigation.
- Precache the offline fallback page (`offline.html`) as part of the manifest.

**Important:** With `@vite-pwa/sveltekit`, if a custom service worker is needed (e.g., `src/service-worker.js`), it must remove the SvelteKit service worker module references. See [vite-pwa docs](https://github.com/vite-pwa/docs/blob/main/frameworks/sveltekit.md).

### 1.5 Cache Versioning and Cleanup

Use the `version` from `$service-worker` to generate unique cache names. On `activate`, delete old caches:

```javascript
const CACHE = `dcs-cache-${version}`;
// In activate event:
const keys = await caches.keys();
for (const key of keys) {
	if (key !== CACHE) await caches.delete(key);
}
```

---

## 2. Static JSON Data Caching Approach

### 2.1 Data Architecture

The app's sole data source is `src/lib/data/services.json` (~540 lines, ~3.1.0 version). This file is:

- Served as a static asset from GitHub Pages
- Imported by `+page.server.ts` and `src/lib/index.ts`
- Contains `version`, `lastUpdated`, `lastVerified`, `lastScraped` metadata fields
- Structure: `ServicesData` with `services: ServiceLocation[]` and `metadata` object

### 2.2 Caching Approach: Cache API with Stale-While-Revalidate

Since all data is static JSON, the strategy is:

1. **Precache `services.json`** during service worker installation (via `workbox.precaching`).
2. **Use StaleWhileRevalidate** for runtime requests to `services.json`. This ensures:
   - Users see data immediately (even on first load after install, the precached version is used)
   - Background fetch updates the cache for the next visit
   - No loading spinner for data on subsequent visits

3. **Cache the JSON in two layers:**
   - **HTTP Cache:** Set `Cache-Control: max-age=3600` on the JSON file via GitHub Pages headers (`.nojekyll` + custom headers) to leverage browser HTTP caching.
   - **Cache API:** Workbox `StaleWhileRevalidate` stores the JSON in a named cache (`data-json`) with expiration.

### 2.3 Data Size Considerations

- The `services.json` file is a single request containing all service locations (~500+ entries). This is acceptable for a single-cache approach.
- If the file grows beyond ~500KB, consider splitting by category or region to allow selective caching.
- For now, the monolithic JSON is appropriate given it's a small directory.

### 2.4 Import vs. Fetch

The app currently imports JSON directly (`import services from '$lib/data/services.json'`). For offline support, two modes are needed:

- **Online:** The JSON can be imported at build time (for the initial page render) AND fetched at runtime for the freshest data.
- **Offline:** The service worker serves the cached `services.json`. The app should detect offline mode and read from the cache rather than relying on the server-side import.

**Implementation:**

```typescript
// In +page.server.ts or client-side load function:
export async function load() {
	// Try fetching fresh data; fall back to cached import
	try {
		const response = await fetch('/services.json');
		if (response.ok) return { services: await response.json(), source: 'network' };
	} catch {
		// Offline — use the build-time imported data
		return { services: servicesData.services, source: 'cache' };
	}
}
```

---

## 3. Offline Fallback Page Design

### 3.1 Requirements

Per [web.dev: Create an offline fallback page](https://web.dev/articles/offline-fallback-page) and [MDN: PWA Best Practices](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Best_practices):

- Must be a self-contained HTML page cached during service worker installation
- Must be served when navigation requests fail and no cached page is available
- Must inform the user they are offline with actionable information
- Must be accessible (screen reader compatible, large text, semantic HTML)

### 3.2 Page Content

The offline page for Dublin City Support Services should include:

1. **Clear status message:** "You're currently offline" — using plain, action-based language, not technical jargon [web.dev offline UX guidelines](https://web.dev/articles/offline-ux-design-guidelines)
2. **What's still available:** A brief list of features that work offline (e.g., "View saved services, hours, and contact information")
3. **Auto-reconnect:** JavaScript listening for `window.addEventListener('online', ...)` to reload automatically
4. **Manual reload button:** For users who want to retry immediately
5. **Emergency contact information:** Since this serves vulnerable populations, include Dublin-specific emergency numbers
6. **Branded styling:** Use the app's theme color (`#1a73e8`)

### 3.3 Accessibility Requirements for Offline Page

- `<h1>` heading with clear status
- `lang="en"` attribute on `<html>`
- Sufficient color contrast (WCAG AA: 4.5:1 for normal text, 3:1 for large text)
- All interactive elements keyboard-navigable
- ARIA live regions to announce status changes
- Inline styles (no external CSS dependency) to ensure it loads when offline

### 3.4 Workbox Integration

Using Workbox's offline fallback recipe:

```javascript
import { registerRoute, Route } from 'workbox-routing';
import { NetworkOnly } from 'workbox-strategies';
import { PrecacheFallbackPlugin } from 'workbox-recipes';
import { precacheAndRoute } from 'workbox-precaching';

precacheAndRoute(self.__WB_MANIFEST);

const networkOnlyNavigationRoute = new Route(
	({ request }) => request.mode === 'navigate',
	new NetworkOnly({
		plugins: [
			new PrecacheFallbackPlugin({
				fallbackURL: '/offline.html'
			})
		]
	})
);

registerRoute(networkOnlyNavigationRoute);
```

### 3.5 Offline Page Data Content

Since this is a social services directory, the offline page should include a curated list of **critical 24/7 services** (e.g., emergency shelters, crisis lines) that are always relevant. These should be embedded in the page or precached as a separate JSON:

```html
<!-- In offline.html -->
<section aria-label="Emergency services">
	<h2>Emergency Contacts</h2>
	<ul>
		<li>Emergency Services: 999</li>
		<li>HSE Mental Health: 111</li>
		<li>Peter McVerry Trust: 1890 253 727</li>
		<!-- ... -->
	</ul>
</section>
```

---

## 4. Data Freshness Strategy

### 4.1 The Problem

Without a backend, there's no server-side timestamp negotiation. The service worker cannot check `If-Modified-Since` or `ETag` headers against a dynamic origin. The challenge: **how does the app know if cached JSON data is stale?**

### 4.2 Available Metadata Fields

The `services.json` file already contains:

| Field               | Description                     | Use Case                             |
| ------------------- | ------------------------------- | ------------------------------------ |
| `version`           | Semver string (e.g., `"3.1.0"`) | Detect structural data changes       |
| `lastUpdated`       | ISO 8601 timestamp              | Know when data was last generated    |
| `lastVerified`      | Date string per service         | Know when each location was verified |
| `lastScraped`       | ISO 8601 per service            | Know when each entry was scraped     |
| `metadata.nextSync` | Scheduled pipeline run          | Tell users when data will be updated |

### 4.3 Freshness Strategy: Version-Based + Time-Based

**Strategy A: Version comparison on network fetch**

When the service worker revalidates `services.json` in the background:

1. Fetch the current `services.json` from the network
2. Compare the `version` field with the cached version
3. If versions differ → cache is stale, update cache, notify user
4. If versions match → cache is current, no action needed

**Strategy B: Time-based staleness indicator**

In the UI, calculate staleness relative to `lastUpdated`:

```typescript
const lastUpdated = new Date(data.lastUpdated);
const now = new Date();
const hoursSinceUpdate = (now.getTime() - lastUpdated.getTime()) / (1000 * 60 * 60);

// Display appropriate freshness indicator
// < 24h: "Updated today"
// < 7 days: "Updated {days} ago"
// > 7 days: "Last updated {date}"
```

**Strategy C: Manifest-based update detection**

The `@vite-pwa/sveltekit` plugin supports `registerType: 'prompt'` which shows a banner when new content is available. This leverages the service worker's built-in update detection (byte-difference in the SW script). Combined with version comparison of the JSON data, this gives a two-layer freshness signal:

- **SW update** → App shell changed → Full reload recommended
- **Data update** → `version` changed → New data available in cache

### 4.4 Implementation Pattern

```typescript
// In the service worker (runtime caching callback):
import { StaleWhileRevalidate } from 'workbox-strategies';

const dataStrategy = new StaleWhileRevalidate({
	cacheName: 'data-json',
	plugins: [
		{
			cachedResponseWillBeUsed: async ({ cachedResponse, request }) => {
				if (!cachedResponse) return cachedResponse;
				const cachedData = await cachedResponse.clone().json();
				// Store cached version for comparison
				self.__cachedVersion = cachedData.version;
				return cachedResponse;
			},
			networkResponseWillBeUsed: async ({ networkResponse }) => {
				const networkData = await networkResponse.clone().json();
				if (self.__cachedVersion && networkData.version !== self.__cachedVersion) {
					// Data has changed — broadcast to clients
					const clients = await self.clients.matchAll();
					clients.forEach((client) => {
						client.postMessage({
							type: 'DATA_UPDATE',
							version: networkData.version,
							lastUpdated: networkData.lastUpdated
						});
					});
				}
				return networkResponse;
			}
		}
	]
});
```

### 4.5 User-Facing Freshness Communication

The UI should always show:

- **Last updated date** from `services.lastUpdated`
- **Staleness indicator** (e.g., "Data last updated 2 days ago")
- **Next sync date** from `metadata.nextSync`
- **Visual cue** when new data is available (toast notification via service worker `message` event)

Per [web.dev offline UX design guidelines](https://web.dev/articles/offline-ux-design-guidelines): "Be clear about what options you're providing. Show the last time they were updated."

---

## 5. Low-Data Mode Implementation

### 5.1 Design Philosophy

Low-data mode must minimize:

- Total bytes transferred over the network
- Number of network requests
- Background sync activity
- Unnecessary resource loading

For users experiencing homelessness who may be on limited data plans or unreliable connections, this is critical. Per [web.dev offline UX design guidelines](https://web.dev/articles/offline-ux-design-guidelines): "If your app doesn't require much data, then cache that data by default. Users can become increasingly frustrated if they can only access their data with a network connection."

### 5.2 Implementation Layers

**Layer 1: Service Worker — Cached-Only Mode**

Add a `lowData` mode that switches all strategies to `CacheOnly` or `CacheFirst`:

```typescript
// Detect low-data mode from user preference or network condition
const isLowData =
	localStorage.getItem('lowDataMode') === 'true' ||
	(navigator.connection && navigator.connection.saveData);

// In service worker fetch handler:
if (isLowData) {
	// Serve everything from cache, no network requests
	const cached = await cache.match(request);
	if (cached) return cached;
	return new Response('Offline content unavailable', { status: 503 });
}
```

**Layer 2: Minimal Service Worker Footprint**

- The generated service worker should be as small as possible
- `@vite-pwa/sveltekit` with `generateSW` strategy produces a minimal Workbox runtime
- Avoid unnecessary plugins (e.g., Background Sync, Push)
- Keep the service worker script under 10KB

**Layer 3: Data Minimization**

- Serve only the JSON fields needed for the current view (e.g., map view needs lat/lng/name/address; detail view needs full record)
- Consider creating a `services-compact.json` for low-data mode with only essential fields
- Precache only the compact JSON; fetch full data only on Wi-Fi

```json
// services-compact.json structure
{
	"version": "3.1.0",
	"lastUpdated": "2026-09-13T09:53:39.731Z",
	"services": [
		{
			"id": "capuchin-day-centre",
			"name": "Capuchin Day Centre",
			"latitude": 53.3481,
			"longitude": -6.2758,
			"category": "Emergency Shelter",
			"tags": ["food", "medical"]
		}
	]
}
```

**Layer 4: Network Information API Detection**

Automatically enable low-data mode when the browser reports expensive connectivity:

```javascript
if ('connection' in navigator) {
	const conn = navigator.connection;
	if (conn.saveData || conn.effectiveType === '2g' || conn.effectiveType === 'slow-2g') {
		enableLowDataMode();
	}
}
```

**Layer 5: User-Controlled Toggle**

Provide a visible toggle in the app UI:

- "Low data mode" switch in settings
- When enabled: cache-only, no background updates, compact data, reduced animations
- When disabled: normal stale-while-revalidate behavior

### 5.3 Low-Data Mode Behavior Matrix

| Feature             | Normal Mode          | Low-Data Mode                      |
| ------------------- | -------------------- | ---------------------------------- |
| JSON caching        | StaleWhileRevalidate | CacheOnly                          |
| Map tiles           | CacheFirst           | CacheOnly                          |
| Background updates  | Enabled              | Disabled                           |
| Data payload        | Full JSON            | Compact JSON                       |
| Animations          | Enabled              | Disabled                           |
| Offline page        | Standard             | Standard (with emergency contacts) |
| Service worker size | Full Workbox         | Minimal Workbox                    |
| Network requests    | All allowed          | Cache only                         |

---

## 6. Accessibility Considerations for Offline Mode

### 6.1 WCAG Compliance Context

The app serves vulnerable populations including people experiencing homelessness, people with disabilities, and those with limited digital literacy. Must comply with [WCAG 2.1 Level AA](https://www.w3.org/TR/WCAG21/) (and ideally [WCAG 2.2](https://www.w3.org/TR/WCAG22/)) [W3C WAI](https://www.w3.org/WAI/standards-guidelines/wcag).

### 6.2 Large Text Support

**Current state:** The `app.html` already has `<meta name="text-scale" content="scale">` which indicates intent for text scaling support.

**Requirements:**

- All text must be resizable up to 200% without loss of content or functionality (WCAG 1.4.4 Resize Text, Level AA)
- Use relative units (`rem`, `em`) for all font sizes — avoid `px`
- Ensure line-height is at least 1.5 for body text (WCAG 1.4.12, Level AA)
- Touch targets must be at least 44×44px (WCAG 2.5.8, Level AA in 2.2)

**Implementation for offline mode:**

- The offline fallback page must use the same CSS relative units
- CSS `clamp()` for responsive font sizing that respects user preferences
- Ensure the offline page's emergency contact information is prominent and large enough to read

```css
/* Base accessibility styles */
html {
	font-size: 100%; /* Respects browser default (usually 16px) */
}

body {
	font-size: 1rem;
	line-height: 1.6;
}

h1 {
	font-size: clamp(1.5rem, 4vw, 2.5rem);
}
h2 {
	font-size: clamp(1.25rem, 3vw, 2rem);
}

/* High contrast mode support */
@media (prefers-contrast: high) {
	body {
		background: #000;
		color: #fff;
	}
	a {
		color: #ffff00;
	}
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
	* {
		animation: none;
		transition: none;
	}
}
```

### 6.3 Screen Reader Accessibility

**Offline page must be screen-reader friendly:**

- Semantic HTML structure (`<main>`, `<section>`, `<ul>`, `<h1>`-`<h3>`)
- All images must have `alt` text (or be decorative with `alt=""`)
- ARIA live regions for status updates when connectivity changes
- Skip navigation link for keyboard users

```html
<!-- Offline page accessibility markup -->
<a href="#main-content" class="skip-link">Skip to main content</a>
<main id="main-content" role="main" aria-label="Offline mode">
	<h1>You're currently offline</h1>
	<p aria-live="polite">Your saved Dublin support services are available.</p>
	<section aria-label="Emergency contacts">
		<h2>Emergency Contacts</h2>
		<!-- ... -->
	</section>
</main>
```

**Service worker broadcast for accessibility:**
When the service worker detects a data update or connection change, broadcast via `clients.matchAll()` and update ARIA live regions:

```javascript
// In service worker:
self.addEventListener('message', (event) => {
	if (event.data.type === 'DATA_UPDATE') {
		// Clients update their ARIA live region
	}
});

// In the app:
navigator.serviceWorker.addEventListener('message', (event) => {
	if (event.data.type === 'DATA_UPDATE') {
		const liveRegion = document.getElementById('status-announcer');
		if (liveRegion) {
			liveRegion.textContent = `Service directory updated to version ${event.data.version}`;
		}
	}
});
```

### 6.4 Color and Contrast

- Minimum contrast ratio: **4.5:1** for normal text, **3:1** for large text (WCAG 1.4.3, 1.4.6)
- Do not rely on color alone to indicate state (e.g., offline vs. online) — use icons, labels, and text [web.dev offline UX guidelines](https://web.dev/articles/offline-ux-design-guidelines): "Using only color to show state can be hard for users to notice, or even completely inaccessible"
- Support `prefers-color-scheme` for dark mode
- Support `prefers-contrast: high` for high-contrast mode

### 6.5 Keyboard and Touch Accessibility

- All interactive elements reachable via Tab key
- Focus indicators clearly visible (`:focus-visible`)
- Touch targets minimum 44×44px
- No hover-only interactions (critical for offline mode where some devices may not have hover)

### 6.6 Cognitive Accessibility

For users experiencing homelessness who may have cognitive disabilities or limited digital literacy:

- Use plain, action-based language (not "service worker" or "cache")
- Consistent navigation across online and offline modes
- Progressive disclosure — show essential info first, details on demand
- Emergency information always visible without scrolling
- Error messages should be constructive: "You're offline — here's what you can still do" not "Connection failed"

### 6.7 Offline-Specific Accessibility Checklist

| Requirement                   | WCAG Success Criterion | Implementation                         |
| ----------------------------- | ---------------------- | -------------------------------------- |
| Text resizable to 200%        | 1.4.4 (AA)             | Relative units, no fixed widths        |
| Color contrast ≥ 4.5:1        | 1.4.3 (AA)             | Theme verification, `prefers-contrast` |
| Screen reader announcements   | 4.1.3 (AA)             | ARIA live regions, semantic HTML       |
| Keyboard navigation           | 2.1.1 (A)              | All interactive elements focusable     |
| Skip navigation link          | 2.4.1 (A)              | Skip link in offline page              |
| Language declared             | 3.1.1 (A)              | `lang="en"` on offline page            |
| Error identification          | 3.3.1 (A)              | Clear offline status messaging         |
| Consistent navigation         | 3.2.3 (AA)             | Same layout online and offline         |
| Time-based media alternatives | 1.2 (A)                | N/A (static text content)              |

---

## Implementation Priority

Given the critical nature of this service for vulnerable populations, implementation should follow this priority order:

1. **P0 — Critical:** Service worker precaching + offline fallback page + JSON caching
2. **P0 — Critical:** Data freshness indicators in the UI
3. **P1 — High:** Low-data mode toggle + Network Information API detection
4. **P1 — High:** Screen reader support + keyboard navigation in offline page
5. **P2 — Medium:** Large text / responsive typography enhancements
6. **P2 — Medium:** BroadcastChannel data update notifications
7. **P3 — Nice to have:** Compact JSON payloads, Background Sync for future server connectivity

---

## Sources

- [Workbox Caching Strategies Overview](https://developer.chrome.com/docs/workbox/caching-strategies-overview/)
- [web.dev: Service Worker Caching and HTTP Caching](https://web.dev/articles/service-worker-caching-and-http-caching)
- [web.dev: Create an Offline Fallback Page](https://web.dev/articles/offline-fallback-page)
- [web.dev: Offline UX Design Guidelines](https://web.dev/articles/offline-ux-design-guidelines)
- [MDN: PWA Best Practices](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Best_practices)
- [MDN: PWA Caching](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Caching)
- [SvelteKit Service Workers Documentation](https://svelte.dev/docs/kit/service-workers)
- [vite-pwa/sveltekit Documentation](https://github.com/vite-pwa/docs/blob/main/frameworks/sveltekit.md)
- [WCAG 2.1 W3C Recommendation](https://www.w3.org/TR/WCAG21/)
- [WCAG 2.2 W3C Recommendation](https://www.w3.org/TR/WCAG22/)
- [Google Chrome Workbox Strategies](https://developer.chrome.com/docs/workbox/modules/workbox-strategies)
