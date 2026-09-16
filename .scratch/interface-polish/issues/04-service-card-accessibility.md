# 04: Fix ServiceCard nested interactive content

**What to build:** Service cards that are a single link wrapper with non-interactive badges inside, instead of badges that appear clickable but navigate the card.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Change `src/lib/components/ServiceCard.svelte` card from `<a>` wrapping everything to `<article>` with a single "View details" link
- [ ] Move "Open now"/"Closed" badges outside the link or make them plain text with `aria-label`
- [ ] Keep card clickable via the "View details" link (or make entire card a link but remove nested interactive elements)
- [ ] Ensure card still has hover/focus states for the link
- [ ] Verify no nested `<a>` or `<button>` inside the card link
