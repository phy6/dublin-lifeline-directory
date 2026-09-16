# 11: Apply semantic color tokens and dark mode

**What to build:** Replace all hard-coded hex values with semantic tokens; add dark mode support via `prefers-color-scheme`.

**Blocked by:** 01-design-tokens, 06-color-contrast

**Status:** ready-for-agent

- [ ] Replace all `#1a73e8` with `var(--color-accent)` or appropriate semantic token
- [ ] Replace `#4caf50`/`#f44336` with `var(--color-success)`/`var(--color-danger)`
- [ ] Replace `#333`/`#555`/`#666`/`#999` with `var(--color-text-primary)`/`var(--color-text-secondary)`/`var(--color-text-muted)`
- [ ] Replace `#fff`/`#f8f9fa`/`#e8f0fe` with `var(--color-surface)`/`var(--color-surface-hover)`/`var(--color-accent-container)`
- [ ] Tag styles: `background: var(--color-accent-container); color: var(--color-accent-on-container)`
- [ ] Add `@media (prefers-color-scheme: dark)` block with dark mode token overrides
- [ ] Test both light and dark modes in browser
- [ ] Verify contrast in both modes
