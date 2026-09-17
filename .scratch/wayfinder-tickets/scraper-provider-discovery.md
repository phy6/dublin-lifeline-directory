# Ticket: Provider discovery feature

**Blocked by:** scraper-python-implementation
**Blocks:** None
**Status:** Closed — Out of scope for MVP

> **Closed per wayfinder review:** Provider discovery deferred as out of scope for MVP. See map's "Out of scope" section.

## Question

The old scraper has a "discovery" feature that crawls directory sites (Dublin City Council, Charity Navigator, etc.) to find new provider URLs. Config in sources.json includes:
- 7 discovery URLs
- Selectors for name, url, description, phone, category, address
- 60 second interval between discovery requests
- Max 50 results

Should we port this?
- **Yes**: Keeps the scraper extensible; can discover new services automatically
- **No**: Out of scope for MVP; current 14 targets are sufficient; discovery adds complexity and maintenance
- **Defer**: Build core scraper first; add discovery in a follow-up ticket

Recommendation: **Defer**. The current target list is stable. Discovery can be added later if needed.