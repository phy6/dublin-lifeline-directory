<script lang="ts">
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/lang.svelte';
	import { DAY_KEYS, DAY_LABELS, type DayKey } from '$lib/utils/hours';
	import { monthGrid, type PlannerAppointment } from '$lib/utils/planner';
	import {
		weekDates,
		expandWeek,
		toISODate,
		mondayOf,
		dayKeyOf,
		isToday,
		countsForDate
	} from '$lib/utils/week';
	import { loadPlan, savePlan } from '$lib/utils/planner-io';
	import {
		parseBackup,
		serializeBackup,
		backupFilename,
		downloadFile
	} from '$lib/utils/planner-io';
	import { weekToICS } from '$lib/utils/ics';
	import AppointmentCard from '$lib/components/AppointmentCard.svelte';
	import AppointmentForm, {
		type AppointmentFormFields
	} from '$lib/components/AppointmentForm.svelte';
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
	let formApi: AppointmentForm | undefined = $state();

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
	/** Dots for a month cell: counts of meals + appointments landing on that date. */
	function dotsFor(date: Date): { meals: number; appts: number } {
		return countsForDate(plan, meals as MealEntry[], date);
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

	function openAdd(day: DayKey) {
		formApi?.openAdd(day);
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

	function saveFromForm(editingId: string | null, fields: AppointmentFormFields) {
		const weekOf = editingId
			? (plan.find((p) => p.id === editingId)?.weekOf ?? weekOfFor(fields.day))
			: weekOfFor(fields.day);
		if (editingId) {
			persist(
				plan.map((p) =>
					p.id === editingId
						? {
								...p,
								title: fields.title,
								day: fields.day,
								start: fields.start,
								end: fields.end,
								location: fields.location,
								notes: fields.notes,
								orgId: fields.orgId || null,
								recurrence: fields.recurrence,
								weekOf
							}
						: p
				)
			);
		} else {
			const appt: PlannerAppointment = {
				id: newId(),
				title: fields.title,
				day: fields.day,
				start: fields.start,
				end: fields.end,
				location: fields.location,
				notes: fields.notes,
				orgId: fields.orgId || null,
				recurrence: fields.recurrence,
				source: 'personal',
				weekOf
			};
			persist([...plan, appt]);
		}
	}

	function startEdit(appt: PlannerAppointment) {
		formApi?.openEdit(appt);
	}

	function removeAppt(id: string) {
		const appt = plan.find((p) => p.id === id);
		if (!appt) return;
		pendingDelete = { id, title: appt.title };
		deleteTrigger = document.activeElement instanceof HTMLElement ? document.activeElement : null;
		confirmDialog?.showModal();
		confirmBtn?.focus();
	}

	function confirmDelete() {
		const target = pendingDelete;
		if (target) {
			persist(plan.filter((p) => p.id !== target.id));
			formApi?.closeIfEditing(target.id);
			pendingDelete = null;
		}
		confirmDialog?.close();
		deleteTrigger?.focus();
	}

	function cancelDelete() {
		pendingDelete = null;
		confirmDialog?.close();
		deleteTrigger?.focus();
	}

	function downloadOne(appt: PlannerAppointment, date: Date) {
		downloadFile(`${appt.id}.ics`, weekToICS([{ appt, date }]), 'text/calendar');
	}

	function downloadWeek() {
		downloadFile(`planner-week-${toISODate(dates[0])}.ics`, weekToICS(expanded), 'text/calendar');
	}

	let backupMessage = $state('');
	let confirmDialog: HTMLDialogElement | undefined = $state();
	let confirmBtn: HTMLButtonElement | undefined = $state();
	let pendingDelete = $state<{ id: string; title: string } | null>(null);
	let deleteTrigger: HTMLElement | null = null;

	function downloadBackup() {
		downloadFile(backupFilename(), serializeBackup(plan), 'application/json');
	}

	async function restoreBackup(e: Event) {
		backupMessage = '';
		const input = e.target as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;
		const parsed = parseBackup(await file.text());
		if (!parsed) {
			backupMessage = t('planner-invalid');
		} else {
			persist(parsed);
			backupMessage = t('planner-restored').replace('{count}', String(parsed.length));
		}
		input.value = '';
	}

	// Days rendered by the current view: single day, full week, or (month handled separately).
	let visibleDays = $derived(view === 'day' ? [dayKeyOf(anchor)] : [...DAY_KEYS]);
	let visibleDates = $derived(view === 'day' ? [anchor] : dates);
</script>

<main id="main-content">
	<h1>{t('planner-title')}</h1>
	<p class="device-warning">{t('planner-device-warning')}</p>

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
			role="group"
			aria-label={`${MONTH_LABELS[anchor.getMonth()]} ${anchor.getFullYear()}`}
		>
			{#each DAY_LABELS as label (label)}
				<span class="month-dow">{label}</span>
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
					<h2>
						{DAY_LABELS[DAY_KEYS.indexOf(day)]} <span class="day-date">{toISODate(date)}</span>
					</h2>
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
							<AppointmentCard
								{appt}
								date={apptDate}
								onEdit={startEdit}
								onDownload={downloadOne}
								onDelete={removeAppt}
							/>
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
</main>

<dialog
	bind:this={confirmDialog}
	class="confirm"
	aria-label={t('planner-delete')}
	onclick={(e) => {
		if (e.target === confirmDialog) cancelDelete();
	}}
>
	{#if pendingDelete}
		<h2>{t('planner-delete')}</h2>
		<p>{t('planner-confirm-delete').replace('{title}', pendingDelete.title)}</p>
		<div class="form-actions">
			<button type="button" bind:this={confirmBtn} onclick={confirmDelete}>
				{t('planner-delete')}
			</button>
			<button type="button" onclick={cancelDelete}>{t('planner-cancel')}</button>
		</div>
	{/if}
</dialog>

<AppointmentForm
	bind:this={formApi}
	services={services as ServiceLocation[]}
	onSave={saveFromForm}
/>

<style>
	h1 {
		padding: 0 var(--space-3);
		color: var(--color-accent);
		margin-bottom: var(--space-2);
		font-size: var(--text-2xl);
		line-height: var(--leading-tight);
		text-wrap: balance;
	}
	@media (max-width: 600px) {
		h1 {
			font-size: var(--text-xl);
		}
	}
	.device-warning {
		margin: 0 var(--space-3) var(--space-3);
		padding: var(--space-2) var(--space-3);
		background: var(--color-warning-bg, #fff8e1);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		font-size: var(--text-base);
		line-height: var(--leading-relaxed);
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
			grid-template-columns: repeat(3, minmax(0, 1fr));
		}
	}
	@media (max-width: 600px) {
		.week-grid:not(.single) {
			grid-template-columns: 1fr;
		}
		.month-grid {
			max-width: 24rem;
		}
		.month-cell {
			min-height: 44px;
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
	.meal-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-2);
		opacity: 0.85;
	}
	.week-controls button:focus-visible,
	.inline-add:focus-visible,
	.month-cell:focus-visible,
	ul button:focus-visible,
	input:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
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
	dialog.confirm {
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		padding: var(--space-3);
		max-width: min(24rem, 90vw);
		background: var(--color-surface);
		color: inherit;
	}
	dialog.confirm::backdrop {
		background: rgb(0 0 0 / 0.4);
	}
	dialog.confirm h2 {
		margin: 0 0 var(--space-2);
		font-size: var(--text-lg);
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
