# 03-research-framework: PWA framework re-evaluation

**Label:** `wayfinder:research`
**Type:** Research (AFK)
**Blocked by:** None (can start immediately)
**Supersedes:** 03-research-framework (Flutter research — superseded by PWA pivot)
**Assigned to:** phy6 (claimed)
**Status:** closed
**Resolution date:** 2026-09-14

**Resolution:** ✅ Continue with SvelteKit. `@vite-pwa/sveltekit` + `@sveltejs/adapter-static` is the optimal stack — zero-friction GitHub Pages deployment (Next.js has underscore file 404 blocker), built-in accessibility platform (route announcements, focus management, compile-time checks), already-installed PWA plugin with Workbox. Leaflet already in use. Full recommendation at `research/pwa-framework-recommendation.md`. [→ 03-pwa-framework.md](03-pwa-framework.md)

---

**Question:** What PWA framework should be used to build a static Progressive Web App hosted on GitHub Pages? The app needs offline support via Service Workers, map rendering, and accessibility features. Must produce static HTML/CSS/JS files with no backend dependency.

**Acceptance criteria:**

- Evaluation of PWA frameworks (SvelteKit, Next.js, Nuxt.js) for static generation
- PWA manifest and service worker setup
- Offline support via Cache API and service worker caching strategies
- Map rendering capability (Mapbox GL JS, Leaflet, or similar)
- Accessibility features (large text, screen reader support, low-data mode)
- GitHub Pages deployment configuration
- Output: framework recommendation with PWA-specific rationale
