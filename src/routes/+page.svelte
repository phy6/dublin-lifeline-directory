<script lang="ts">
	import ServiceList from '$lib/components/ServiceList.svelte';
	import FilterBar from '$lib/components/FilterBar.svelte';
	import { applyFilters } from '$lib/utils/services';
	import type { DayKey } from '$lib/utils/hours';
	import { assets } from '$app/paths';
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

	function refreshFiltered() {
		filtered = applyFilters(services, {
			category: selectedCategory,
			day: selectedDay as DayKey | 'all',
			query: searchQuery
		});
	}

	function handleFilter(category: string) {
		selectedCategory = category;
		refreshFiltered();
	}

	function handleSearch(query: string) {
		searchQuery = query;
		refreshFiltered();
	}

	function handleDayFilter(day: string) {
		selectedDay = day;
		refreshFiltered();
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

<svelte:head>
	<title>Dublin City Support</title>
	<meta name="description" content="Find nearby support services in Dublin City" />
	<link rel="manifest" href="{assets}/manifest.webmanifest" />
</svelte:head>

<main id="main-content">
	<h1>{t('app-title')}</h1>
	<p>{t('app-intro')}</p>

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

	<nav>
		<a href="{assets}/map">{t('view-on-map')}</a>
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
