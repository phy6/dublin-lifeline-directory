<script lang="ts">
	import { t } from '$lib/stores/lang.svelte';
	import { DAY_KEYS, DAY_LABELS, type DayKey } from '$lib/utils/hours';
	import type { PlannerAppointment } from '$lib/utils/planner';
	import type { ServiceLocation } from '$lib/types';

	export interface AppointmentFormFields {
		title: string;
		day: DayKey;
		start: string;
		end: string;
		location: string;
		notes: string;
		orgId: string;
		recurrence: 'once' | 'weekly';
	}

	let {
		services,
		onSave
	}: {
		services: ServiceLocation[];
		onSave: (editingId: string | null, fields: AppointmentFormFields) => void;
	} = $props();

	let sheet: HTMLDialogElement | undefined = $state();
	let editingId = $state<string | null>(null);
	let form = $state<AppointmentFormFields>({
		title: '',
		day: 'mon',
		start: '09:00',
		end: '10:00',
		location: '',
		notes: '',
		orgId: '',
		recurrence: 'once'
	});

	export function openAdd(day: DayKey): void {
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
		sheet?.showModal();
	}

	export function openEdit(appt: PlannerAppointment): void {		editingId = appt.id;
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
		sheet?.showModal();
	}

	function closeSheet(): void {
		sheet?.close();
	}

	export function closeIfEditing(id: string): void {
		if (editingId === id) {
			editingId = null;
			closeSheet();
		}
	}

	function sheetBackdrop(e: MouseEvent): void {
		if (e.target === sheet) closeSheet();
	}

	function submitForm(e: Event): void {
		e.preventDefault();
		if (!form.title.trim()) return;
		onSave(editingId, { ...form, title: form.title.trim() });
		editingId = null;
		closeSheet();
	}
</script>

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
			>{t('planner-notes')}<textarea bind:value={form.notes} rows="2" maxlength="500"></textarea></label
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
	input:focus-visible,
	select:focus-visible,
	textarea:focus-visible,
	button:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
	}
</style>
