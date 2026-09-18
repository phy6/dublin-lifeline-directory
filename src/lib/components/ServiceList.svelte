<script lang="ts">
	import type { ServiceLocation } from '$lib/types';
	import { t } from '$lib/stores/lang.svelte';
	import ServiceCard from './ServiceCard.svelte';

	let {
		services,
		id = 'service-list',
		onReset
	}: { services: ServiceLocation[]; id?: string; onReset?: () => void } = $props();
</script>

<div class="service-list" {id}>
	{#each services as service (service.id)}
		<ServiceCard {service} />
	{:else}
		<div class="empty-state">
			<p>{t('no-matching-services')}</p>
			{#if onReset}
				<button onclick={onReset}>{t('clear-filters')}</button>
			{/if}
		</div>
	{/each}
</div>

<style>
	.service-list {
		display: flex;
		flex-direction: column;
		gap: 0;
		padding: 0;
	}
	@media (min-width: 700px) {
		.service-list {
			display: grid;
			grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
			gap: var(--space-3);
		}
	}
	.empty-state {
		grid-column: 1 / -1;
		text-align: center;
		padding: var(--space-5) var(--space-3);
		color: var(--color-text-secondary);
	}
	.empty-state p {
		font-size: var(--text-base);
		margin-bottom: var(--space-3);
	}
	.empty-state button {
		min-height: 48px;
		padding: var(--space-2) var(--space-4);
		border-radius: var(--radius-full);
		border: 0;
		background: var(--color-accent);
		color: var(--color-text-on-accent);
		font-size: var(--text-base);
		font-weight: 700;
		cursor: pointer;
		font-family: var(--font-sans);
	}
	.empty-state button:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
	}
</style>
