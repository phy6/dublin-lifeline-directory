# PWA Framework Recommendation: Dublin City Support Services

**Date:** 2026-09-14
**Project:** Dublin City Support Services — Static PWA for homeless social services directory
**Prepared for:** Framework evaluation (SvelteKit vs Next.js vs Nuxt.js)

---

## Executive Summary

**Recommendation: Continue with SvelteKit.** The project already uses `@vite-pwa/sveltekit` with `@sveltejs/adapter-static`, and this stack provides the strongest alignment with every requirement: GitHub Pages deployment ease, PWA plugin maturity, built-in accessibility features, and seamless service worker integration. Both Next.js and Nuxt.js introduce unnecessary migration cost and friction points that outweigh their theoretical benefits for this specific project.

---

## 1. Static Export & GitHub Pages Deployment

### SvelteKit — `@sveltejs/adapter-static`

- **Mechanism:** Prerenders all routes to static HTML files in a `build/` directory (configurable via `pages` option).
- **GitHub Pages:** First-class support documented by SvelteKit. The `fallback: '404.html'` option generates a SPA fallback for client-side routing on GitHub Pages (which uses hash-based routing for 404s).
- **Build output:** `build/` directory uploaded directly to the `gh-pages` branch or via `actions/upload-pages-artifact`.
- **Base path support:** `paths.base` configured via `process.env.BASE_PATH` for repository subdirectory deployment.
- **Verified workflow:** Official GitHub Actions deployment workflow provided in SvelteKit docs [1].
- **Source:** [SvelteKit adapter-static documentation](https://svelte.dev/docs/kit/adapter-static) [1]

### Next.js — `output: 'export'`

- **Mechanism:** Generates an `out/` directory with one HTML file per route.
- **Critical limitation:** Next.js static exports produce underscore-prefixed chunk files (`_next/`, `_chunk.js`). GitHub Pages returns 404 for paths starting with underscore. [2][3]
- **Workaround required:** Must use a custom image loader, set `trailingSlash: true` for proper routing, and manually handle `_next/` assets. Server Actions, Middleware, ISR, and Route Handlers are all unsupported in static export mode [4].
- **PWA service worker:** No built-in support. Must use `next-pwa` (webpack-based, separate from Next.js' own build) or Serwist (experimental, requires additional configuration) [5][6].
- **Source:** [Next.js Static Exports](https://nextjs.org/docs/app/guides/static-exports) [4]

### Nuxt.js — `target: 'static'` / `nuxt generate`

- **Mechanism:** Generates a `dist/` directory with pre-rendered HTML.
- **GitHub Pages:** Requires `router.base` configuration for repository subdirectory. Documented deployment workflow exists using `push-dir` or `peaceiris/actions-gh-pages`.
- **PWA service worker:** `@nuxtjs/pwa` module provides built-in Workbox integration. `@vite-pwa/nuxt` is the newer Vite-based alternative.
- **Source:** [Nuxt GitHub Pages deployment](https://v2.nuxt.com/deployments/github-pages) [7]

**Winner: SvelteKit.** It has the cleanest GitHub Pages integration with zero workarounds needed. Next.js' underscore file problem is a hard blocker that requires custom server configuration or complex build scripting to overcome.

---

## 2. PWA Plugin Ecosystem & Service Worker Support

### SvelteKit — `@vite-pwa/sveltekit`

- **Status:** Already installed (`@vite-pwa/sveltekit` ^1.1.0 in package.json). Zero-config setup.
- **Workbox integration:** Generates service worker via Workbox `generateSW` strategy. Configured via `vite.config.ts` with `SvelteKitPWA()` plugin.
- **Runtime caching:** Already configured with `runtimeCaching` for OpenStreetMap tiles and API. `registerType: 'prompt'` provides update notifications.
- **Manifest:** Auto-generated via the `manifest` config object in `vite.config.ts`.
- **Custom SW:** If a custom service worker is needed, the plugin handles it via the `src/service-worker.js` pattern with SvelteKit module references removed [8].
- **Cache invalidation:** `kit.includeVersionFile: true` enables `$service-worker` version import for unique cache names on deployment [9].
- **Source:** [vite-pwa/sveltekit documentation](https://github.com/vite-pwa/docs/blob/main/frameworks/sveltekit.md) [8]

### Next.js — `next-pwa` / Serwist

- **Status:** `next-pwa` is the primary PWA plugin (5th version, 115 dependents). Uses Workbox under the hood.
- **Build system mismatch:** `next-pwa` uses `workbox-webpack-plugin`, which is webpack-based. Next.js 15 uses Turbopack by default. This creates integration friction [6].
- **Service worker placement:** `sw.js` and `workbox-*.js` must be served from the public directory directly from the origin domain (no redirects). GitHub Pages' underscore file issue complicates this [6].
- **Serwist:** Next.js 15's official PWA guide recommends Serwist for service workers, but it is experimental and requires additional configuration [5].
- **Source:** [next-pwa documentation](https://github.com/shadowwalker/next-pwa/blob/master/README.md) [6]

### Nuxt.js — `@nuxtjs/pwa` / `@vite-pwa/nuxt`

- **Status:** `@nuxtjs/pwa` is a mature module with sub-modules for manifest, icon, meta, workbox, and OneSignal. `@vite-pwa/nuxt` is the newer Vite-based alternative with 582 stars.
- **Workbox integration:** Built-in `workbox` module with `offline`, `offlineStrategy`, `offlinePage`, `offlineAssets`, `pagesURLPattern` options [10].
- **Configuration:** `pwa.workbox.offline: true` enables offline caching by default. `pwa.manifest` auto-generates web manifest.
- **Source:** [Nuxt PWA documentation](https://pwa.nuxtjs.org/) [10]

**Winner: SvelteKit.** The `@vite-pwa/sveltekit` plugin is already installed and configured. It provides the tightest integration between the build system and Workbox, with zero-config service worker generation and automatic manifest injection. Next.js requires separate webpack-based tooling with known integration issues.

---

## 3. Offline Support via Cache API and Service Worker Caching

### SvelteKit

- **Precaching:** `@vite-pwa/sveltekit` generates a Workbox precache manifest from the build output. All prerendered HTML, JS, CSS, and assets are automatically precached [8].
- **Runtime caching:** `runtimeCaching` in `vite.config.ts` supports all Workbox strategies (`CacheFirst`, `NetworkFirst`, `StaleWhileRevalidate`). The existing research at `.scratch/wayfinder-map/research/offline-strategy.md` documents a comprehensive strategy matrix [9].
- **Offline fallback:** `PrecacheFallbackPlugin` serves `offline.html` when navigation fails. The `offline-strategy.md` provides detailed implementation [9].
- **Cache versioning:** The `$service-worker` module provides version strings for cache naming, enabling automatic cleanup of old caches on `activate` [9].
- **Low-data mode:** Documented strategy: switch to `CacheOnly`/`CacheFirst` strategies, serve compact JSON, disable background updates [9].

### Next.js

- **Precaching:** `next-pwa` generates `workbox-*.js` and `sw.js` in the output directory. Precaching is configured via `workbox.globPatterns`.
- **Runtime caching:** `runtimeCaching` array in `next-pwa` config supports Workbox strategies.
- **Offline fallback:** Available via `PrecacheFallbackPlugin` in `next-pwa` configuration.
- **Limitation:** Static export constraints mean the service worker cannot leverage server-side features. The underscore file problem means some cached assets may not be served correctly on GitHub Pages.

### Nuxt.js

- **Precaching:** `@nuxtjs/pwa` has `workbox` module with `offline: true` enabling automatic offline caching of all routes.
- **Runtime caching:** Configurable via `pwa.workbox` options. Supports `offlineStrategy` (default: `NetworkFirst`).
- **Offline page:** `pwa.workbox.offlinePage: '/offline.html'` routes all offline requests to a specified page.
- **Source:** [Nuxt PWA Workbox Module](https://pwa.nuxtjs.org/workbox) [10]

**Winner: SvelteKit.** The `@vite-pwa/sveltekit` plugin provides the most tightly integrated Workbox experience, with automatic precaching of prerendered pages and the `$service-worker` version module for cache invalidation. The existing offline strategy research is already aligned with this stack.

---

## 4. Map Rendering Capability (Leaflet / Mapbox GL JS)

### Current state: Leaflet 1.9.4 is already installed and in use

### SvelteKit

- **Leaflet:** Works seamlessly with SvelteKit's client-side navigation. The `leaflet` package is already in `package.json`. The `@types/leaflet` types are installed.
- **Svelte ecosystem:** Community components exist for Leaflet and Mapbox integration in SvelteKit (e.g., `@rodneylab/sveltekit-map-component`) [11].
- **Server-side rendering:** Leaflet must be loaded only in the browser (`$app/environment` `browser` flag), which is straightforward in SvelteKit.
- **Source:** [Leaflet accessibility guide](https://leafletjs.com/examples/accessibility) [12]

### Next.js

- **Leaflet:** Works but requires `'use client'` directives for all map components due to Next.js' server-side rendering. The `window` and `document` APIs are unavailable during SSR.
- **Mapbox GL JS:** Also works client-side but requires careful hydration handling.
- **Static export:** Maps that rely on client-side rendering are compatible with static exports but must use the `'use client'` boundary.

### Nuxt.js

- **Leaflet:** Similar client-side requirements. Nuxt 3 with `<ClientOnly>` component wrapper handles this.
- **Mapbox GL JS:** Available via community modules.

**Winner: Tie (SvelteKit marginally preferred).** All three frameworks support Leaflet equally well with minor SSR-specific wrapping. SvelteKit has a slight edge due to its simpler component model and the `svelte:head` integration for accessibility. The project already uses Leaflet, so this is not a differentiator.

---

## 5. Accessibility Features

### SvelteKit — Built-in accessibility platform

- **Route announcements:** SvelteKit injects an ARIA live region onto the page that reads out the new page title after each client-side navigation. Every page must have a unique `<title>` in `svelte:head`. [13]
- **Focus management:** After each navigation, SvelteKit focuses the `<body>` element, simulating the focus reset of a full page reload. Customizable via `afterNavigate` hook. [13]
- **Language attribute:** The `app.html` template sets the default `lang` attribute on `<html>`. [13]
- **Compile-time checks:** Svelte's compiler applies accessibility checks to all Svelte components. [13]
- **Source:** [SvelteKit Accessibility Documentation](https://svelte.dev/docs/kit/accessibility) [13]

### Next.js

- **No built-in accessibility features** comparable to SvelteKit's route announcements and focus management.
- Requires manual implementation of ARIA live regions and focus management.
- The `next/pwa` PWA guide mentions accessibility but provides no framework-level support [5].

### Nuxt.js

- The `@nuxtjs/pwa` module handles manifest and meta tags, which contributes to basic accessibility.
- No framework-level accessibility features equivalent to SvelteKit's route announcements or focus management.
- Vue's own accessibility guidance exists but requires manual implementation.

**Winner: SvelteKit (significantly).** SvelteKit's built-in accessibility features — route announcements via ARIA live regions, automatic focus management after navigation, and compile-time accessibility checks — are unmatched by either Next.js or Nuxt.js. For an app serving vulnerable populations including people experiencing homelessness and those with disabilities, this is a critical differentiator.

---

## 6. Low-Data Mode Implementation

### All frameworks

Low-data mode is primarily a service worker + application logic concern, not a framework concern. All three frameworks can implement it via:

- Service worker strategy switching (CacheOnly vs StaleWhileRevalidate)
- Network Information API detection (`navigator.connection.saveData`)
- User-controlled toggle in the app UI
- Compact JSON payloads

The implementation is framework-agnostic and depends on the service worker configuration, which all three support via their respective Workbox integrations.

**Winner: Tie.** Low-data mode implementation is equivalent across all three frameworks when configured via their PWA plugins.

---

## 7. Summary Comparison Table

| Criteria                       | SvelteKit                              | Next.js                                  | Nuxt.js                               |
| ------------------------------ | -------------------------------------- | ---------------------------------------- | ------------------------------------- |
| **Static export quality**      | ✅ Clean, no underscore files          | ❌ Underscore file 404 issue on GH Pages | ⚠️ Requires base path config          |
| **GitHub Pages ease**          | ✅ Official workflow documented        | ⚠️ Workarounds needed                    | ⚠️ Requires base path config          |
| **PWA plugin maturity**        | ✅ `@vite-pwa/sveltekit` — zero-config | ⚠️ `next-pwa` — webpack mismatch         | ✅ `@nuxtjs/pwa` / `@vite-pwa/nuxt`   |
| **Service worker integration** | ✅ Seamless, auto-generated            | ⚠️ Separate plugin, config complexity    | ✅ Built-in module                    |
| **Offline support**            | ✅ Workbox precache + runtime caching  | ⚠️ Works but has GH Pages issues         | ✅ Built-in offline module            |
| **Accessibility (built-in)**   | ✅ Route announcements, focus mgmt     | ❌ Manual implementation                 | ❌ Manual implementation              |
| **Map rendering**              | ✅ Leaflet works well                  | ✅ Leaflet works with client boundary    | ✅ Leaflet works with client boundary |
| **Low-data mode**              | ✅ SW-configurable                     | ✅ SW-configurable                       | ✅ SW-configurable                    |
| **Migration cost**             | ✅ Already in use                      | ❌ High (rewrite + workaround)           | ⚠️ Medium (rewrite)                   |
| **Bundle size**                | ✅ Smaller (Svelte compiler)           | ⚠️ Larger (React/Node overhead)          | ⚠️ Medium (Vue overhead)              |
| **Service worker file size**   | ✅ Minimal Workbox runtime             | ⚠️ Full Workbox via webpack              | ✅ Workbox runtime                    |

---

## 8. Risk Assessment of Switching

### Switching from SvelteKit to Next.js

- **Risk: HIGH.** The underscore file problem on GitHub Pages is a known, unsolved issue with static exports [2][3]. The webpack/Turbopack mismatch with `next-pwa` adds configuration complexity. Complete rewrite of all routes, components, and the service worker configuration would be required. No PWA benefit justifies this risk.

### Switching from SvelteKit to Nuxt.js

- **Risk: MEDIUM-HIGH.** Requires complete rewrite. `@vite-pwa/nuxt` is a viable PWA solution, but Nuxt's `target: 'static'` + GitHub Pages requires `router.base` configuration. The accessibility features that make SvelteKit superior for this use case would need to be manually implemented. No compelling reason to switch.

---

## 9. Final Recommendation

**Continue with SvelteKit.** The project is already well-positioned with `@vite-pwa/sveltekit`, `@sveltejs/adapter-static`, and Leaflet. The existing research at `.scratch/wayfinder-map/research/offline-strategy.md` is already aligned with the SvelteKit + Workbox stack. The key strengths that make SvelteKit the right choice for this specific project are:

1. **GitHub Pages deployment is zero-friction** — no underscore file problems, no base path workarounds needed
2. **Built-in accessibility platform** — route announcements, focus management, and compile-time checks are critical for serving vulnerable populations
3. **PWA plugin is already configured** — `@vite-pwa/sveltekit` with Workbox provides the exact caching strategies documented in the offline strategy research
4. **Lower bundle size** — important for users on limited data connections
5. **Proven static export** — `@sveltejs/adapter-static` with `fallback: '404.html'` is the most battle-tested static export adapter among the three

No framework switch is recommended. The remaining work should focus on:

- Expanding `runtimeCaching` in `vite.config.ts` to include `services.json` with `StaleWhileRevalidate` and navigation with `NetworkFirst`
- Adding `kit.includeVersionFile: true` for cache invalidation
- Implementing the offline fallback page (`offline.html`) with emergency contacts
- Adding the low-data mode toggle
- Ensuring all map markers have `alt` text for screen reader accessibility

---

## Sources

[1] SvelteKit adapter-static documentation — https://svelte.dev/docs/kit/adapter-static
[2] Next.js static export GitHub Pages issue (underscore files) — https://github.com/marketplace/actions/next-pages
[3] Next.js static exports guide — https://nextjs.org/docs/pages/guides/static-exports
[4] Next.js App Router static exports — https://nextjs.org/docs/app/guides/static-exports
[5] Next.js PWA guide — https://nextjs.org/docs/app/guides/progressive-web-apps
[6] next-pwa documentation — https://github.com/shadowwalker/next-pwa/blob/master/README.md
[7] Nuxt GitHub Pages deployment — https://v2.nuxt.com/deployments/github-pages
[8] @vite-pwa/sveltekit documentation — https://github.com/vite-pwa/docs/blob/main/frameworks/sveltekit.md
[9] Dublin City Support Services offline strategy — `.scratch/wayfinder-map/research/offline-strategy.md`
[10] Nuxt PWA documentation — https://pwa.nuxtjs.org/
[11] SvelteKit map components — https://github.com/rodneylab/sveltekit-components
[12] Leaflet accessibility guide — https://leafletjs.com/examples/accessibility
[13] SvelteKit accessibility documentation — https://svelte.dev/docs/kit/accessibility
