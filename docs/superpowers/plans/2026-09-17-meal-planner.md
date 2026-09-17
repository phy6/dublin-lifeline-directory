# Meal & Appointment Week-Planner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the on-device week-planner: curated `meals.json`, `/planner` week-grid with meal markers + personal appointments + weekly recurrence, `localStorage` persistence, client-side `.ics` export and JSON backup/restore.

**Architecture:** Static data (`src/lib/data/meals.json` imported like `services.json`) plus three pure utility modules (recurrence/week-math, `.ics` builder, versioned `localStorage` store) covered by vitest unit tests; one new `/planner` route with a tab-bar entry; no new dependencies.

**Tech Stack:** SvelteKit 2 + Svelte 5, TypeScript, vitest (`npm run test:unit`), `svelte-check`, prettier/eslint. No date libraries, no IndexedDB.

**Spec:** `/home/martin/Dublin City Support Services/docs/superpowers/specs/2026-09-17-meal-planner-design.md`

## Global Constraints

- Static-only PWA on GitHub Pages: no backend, no network calls from planner code, works offline after first load.
- No UI library, no date library — hand-rolled week math, string-template `.ics`.
- Planner must add only a few KB to the bundle; do not import `services.json` client-side where `services-compact.json` suffices (follow existing route patterns).
- Code and data commits stay separate: `feat(planner):` for code, `data(meals):` for `meals.json` content.
- i18n: user-facing strings go through the `t()` store in `src/lib/stores/lang.svelte.ts` (add `planner` keys alongside `directory`/`map`/`search`).
- Accessibility: week-grid is keyboard navigable, blocks are real buttons, follows the landmark/focus patterns from the recent UI slices.
- Verify with `git status` + `git log --oneline -5` before touching anything; run `npm run test:unit`, `npm run check`, `npm run lint` before claiming done (per `verification-before-completion`).

---

### Task 1: Meal data + types

**Files:**

- Create: `src/lib/data/meals.json`
- Modify: `src/lib/types.ts` (append `MealEntry` interface)
- Test: `src/test/unit/meals.test.ts`

**Interfaces:**

- Consumes: `DayKey` from `$lib/utils/hours` (reuse `DAY_KEYS`, do not redefine day keys).
- Produces: `MealEntry` type (`id: string`, `orgId: string`, `mealType: 'breakfast' | 'lunch' | 'dinner'`, `days: DayKey[]`, `start: string`, `end: string`, `address: string`, `notes: string`, `verifiedDate: string`); `MEALS_VERSION = 1` export from types or data module for later migration use.

- [ ] **Step 1: Curate `meals.json` (data commit)**

  Research each org's site (Capuchin Day Centre, Merchants Quay Ireland, Mendicity Institution, Crosscare, Dublin Simon Community) and record real serving windows. Seed from scraper `hours` in `src/lib/data/services.json` where they visibly match (e.g. Capuchin's `07:30-11:30, 12:30-15:00` Mon–Sat). Only include meals you can verify; orgs without verifiable meal times get no records. Every record carries what/when/where + `verifiedDate: "2026-09-17"`. Example record shape:

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

- [ ] **Step 2: Write the failing test**

  ```ts
  import { describe, it, expect } from 'vitest';
  import meals from '$lib/data/meals.json';
  import { DAY_KEYS } from '$lib/utils/hours';

  describe('meals data', () => {
  	it('every meal has what/when/where and a verification date', () => {
  		expect(meals.length).toBeGreaterThan(0);
  		for (const m of meals) {
  			expect(['breakfast', 'lunch', 'dinner']).toContain(m.mealType);
  			expect(m.days.length).toBeGreaterThan(0);
  			for (const d of m.days) expect(DAY_KEYS as readonly string[]).toContain(d);
  			expect(/^([01]\d|2[0-3]):[0-5]\d$/.test(m.start)).toBe(true);
  			expect(/^([01]\d|2[0-3]):[0-5]\d$/.test(m.end)).toBe(true);
  			expect(m.orgId.length).toBeGreaterThan(0);
  			expect(m.address.length).toBeGreaterThan(0);
  			expect(m.verifiedDate.length).toBeGreaterThan(0);
  		}
  	});

  	it('every meal orgId exists in services.json', async () => {
  		const services = (await import('$lib/data/services.json')).default;
  		const ids = new Set(services.services.map((s: { id: string }) => s.id));
  		for (const m of meals) expect(ids.has(m.orgId)).toBe(true);
  	});
  });
  ```

