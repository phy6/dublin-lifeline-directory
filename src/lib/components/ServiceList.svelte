<script lang="ts">
	import type { ServiceLocation } from '$lib/types';
	import ServiceCard from './ServiceCard.svelte';

	let { services, id = 'service-list' }: { services: ServiceLocation[]; id?: string } = $props();
</script>

<div class="service-list" {id}>
	{#each services as service (service.id)}
		<ServiceCard {service} />
	{/each}
</div>

<style>
	.service-list {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: var(--space-3);
		padding: var(--space-3);
	}
</style>
