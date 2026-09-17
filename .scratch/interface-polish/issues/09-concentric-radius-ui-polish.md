# 09: Fix concentric radius and UI polish

**What to build:** Consistent border radius hierarchy, proper focus rings, press states, and elevation shadows across all components.

**Blocked by:** 01-design-tokens

**Status:** completed

- [x] ServiceCard: Card `var(--radius-lg)`, header bleeds to edge (no radius) or uses `var(--radius-md)` with negative margin
- [x] FilterBar chips: `var(--radius-full)` (pill); add `box-shadow: 0 0 0 3px var(--color-focus-ring)` on `:focus-visible` for both active/inactive
- [x] Nav: Remove bottom-only radius or add `box-shadow: 0 2px 8px rgba(0,0,0,0.1)` for elevation
- [x] TextScaleToggle panel: `border: 1px solid var(--color-border); border-radius: var(--radius-md); box-shadow: 0 4px 12px rgba(0,0,0,0.1)`
- [x] LowDataToggle: Add `max(1rem, env(safe-area-inset-bottom))` positioning
- [x] ServiceCard hover: Wrap in `@media (prefers-reduced-motion: no-preference)`; add press state `active: transform: scale(0.98)`
- [x] Skip link: Add `transition: top 0.15s ease-out`
- [x] Hours rows: `border-bottom: 1px solid var(--color-border); padding: var(--space-2) 0`