- [ ] **Step 3: Run test to verify it fails**

  Run: `npm run test:unit -- src/test/unit/meals.test.ts`
  Expected: FAIL with "Failed to resolve import $lib/data/meals.json" (file does not exist yet; the `MealEntry` type does not exist either).

- [ ] **Step 4: Create `meals.json` + append `MealEntry` to `src/lib/types.ts`**

  ```ts
  import type { DayKey } from '$lib/utils/hours';

  export type MealType = 'breakfast' | 'lunch' | 'dinner';

  export interface MealEntry {
  	id: string;
  	orgId: string;
  	mealType: MealType;
  	days: DayKey[];
  	start: string;
  	end: string;
  	address: string;
  	notes: string;
  	verifiedDate: string;
  }
  ```

- [ ] **Step 5: Run test to verify it passes**

  Run: `npm run test:unit -- src/test/unit/meals.test.ts`
  Expected: PASS.

- [ ] **Step 6: Commit (two commits — data and code stay separate)**

  ```bash
  git add src/lib/data/meals.json && git commit -m "data(meals): curated week-planner meal windows with verification dates"
  git add src/lib/types.ts src/test/unit/meals.test.ts && git commit -m "feat(planner): MealEntry type and meals data contract test"
  ```

### Task 2: Planner domain utils (recurrence, .ics, storage)

**Files:**

- Create: `src/lib/utils/planner.ts`
- Create: `src/lib/utils/ics.ts`
- Create: `src/lib/utils/planner-store.ts`
- Test: `src/test/unit/planner.test.ts`, `src/test/unit/ics.test.ts`, `src/test/unit/planner-store.test.ts`

**Interfaces:**

- Consumes: `MealEntry`, `DayKey`/`DAY_KEYS` from `$lib/utils/hours`.
- Produces:
  - `PlannerAppointment { id: string; title: string; day: DayKey; start: string; end: string; location: string; notes: string; orgId: string | null; recurrence: 'once' | 'weekly'; source: 'meal' | 'personal' }`
  - `weekDates(weekMonday: Date): Date[]` — 7 dates Mon–Sun, pure, no mutation of input.
  - `expandWeek(appts: PlannerAppointment[], weekMonday: Date): { appt, date }[]` — weekly entries appear every week, `once` entries carry their `weekOf` date and appear only that week (`weekOf: string` ISO date field on once-appointments).
  - `appointmentToICS(appt, date: Date): string` and `weekToICS(items): string` — RFC 5545 `VCALENDAR` text with `UID`, `DTSTAMP`, `DTSTART`, `DTEND`, `SUMMARY`, `LOCATION`, `DESCRIPTION`, and `RRULE:FREQ=WEEKLY` for weekly entries. Dates formatted as `YYYYMMDDTHHMMSS` floating local time.
  - `planner-store.ts`: `loadPlan(): PlannerAppointment[]`, `savePlan(appts): void`, `STORAGE_KEY = 'lifeline.planner.v1'`; try/catch around JSON parse (corrupt data → `[]`), `typeof localStorage === 'undefined'` guard for SSR.

