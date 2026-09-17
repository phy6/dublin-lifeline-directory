# 11: Apply semantic color tokens and dark mode

**What to build:** Replace all hard-coded hex values with semantic tokens; add dark mode support via `prefers-color-scheme`.

**Blocked by:** 01-design-tokens, 06-color-contrast

**Status:** completed

- [x] Replace all `#1a73e8` with `var(--color-accent)` or appropriate semantic token
- [x] Replace `#4caf50`/`#f44336` with `var(--color-success)`/`var(--color-danger)`
- [x] Replace `#333`/`#555`/`#666`/`#999` with `var(--color-text-primary)`/`var(--color-text-secondary)`/`var(--color-text-muted)`
- [x] Replace `#fff`/`#f8f9fa`/`#e8f0fe` with `var(--color-surface)`/`var(--color-surface-hover)`/`var(--color-accent-container)`
- [x] Tag styles: `background: var(--color-accent-container); color: var(--color-accent-on-container)`
- [x] Add `@media (prefers-color-scheme: dark)` block with dark mode token overrides
- [x] Test both light and dark modes in browser
- [x] Verify contrast in both modes
