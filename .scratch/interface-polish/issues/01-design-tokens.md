# 01: Establish design token system

**What to build:** A CSS custom property system for colors, spacing, border radius, and type scale that replaces all hard-coded values across the codebase. This is the foundation that unblocks all other visual polish work.

**Blocked by:** None (can start immediately)

**Status:** completed

- [x] Create `src/lib/styles/tokens.css` with:
  - Color tokens: `--color-accent`, `--color-accent-hover`, `--color-success`, `--color-danger`, `--color-text-primary`, `--color-text-secondary`, `--color-text-muted`, `--color-border`, `--color-surface`, `--color-surface-hover`, `--color-error`, `--color-warning`, `--color-info`
  - Spacing tokens: `--space-1: 4px`, `--space-2: 8px`, `--space-3: 16px`, `--space-4: 24px`, `--space-5: 32px`, `--space-6: 48px`
  - Radius tokens: `--radius-sm: 4px`, `--radius-md: 8px`, `--radius-lg: 12px`, `--radius-xl: 16px`, `--radius-full: 9999px`
  - Type scale: `--text-xs: 0.75rem`, `--text-sm: 0.875rem`, `--text-base: 1rem`, `--text-lg: 1.125rem`, `--text-xl: 1.25rem`, `--text-2xl: 1.5rem`, `--text-3xl: 1.875rem`
  - Line heights: `--leading-tight: 1.1`, `--leading-normal: 1.5`, `--leading-relaxed: 1.6`
- [x] Import tokens in `src/app.html` or `src/routes/+layout.svelte` so they're globally available
- [x] Verify all existing hard-coded values have a token equivalent
