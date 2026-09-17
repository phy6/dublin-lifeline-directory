# Field-addition path

Tags: wayfinder:task
Status: closed

## Resolution

- Pilot field: `opening_hours` (trickiest shape; if the contract survives it, it survives everything).
- Validation: Zod schema at ingestion boundary, fail-closed — bad rows rejected with log.
- Normalizer + tests: canonical typed record + one unit test per stage (scrape parse, validate, normalize); every new field ships with these three tests.

## Question

Define the repeatable contract scraper/editorial → validation → normalizer → tests, proven with one pilot field.

## Blocked by

None (frontier — can start immediately)
