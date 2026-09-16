<script lang="ts">
	import type { ServiceLocation } from '$lib/types';
	import { getOpenNowStatus } from '$lib/utils/hours';

	let { service }: { service: ServiceLocation } = $props();
	const openStatus = $derived(getOpenNowStatus(service.hours));
</script>

<a href="/service/{service.id}" class="card">
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
		{#each service.tags.slice(0, 4) as tag (tag)}
			<span class="tag">{tag}</span>
		{/each}
	</div>
	<div class="hours">
		{#each Object.entries(service.hours) as [day, hours] (day)}
			<span class="day">{day}: {hours}</span>
		{/each}
	</div>
</a>

<style>
	.card {
		display: block;
		background: #fff;
		border-radius: 12px;
		padding: 1rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		text-decoration: none;
		color: inherit;
		transition:
			transform 0.2s,
			box-shadow 0.2s;
	}
	.card:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
	}
	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}
	.category {
		background: #1a73e8;
		color: #fff;
		padding: 2px 8px;
		border-radius: 4px;
		font-size: 0.75rem;
		display: inline-block;
	}
	.open-badge {
		background: #4caf50;
		color: #fff;
		padding: 2px 8px;
		border-radius: 4px;
		font-size: 0.7rem;
		font-weight: bold;
		display: inline-block;
	}
	.closed-badge {
		background: #f44336;
		color: #fff;
		padding: 2px 8px;
		border-radius: 4px;
		font-size: 0.7rem;
		font-weight: bold;
		display: inline-block;
	}
	h3 {
		margin: 0.25rem 0;
		font-size: 1.1rem;
	}
	.address {
		color: #666;
		margin: 0.25rem 0;
		font-size: 0.9rem;
	}
	.phone {
		color: #1a73e8;
		margin: 0.25rem 0;
		font-size: 0.85rem;
	}
	.tags {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
		margin: 0.5rem 0;
	}
	.tag {
		background: #e8f0fe;
		color: #1a73e8;
		padding: 2px 6px;
		border-radius: 4px;
		font-size: 0.75rem;
	}
	.day {
		display: block;
		font-size: 0.8rem;
		color: #555;
		margin: 1px 0;
	}
	.hours {
		margin-top: 0.5rem;
	}
</style>
