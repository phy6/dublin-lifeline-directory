# 05: Fix FAB accessibility and positioning

**What to build:** Emergency FAB, language selector, and accessibility FABs that have proper labels, safe-area positioning, and don't overlap content.

**Blocked by:** 01-design-tokens (needs spacing/radius tokens)

**Status:** ready-for-agent

- [ ] Emergency FAB (`src/routes/+layout.svelte:38-40`): Add `aria-label="Call emergency services 112"` directly on `<a>`; ensure 44×44px hit area
- [ ] Language selector (`src/routes/+layout.svelte:42-47`): Add `<label for="lang-select">Language</label>` visually hidden; associate via `id`
- [ ] Text scale toggle (`src/lib/components/TextScaleToggle.svelte:21-34`): Fix `aria-labelledby` to reference existing element
- [ ] Position all fixed FABs using `env(safe-area-inset-*)` and spacing tokens from ticket 01
- [ ] Stack accessibility FABs vertically with gap token; inset from edges
- [ ] Test at 320px width and 200% zoom: no clipping, no overlap
