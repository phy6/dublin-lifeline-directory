# 08: Apply type scale and spacing tokens

**What to build:** Consistent typography and spacing across all components using tokens from ticket 01.

**Blocked by:** 01-design-tokens

**Status:** ready-for-agent

- [ ] Home page (`src/routes/+page.svelte`): H1 `--text-2xl` with `text-wrap: balance`, body `--text-base`/`--leading-relaxed`
- [ ] Service Detail (`src/routes/service/[id]/+page.svelte`): H1 `--text-3xl`, H2 `--text-xl`, H3 `--text-lg`; all with descending weights
- [ ] ServiceCard: Name `--text-lg`, address/phone `--text-sm`, tags/hours `--text-xs`; hours add `text-wrap: pretty`
- [ ] FilterBar: Chip buttons `var(--text-sm)` on desktop, `var(--text-base)` on mobile (≥16px)
- [ ] Nav links: `var(--text-sm)` with `font-weight: 600`, slight `letter-spacing`
- [ ] Apply spacing tokens: intra-group `var(--space-2)`, inter-group `var(--space-3)` or `var(--space-4)`
- [ ] Offline page: add `line-height: var(--leading-relaxed)` to clamped font-size
