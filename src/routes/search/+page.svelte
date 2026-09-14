<script lang="ts">
	import { onMount } from 'svelte';
	import ServiceList from '$lib/components/ServiceList.svelte';
	import FilterBar from '$lib/components/FilterBar.svelte';
	import type { ServiceLocation } from '$lib/types';

	let services = $state<ServiceLocation[]>([]);
	let filtered = $state<ServiceLocation[]>([]);
	let categories = $state<string[]>([]);
	let loading = $state(true);

	onMount(async () => {
		const res = await fetch('/services.json');
		const data = await res.json();
		services = data.services;
		filtered = services;
		categories = [...new Set(services.map((s) => s.category))].sort();
		loading = false;
	});

	function handleFilter(category: string) {
		if (category === 'All') {
			filtered = services;
		} else {
			filtered = services.filter((s) => s.category === category);
		}
	}

	function handleSearch(query: string) {
		const q = query.toLowerCase();
		if (!q) {
			filtered = services;
			return;
		}
		filtered = services.filter(
			(s) =>
				s.name.toLowerCase().includes(q) ||
				s.address.toLowerCase().includes(q) ||
				s.services.some((srv) => srv.toLowerCase().includes(q)) ||
				s.tags.some((t) => t.toLowerCase().includes(q))
		);
	}
</script>

<main>
	<h1>Search Services</h1>
	{#if !loading}
		<FilterBar {categories} onFilter={handleFilter} onSearch={handleSearch} />
		<ServiceList services={filtered} />
	{:else}
		<p>Loading...</p>
	{/if}
</main>

<style>
	main {
		max-width: 800px;
		margin: 0 auto;
		padding: 1rem;
	}
	h1 {
		color: #1a73e8;
	}
</style>
