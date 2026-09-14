# Issue Tracker

**Type:** Local markdown

Issues live as files under `.scratch/<feature-slug>/issues/`. Each issue is a numbered markdown file. Blocking edges are declared in each file's "Blocked by" section.

## Tracker Operations

- **Create issue**: Write a markdown file under `.scratch/<feature-slug>/issues/NN-slug.md`
- **Block**: Add a "Blocked by" section listing issue numbers
- **Resolve**: Change status to `ready-for-agent`, mark acceptance criteria as done
- **Map**: Issues tagged `wayfinder:map` are part of the shared planning map
- **Triage**: Use the default labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`)
