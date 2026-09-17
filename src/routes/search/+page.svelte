<script lang="ts">
	import ServiceList from '$lib/components/ServiceList.svelte';
	import FilterBar from '$lib/components/FilterBar.svelte';
	import { isOpenOnDay, type DayKey } from '$lib/utils/hours';
	import { t } from '$lib/stores/lang.svelte';

	const { data } = $props();
	const dataServices = data.services;
	let services = $state(dataServices);
	let filtered = $state(dataServices);
	let categories = $state(data.categories);
	let selectedCategory = $state<string>('All');
	let selectedDay = $state<string>('all');
	let searchQuery = $state('');

	function resetAll() {
		searchQuery = '';
		selectedCategory = 'All';
		selectedDay = 'all';
		filtered = services;
	}

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
			announceText = t('results-day')
				.replace('{count}', String(filtered.length))
				.replace('{day}', selectedDay.toUpperCase());
		} else {
			announceText = t('results-all')
				.replace('{count}', String(filtered.length))
				.replace('{categories}', String(categories.length));
		}
	});
</script>

<main id="main-content">
	<h1>{t('search-title')}</h1>
	<FilterBar
		{categories}
		{selectedCategory}
		{selectedDay}
		bind:query={searchQuery}
		onFilter={handleFilter}
		onSearch={handleSearch}
		onDayFilter={handleDayFilter}
		resultsId="service-list"
	/>
	<div role="status" aria-live="polite" class="sr-only" aria-atomic="true">
		{announceText}
	</div>
	<div class="stats">
		{#if selectedDay !== 'all'}
			{t('results-day')
				.replace('{count}', String(filtered.length))
				.replace('{day}', selectedDay.toUpperCase())}
		{:else}
			{t('results-all')
				.replace('{count}', String(filtered.length))
				.replace('{categories}', String(categories.length))}
		{/if}
	</div>
	<ServiceList services={filtered} id="service-list" onReset={resetAll} />
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
		font-size: var(--text-2xl);
		line-height: var(--leading-tight);
		text-wrap: balance;
	}
	.stats {
		color: var(--color-text-muted);
		font-size: var(--text-sm);
		margin: var(--space-2) 0;
	}
	@media (max-width: 600px) {
		main {
			padding: var(--space-2);
		}
		h1 {
			font-size: var(--text-xl);
		}
	}
</style>
