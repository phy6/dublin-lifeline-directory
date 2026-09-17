# 06: Fix color contrast failures

**What to build:** All color pairs meeting WCAG 2.1 AA (4.5:1 for text, 3:1 for UI components) using design tokens from ticket 01.

**Blocked by:** 01-design-tokens

**Status:** completed

- [x] ServiceCard badges: Open `#2e7d32` (7.1:1), Closed `#c62828` (6.1:1) — or increase font to ≥18px
- [x] Emergency FAB: `#166b32` (6.2:1) or `#0d501f` (8.9:1); keep yellow border for distinction
- [x] Language select border: `#b88600` (3.1:1) or `#8a6600` (4.5:1)
- [x] TextScaleToggle panel border: `#1557b0` (5.8:1) or `#0d47a1` (7.2:1)
- [x] LowDataToggle active state: `#e68900` (4.1:1) or `#ef6c00` (3.8:1)
- [x] Category badge: separate `--color-category-bg`/`--color-category-text` tokens (not accent)
- [x] Offline page banner: `--color-info-bg`/`--color-info-text` tokens
- [x] Define dark mode variants for all tokens
- [x] Verify all pairs with contrast calculator
