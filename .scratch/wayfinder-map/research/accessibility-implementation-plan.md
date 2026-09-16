# Accessibility Implementation Plan — Dublin City Support Services PWA

**Task:** 08 — Implement accessibility features  
**Framework:** SvelteKit (confirmed via framework recommendation research)  
**Date:** 2026-09-14  
**Status:** Research complete — ready for agent implementation

---

## Table of Contents

1. [Overview & Architecture Context](#1-overview--architecture-context)
2. [Acceptance Criterion 1: Offline Mode with Cached Data Display](#2-acceptance-criterion-1-offline-mode-with-cached-data-display)
3. [Acceptance Criterion 2: Large Text Mode (Configurable Font Sizes)](#3-acceptance-criterion-2-large-text-mode-configurable-font-sizes)
4. [Acceptance Criterion 3: Low-Data Mode (Minimal Network Usage, Cached-First)](#4-acceptance-criterion-3-low-data-mode-minimal-network-usage-cached-first)
5. [Acceptance Criterion 4: Screen Reader Support](#5-acceptance-criterion-4-screen-reader-support)
6. [Acceptance Criterion 5: Intuitive Navigation](#6-acceptance-criterion-5-intuitive-navigation)
7. [Integration with Existing Offline Strategy & PWA Framework](#7-integration-with-existing-offline-strategy--pwa-framework)
8. [Testing & QA Checklist](#8-testing--qa-checklist)
9. [Implementation Priority & Timeline](#9-implementation-priority--timeline)

---

## 1. Overview & Architecture Context

The Dublin City Support Services PWA uses **SvelteKit** with `@vite-pwa/sveltekit`, `@sveltejs/adapter-static`, and `@vite-pwa/sveltekit` for service worker generation. The app serves a vulnerable population (people experiencing homelessness, low digital literacy, varying disabilities) and must be accessible under intermittent connectivity, constrained data plans, and diverse device capabilities.

**Key existing assets:**

- `vite.config.ts` — Workbox runtime caching for OSM tiles/API only (needs expansion)
- `svelte.config.js` — `@sveltejs/adapter-static` with `fallback: 'index.html'`, prerender entries `['*']`
- `src/app.html` — Has `<meta name="text-scale" content="scale">` but lacks full a11y markup
- `src/lib/data/services.json` — ~540 lines, version 3.1.0, contains service metadata
- `src/routes/` — Existing routes: `+page.svelte`, `+page.server.ts`, `map/+page.svelte`, `search/+page.svelte`, `service/[id]/+page.svelte`, `+layout.svelte`

**Strategy:** Cache-first, offline-first architecture per the offline-strategy research. All five accessibility features build on top of the existing SvelteKit + Workbox stack. No framework switch is needed or recommended.

---

## 2. Acceptance Criterion 1: Offline Mode with Cached Data Display

### 2.1 Service Worker Configuration Expansion

The existing `vite.config.ts` needs expanded `runtimeCaching` rules per the offline-strategy research.

**File: `vite.config.ts`** — Add the following runtime caching rules:

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
					maxAgeSeconds: 30 * 24 * 60 * 60
				},
				cacheableResponse: { statuses: [0, 200] }
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
					maxAgeSeconds: 7 * 24 * 60 * 60
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
					maxAgeSeconds: 1 * 24 * 60 * 60
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

**File: `svelte.config.js`** — Enable version-based cache invalidation:

```javascript
export default {
	compilerOptions: {/* existing */},
	kit: {
		adapter: adapter({ strict: false, fallback: 'index.html' }),
		prerender: { entries: ['*'], handleUnseenRoutes: 'ignore' },
		includeVersionFile: true
	}
};
```

### 2.2 Offline Fallback Page

**File: `src/routes/offline/+page.svelte`** — Create an accessible offline page:

- Self-contained HTML with inline styles (no external CSS dependency)
- `<h1>` heading with "You're currently offline"
- `lang="en"` on the page
- ARIA live regions for status announcements
- Skip navigation link
- Emergency contacts section (hardcoded critical 24/7 services)
- Auto-reconnect listener via `window.addEventListener('online', ...)`
- Manual reload button
- Visible connectivity status with high-contrast icon + text label

**Svelte component pattern:**

```svelte
<script>
	import { onMount } from 'svelte';
	let online = navigator.onLine;
	onMount(() => {
		window.addEventListener('online', () => {
			online = true;
		});
		window.addEventListener('offline', () => {
			online = false;
		});
	});
</script>

<a href="#main-content" class="skip-link">Skip to main content</a>
<main id="main-content" role="main" aria-label="Offline mode">
	<h1>You're currently offline</h1>
	<p aria-live="polite">
		{#if online}
			Reconnecting... Your saved Dublin support services are available.
		{:else}
			Showing cached data from {lastUpdated}. Essential services are still available.
		{/if}
	</p>
	<section aria-label="Emergency contacts">
		<h2>Emergency Contacts</h2>
		<ul>
			<li>Emergency Services: 999</li>
			<li>HSE Mental Health: 111</li>
			<li>Peter McVerry Trust: 1890 253 727</li>
		</ul>
	</section>
	<button on:click={() => window.location.reload()}>Try Again</button>
</main>
```

### 2.3 Load Function — Offline-First Data Strategy

**File: `src/routes/+page.server.ts`** — Implement the load function with offline fallback:

```typescript
import servicesData from '$lib/data/services.json';

export async function load({ fetch }) {
	try {
		const response = await fetch('/services.json');
		if (response.ok) {
			const data = await response.json();
			return { services: data.services, source: 'network', lastUpdated: data.lastUpdated };
		}
	} catch {
		// Offline — use build-time imported data
		return {
			services: servicesData.services,
			source: 'cache',
			lastUpdated: servicesData.lastUpdated
		};
	}
}
```

**File: `src/routes/+page.svelte`** — Display connectivity status badge:

```svelte
<script>
	import { onMount } from 'svelte';
	export let data;
	let online = navigator.onLine;
	onMount(() => {
		window.addEventListener('online', () => {
			online = true;
		});
		window.addEventListener('offline', () => {
			online = false;
		});
	});
</script>

<div class="connectivity-badge" aria-live="polite" role="status">
	{#if online}
		<span class="icon" aria-hidden="true">●</span> Online
	{:else}
		<span class="icon" aria-hidden="true">○</span> Offline — showing cached data
	{/if}
</div>
```

### 2.4 Data Freshness Indicator

Add a staleness indicator to every service list page using the `lastUpdated` metadata:

```svelte
<script>
	function getStaleness(lastUpdated) {
		const hours = (Date.now() - new Date(lastUpdated).getTime()) / (1000 * 60 * 60);
		if (hours < 24) return 'Updated today';
		if (hours < 168) return `Updated ${Math.floor(hours / 24)} day(s) ago`;
		return `Last updated ${new Date(lastUpdated).toLocaleDateString()}`;
	}
</script>

<p class="staleness-indicator" aria-label={`Data freshness: ${getStaleness(data.lastUpdated)}`}>
	{getStaleness(data.lastUpdated)}
</p>
```

### 2.5 Service Worker Data Update Broadcast

**File: `src/service-worker.js`** — Remove SvelteKit module references and add data update broadcasting:

```javascript
/// <reference types="workbox" />
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { StaleWhileRevalidate, NetworkFirst } from 'workbox-strategies';
import { PrecacheFallbackPlugin } from 'workbox-recipes';

precacheAndRoute(self.__WB_MANIFEST);

// Data update broadcast
const dataStrategy = new StaleWhileRevalidate({
	cacheName: 'data-json',
	plugins: [
		{
			networkResponseWillBeUsed: async ({ networkResponse }) => {
				const networkData = await networkResponse.clone().json();
				const clients = await self.clients.matchAll();
				clients.forEach((client) => {
					client.postMessage({
						type: 'DATA_UPDATE',
						version: networkData.version,
						lastUpdated: networkData.lastUpdated
					});
				});
				return networkResponse;
			}
		}
	]
});

registerRoute(/\/services\.json/, dataStrategy);

registerRoute(
	({ request }) => request.mode === 'navigate',
	new NetworkFirst({
		cacheName: 'pages',
		networkTimeoutSeconds: 3,
		plugins: [new PrecacheFallbackPlugin({ fallbackURL: '/offline' })]
	})
);

self.addEventListener('message', (event) => {
	if (event.data.type === 'SKIP_WAITING') self.skipWaiting();
});
```

**Client-side listener** (`src/routes/+layout.svelte`):

```svelte
<script>
	import { onMount } from 'svelte';
	onMount(() => {
		navigator.serviceWorker.addEventListener('message', (event) => {
			if (event.data.type === 'DATA_UPDATE') {
				const liveRegion = document.getElementById('status-announcer');
				if (liveRegion) {
					liveRegion.textContent = `Service directory updated to version ${event.data.version}`;
				}
			}
		});
	});
</script>

<div id="status-announcer" aria-live="assertive" aria-atomic="true" class="sr-only"></div>
```

---

## 3. Acceptance Criterion 2: Large Text Mode (Configurable Font Sizes)

### 3.1 CSS Architecture for Text Scaling

All font sizes must use relative units (`rem`, `em`) — never `px`. The app.html already has `<meta name="text-scale" content="scale">`.

**File: `src/app.css`** (or global styles) — Add accessibility-focused CSS:

```css
/* Base typography — respects browser default (16px) */
html {
	font-size: 100%;
	-webkit-text-size-adjust: 100%;
	text-size-adjust: 100%;
}

body {
	font-size: 1rem;
	line-height: 1.6;
	min-height: 100vh;
}

/* Heading scales using clamp() for responsive sizing */
h1 {
	font-size: clamp(1.5rem, 4vw, 2.5rem);
	line-height: 1.3;
}
h2 {
	font-size: clamp(1.25rem, 3vw, 2rem);
	line-height: 1.3;
}
h3 {
	font-size: clamp(1.1rem, 2.5vw, 1.5rem);
	line-height: 1.4;
}

/* Body text minimum 1rem, scales with user preferences */
p,
li,
td,
th {
	font-size: 1rem;
	line-height: 1.6;
}

/* Large text mode — user-configurable via data attribute */
html[data-text-scale='large'] {
	font-size: 125%;
}

html[data-text-scale='x-large'] {
	font-size: 150%;
}

html[data-text-scale='xx-large'] {
	font-size: 200%;
}

/* Ensure touch targets scale with text */
button,
a,
[role='button'] {
	min-width: 48px;
	min-height: 48px;
	padding: 0.5em 1em;
}

/* Focus indicators */
:focus-visible {
	outline: 3px solid #1a73e8;
	outline-offset: 2px;
}

/* Skip link */
.skip-link {
	position: absolute;
	top: -100%;
	left: 0;
	background: #1a73e8;
	color: white;
	padding: 1rem;
	z-index: 1000;
	font-size: 1rem;
}
.skip-link:focus {
	top: 0;
}
```

### 3.2 Text Scale Toggle Component

**File: `src/lib/components/TextScaleToggle.svelte`** — Accessible font size control:

```svelte
<script>
	export let currentScale = 'medium';

	const scales = [
		{ key: 'small', label: 'Small text', icon: 'A−' },
		{ key: 'medium', label: 'Medium text', icon: 'A' },
		{ key: 'large', label: 'Large text', icon: 'A+' },
		{ key: 'x-large', label: 'Extra large text', icon: 'A++' }
	];

	function setScale(scale) {
		document.documentElement.setAttribute('data-text-scale', scale);
		localStorage.setItem('textScale', scale);
		currentScale = scale;
	}

	onMount(() => {
		const saved = localStorage.getItem('textScale');
		if (saved) setScale(saved);
	});
</script>

<div class="text-scale-group" role="radiogroup" aria-label="Text size">
	{#each scales as scale}
		<button
			role="radio"
			aria-checked={currentScale === scale.key}
			aria-label={scale.label}
			on:click={() => setScale(scale.key)}
			class:active={currentScale === scale.key}
		>
			{scale.icon}
		</button>
	{/each}
</div>
```

### 3.3 Accessibility Settings Persistence

Store accessibility preferences in `localStorage` and apply on page load via `+layout.svelte`:

```svelte
<script>
	import { onMount } from 'svelte';
	onMount(() => {
		const textScale = localStorage.getItem('textScale') || 'medium';
		const lowData = localStorage.getItem('lowDataMode') === 'true';
		const highContrast = localStorage.getItem('highContrast') === 'true';
		document.documentElement.setAttribute('data-text-scale', textScale);
		document.documentElement.setAttribute('data-low-data', lowData.toString());
		document.documentElement.setAttribute('data-high-contrast', highContrast.toString());
	});
</script>
```

### 3.4 High Contrast Mode

```css
/* System high contrast */
@media (prefers-contrast: high) {
	html[data-high-contrast='true'],
	:root:has(:checked) {
		--bg: #000;
		--fg: #fff;
		--accent: #ffff00;
	}
	body {
		background: var(--bg);
		color: var(--fg);
	}
	a {
		color: var(--accent);
	}
	button {
		border: 2px solid var(--accent);
	}
}

/* Manual toggle also applies the same CSS variables */
html[data-high-contrast='true'] {
	--bg: #000;
	--fg: #fff;
	--accent: #ffff00;
}
```

### 3.5 Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
	html {
		scroll-behavior: auto;
	}
	*,
	*::before,
	*::after {
		animation-duration: 0.01ms !important;
		animation-iteration-count: 1 !important;
		transition-duration: 0.01ms !important;
		scroll-behavior: auto !important;
	}
}
```

---

## 4. Acceptance Criterion 3: Low-Data Mode (Minimal Network Usage, Cached-First)

### 4.1 Service Worker Low-Data Mode

**File: `src/service-worker.js`** — Add low-data mode detection and CacheOnly strategy:

```javascript
// Detect low-data mode from Cache API or broadcast
const LOW_DATA_KEY = 'lowDataMode';

async function isLowDataMode() {
	// Check client preferences via IndexedDB or Cache API
	// Also check Network Information API
	if ('connection' in navigator) {
		const conn = navigator.connection;
		if (conn.saveData || conn.effectiveType === '2g' || conn.effectiveType === 'slow-2g') {
			return true;
		}
	}
	return false;
}

// Low-data handler: serve everything from cache only
const lowDataHandler = {
	handler: 'CacheOnly',
	options: {
		cacheName: 'data-json',
		matchOptions: { ignoreSearch: true }
	}
};
```

**Alternative: Strategy switching at runtime based on mode:**

```javascript
// In service worker fetch handler
self.addEventListener('fetch', (event) => {
	if (event.request.url.includes('/services.json')) {
		if (await isLowDataMode()) {
			event.respondWith(caches.match('/services.json'));
		} else {
			event.respondWith(
				(new StaleWhileRevalidate({ cacheName: 'data-json' })).handle(event.request)
			);
		}
	}
});
```

### 4.2 Network Information API Detection

**File: `src/lib/lowData.ts`** — Utility for detecting and managing low-data mode:

```typescript
export function detectLowData(): boolean {
	if (!('connection' in navigator)) return false;
	const conn = navigator.connection as NetworkInformation;
	return conn.saveData || conn.effectiveType === '2g' || conn.effectiveType === 'slow-2g';
}

export function getEffectiveConnectionType(): string {
	if (!('connection' in navigator)) return 'unknown';
	return (navigator.connection as NetworkInformation).effectiveType;
}
```

### 4.3 User-Controlled Toggle

**File: `src/lib/components/LowDataToggle.svelte`** — Settings toggle:

```svelte
<script>
	export let enabled = false;

	function toggle() {
		enabled = !enabled;
		localStorage.setItem('lowDataMode', enabled.toString());
		document.documentElement.setAttribute('data-low-data', enabled.toString());
		// Notify service worker
		if (navigator.serviceWorker.controller) {
			navigator.serviceWorker.controller.postMessage({
				type: 'LOW_DATA_TOGGLE',
				enabled
			});
		}
	}
</script>

<label class="low-data-toggle">
	<input type="checkbox" bind:checked={enabled} on:change={toggle} />
	<span>Low data mode</span>
	<p class="hint">Reduces data usage by loading only cached content</p>
</label>
```

### 4.4 Compact JSON for Low-Data Mode

Create `src/lib/data/services-compact.json` — Only essential fields (id, name, latitude, longitude, category, tags):

```json
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
			"tags": ["food", "medical"],
			"phone": "+353-1-878-0404"
		}
	]
}
```

Load compact vs full data based on mode in `+page.server.ts`:

```typescript
import servicesData from '$lib/data/services.json';
import compactData from '$lib/data/services-compact.json';

export async function load({ fetch, url }) {
	const isLowData = localStorage.getItem('lowDataMode') === 'true';
	const source = isLowData ? compactData : servicesData;
	// ... rest of load logic
}
```

### 4.5 Low-Data Mode Behavior Matrix (Implementation Reference)

| Feature            | Normal Mode          | Low-Data Mode            | Implementation                 |
| ------------------ | -------------------- | ------------------------ | ------------------------------ |
| JSON caching       | StaleWhileRevalidate | CacheOnly                | Service worker strategy switch |
| Map tiles          | CacheFirst           | CacheOnly                | Service worker strategy switch |
| Background updates | Enabled              | Disabled                 | Remove background sync         |
| Data payload       | Full JSON            | Compact JSON             | Conditional import             |
| Animations         | Enabled              | Disabled                 | CSS `data-low-data` attribute  |
| Images             | Full WebP            | No images / placeholders | CSS `data-low-data` attribute  |
| Network requests   | All allowed          | Cache only               | Service worker                 |

### 4.6 CSS for Low-Data Mode

```css
html[data-low-data='true'] {
	/* Disable all images */
	img {
		display: none;
	}
	/* Disable animations */
	*,
	*::before,
	*::after {
		animation: none !important;
		transition: none !important;
	}
	/* Remove background images */
	*[style*='background-image'] {
		background-image: none !important;
	}
}
```

---

## 5. Acceptance Criterion 4: Screen Reader Support

### 5.1 Semantic HTML Structure

Every page must have proper heading hierarchy, landmarks, and ARIA attributes.

**File: `src/routes/+layout.svelte`** — Add skip navigation and status announcer:

```svelte
<script>
	import '../app.css';
	export let data;
</script>

<a href="#main-content" class="skip-link">Skip to main content</a>
<div id="status-announcer" aria-live="assertive" aria-atomic="true" class="sr-only"></div>
<div id="polite-announcer" aria-live="polite" aria-atomic="true" class="sr-only"></div>

<header role="banner">
	<h1>Dublin City Support</h1>
	<nav aria-label="Main navigation">
		<!-- Tab bar navigation -->
	</nav>
</header>

<main id="main-content" role="main" aria-label="Content">
	<slot />
</main>

<footer role="contentinfo">
	<!-- Emergency button always visible -->
</footer>
```

### 5.2 Screen Reader-Optimized Service Cards

**File: `src/lib/components/ServiceCard.svelte`** — Group all information into a single semantic unit:

```svelte
<script>
	export let service;
</script>

<article
	class="service-card"
	aria-label="{service.name}, {service.category}, {service.status}, {service.distance} away"
	role="listitem"
>
	<div class="service-icon" aria-hidden="true">
		<!-- Category icon, decorative -->
	</div>
	<div class="service-info">
		<h2>{service.name}</h2>
		<p class="category">{service.category}</p>
		<p class="status" aria-label="Status: {service.status}">{service.status}</p>
		<p class="distance" aria-label="Distance: {service.distance}">{service.distance}</p>
	</div>
	<a href="/service/{service.id}" aria-label="Get directions to {service.name}"> Get Directions </a>
</article>
```

### 5.3 Screen Reader-Optimized Search Results

**File: `src/routes/search/+page.svelte`** — Live region announcements:

```svelte
<script>
	export let results = [];
</script>

<div aria-live="polite" aria-atomic="true">
	{#if results.length > 0}
		<p>Showing {results.length} services found.</p>
	{:else}
		<p>No services found. Try a different category or check nearby.</p>
	{/if}
</div>

<ul role="list" aria-label="Search results">
	{#each results as service}
		<li>
			<article aria-label="{service.name}, {service.category}, {service.status}">
				<h3>{service.name}</h3>
				<p>{service.category}</p>
				<p>{service.status}</p>
			</article>
		</li>
	{/each}
</ul>
```

### 5.4 Map Marker Accessibility

**File: `src/routes/map/+page.svelte`** — Accessible map markers:

```svelte
<script>
	import { onMount } from 'svelte';
	export let services = [];

	let map;
	let markers = [];

	onMount(() => {
		// Initialize Leaflet map
		// For each service, create a marker with accessible tooltip
		services.forEach((service) => {
			const marker = L.marker([service.latitude, service.longline], {
				alt: `${service.name}, ${service.category}, ${service.status}`
			}).addTo(map);
			marker.bindPopup(
				`
				<h2>${service.name}</h2>
				<p>${service.category}</p>
				<p>Status: ${service.status}</p>
				<p>${service.distance} away</p>
			`,
				{ closeButton: true }
			);
			// Make marker focusable for screen readers
			marker.getElement().setAttribute('role', 'button');
			marker.getElement().setAttribute('aria-label', `${service.name}, ${service.category}`);
		});
	});
</script>

<div id="map" role="application" aria-label="Map showing nearby services">
	<div id="map-container" aria-hidden="true">
		<!-- Leaflet map rendered here -->
	</div>
</div>
<div class="map-list" aria-label="List of services on map">
	<!-- Alternative list view for screen readers -->
	{#each services as service}
		<button aria-label="{service.name}, {service.category}, {service.distance}">
			{service.name}
		</button>
	{/each}
</div>
```

### 5.5 Accessible Emergency Button

```svelte
<button
	class="emergency-button"
	aria-label="Emergency help — click to call emergency services"
	title="Emergency help"
>
	<span aria-hidden="true">🚨</span>
	<span>Emergency</span>
</button>
```

### 5.6 Live Region Announcements for Dynamic Content

**File: `src/lib/components/ConnectivityBadge.svelte`** — Announce connectivity changes:

```svelte
<script>
	import { onMount } from 'svelte';
	let online = navigator.onLine;
	onMount(() => {
		window.addEventListener('online', () => {
			online = true;
			announce('You are now online. Data will be refreshed.');
		});
		window.addEventListener('offline', () => {
			online = false;
			announce('You are now offline. Showing cached data.');
		});
	});

	function announce(message) {
		const liveRegion = document.getElementById('status-announcer');
		if (liveRegion) {
			liveRegion.textContent = message;
			setTimeout(() => {
				liveRegion.textContent = '';
			}, 1000);
		}
	}
</script>

<div class="connectivity-badge" role="status" aria-live="polite">
	{#if online}
		<span aria-hidden="true">●</span> Online
	{:else}
		<span aria-hidden="true">○</span> Offline — showing cached data
	{/if}
</div>
```

### 5.7 Screen Reader Testing Checklist

| Component           | VoiceOver (iOS)                    | TalkBack (Android) | Status   |
| ------------------- | ---------------------------------- | ------------------ | -------- |
| Navigation tab bar  | ✅ Must test                       | ✅ Must test       | Required |
| Service cards       | ✅ Announce name, category, status | ✅ Must test       | Required |
| Map pins            | ✅ Sequential focus                | ✅ Must test       | Required |
| Search results      | ✅ Announce count + each result    | ✅ Must test       | Required |
| Emergency button    | ✅ Largest touch target announced  | ✅ Must test       | Required |
| Connectivity badge  | ✅ Announce online/offline         | ✅ Must test       | Required |
| Offline page        | ✅ Skip link + semantic HTML       | ✅ Must test       | Required |
| Text scale controls | ✅ Radio group announced           | ✅ Must test       | Required |
| Low-data toggle     | ✅ Checkbox announced              | ✅ Must test       | Required |

---

## 6. Acceptance Criterion 5: Intuitive Navigation

### 6.1 Tab Bar Navigation Architecture

**File: `src/routes/+layout.svelte`** — Persistent tab bar with max 4 tabs:

```svelte
<script>
	import { page } from '$app/stores';
	import TextScaleToggle from '$lib/components/TextScaleToggle.svelte';
	import LowDataToggle from '$lib/components/LowDataToggle.svelte';
	import ConnectivityBadge from '$lib/components/ConnectivityBadge.svelte';
</script>

<nav aria-label="Main navigation" class="tab-bar">
	<a
		href="/"
		aria-label="Nearby services"
		aria-current={$page.url.pathname === '/' ? 'page' : undefined}
	>
		<span aria-hidden="true">📍</span>
		<span>Nearby</span>
	</a>
	<a
		href="/categories"
		aria-label="Categories"
		aria-current={$page.url.pathname === '/categories' ? 'page' : undefined}
	>
		<span aria-hidden="true">📂</span>
		<span>Categories</span>
	</a>
	<a
		href="/help"
		aria-label="Help and emergency contacts"
		aria-current={$page.url.pathname === '/help' ? 'page' : undefined}
	>
		<span aria-hidden="true">🆘</span>
		<span>Help</span>
	</a>
	<a
		href="/settings"
		aria-label="Settings"
		aria-current={$page.url.pathname === '/settings' ? 'page' : undefined}
	>
		<span aria-hidden="true">⚙️</span>
		<span>Settings</span>
	</a>
</nav>

<button class="emergency-fab" aria-label="Emergency services — call 999">
	<span aria-hidden="true">🚨</span>
</button>
```

### 6.2 CSS for Tab Bar and Emergency Button

```css
/* Tab bar — fixed at bottom, large touch targets */
.tab-bar {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	display: flex;
	justify-content: space-around;
	align-items: center;
	background: #fff;
	border-top: 2px solid #ddd;
	padding: 0.5rem 0;
	z-index: 100;
	max-height: 56px;
}

.tab-bar a {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 0.25rem;
	min-width: 48px;
	min-height: 48px;
	padding: 0.5rem;
	text-decoration: none;
	color: #333;
	font-size: 0.75rem;
	border-radius: 8px;
}

.tab-bar a[aria-current='page'] {
	color: #1a73e8;
	font-weight: bold;
}

/* Emergency floating action button */
.emergency-fab {
	position: fixed;
	bottom: 72px;
	right: 16px;
	width: 56px;
	height: 56px;
	border-radius: 50%;
	background: #d32f2f;
	color: white;
	border: none;
	font-size: 1.5rem;
	cursor: pointer;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
	z-index: 99;
	display: flex;
	align-items: center;
	justify-content: center;
}

.emergency-fab:hover,
.emergency-fab:focus-visible {
	background: #b71c1c;
	transform: scale(1.1);
}
```

### 6.3 Single-Purpose Screens

Each screen delivers one primary action:

**Navigation structure (flat, max 2 levels):**

```
Home (Nearby) → Category filter → Service detail
Home (Categories) → Category list → Service detail
Home (Help) → Emergency contacts / Crisis mode
Home (Settings) → Accessibility settings → Text scale / Low data / High contrast
```

**Maximum 3 taps to any service:**

- Home → Category → Service detail = 3 taps (from list view)
- Home → Service detail (from featured) = 2 taps
- No login required
- No hidden menus
- No hamburger/drawer navigation

### 6.4 Navigation Guard for Unsaved Data

```svelte
<script>
	import { beforeNavigate } from '$app/navigation';
	let unsavedChanges = false;

	beforeNavigate(({ from, to }) => {
		if (unsavedChanges && to && from && to.url.pathname !== from.url.pathname) {
			const confirmed = confirm('You have unsaved changes. Are you sure you want to leave?');
			if (!confirmed) return false;
		}
	});
</script>
```

### 6.5 Visual Progress Indicators

For multi-step flows (e.g., getting directions):

```svelte
<div
	class="progress-indicator"
	role="progressbar"
	aria-valuenow={step}
	aria-valuemax={totalSteps}
	aria-label={`Step ${step} of ${totalSteps}`}
>
	{#each steps as s, i}
		<span class:active={i + 1 === step} aria-current={i + 1 === step ? 'step' : undefined}>
			{i + 1}. {s}
		</span>
	{/each}
</div>
```

### 6.6 Cognitive Accessibility — Plain Language

- All UI text at ≤6th-grade reading level
- Avoid jargon: "service" not "provider endpoint", "location" not "coordinates"
- Every interactive element has visible text label (never icon-only)
- Confirmation dialogs use plain language: "Call emergency services? This will make a phone call." not "Confirm action?"
- Error messages are constructive: "You're offline — here's what you can still do" not "Connection failed"

### 6.7 Onboarding & First-Run

```svelte
<!-- No tutorial screen at launch. Option to skip entirely. -->
<script>
	import { onMount } from 'svelte';
	let hasSeenCoachMark = localStorage.getItem('hasSeenCoachMark');
	onMount(() => {
		if (!hasSeenCoachMark) {
			// Show contextual coach mark
			showCoachMark('Tap the 📍 tab to see services near you');
		}
	});
</script>
```

---

## 7. Integration with Existing Offline Strategy & PWA Framework

### 7.1 How This Plan Builds on Existing Research

| Existing Research                                              | This Plan's Integration                                                       |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `offline-strategy.md` §1.2-1.3 — Service Worker caching matrix | Expanded `runtimeCaching` in `vite.config.ts` with all 5 strategies           |
| `offline-strategy.md` §2.2 — Static JSON caching               | `+page.server.ts` load function with offline fallback to `services.json`      |
| `offline-strategy.md` §3 — Offline fallback page               | `offline/+page.svelte` with emergency contacts, auto-reconnect                |
| `offline-strategy.md` §4 — Data freshness                      | `lastUpdated` staleness indicator on every list page                          |
| `offline-strategy.md` §5 — Low-data mode                       | `LowDataToggle.svelte` + `services-compact.json` + service worker CacheOnly   |
| `offline-strategy.md` §6 — Accessibility for offline           | Skip links, ARIA live regions, semantic HTML, `lang="en"`                     |
| `pwa-framework-recommendation.md` §5 — SvelteKit a11y          | Leverages built-in route announcements, focus management, compile-time checks |
| `accessibility-spec.md` §2-4 — Full spec                       | All features mapped to implementation patterns above                          |

### 7.2 File Changes Summary

| File                                          | Action        | Purpose                                                               |
| --------------------------------------------- | ------------- | --------------------------------------------------------------------- |
| `vite.config.ts`                              | Modify        | Add expanded `runtimeCaching` rules                                   |
| `svelte.config.js`                            | Modify        | Add `includeVersionFile: true`                                        |
| `src/app.html`                                | Modify        | Add `data-sveltekit-preload-data="hover"` (exists), add inline styles |
| `src/app.css`                                 | Create/modify | Add all accessibility CSS                                             |
| `src/service-worker.js`                       | Create/modify | Remove SvelteKit references, add data update broadcasting             |
| `src/routes/+layout.svelte`                   | Modify        | Add skip link, tab bar, status announcer, emergency button            |
| `src/routes/+page.svelte`                     | Modify        | Add connectivity badge, staleness indicator                           |
| `src/routes/+page.server.ts`                  | Modify        | Add offline fallback data loading                                     |
| `src/routes/offline/+page.svelte`             | Create        | Offline fallback page with emergency contacts                         |
| `src/lib/components/TextScaleToggle.svelte`   | Create        | Font size controls                                                    |
| `src/lib/components/LowDataToggle.svelte`     | Create        | Low-data mode toggle                                                  |
| `src/lib/components/ConnectivityBadge.svelte` | Create        | Online/offline status                                                 |
| `src/lib/components/ServiceCard.svelte`       | Modify        | Add ARIA labels, screen reader grouping                               |
| `src/lib/data/services-compact.json`          | Create        | Compact data for low-data mode                                        |
| `src/lib/lowData.ts`                          | Create        | Network Information API utility                                       |

### 7.3 SvelteKit Built-in Accessibility Features (Leverage These)

Per `pwa-framework-recommendation.md` §5, SvelteKit provides:

1. **Route announcements** — ARIA live region auto-injected on navigation. Every page must have a unique `<title>` in `svelte:head`.
2. **Focus management** — After each navigation, SvelteKit focuses `<body>`, simulating a page reload. Customizable via `afterNavigate`.
3. **Language attribute** — `app.html` already sets `lang="en"`.
4. **Compile-time checks** — Svelte compiler applies accessibility checks to all components.

All pages must have unique `<title>` elements:

```svelte
<!-- In each +page.svelte or +layout.svelte -->
<svelte:head>
	<title>Service Name — Dublin City Support</title>
</svelte:head>
```

### 7.4 Service Worker Lifecycle Integration

```javascript
// In service-worker.js
self.addEventListener('install', (event) => {
	event.waitUntil(
		caches.open('app-shell').then((cache) => {
			return cache.addAll(['/offline', '/']);
		})
	);
});

self.addEventListener('activate', (event) => {
	event.waitUntil(
		caches.keys().then((keys) => {
			return Promise.all(
				keys.filter((key) => !key.startsWith('dcs-cache-')).map((key) => caches.delete(key))
			);
		})
	);
});
```

---

## 8. Testing & QA Checklist

### 8.1 Automated Tests

| Test                      | Tool                                            | Command                            |
| ------------------------- | ----------------------------------------------- | ---------------------------------- |
| Accessibility audit       | `@eslint-plugin-jsx-a11y` equivalent for Svelte | Integrate into CI                  |
| Color contrast validation | `contrast-checker` or similar                   | Verify WCAG AAA 7:1                |
| Touch target validation   | Custom script or `accessibility_tools`          | Verify ≥48dp/44pt                  |
| Service worker caching    | Workbox `workbox-cli`                           | Verify precache manifest           |
| Offline page load         | Browser DevTools                                | Disable network, verify page loads |
| Low-data mode             | Network throttling (2G, 3G)                     | Verify text-only mode              |

### 8.2 Manual Testing Checklist

- [ ] All screens navigable with keyboard only (Tab, Enter, Escape)
- [ ] Screen reader test: VoiceOver (iOS) — every screen fully navigable
- [ ] Screen reader test: TalkBack (Android) — every screen fully navigable
- [ ] Text scaling to 200% — no content loss or overflow
- [ ] High contrast mode — all text readable, WCAG AAA 7:1
- [ ] Reduced motion — all animations disabled
- [ ] Offline mode — app loads, cached data displayed, emergency contacts visible
- [ ] Low-data mode — no images loaded, compact JSON served, cache-only strategy
- [ ] Emergency button visible and accessible from every screen
- [ ] Tab bar labels clear, all icons have text labels
- [ ] Skip navigation link works
- [ ] Focus indicators visible on all interactive elements
- [ ] Offline connectivity badge updates correctly
- [ ] Data freshness indicator shows correct staleness
- [ ] Service cards announced as single semantic units by screen reader
- [ ] Map markers focusable and announced by screen reader
- [ ] No horizontal-only navigation
- [ ] All gestures have tap/button alternatives

### 8.3 Real User Testing

- Test with actual users experiencing homelessness and low digital literacy
- Test with assistive technologies (switch control, voice control, assistive touch)
- Test on low-end devices (2GB RAM, Android 7+, iPhone SE)
- Test under network conditions (2G, 3G, intermittent connectivity)

---

## 9. Implementation Priority & Timeline

### Phase 1 — P0: Critical (MVP)

| #   | Task                                                   | Files                                         | Est. Effort |
| --- | ------------------------------------------------------ | --------------------------------------------- | ----------- |
| 1   | Expand service worker `runtimeCaching`                 | `vite.config.ts`                              | 2 hours     |
| 2   | Add `includeVersionFile: true`                         | `svelte.config.js`                            | 15 min      |
| 3   | Create offline fallback page                           | `src/routes/offline/+page.svelte`             | 3 hours     |
| 4   | Implement offline data loading                         | `src/routes/+page.server.ts`                  | 2 hours     |
| 5   | Add connectivity badge                                 | `src/lib/components/ConnectivityBadge.svelte` | 1 hour      |
| 6   | Add skip link + ARIA live regions                      | `src/routes/+layout.svelte`                   | 1.5 hours   |
| 7   | Add screen reader semantics to service cards           | `src/lib/components/ServiceCard.svelte`       | 2 hours     |
| 8   | Add persistent tab bar + emergency button              | `src/routes/+layout.svelte`                   | 2 hours     |
| 9   | Ensure unique `<title>` on all pages                   | All `+page.svelte`                            | 1 hour      |
| 10  | Create accessible offline page with emergency contacts | `src/routes/offline/+page.svelte`             | 2 hours     |

### Phase 2 — P1: High (MVP+1)

| #   | Task                                       | Files                                       | Est. Effort |
| --- | ------------------------------------------ | ------------------------------------------- | ----------- |
| 11  | Create TextScaleToggle component           | `src/lib/components/TextScaleToggle.svelte` | 2 hours     |
| 12  | Add large text CSS (relative units, clamp) | `src/app.css`                               | 1.5 hours   |
| 13  | Add text scale persistence                 | `src/routes/+layout.svelte`                 | 1 hour      |
| 14  | Create LowDataToggle component             | `src/lib/components/LowDataToggle.svelte`   | 2 hours     |
| 15  | Create compact JSON                        | `src/lib/data/services-compact.json`        | 1 hour      |
| 16  | Implement low-data service worker logic    | `src/service-worker.js`                     | 2 hours     |
| 17  | Add low-data CSS                           | `src/app.css`                               | 1 hour      |
| 18  | Add Network Information API detection      | `src/lib/lowData.ts`                        | 1 hour      |
| 19  | Add data freshness indicators              | `src/routes/+page.svelte`                   | 1.5 hours   |
| 20  | Add high contrast + reduced motion CSS     | `src/app.css`                               | 1 hour      |

### Phase 3 — P2: Medium (Post-MVP)

| #   | Task                                                          | Files                                                | Est. Effort |
| --- | ------------------------------------------------------------- | ---------------------------------------------------- | ----------- |
| 21  | Service worker data update broadcast                          | `src/service-worker.js`, `src/routes/+layout.svelte` | 1.5 hours   |
| 22  | Map marker accessibility                                      | `src/routes/map/+page.svelte`                        | 2 hours     |
| 23  | Search results live region announcements                      | `src/routes/search/+page.svelte`                     | 1 hour      |
| 24  | Visual progress indicators                                    | `src/lib/components/ProgressIndicator.svelte`        | 1 hour      |
| 25  | Contextual coach marks                                        | `src/lib/components/CoachMark.svelte`                | 1.5 hours   |
| 26  | Add `src/service-worker.js` custom SW (remove SvelteKit refs) | `src/service-worker.js`                              | 1 hour      |

### Phase 4 — P3: Low (Post-MVP)

| #   | Task                                    | Files                                  | Est. Effort |
| --- | --------------------------------------- | -------------------------------------- | ----------- |
| 27  | Voice search integration                | `src/routes/search/+page.svelte`       | 3 hours     |
| 28  | Haptic feedback                         | Platform-specific                      | 2 hours     |
| 29  | Data budget controls                    | `src/lib/components/DataBudget.svelte` | 2 hours     |
| 30  | Audio/video help tutorials              | `src/routes/help/+page.svelte`         | 4 hours     |
| 31  | Switch control / external input testing | Manual                                 | 2 hours     |

---

## Sources

- Accessibility Specification: `.scratch/wayfinder-map/research/accessibility-spec.md`
- Offline Strategy: `.scratch/wayfinder-map/research/offline-strategy.md`
- PWA Framework Recommendation: `.scratch/wayfinder-map/research/pwa-framework-recommendation.md`
- SvelteKit Accessibility Documentation: https://svelte.dev/docs/kit/accessibility
- SvelteKit Service Workers: https://svelte.dev/docs/kit/service-workers
- @vite-pwa/sveltekit Documentation: https://github.com/vite-pwa/docs/blob/main/frameworks/sveltekit.md
- WCAG 2.2 W3C Recommendation: https://www.w3.org/TR/WCAG22/
- Workbox Caching Strategies: https://developer.chrome.com/docs/workbox/caching-strategies-overview/
- web.dev: Offline UX Design Guidelines: https://web.dev/articles/offline-ux-design-guidelines
- MDN: PWA Caching: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Caching
