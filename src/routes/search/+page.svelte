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
	<p class="kicker">Baile Átha Cliath</p>
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
		max-width: 640px;
		margin: 0 auto;
		padding: var(--space-3);
		box-sizing: border-box;
		background: var(--color-surface);
	}
	.kicker {
		font-size: var(--text-sm);
		font-weight: 700;
		color: var(--color-accent);
		margin: 0 0 2px;
	}
	h1 {
		color: var(--color-text-primary);
		margin: 0 0 var(--space-2);
		font-family: var(--font-display);
		font-weight: 800;
		letter-spacing: -0.02em;
		font-size: var(--text-3xl);
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
	@media (max-width: 600px) {
		main {
			padding: var(--space-2);
		}
		h1 {
			font-size: var(--text-xl);
		}
	}
</style>