- [ ] **Step 1: Write failing tests for week math + recurrence**

  ```ts
  import { describe, it, expect } from 'vitest';
  import { weekDates, expandWeek, type PlannerAppointment } from '$lib/utils/planner';

  const monday = new Date(2026, 8, 14); // a Monday

  describe('weekDates', () => {
  	it('returns 7 dates starting Monday without mutating input', () => {
  		const before = monday.getTime();
  		const days = weekDates(monday);
  		expect(days).toHaveLength(7);
  		expect(days[0].getDay()).toBe(1);
  		expect(days[6].getDay()).toBe(0);
  		expect(monday.getTime()).toBe(before);
  	});
  });

  describe('expandWeek', () => {
  	it('shows weekly entries every week and once entries only their week', () => {
  		const weekly: PlannerAppointment = {
  			id: 'a',
  			title: 'Breakfast',
  			day: 'tue',
  			start: '07:30',
  			end: '11:30',
  			location: 'Capuchin',
  			notes: '',
  			orgId: 'capuchin-day-centre',
  			recurrence: 'weekly',
  			source: 'meal',
  			weekOf: '2026-09-14'
  		};
  		const once: PlannerAppointment = {
  			id: 'b',
  			title: 'GP',
  			day: 'wed',
  			start: '10:00',
  			end: '10:30',
  			location: '',
  			notes: '',
  			orgId: null,
  			recurrence: 'once',
  			source: 'personal',
  			weekOf: '2026-09-16'
  		};
  		const thisWeek = expandWeek([weekly, once], new Date(2026, 8, 14));
  		expect(thisWeek.map((i) => i.appt.id).sort()).toEqual(['a', 'b']);
  		const nextWeek = expandWeek([weekly, once], new Date(2026, 8, 21));
  		expect(nextWeek.map((i) => i.appt.id)).toEqual(['a']);
  	});
  });
  ```

- [ ] **Step 2: Run to verify they fail**

  Run: `npm run test:unit -- src/test/unit/planner.test.ts`
  Expected: FAIL with "Failed to resolve import $lib/utils/planner".

- [ ] **Step 3: Implement `src/lib/utils/planner.ts` (pure functions only, no Svelte, no browser APIs)**

  Minimal week math with `getDay()` Monday-first index `((getDay() + 6) % 7)`, `weekOf` stored as ISO `yyyy-mm-dd` derived from the date; `expandWeek` matches `once` entries by comparing `weekOf` to the ISO date of the Monday of the displayed week for that entry's day offset.

- [ ] **Step 4: Write failing tests for `.ics` builder**

  ```ts
  import { describe, it, expect } from 'vitest';
  import { appointmentToICS } from '$lib/utils/ics';

  describe('appointmentToICS', () => {
  	it('emits VEVENT with RRULE for weekly entries', () => {
  		const ics = appointmentToICS(
  			{
  				id: 'a',
  				title: 'Breakfast @ Capuchin',
  				day: 'tue',
  				start: '07:30',
  				end: '11:30',
  				location: '29 Bow St, Dublin 7',
  				notes: '',
  				orgId: 'capuchin-day-centre',
  				recurrence: 'weekly',
  				source: 'meal',
  				weekOf: '2026-09-15'
  			},
  			new Date(2026, 8, 15)
  		);
  		expect(ics).toContain('BEGIN:VEVENT');
  		expect(ics).toContain('SUMMARY:Breakfast @ Capuchin');
  		expect(ics).toContain('DTSTART:20260915T073000');
  		expect(ics).toContain('DTEND:20260915T113000');
  		expect(ics).toContain('RRULE:FREQ=WEEKLY');
  		expect(ics).toContain('LOCATION:29 Bow St\\, Dublin 7');
  	});

  	it('omits RRULE for once entries and escapes commas/semicolons', () => {
  		const ics = appointmentToICS(
  			{
  				id: 'b',
  				title: 'GP; follow-up, urgent',
  				day: 'wed',
  				start: '10:00',
  				end: '10:30',
  				location: '',
  				notes: 'Bring; papers',
  				orgId: null,
  				recurrence: 'once',
  				source: 'personal',
  				weekOf: '2026-09-16'
  			},
  			new Date(2026, 8, 16)
  		);
  		expect(ics).not.toContain('RRULE');
  		expect(ics).toContain('SUMMARY:GP\\; follow-up\\, urgent');
  	});
  });
  ```

- [ ] **Step 5: Run to verify they fail, then implement `src/lib/utils/ics.ts`**

  Run: `npm run test:unit -- src/test/unit/ics.test.ts` → FAIL, then implement text escaping (`,` → `\,`, `;` → `\;`, newline → `\n`), `weekToICS` wrapping events in `BEGIN:VCALENDAR/VERSION:2.0/PRODID:-//DublinLifeline//Planner//EN/END:VCALENDAR`, stable `UID`s as `${appt.id}@dublinlifeline`.

