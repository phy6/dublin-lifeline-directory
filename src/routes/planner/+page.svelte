<script lang="ts">
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/lang.svelte';
	import { DAY_KEYS, DAY_LABELS, type DayKey } from '$lib/utils/hours';
	import {
		weekDates,
		expandWeek,
		monthGrid,
		toISODate,
		type PlannerAppointment
	} from '$lib/utils/planner';
	import { loadPlan, savePlan } from '$lib/utils/planner-store';
	import { weekToICS } from '$lib/utils/ics';
	import type { MealEntry } from '$lib/types';
	import type { ServiceLocation } from '$lib/types';

	const MONTH_LABELS = [
		'January',
		'February',
		'March',
		'April',
		'May',
		'June',
		'July',
		'August',
		'September',
		'October',
		'November',
		'December'
	];

	let { data } = $props<{ data: { services: ServiceLocation[]; meals: MealEntry[] } }>();
	const services = data.services;
	const meals = data.meals;

	type PlannerView = 'day' | 'week' | 'month';
	let view = $state<PlannerView>('week');
	const nowInit = new Date();
	let anchor = $state(new Date(nowInit.getFullYear(), nowInit.getMonth(), nowInit.getDate()));
	let plan = $state<PlannerAppointment[]>([]);
	let editingId = $state<string | null>(null);
	let sheet: HTMLDialogElement | undefined = $state();
	let form = $state({
		title: '',
		day: 'mon' as DayKey,
		start: '09:00',
		end: '10:00',
		location: '',
		notes: '',
		orgId: '' as string,
		recurrence: 'once' as 'once' | 'weekly'
	});

	function mondayOf(base: Date): Date {
		const dow = (base.getDay() + 6) % 7;
		return new Date(base.getFullYear(), base.getMonth(), base.getDate() - dow);
	}

	let monday = $derived(mondayOf(anchor));
	let dates = $derived(weekDates(monday));
	let expanded = $derived(expandWeek(plan, monday));
	let monthRows = $derived(monthGrid(anchor.getFullYear(), anchor.getMonth()));

	function apptsForDay(day: DayKey) {
		return expanded.filter((e) => e.appt.day === day);
	}
	function mealsForDay(day: DayKey) {
		return (meals as MealEntry[]).filter((m: MealEntry) => m.days.includes(day));
	}
	function orgName(id: string | null): string {
		if (!id) return '';
		return (services as ServiceLocation[]).find((s: ServiceLocation) => s.id === id)?.name ?? id;
	}
	function dayKeyOf(date: Date): DayKey {
		return DAY_KEYS[(date.getDay() + 6) % 7];
	}
	/** Dots for a month cell: counts of meals + appointments landing on that date. */
	function dotsFor(date: Date): { meals: number; appts: number } {
		const key = dayKeyOf(date);
		const iso = toISODate(date);
		const mealCount = (meals as MealEntry[]).filter((m: MealEntry) => m.days.includes(key)).length;
		const apptCount = plan.filter((p) => {
			if (DAY_KEYS.indexOf(p.day) !== (date.getDay() + 6) % 7) return false;
			return p.recurrence === 'weekly' || p.weekOf === iso;
		}).length;
		return { meals: mealCount, appts: apptCount };
	}
	function isToday(date: Date): boolean {
		const now = new Date();
		return (
			date.getFullYear() === now.getFullYear() &&
			date.getMonth() === now.getMonth() &&
			date.getDate() === now.getDate()
		);
	}

	function shift(days: number) {
		anchor = new Date(anchor.getFullYear(), anchor.getMonth(), anchor.getDate() + days);
	}
	function shiftMonth(delta: number) {
		anchor = new Date(anchor.getFullYear(), anchor.getMonth() + delta, 1);
	}
	function goToday() {
		const now = new Date();
		anchor = new Date(now.getFullYear(), now.getMonth(), now.getDate());
	}
	function openMonthDay(date: Date) {
		anchor = new Date(date.getFullYear(), date.getMonth(), date.getDate());
		view = 'day';
	}

	onMount(() => {
		plan = loadPlan();
	});

	function persist(next: PlannerAppointment[]) {
		plan = next;
		savePlan(plan);
	}

	function newId(): string {
		return typeof crypto !== 'undefined' && 'randomUUID' in crypto
			? crypto.randomUUID()
			: `appt-${Date.now()}-${Math.floor(Math.random() * 1e6)}`;
	}

	function weekOfFor(day: DayKey): string {
		const idx = DAY_KEYS.indexOf(day);
		return toISODate(dates[idx]);
	}

	function openSheet() {
		sheet?.showModal();
	}
	function openAdd(day: DayKey) {
		editingId = null;
		form = {
			title: '',
			day,
			start: '09:00',
			end: '10:00',
			location: '',
			notes: '',
			orgId: '',
			recurrence: 'once'
		};
		openSheet();
	}
	function closeSheet() {
		sheet?.close();
	}

	function addFromMeal(meal: MealEntry, day: DayKey) {
		const appt: PlannerAppointment = {
			id: newId(),
			title: `${meal.mealType} — ${orgName(meal.orgId) || meal.address}`,
			day,
			start: meal.start,
			end: meal.end,
			location: meal.address,
			notes: meal.notes,
			orgId: meal.orgId,
			recurrence: 'weekly',
			source: 'meal',
			weekOf: weekOfFor(day)
		};
		persist([...plan, appt]);
	}

	function submitForm(e: Event) {
		e.preventDefault();
		if (!form.title.trim()) return;
		const weekOf = editingId
			? (plan.find((p) => p.id === editingId)?.weekOf ?? weekOfFor(form.day))
			: weekOfFor(form.day);
		if (editingId) {
			persist(
				plan.map((p) =>
					p.id === editingId
						? {
								...p,
								title: form.title.trim(),
								day: form.day,
								start: form.start,
								end: form.end,
								location: form.location,
								notes: form.notes,
								orgId: form.orgId || null,
								recurrence: form.recurrence,
								weekOf
							}
						: p
				)
			);
		} else {
			const appt: PlannerAppointment = {
				id: newId(),
				title: form.title.trim(),
				day: form.day,
				start: form.start,
				end: form.end,
				location: form.location,
				notes: form.notes,
				orgId: form.orgId || null,
				recurrence: form.recurrence,
				source: 'personal',
				weekOf
			};
			persist([...plan, appt]);
		}
		editingId = null;
		closeSheet();
	}

	function startEdit(appt: PlannerAppointment) {
		editingId = appt.id;
		form = {
			title: appt.title,
			day: appt.day,
			start: appt.start,
			end: appt.end,
			location: appt.location,
			notes: appt.notes,
			orgId: appt.orgId ?? '',
			recurrence: appt.recurrence
		};
		openSheet();
	}

	function removeAppt(id: string) {
		if (!confirm(t('planner-delete'))) return;
		persist(plan.filter((p) => p.id !== id));
		if (editingId === id) {
			editingId = null;
			closeSheet();
		}
	}

	function download(filename: string, text: string) {
		const blob = new Blob([text], { type: 'text/calendar' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = filename;
		document.body.appendChild(a);
		a.click();
		a.remove();
		URL.revokeObjectURL(url);
	}

	function downloadOne(appt: PlannerAppointment, date: Date) {
		download(`${appt.id}.ics`, weekToICS([{ appt, date }]));
	}

	function downloadWeek() {
		download(`planner-week-${toISODate(dates[0])}.ics`, weekToICS(expanded));
	}

	let backupMessage = $state('');

	function downloadBackup() {
		const now = new Date();
		const stamp = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
		const blob = new Blob([JSON.stringify(loadPlan())], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `lifeline-planner-backup-${stamp}.json`;
		document.body.appendChild(a);
		a.click();
		a.remove();
		URL.revokeObjectURL(url);
	}

	function isValidEntry(e: unknown): e is PlannerAppointment {
		if (typeof e !== 'object' || e === null) return false;
		const o = e as Record<string, unknown>;
		return (
			typeof o.id === 'string' &&
			typeof o.title === 'string' &&
			typeof o.day === 'string' &&
			typeof o.start === 'string'
		);
	}

	async function restoreBackup(e: Event) {
		backupMessage = '';
		const input = e.target as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;
		try {
			const parsed: unknown = JSON.parse(await file.text());
			if (!Array.isArray(parsed) || !parsed.every(isValidEntry)) {
				backupMessage = t('planner-invalid');
				return;
			}
			persist(parsed);
			backupMessage = t('planner-restored').replace('{count}', String(parsed.length));
		} catch {
			backupMessage = t('planner-invalid');
		} finally {
			input.value = '';
		}
	}

	function sheetBackdrop(e: MouseEvent) {
		if (e.target === sheet) closeSheet();
	}

	// Days rendered by the current view: single day, full week, or (month handled separately).
	let visibleDays = $derived(view === 'day' ? [dayKeyOf(anchor)] : [...DAY_KEYS]);
	let visibleDates = $derived(view === 'day' ? [anchor] : dates);
</script>

<h1>{t('planner-title')}</h1>
<p class="device-warning" role="note">{t('planner-device-warning')}</p>

<div class="view-switch" role="group" aria-label={t('planner-view')}>
	<button type="button" aria-pressed={view === 'day'} onclick={() => (view = 'day')}
		>{t('planner-view-day')}</button
	>
	<button type="button" aria-pressed={view === 'week'} onclick={() => (view = 'week')}
		>{t('planner-view-week')}</button
	>
	<button type="button" aria-pressed={view === 'month'} onclick={() => (view = 'month')}
		>{t('planner-view-month')}</button
	>
</div>

<div class="week-controls" role="group" aria-label={t('planner-title')}>
	{#if view === 'day'}
		<button type="button" onclick={() => shift(-1)}>← {t('planner-prev-day')}</button>
		<button type="button" onclick={goToday}>{t('planner-today')}</button>
		<button type="button" onclick={() => shift(1)}>{t('planner-next-day')} →</button>
	{:else if view === 'week'}
		<button type="button" onclick={() => shift(-7)}>← {t('planner-prev')}</button>
		<button type="button" onclick={goToday}>{t('planner-today')}</button>
		<button type="button" onclick={() => shift(7)}>{t('planner-next')} →</button>
		<button type="button" onclick={downloadWeek}>{t('planner-download-week')}</button>
	{:else}
		<button type="button" onclick={() => shiftMonth(-1)}>← {t('planner-prev-month')}</button>
		<button type="button" onclick={goToday}>{t('planner-today')}</button>
		<button type="button" onclick={() => shiftMonth(1)}>{t('planner-next-month')} →</button>
	{/if}
	<button type="button" onclick={downloadBackup}>{t('planner-backup')}</button>
	<label
		>{t('planner-restore')}<input
			type="file"
			accept="application/json"
			onchange={restoreBackup}
		/></label
	>
</div>
{#if backupMessage}<p role="status">{backupMessage}</p>{/if}

{#if view === 'month'}
	<h2 class="month-title">{MONTH_LABELS[anchor.getMonth()]} {anchor.getFullYear()}</h2>
	<div
		class="month-grid"
		role="grid"
		aria-label={`${MONTH_LABELS[anchor.getMonth()]} ${anchor.getFullYear()}`}
	>
		{#each DAY_LABELS as label (label)}
			<span class="month-dow" aria-hidden="true">{label}</span>
		{/each}
		{#each monthRows.flat() as cell (cell ? toISODate(cell) : `pad-${cell}`)}
			{#if cell}
				{@const dots = dotsFor(cell)}
				<button
					type="button"
					class="month-cell"
					class:today={isToday(cell)}
					onclick={() => openMonthDay(cell)}
					aria-label={`${toISODate(cell)}: ${dots.appts} appointments, ${dots.meals} meals`}
				>
					<span class="month-num">{cell.getDate()}</span>
					<span class="dots" aria-hidden="true">
						{#if dots.meals > 0}<i class="dot meal"></i>{/if}
						{#if dots.appts > 0}<i class="dot appt"></i>{/if}
					</span>
				</button>
			{:else}
				<span class="month-cell pad" aria-hidden="true"></span>
			{/if}
		{/each}
	</div>
{:else}
	<div class="week-grid" class:single={view === 'day'}>
		{#each visibleDays as day, i (day)}
			{@const date = visibleDates[i]}
			<section
				class="day-col"
				class:today={isToday(date)}
				aria-label={`${DAY_LABELS[DAY_KEYS.indexOf(day)]} ${toISODate(date)}`}
			>
				<h2>{DAY_LABELS[DAY_KEYS.indexOf(day)]} <span class="day-date">{toISODate(date)}</span></h2>
				{#if mealsForDay(day).length > 0}
					<h3>{t('planner-meals')}</h3>
					<ul>
						{#each mealsForDay(day) as meal (meal.id)}
							<li class="meal-row">
								<span>{meal.mealType} · {meal.start}–{meal.end} · {orgName(meal.orgId)}</span>
								<button type="button" onclick={() => addFromMeal(meal, day)}
									>{t('planner-add')}</button
								>
							</li>
						{/each}
					</ul>
				{/if}
				<h3>{t('planner-appointments')}</h3>
				<ul>
					{#each apptsForDay(day) as { appt, date: apptDate } (appt.id)}
						<li class="appt-card">
							<div class="appt-main">
								<strong>{appt.title}</strong>
								<span class="appt-when"
									>{appt.start}–{appt.end}{appt.location ? ` · ${appt.location}` : ''}</span
								>
							</div>
							<details class="card-menu">
								<summary aria-label={t('planner-actions')}>…</summary>
								<div class="menu-items">
									<button type="button" onclick={() => startEdit(appt)}>{t('planner-edit')}</button>
									<button type="button" onclick={() => downloadOne(appt, apptDate)}
										>{t('planner-download')}</button
									>
									<button type="button" onclick={() => removeAppt(appt.id)}
										>{t('planner-delete')}</button
									>
								</div>
							</details>
						</li>
					{:else}
						<li class="empty">{t('planner-empty')}</li>
					{/each}
				</ul>
				<button type="button" class="inline-add" onclick={() => openAdd(day)}
					>+ {t('planner-add-appt')}</button
				>
			</section>
		{/each}
	</div>
{/if}

<dialog bind:this={sheet} class="sheet" onclick={sheetBackdrop} aria-label={t('planner-add-title')}>
	<form class="appt-form" method="dialog" onsubmit={submitForm}>
		<h2>{editingId ? t('planner-edit-title') : t('planner-add-title')}</h2>
		<label
			>{t('planner-title-label')}<input bind:value={form.title} required maxlength="120" /></label
		>
		<label
			>{t('planner-day')}
			<select bind:value={form.day}>
				{#each DAY_KEYS as d, i (d)}
					<option value={d}>{DAY_LABELS[i]}</option>
				{/each}
			</select>
		</label>
		<label>{t('planner-start')}<input type="time" bind:value={form.start} required /></label>
		<label>{t('planner-end')}<input type="time" bind:value={form.end} required /></label>
		<label>{t('planner-location')}<input bind:value={form.location} maxlength="200" /></label>
		<label
			>{t('planner-notes')}<textarea bind:value={form.notes} rows="2" maxlength="500"
			></textarea></label
		>
		<label
			>{t('planner-org')}
			<select bind:value={form.orgId}>
				<option value="">{t('planner-no-org')}</option>
				{#each services as s (s.id)}
					<option value={s.id}>{s.name}</option>
				{/each}
			</select>
		</label>
		<label
			>{t('planner-recurrence')}
			<select bind:value={form.recurrence}>
				<option value="once">{t('planner-once')}</option>
				<option value="weekly">{t('planner-weekly')}</option>
			</select>
		</label>
		<div class="form-actions">
			<button type="submit">{t('planner-save')}</button>
			<button type="button" onclick={closeSheet}>{t('planner-cancel')}</button>
		</div>
	</form>
</dialog>

<style>
	h1 {
		padding: 0 var(--space-3);
	}
	.device-warning {
		margin: 0 var(--space-3) var(--space-3);
		padding: var(--space-2) var(--space-3);
		background: var(--color-warning-bg, #fff8e1);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
	}
	.view-switch {
		display: flex;
		gap: var(--space-1);
		padding: 0 var(--space-3) var(--space-2);
	}
	.view-switch button[aria-pressed='true'] {
		font-weight: 700;
		text-decoration: underline;
		text-underline-offset: 3px;
	}
	.week-controls {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
		padding: 0 var(--space-3) var(--space-3);
	}
	.week-grid {
		display: grid;
		grid-template-columns: repeat(7, minmax(0, 1fr));
		gap: var(--space-2);
		padding: 0 var(--space-3) var(--space-4);
	}
	.week-grid.single {
		grid-template-columns: minmax(0, 32rem);
	}
	@media (max-width: 900px) {
		.week-grid:not(.single) {
			grid-template-columns: 1fr;
		}
	}
	.day-col {
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		padding: var(--space-2);
		background: var(--color-surface);
	}
	.day-col.today {
		border-width: 2px;
		border-color: var(--color-focus-ring);
	}
	.day-col h2 {
		margin: 0 0 var(--space-1);
		font-size: var(--text-sm);
	}
	.day-date {
		color: var(--color-text-secondary);
		font-weight: 400;
	}
	.day-col ul {
		list-style: none;
		margin: 0 0 var(--space-2);
		padding: 0;
		display: grid;
		gap: var(--space-1);
	}
	.meal-row,
	.appt-card {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-2);
	}
	.meal-row {
		opacity: 0.85;
	}
	.appt-card {
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		background: var(--color-surface);
		padding: var(--space-2);
		border-left-width: 4px;
		border-left-color: var(--color-focus-ring);
	}
	.appt-main {
		display: grid;
		gap: 2px;
		min-width: 0;
	}
	.appt-when {
		color: var(--color-text-secondary);
		font-size: var(--text-sm);
	}
	.card-menu {
		position: relative;
		flex-shrink: 0;
	}
	.card-menu summary {
		list-style: none;
		cursor: pointer;
		min-width: 44px;
		min-height: 44px;
		display: grid;
		place-items: center;
		font-size: 1.25rem;
		letter-spacing: 1px;
		border-radius: var(--radius-sm);
	}
	.card-menu summary::-webkit-details-marker {
		display: none;
	}
	.card-menu summary:focus-visible,
	.menu-items button:focus-visible,
	.view-switch button:focus-visible,
	.week-controls button:focus-visible,
	.inline-add:focus-visible,
	.month-cell:focus-visible,
	ul button:focus-visible,
	input:focus-visible,
	select:focus-visible,
	textarea:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
	}
	.menu-items {
		position: absolute;
		right: 0;
		top: 100%;
		z-index: 10;
		display: grid;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		box-shadow: 0 4px 16px rgb(0 0 0 / 0.15);
		min-width: 12rem;
	}
	.menu-items button {
		text-align: left;
		background: none;
		border: 0;
		padding: var(--space-2) var(--space-3);
		min-height: 44px;
		cursor: pointer;
		font: inherit;
		color: inherit;
	}
	.inline-add {
		width: 100%;
		background: none;
		border: 1px dashed var(--color-border);
		border-radius: var(--radius-sm);
		color: var(--color-text-secondary);
		padding: var(--space-2);
		cursor: pointer;
		font: inherit;
	}
	.month-title {
		padding: 0 var(--space-3);
	}
	.month-grid {
		display: grid;
		grid-template-columns: repeat(7, minmax(0, 1fr));
		gap: 2px;
		padding: 0 var(--space-3) var(--space-4);
		max-width: 40rem;
	}
	.month-dow {
		text-align: center;
		font-size: var(--text-sm);
		color: var(--color-text-secondary);
		padding: var(--space-1) 0;
	}
	.month-cell {
		aspect-ratio: 1;
		display: grid;
		place-items: center;
		align-content: center;
		gap: 2px;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		background: var(--color-surface);
		cursor: pointer;
		font: inherit;
		color: inherit;
	}
	.month-cell.pad {
		border: 0;
		background: none;
	}
	.month-cell.today .month-num {
		font-weight: 700;
		text-decoration: underline;
		text-underline-offset: 3px;
	}
	.dots {
		display: flex;
		gap: 3px;
		min-height: 6px;
	}
	.dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--color-text-secondary);
	}
	.dot.appt {
		background: var(--color-focus-ring);
	}
	dialog.sheet {
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm) var(--radius-sm) 0 0;
		padding: 0;
		margin: auto auto 0;
		width: min(32rem, 100vw);
		max-height: 90dvh;
		overflow: auto;
		background: var(--color-surface);
		color: inherit;
	}
	dialog.sheet::backdrop {
		background: rgb(0 0 0 / 0.4);
	}
	.appt-form {
		display: grid;
		gap: var(--space-2);
		padding: var(--space-3);
	}
	.appt-form label {
		display: grid;
		gap: 4px;
		font-weight: 600;
	}
	.form-actions {
		display: flex;
		gap: var(--space-2);
	}
	button {
		min-height: 44px;
		cursor: pointer;
	}
</style>
