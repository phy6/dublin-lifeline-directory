<script lang="ts">
	import { onMount } from 'svelte';
	import ServiceList from '$lib/components/ServiceList.svelte';
	import FilterBar from '$lib/components/FilterBar.svelte';
	import type { ServiceLocation } from '$lib/types';
	import { isOpenOnDay, type DayKey } from '$lib/utils/hours';

	const { data } = $props();
	const dataServices = data.services as ServiceLocation[];
	let services = $state(dataServices);
	let filtered = $state(dataServices);
	let categories = $state(data.categories);
	let selectedCategory = $state<string>('All');
	let selectedDay = $state<string>('all');

	function handleFilter(category: string) {
		selectedCategory = category;
		let base = services;
		if (category !== 'All') {
			base = base.filter((s) => s.category === category);
		}
		if (selectedDay !== 'all') {
			base = base.filter((s) => isOpenOnDay(s.hours, selectedDay as DayKey));
		}
		filtered = base;
	}

	function handleSearch(query: string) {
		const q = query.toLowerCase();
		let base = services;
		if (selectedCategory !== 'All') {
			base = base.filter((s) => s.category === selectedCategory);
		}
		if (selectedDay !== 'all') {
			base = base.filter((s) => isOpenOnDay(s.hours, selectedDay as DayKey));
		}
		if (!q) {
			filtered = base;
			return;
		}
		filtered = base.filter(
			(s) =>
				s.name.toLowerCase().includes(q) ||
				s.address.toLowerCase().includes(q) ||
				s.services.some((srv) => srv.toLowerCase().includes(q)) ||
				s.tags.some((t) => t.toLowerCase().includes(q))
		);
	}

	function handleDayFilter(day: string) {
		selectedDay = day;
		let base = services;
		if (selectedCategory !== 'All') {
			base = base.filter((s) => s.category === selectedCategory);
		}
		if (day === 'all') {
			filtered = base;
		} else {
			filtered = base.filter((s) => isOpenOnDay(s.hours, day as DayKey));
		}
	}
</script>

<main id="main-content">
	<h1>Search Services</h1>
	<FilterBar
		{categories}
		selectedCategory={selectedCategory}
		selectedDay={selectedDay}
		onFilter={handleFilter}
		onSearch={handleSearch}
		onDayFilter={handleDayFilter}
	/>
	<div class="stats">
		{filtered.length} services found
		{#if selectedDay !== 'all'}
			open on {selectedDay.toUpperCase()}
		{:else}
			across {categories.length} categories
		{/if}
	</div>
	<ServiceList services={filtered} />
</main>

<style>
	main {
		max-width: 800px;
		margin: 0 auto;
		padding: 1rem;
		box-sizing: border-box;
	}
	h1 {
		color: #1a73e8;
		font-size: 1.5rem;
	}
	.stats {
		color: #666;
		font-size: 0.9rem;
		margin: 0.5rem 0;
	}
	@media (max-width: 600px) {
		main {
			padding: 0.5rem;
		}
		h1 {
			font-size: 1.25rem;
		}
	}
</style>
