<script lang="ts">
	import { DAY_KEYS, DAY_LABELS } from '$lib/utils/hours';
	import { t } from '$lib/stores/lang.svelte';

	let {
		categories,
		selectedCategory = 'All',
		selectedDay = 'all',
		query = $bindable(''),
		onFilter,
		onSearch,
		onDayFilter,
		resultsId = 'service-list'
	}: {
		categories: string[];
		selectedCategory?: string;
		selectedDay?: string;
		query?: string;
		onFilter: (cat: string) => void;
		onSearch: (q: string) => void;
		onDayFilter: (day: string) => void;
		resultsId?: string;
	} = $props();
</script>

<div class="filter-bar">
	<label for="search-input" class="sr-only">Search services</label>
	<input
		id="search-input"
		type="search"
		placeholder={t('search-placeholder')}
		bind:value={query}
		oninput={() => onSearch(query)}
	/>
	<div class="filter-chips" role="group" aria-label={t('filter-category')}>
		<button
			class:active={selectedCategory === 'All'}
			onclick={() => onFilter('All')}
			aria-pressed={selectedCategory === 'All'}
			aria-controls={resultsId}
		>
			{t('all-categories')}
		</button>
		{#each categories as cat (cat)}
			<button
				class:active={selectedCategory === cat}
				onclick={() => onFilter(cat)}
				aria-pressed={selectedCategory === cat}
				aria-controls={resultsId}
			>
				{cat}
			</button>
		{/each}
	</div>
	<div class="filter-chips" role="group" aria-label={t('filter-day')}>
		<button
			class:active={selectedDay === 'all'}
			onclick={() => onDayFilter('all')}
			aria-pressed={selectedDay === 'all'}
			aria-controls={resultsId}
		>
			{t('all-days')}
		</button>
		{#each DAY_KEYS as day, i (day)}
			<button
				class:active={selectedDay === day}
				onclick={() => onDayFilter(day)}
				aria-pressed={selectedDay === day}
				aria-controls={resultsId}
			>
				{DAY_LABELS[i]}
			</button>
		{/each}
	</div>
</div>

<style>
	.filter-bar {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		padding: var(--space-2);
		background: var(--color-surface);
		margin-bottom: var(--space-2);
		position: sticky;
		top: 0;
		z-index: 900;
		border-bottom: 1px solid var(--color-border);
	}
	input[type='search'] {
		flex: 1;
		min-width: 200px;
		padding: var(--space-2) var(--space-3);
		border: 2px solid var(--color-border-strong);
		border-radius: var(--radius-full);
		font-size: var(--text-base);
		box-sizing: border-box;
		min-height: 48px;
		font-family: var(--font-sans);
		background: var(--color-surface);
	}
	input[type='search']:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
		border-color: var(--color-accent);
	}
	.filter-chips {
		display: flex;
		flex-wrap: nowrap;
		overflow-x: auto;
		overflow-y: hidden;
		gap: var(--space-2);
		padding-bottom: var(--space-2);
		scrollbar-width: thin;
		overscroll-behavior-x: contain;
		-webkit-overflow-scrolling: touch;
	}
	.filter-chips::-webkit-scrollbar {
		height: 8px;
	}
	.filter-chips::-webkit-scrollbar-thumb {
		background: var(--color-border-strong);
		border-radius: var(--radius-full);
	}
	.filter-chips button {
		padding: var(--space-2) var(--space-3);
		border: 2px solid var(--color-border-strong);
		border-radius: var(--radius-full);
		background: var(--color-surface);
		color: var(--color-text-primary);
		font-size: var(--text-sm);
		font-weight: 700;
		cursor: pointer;
		min-height: 44px;
		min-width: 44px;
		white-space: nowrap;
		flex: none;
		font-family: var(--font-sans);
	}
	@media (prefers-reduced-motion: no-preference) {
		.filter-chips button {
			transition:
				background-color 0.15s,
				border-color 0.15s;
		}
	}
	.filter-chips button:hover {
		border-color: var(--color-accent);
		background: var(--color-accent-container);
	}
	.filter-chips button.active {
		background: var(--color-accent);
		color: var(--color-text-on-accent);
		border-color: var(--color-accent);
	}
	.filter-chips button:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
	}
	@media (min-width: 601px) {
		.filter-chips {
			flex-wrap: wrap;
			overflow: visible;
		}
	}
	@media (max-width: 600px) {
		.filter-bar {
			padding: var(--space-2);
			position: sticky;
			top: 0;
			z-index: 900;
			box-shadow: var(--shadow-sm);
		}
		input[type='search'] {
			font-size: var(--text-base);
			min-height: 44px;
		}
		.filter-chips button {
			font-size: var(--text-xs);
			padding: var(--space-1) var(--space-2);
			min-height: 44px;
		}
	}
</style>
