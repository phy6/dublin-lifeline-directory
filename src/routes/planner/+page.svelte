<script lang="ts">
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/lang.svelte';
	import { DAY_KEYS, DAY_LABELS, type DayKey } from '$lib/utils/hours';
	import { weekDates, expandWeek, toISODate, type PlannerAppointment } from '$lib/utils/planner';
	import { loadPlan, savePlan } from '$lib/utils/planner-store';
	import { appointmentToICS, weekToICS } from '$lib/utils/ics';
	import type { MealEntry } from '$lib/types';
	import type { ServiceLocation } from '$lib/types';

	let { data } = $props<{ data: { services: ServiceLocation[]; meals: MealEntry[] } }>();
	const services = data.services;
	const meals = data.meals;

	let weekOffset = $state(0);
	let plan = $state<PlannerAppointment[]>([]);
	let editingId = $state<string | null>(null);
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

	function mondayOf(offset: number): Date {
		const now = new Date();
		const base = new Date(now.getFullYear(), now.getMonth(), now.getDate());
		const dow = (base.getDay() + 6) % 7;
		return new Date(base.getFullYear(), base.getMonth(), base.getDate() - dow + offset * 7);
	}

	let monday = $derived(mondayOf(weekOffset));
	let dates = $derived(weekDates(monday));
	let expanded = $derived(expandWeek(plan, monday));

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

	function resetForm() {
		form = {
			title: '',
			day: 'mon',
			start: '09:00',
			end: '10:00',
			location: '',
			notes: '',
			orgId: '',
			recurrence: 'once'
		};
		editingId = null;
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
		resetForm();
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
	}

	function removeAppt(id: string) {
		if (!confirm(t('planner-delete'))) return;
		persist(plan.filter((p) => p.id !== id));
		if (editingId === id) resetForm();
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
		const ics = [
			'BEGIN:VCALENDAR',
			'VERSION:2.0',
			'PRODID:-//DublinLifeline//Planner//EN',
			appointmentToICS(appt, date),
			'END:VCALENDAR'
		].join('\r\n');
		download(`${appt.id}.ics`, ics);
	}

	function downloadWeek() {
		download(`planner-week-${toISODate(dates[0])}.ics`, weekToICS(expanded));
	}
</script>

<h1>{t('planner-title')}</h1>
<p class="device-warning" role="note">{t('planner-device-warning')}</p>

<div class="week-controls" role="group" aria-label={t('planner-title')}>
	<button type="button" onclick={() => (weekOffset -= 1)}>← {t('planner-prev')}</button>
	<button type="button" onclick={() => (weekOffset = 0)}>{t('planner-today')}</button>
	<button type="button" onclick={() => (weekOffset += 1)}>{t('planner-next')} →</button>
	<button type="button" onclick={downloadWeek}>{t('planner-download-week')}</button>
</div>

<div class="week-grid">
	{#each DAY_KEYS as day, i (day)}
		<section class="day-col" aria-label={`${DAY_LABELS[i]} ${toISODate(dates[i])}`}>
			<h2>{DAY_LABELS[i]} <span class="day-date">{toISODate(dates[i])}</span></h2>
			<h3>{t('planner-meals')}</h3>
			<ul>
				{#each mealsForDay(day) as meal (meal.id)}
					<li>
						<span>{meal.mealType} · {meal.start}–{meal.end} · {orgName(meal.orgId)}</span>
						<button type="button" onclick={() => addFromMeal(meal, day)}>{t('planner-add')}</button>
					</li>
				{/each}
			</ul>
			<h3>{t('planner-appointments')}</h3>
			<ul>
				{#each apptsForDay(day) as { appt, date } (appt.id)}
					<li>
						<button
							type="button"
							class="appt-block"
							onclick={() => startEdit(appt)}
							aria-label={`${appt.title} ${appt.start}-${appt.end}`}
						>
							<strong>{appt.title}</strong>
							<span>{appt.start}–{appt.end}{appt.location ? ` · ${appt.location}` : ''}</span>
						</button>
						<div class="appt-actions">
							<button type="button" onclick={() => startEdit(appt)}>{t('planner-edit')}</button>
							<button type="button" onclick={() => removeAppt(appt.id)}
								>{t('planner-delete')}</button
							>
							<button type="button" onclick={() => downloadOne(appt, date)}
								>{t('planner-download')}</button
							>
						</div>
					</li>
				{:else}
					<li class="empty">{t('planner-empty')}</li>
				{/each}
			</ul>
		</section>
	{/each}
</div>

<form class="appt-form" onsubmit={submitForm}>
	<h2>{editingId ? t('planner-edit-title') : t('planner-add-title')}</h2>
	<label>{t('planner-title-label')}<input bind:value={form.title} required maxlength="120" /></label
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
		{#if editingId}
			<button type="button" onclick={resetForm}>{t('planner-cancel')}</button>
		{/if}
	</div>
</form>

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
	@media (max-width: 900px) {
		.week-grid {
			grid-template-columns: 1fr;
		}
	}
	.day-col {
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		padding: var(--space-2);
		background: var(--color-surface);
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
	.appt-block {
		display: block;
		width: 100%;
		text-align: left;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		background: var(--color-surface);
		padding: var(--space-2);
		cursor: pointer;
		font: inherit;
		color: inherit;
	}
	.appt-block:focus-visible,
	.week-controls button:focus-visible,
	.appt-actions button:focus-visible,
	.form-actions button:focus-visible,
	ul button:focus-visible,
	input:focus-visible,
	select:focus-visible,
	textarea:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
	}
	.appt-actions {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-1);
		margin-top: var(--space-1);
	}
	.appt-form {
		display: grid;
		gap: var(--space-2);
		max-width: 32rem;
		padding: 0 var(--space-3) var(--space-4);
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
