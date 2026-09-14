<script lang="ts">
	import type { ServiceLocation } from '$lib/types';
	import ServiceCard from './ServiceCard.svelte';

	let { services }: { services: ServiceLocation[] } = $props();
</script>

<div class="service-list">
	{#each services as service (service.id)}
		<ServiceCard {service} />
	{/each}
</div>

<style>
	.service-list {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 1rem;
		padding: 1rem;
	}
</style>
