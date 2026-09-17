<script lang="ts">
	import { base } from '$app/paths';
	import type { ServiceLocation } from '$lib/types';
	import { getOpenNowStatus } from '$lib/utils/hours';

	let { service }: { service: ServiceLocation } = $props();
	const openStatus = $derived(getOpenNowStatus(service.hours));
	const hourEntries = $derived(
		service.hours && typeof service.hours === 'object' ? Object.entries(service.hours) : []
	);
</script>

<article class="card">
	<div class="card-header">
		<div class="category">{service.category}</div>
		{#if openStatus === 'open'}
			<span class="open-badge" aria-label="Open now">Open now</span>
		{:else if openStatus === 'closed'}
			<span class="closed-badge" aria-label="Closed now">Closed</span>
		{/if}
	</div>
	<h3>{service.name}</h3>
	<p class="address">{service.address}</p>
	<p class="phone">{service.phone}</p>
	<div class="tags">
		{#each (service.tags ?? []).slice(0, 4) as tag (tag)}
			<span class="tag">{tag}</span>
		{/each}
	</div>
	<div class="hours">
		{#if typeof service.hours === 'string'}
			<span class="day">{service.hours}</span>
		{:else}
			{#each hourEntries as [day, hours] (day)}
				<span class="day">{day}: {hours}</span>
			{/each}
		{/if}
	</div>
	<a href="{base}/service/{service.id}" class="card-link">View details</a>
</article>

<style>
	.card {
		display: flex;
		flex-direction: column;
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		padding: var(--space-3);
		box-shadow: var(--shadow-md);
		text-decoration: none;
		color: inherit;
		transition:
			transform 0.2s,
			box-shadow 0.2s;
		max-width: 100%;
		box-sizing: border-box;
		border: 1px solid var(--color-border);
	}
	@media (prefers-reduced-motion: no-preference) {
		.card:hover {
			transform: translateY(-2px);
			box-shadow: var(--shadow-lg);
		}
		.card:active {
			transform: scale(0.98);
		}
	}
	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-2);
		flex-wrap: wrap;
		gap: var(--space-1);
	}
	.category {
		background: var(--color-accent);
		color: var(--color-text-on-accent);
		padding: 2px 8px;
		border-radius: var(--radius-sm);
		font-size: var(--text-xs);
		display: inline-block;
	}
	.open-badge {
		background: var(--color-success);
		color: var(--color-text-on-accent);
		padding: 2px 8px;
		border-radius: var(--radius-sm);
		font-size: var(--text-xs);
		font-weight: bold;
		display: inline-block;
	}
	.closed-badge {
		background: var(--color-danger);
		color: var(--color-text-on-accent);
		padding: 2px 8px;
		border-radius: var(--radius-sm);
		font-size: var(--text-xs);
		font-weight: bold;
		display: inline-block;
	}
	h3 {
		margin: var(--space-1) 0;
		font-size: var(--text-lg);
		word-wrap: break-word;
	}
	.address {
		color: var(--color-text-secondary);
		margin: var(--space-1) 0;
		font-size: var(--text-sm);
		word-wrap: break-word;
	}
	.phone {
		color: var(--color-accent);
		margin: var(--space-1) 0;
		font-size: var(--text-sm);
	}
	.tags {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-1);
		margin: var(--space-2) 0;
	}
	.tag {
		background: var(--color-accent-container);
		color: var(--color-accent-on-container);
		padding: 2px 6px;
		border-radius: var(--radius-sm);
		font-size: var(--text-xs);
	}
	.day {
		display: block;
		font-size: var(--text-xs);
		color: var(--color-text-muted);
		margin: 1px 0;
		line-height: var(--leading-relaxed);
		text-wrap: pretty;
	}
	.hours {
		margin-top: var(--space-2);
	}
	.card-link {
		margin-top: auto;
		padding: var(--space-2) var(--space-3);
		background: var(--color-accent);
		color: var(--color-text-on-accent);
		border-radius: var(--radius-md);
		text-decoration: none;
		font-weight: 600;
		font-size: var(--text-sm);
		text-align: center;
		transition: background-color 0.15s;
	}
	@media (prefers-reduced-motion: no-preference) {
		.card-link:hover {
			background: var(--color-accent-hover);
		}
		.card-link:active {
			transform: scale(0.98);
		}
	}
	.card-link:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
	}
	@media (max-width: 600px) {
		.card {
			padding: var(--space-2);
		}
		h3 {
			font-size: var(--text-base);
		}
		.address,
		.phone,
		.day,
		.tag {
			font-size: var(--text-xs);
		}
	}
</style>
