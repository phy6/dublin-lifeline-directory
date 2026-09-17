# Meal & Appointment Week-Planner — Design Spec

Date: 2026-09-17. Status: approved in brainstorming, pending user review of this doc.
Repo: Dublin Lifeline Directory (single-maintainer static PWA on GitHub Pages).

## Purpose

A personal week-planner where users keep weekly appointments: directory meal
services and personal entries side by side. Alerts are owned by the phone's
native calendar app via `.ics` export. On-device only — no backend, no sync.

## Data

### `meals.json` (static, curated)

Shipped with the bundle alongside `services.json`. Each record:

```json
{
	"id": "capuchin-breakfast",
	"orgId": "capuchin-day-centre",
	"mealType": "breakfast",
	"days": ["mon", "tue", "wed", "thu", "fri", "sat"],
	"start": "07:30",
	"end": "11:30",
	"address": "29 Bow St, Dublin 7",
	"notes": "",
	"verifiedDate": "2026-09-17"
}
```

- Every meal states **what** (`mealType`), **when** (`days` + window),
  **where** (`orgId` + `address`).
- Curated by hand for the orgs that actually serve meals (~5: Capuchin,
  Merchants Quay, Mendicity, Crosscare, Simon); seeded from scraper `hours`
  where they match. Orgs without meals have no records.
- `verifiedDate` makes staleness visible. Updates are direct edits
  (same workflow as the editorial overlay), code/data commits stay separate.

### Parked (future decision)

Scraper change-watch: compare live `hours` against the snapshot behind each
meal record and fail loudly on drift. Explicitly deferred — static curation
only for v1.

## UI — `/planner` route

- Week-grid Mon–Sun with two block types:
  - **Meal markers** (read-only, from `meals.json`): e.g.
    "Breakfast @ Capuchin 07:30–11:30". Tap to add into the plan.
  - **Personal appointments**: free-form title/time/notes, or linked to any
    of the 13 orgs via picker (pre-fills name/address).
- Tap a block to edit; delete via explicit control. Recurrence per entry:
  once or weekly. Fully usable offline after first load.

## Storage

- Appointments in `localStorage` under a versioned key
  (e.g. `lifeline.planner.v1`) so future schemas migrate cleanly.
- Persists across refresh, tab close, phone restart. Lost only on explicit
  site-data clearing — the UI states plainly that the plan lives only on
  this device and recommends backups.
- **JSON backup/restore**: "Download backup" writes the full plan to a file;
  "Restore from file" re-imports it. Full fidelity (recurrence, notes),
  offline, user-held.

## Calendar export (alerts)

- Per-appointment and per-week "Add to calendar" buttons generate `.ics`
  client-side (string templates, no network, no library): title, start/end,
  location, notes, `RRULE:FREQ=WEEKLY` for recurring entries.
- Meal-derived appointments pre-fill type + venue + serving window.
- The OS calendar owns reminders/alerts. `.ics`-exported entries double as
  an independent partial backup.

## Scope guards

- No date libraries (hand-rolled week math), no IndexedDB wrapper, no UI
  library — planner adds only a few KB (bundle weight is load-bearing for
  low-data users).
- Out of scope for v1: sync/sharing, in-app notifications, richer recurrence
  (daily/monthly/custom), pre-seeded suggestions beyond read-only markers.

## Verification

- Unit tests: recurrence expansion, `.ics` generation (incl. `RRULE`).
- Component test: week-grid renders seeded meals + appointments; add/edit/
  delete flows.
- Manual pass: add → refresh → data persists; backup → clear → restore;
  `.ics` imports into Android + iOS calendars with correct time and repeat.
- Run `verification-before-completion` before claiming done.
