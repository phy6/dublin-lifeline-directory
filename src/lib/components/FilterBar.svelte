<script lang="ts">
	import { DAY_KEYS, DAY_LABELS } from '$lib/utils/hours';

	let {
		categories,
		selectedCategory = 'All',
		selectedDay = 'all',
		onFilter,
		onSearch,
		onDayFilter,
		resultsId = 'service-list'
	}: {
		categories: string[];
		selectedCategory?: string;
		selectedDay?: string;
		onFilter: (cat: string) => void;
		onSearch: (q: string) => void;
		onDayFilter: (day: string) => void;
		resultsId?: string;
	} = $props();
	let query = $state('');
</script>

<div class="filter-bar">
	<label for="search-input" class="sr-only">Search services</label>
	<input
		id="search-input"
		type="search"
		placeholder="Search by name, address, or service type..."
		bind:value={query}
		oninput={() => onSearch(query)}
	/>
	<div class="filter-chips" role="group" aria-label="Filter by category">
		<button
			class:active={selectedCategory === 'All'}
			onclick={() => onFilter('All')}
			aria-pressed={selectedCategory === 'All'}
			aria-controls={resultsId}
		>
			All Categories
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
	<div class="filter-chips" role="group" aria-label="Filter by day">
		<button
			class:active={selectedDay === 'all'}
			onclick={() => onDayFilter('all')}
			aria-pressed={selectedDay === 'all'}
			aria-controls={resultsId}
		>
			All Days
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
		padding: var(--space-3);
		background: var(--color-surface-variant);
		border-radius: var(--radius-lg);
		margin-bottom: var(--space-3);
		flex-wrap: wrap;
	}
	input[type='search'] {
		flex: 1;
		min-width: 200px;
		padding: var(--space-2) var(--space-3);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		font-size: var(--text-base);
		box-sizing: border-box;
		min-height: 44px;
		font-family: var(--font-sans);
	}
	input[type='search']:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
		border-color: var(--color-accent);
	}
	.filter-chips {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-1);
	}
	.filter-chips button {
		padding: var(--space-1) var(--space-2);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-full);
		background: var(--color-surface);
		color: var(--color-text-primary);
		font-size: var(--text-sm);
		font-weight: 600;
		cursor: pointer;
		transition: all 0.15s;
		min-height: 44px;
		min-width: 44px;
		font-family: var(--font-sans);
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
	@media (max-width: 600px) {
		.filter-bar {
			padding: var(--space-2);
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
