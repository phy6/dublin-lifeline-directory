# UI audit tail (LOWs + browser-only verification)

**What to build:** Remainder of the 2026-09-17 whole-repo interface audit (batches 1+2 shipped as `e6c20f9` + `14ab844`). Items below are code-safe small fixes plus checks that need a real browser/device.

**Blocked by:** None (browser items need a human with a device).

**Status:** needs-triage

Code-safe (no device needed):
- [ ] Touch targets: Chatbot `.see-all` link, `.close` corner target, ServiceCard `.card-link` min-height 44px, top-nav desktop hit area 24px baseline
- [ ] Token consistency: Chatbot hardcoded `12px/9px/999px` radii → `--radius-*`; planner `.menu-items` hardcoded shadow → `--shadow-*`; ServiceCard press `scale(0.98)` → `0.96`; FilterBar `transition: all` → named properties
- [ ] `…` card-menu trigger → real icon affordance with open/closed cue
- [ ] Emoji/glyph icons (Chatbot 💬/✕/↺) → SVG `currentColor` set

Browser/device-only:
- [ ] 320px + 200% zoom reflow pass (FilterBar, ServiceList 300px track, month grid)
- [ ] SR announcement check (live regions, chatbot log, month group)
- [ ] Forced-colors / high-contrast mode pass
- [ ] Focus-ring rendering + month-cell overflow at 320px
