<script lang="ts">
	import { t } from '$lib/stores/lang.svelte';
	import type { PlannerAppointment } from '$lib/utils/planner';

	let {
		appt,
		date,
		onEdit,
		onDownload,
		onDelete
	}: {
		appt: PlannerAppointment;
		date: Date;
		onEdit: (appt: PlannerAppointment) => void;
		onDownload: (appt: PlannerAppointment, date: Date) => void;
		onDelete: (id: string) => void;
	} = $props();
</script>

<li class="appt-card">
	<div class="appt-main">
		<strong>{appt.title}</strong>
		<span class="appt-when">{appt.start}–{appt.end}{appt.location ? ` · ${appt.location}` : ''}</span>
	</div>
	<details class="card-menu">
		<summary aria-label={t('planner-actions')}>…</summary>
		<div class="menu-items">
			<button type="button" onclick={() => onEdit(appt)}>{t('planner-edit')}</button>
			<button type="button" onclick={() => onDownload(appt, date)}>{t('planner-download')}</button>
			<button type="button" onclick={() => onDelete(appt.id)}>{t('planner-delete')}</button>
		</div>
	</details>
</li>

<style>
	.appt-card {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-2);
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
		overflow-wrap: break-word;
	}
	.appt-when {
		color: var(--color-text-secondary);
		font-size: var(--text-sm);
		line-height: var(--leading-normal);
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
	.menu-items button:focus-visible {
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
</style>