- [ ] **Step 6: Write failing tests for the store, implement `planner-store.ts`**

  ```ts
  import { describe, it, expect, beforeEach } from 'vitest';
  import { loadPlan, savePlan, STORAGE_KEY } from '$lib/utils/planner-store';

  beforeEach(() => localStorage.clear());

  describe('planner store', () => {
  	it('round-trips appointments', () => {
  		savePlan([
  			{
  				id: 'a',
  				title: 'T',
  				day: 'mon',
  				start: '09:00',
  				end: '10:00',
  				location: '',
  				notes: '',
  				orgId: null,
  				recurrence: 'once',
  				source: 'personal',
  				weekOf: '2026-09-14'
  			}
  		]);
  		expect(loadPlan()).toHaveLength(1);
  		expect(JSON.parse(localStorage.getItem(STORAGE_KEY)!)).toHaveLength(1);
  	});

  	it('returns [] on corrupt data instead of throwing', () => {
  		localStorage.setItem(STORAGE_KEY, '{broken');
  		expect(loadPlan()).toEqual([]);
  	});
  });
  ```

  (vitest environment: repo uses happy-dom/jsdom per devDependencies; if `localStorage` is unavailable in the configured environment, add a minimal in-memory stub at the top of the test file — do not add new devDependencies.)

- [ ] **Step 7: Run all three suites, then commit**

  Run: `npm run test:unit`
  Expected: PASS (all suites, no regressions).

  ```bash
  git add src/lib/utils/planner.ts src/lib/utils/ics.ts src/lib/utils/planner-store.ts src/test/unit/planner.test.ts src/test/unit/ics.test.ts src/test/unit/planner-store.test.ts && git commit -m "feat(planner): week math, recurrence, ics export and localStorage store"
  ```

### Task 3: `/planner` route + tab-bar entry

**Files:**

- Create: `src/routes/planner/+page.server.ts`
- Create: `src/routes/planner/+page.svelte`
- Modify: `src/routes/+layout.svelte` (add Planner tab with inline SVG icon, same pattern as existing three tabs)
- Modify: `src/lib/stores/lang.svelte.ts` (add `planner` label key + any new UI strings, following existing key style)

**Interfaces:**

- Consumes: `normalizeServices` + `services.json` (server load, same as `src/routes/+page.server.ts`), `meals.json`, `MealEntry`, `PlannerAppointment`, `weekDates`/`expandWeek`, `loadPlan`/`savePlan`, `appointmentToICS`/`weekToICS`, `DAY_KEYS`/`DAY_LABELS`, `t()` store.
- Produces: `/planner` page rendering week-grid (Mon–Sun columns on desktop, stacked day sections on mobile), `data` prop `{ services, meals }`.

- [ ] **Step 1: Write the server load (follows `src/routes/+page.server.ts` exactly)**

  ```ts
  import type { PageServerLoad } from './$types';
  import servicesData from '$lib/data/services.json';
  import mealsData from '$lib/data/meals.json';
  import { normalizeServices } from '$lib/utils/services';
  import type { MealEntry } from '$lib/types';

  export const load: PageServerLoad = async () => {
  	const services = normalizeServices(
  		servicesData.services as unknown as Record<string, unknown>[]
  	);
  	return { services, meals: mealsData as MealEntry[] };
  };
  ```

- [ ] **Step 2: Build `+page.svelte`**

  Requirements (no placeholders — implement all): week state (`weekOffset` int, Monday derived via `weekDates`), prev/today/next controls; per-day sections listing meal markers (read-only, from `meals` filtered by day) each with an "Add" button that creates a `source: 'meal'` weekly appointment pre-filled from the meal; personal appointment form (title, day, start, end, location, notes, org picker from `services`, recurrence select) for add + edit-in-place; delete with native `confirm()`; every mutation calls `savePlan`; on mount loads via `loadPlan()` (SSR guard — never touch `localStorage` during server render); device-only warning banner ("Your plan stays on this device — export a backup"); per-appointment `.ics` download via `Blob` + `URL.createObjectURL` + temp `<a download>`; all strings via `t()`; blocks are `<button>`s for keyboard access; tab-order and focus-visible styles match existing components.

