<script lang="ts">
	import { onMount } from 'svelte';
	import ServiceList from '$lib/components/ServiceList.svelte';
	import FilterBar from '$lib/components/FilterBar.svelte';
	import type { ServiceLocation } from '$lib/types';
	import { isOpenOnDay, type DayKey } from '$lib/utils/hours';

	let services = $state<ServiceLocation[]>([]);
	let filtered = $state<ServiceLocation[]>([]);
	let categories = $state<string[]>([]);
	let selectedDay = $state<string>('all');
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
			filtered = applyDayFilter(services, selectedDay);
		} else {
			filtered = applyDayFilter(
				services.filter((s) => s.category === category),
				selectedDay
			);
		}
	}

	function handleSearch(query: string) {
		const q = query.toLowerCase();
		let base = services;
		if (selectedDay !== 'all') {
			base = services.filter((s) => isOpenOnDay(s.hours, selectedDay as DayKey));
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
		if (day === 'all') {
			filtered = services;
		} else {
			filtered = services.filter((s) => isOpenOnDay(s.hours, day as DayKey));
		}
	}

	function applyDayFilter(list: ServiceLocation[], day: string): ServiceLocation[] {
		if (day === 'all') return list;
		return list.filter((s) => isOpenOnDay(s.hours, day as DayKey));
	}
</script>

<svelte:head>
	<title>Dublin City Support</title>
	<meta name="description" content="Find nearby support services in Dublin City" />
	<link rel="manifest" href="/manifest.webmanifest" />
</svelte:head>

<main id="main-content">
	<h1>Dublin City Support</h1>
	<p>
		Find nearby support services for people experiencing homelessness, drug-related issues, and
		other hardships.
	</p>

	{#if !loading}
		<FilterBar
			{categories}
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
	{:else}
		<div class="loading">Loading services...</div>
	{/if}

	<nav>
		<a href="/map">View on Map</a>
	</nav>
</main>

<style>
	main {
		max-width: 800px;
		margin: 0 auto;
		padding: 1rem;
	}
	h1 {
		color: #1a73e8;
		margin-bottom: 0.5rem;
	}
	.stats {
		color: #666;
		font-size: 0.9rem;
		margin: 0.5rem 0;
	}
	.loading {
		padding: 2rem;
		text-align: center;
		font-size: 1.2rem;
		color: #666;
	}
	nav {
		margin-top: 2rem;
		text-align: center;
	}
	nav a {
		color: #1a73e8;
		text-decoration: none;
		font-weight: bold;
	}
	nav a:hover {
		text-decoration: underline;
	}
</style>
