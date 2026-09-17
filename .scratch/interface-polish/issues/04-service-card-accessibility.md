# 04: Fix ServiceCard nested interactive content

**What to build:** Service cards that are a single link wrapper with non-interactive badges inside, instead of badges that appear clickable but navigate the card.

**Blocked by:** None (can start immediately)

**Status:** completed

- [x] Change `src/lib/components/ServiceCard.svelte` card from `<a>` wrapping everything to `<article>` with a single "View details" link
- [x] Move "Open now"/"Closed" badges outside the link or make them plain text with `aria-label`
- [x] Keep card clickable via the "View details" link (or make entire card a link but remove nested interactive elements)
- [x] Ensure card still has hover/focus states for the link
- [x] Verify no nested `<a>` or `<button>` inside the card link