- [ ] **Step 3: Add Planner tab to `src/routes/+layout.svelte` + `planner` key to `lang.svelte.ts`**

  Fourth `<a href="{base}/planner">` with inline stroke SVG (calendar glyph, same `tab-icon` class/attributes as siblings) and `<span class="tab-label">{t('planner')}</span>`; `aria-current` binding identical to siblings. Add `planner: 'Planner'` next to `directory`/`map`/`search` (plus any other locales the store defines — check the store for locale blocks first).

- [ ] **Step 4: Verify in browser + tests**

  Run: `npm run dev`, open `/planner`: add meal-derived + personal appointments, refresh (data persists), edit, delete, week paging, `.ics` download opens in calendar. Then run `npm run test:unit`, `npm run check`, `npm run lint`.
  Expected: no errors; fix and re-run until green.

- [ ] **Step 5: Commit**

  ```bash
  git add src/routes/planner src/routes/+layout.svelte src/lib/stores/lang.svelte.ts && git commit -m "feat(planner): week-grid route with meal markers, appointments and ics download"
  ```

### Task 4: JSON backup/restore + device-only warning copy

**Files:**

- Modify: `src/routes/planner/+page.svelte` (backup/restore controls + warning banner)
- Test: extend `src/test/unit/planner-store.test.ts` (export/import round-trip through `JSON.stringify(loadPlan())`)

**Interfaces:**

- Consumes: `loadPlan`/`savePlan` from Task 2.
- Produces: "Download backup" (serializes `loadPlan()` to `lifeline-planner-backup-YYYY-MM-DD.json`), "Restore" (`<input type="file" accept="application/json">`, validates each entry has `id/title/day/start` before `savePlan`, shows count or error string — no silent partial imports).

- [ ] **Step 1: Write the failing round-trip test**

  ```ts
  it('backup payload restores exactly', () => {
  	const appts = [
  		{
  			id: 'a',
  			title: 'T',
  			day: 'mon',
  			start: '09:00',
  			end: '10:00',
  			location: 'L',
  			notes: 'N',
  			orgId: null,
  			recurrence: 'weekly',
  			source: 'personal',
  			weekOf: '2026-09-14'
  		}
  	];
  	savePlan(appts as never);
  	const payload = JSON.stringify(loadPlan());
  	localStorage.clear();
  	savePlan(JSON.parse(payload));
  	expect(loadPlan()).toEqual(appts);
  });
  ```

- [ ] **Step 2: Implement backup/restore UI in `+page.svelte` + warning banner copy**

  Banner: "Your plan is stored only on this device. Download a backup to keep it safe." Restore validates shape, reports "Restored N appointments" or "Backup file invalid — nothing changed" via `t()` keys.

- [ ] **Step 3: Manual verify + full gate, then commit**

  Run: backup → delete all → restore → entries return; invalid file → error, data untouched. Then `npm run test:unit`, `npm run check`, `npm run lint`.

  ```bash
  git add src/routes/planner src/test/unit/planner-store.test.ts src/lib/stores/lang.svelte.ts && git commit -m "feat(planner): json backup restore and device-only warning"
  ```

### Task 5: Final verification pass

- [ ] **Step 1: Run the full gate**

  ```bash
  git status && git log --oneline -5
  npm run test:unit
  npm run check
  npm run lint
  npm run build
  ```

  Expected: clean tree except intended files, all suites pass, `svelte-check` 0 errors, prettier/eslint clean, static build succeeds (adapter-static must emit `/planner`).

- [ ] **Step 2: Manual acceptance (dev or preview)**

  Add → refresh → persists; backup → clear site data → restore; `.ics` (once + weekly) imports into a phone calendar with correct time/repeat; tab-bar Planner tab highlights; offline (devtools offline) planner still works.

- [ ] **Step 3: Push (only if explicitly requested)**

  Do not push unless the user asks.
