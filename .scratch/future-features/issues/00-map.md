# Wayfinder Map: Ranked Capability Backlog + Locked Sequencing

Tags: wayfinder:map
Status: closed

## Destination

Ranked capability backlog + locked sequencing decisions, ready to hand to build sessions.

## Notes

- v21Deep prototype is a parts bin, not the target; mine it for ideas, do not treat it as the spec.
- Plan-only: produce decisions, not deliverables.
- Skills to consult: `grilling`, `domain-modeling`.
- Tracker: local markdown under `.scratch/future-features/issues/`. Blocking edges declared in each file's "Blocked by" section.

## Decisions so far

- Editorial overlay: per-org Markdown+YAML frontmatter, field-level precedence (editorial allow-list overrides scrape), edited via admin UI.
- Field-addition path: pilot `opening_hours`, Zod fail-closed at ingestion, canonical record + 3 stage tests per field.
- Needs taxonomy: curated flat multi-select set, exact-match chips, fail-closed validation, no migration of 14 records.
- Foundations-done: 5–10 real orgs via 01 pipeline, light+dark toggle, onLine banner only.

## Ranked backlog + locked sequencing

1. Field-addition path (01) — `opening_hours` pilot, Zod fail-closed, 3 stage tests. Unblocks everything.
2. Editorial overlay (02) — per-org Markdown+YAML, allow-list precedence, admin UI. After 01's contract.
3. Needs taxonomy (03) — curated flat multi-select, exact-match chips, fail-closed. Consumes 01's pipeline.
4. Foundations-done gate (04) — 5–10 real orgs, light+dark toggle, onLine banner. Exit check.

## Not yet specified (next wave)

- Chatbot scope
- Planner persistence
- Parcels shape
- Provider dashboard in/out
- Multilingual depth
- GPS/offline edges

## Out of scope

(empty)

## Children

- [Field-addition path](01-field-addition-path.md)
- [Editorial overlay shape](02-editorial-overlay-shape.md)
- [Needs taxonomy replacement](03-needs-taxonomy-replacement.md)
- [Foundations-done exit gate](04-foundations-done.md)
