<script lang="ts">
	import ServiceList from '$lib/components/ServiceList.svelte';
	import FilterBar from '$lib/components/FilterBar.svelte';
	import type { ServiceLocation } from '$lib/types';
	import { isOpenOnDay, type DayKey } from '$lib/utils/hours';
	import { assets } from '$app/paths';

	const { data } = $props();
	const dataServices = data.services;
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
				(s.address ?? '').toLowerCase().includes(q) ||
				(s.services ?? []).some((srv) => srv.toLowerCase().includes(q)) ||
				(s.tags ?? []).some((t) => t.toLowerCase().includes(q))
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

	let announceText = $state('');
	$effect(() => {
		if (selectedDay !== 'all') {
			announceText = `${filtered.length} services found open on ${selectedDay.toUpperCase()}`;
		} else {
			announceText = `${filtered.length} services found across ${categories.length} categories`;
		}
	});
</script>

<svelte:head>
	<title>Dublin City Support</title>
	<meta name="description" content="Find nearby support services in Dublin City" />
	<link rel="manifest" href="{assets}/manifest.webmanifest" />
</svelte:head>

<main id="main-content">
	<h1>Dublin City Support</h1>
	<p>Find day centres, GP clinics, and mobile health units across Dublin City.</p>

	<FilterBar
		{categories}
		{selectedCategory}
		{selectedDay}
		onFilter={handleFilter}
		onSearch={handleSearch}
		onDayFilter={handleDayFilter}
		resultsId="service-list"
	/>
	<div role="status" aria-live="polite" class="sr-only" aria-atomic="true">
		{announceText}
	</div>
	<div class="stats">
		{filtered.length} services found
		{#if selectedDay !== 'all'}
			open on {selectedDay.toUpperCase()}
		{:else}
			across {categories.length} categories
		{/if}
	</div>
	<ServiceList services={filtered} id="service-list" />

	<nav>
		<a href="{assets}/map">View on Map</a>
	</nav>
</main>

<style>
	main {
		max-width: 800px;
		margin: 0 auto;
		padding: var(--space-3);
		box-sizing: border-box;
	}
	h1 {
		color: var(--color-accent);
		margin-bottom: var(--space-2);
		font-size: var(--text-2xl);
		line-height: var(--leading-tight);
		text-wrap: balance;
	}
	p {
		font-size: var(--text-base);
		color: var(--color-text-secondary);
		line-height: var(--leading-relaxed);
	}
	.stats {
		color: var(--color-text-muted);
		font-size: var(--text-sm);
		margin: var(--space-2) 0;
	}
	nav {
		margin-top: var(--space-5);
		text-align: center;
	}
	nav a {
		color: var(--color-accent);
		text-decoration: none;
		font-weight: 600;
		font-size: var(--text-base);
	}
	nav a:hover {
		text-decoration: underline;
	}
	@media (max-width: 600px) {
		main {
			padding: var(--space-2);
		}
		h1 {
			font-size: var(--text-xl);
		}
		p {
			font-size: var(--text-sm);
		}
	}
</style>
