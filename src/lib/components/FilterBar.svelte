<script lang="ts">
	import { DAY_KEYS, DAY_LABELS } from '$lib/utils/hours';

	let {
		categories,
		onFilter,
		onSearch,
		onDayFilter
	}: {
		categories: string[];
		onFilter: (cat: string) => void;
		onSearch: (q: string) => void;
		onDayFilter: (day: string) => void;
	} = $props();
	let query = $state('');
</script>

<div class="filter-bar">
	<input
		type="search"
		placeholder="Search services..."
		bind:value={query}
		oninput={() => onSearch(query)}
	/>
	<div class="filter-chips" role="group" aria-label="Filter by category">
		<button
			class:active={!categories.length || true}
			onclick={() => onFilter('All')}
			aria-pressed={true}
		>
			All Categories
		</button>
		{#each categories as cat (cat)}
			<button class:active={false} onclick={() => onFilter(cat)} aria-pressed={false}>
				{cat}
			</button>
		{/each}
	</div>
	<div class="filter-chips" role="group" aria-label="Filter by day">
		<button class:active={true} onclick={() => onDayFilter('all')} aria-pressed={true}>
			All Days
		</button>
		{#each DAY_KEYS as day, i (day)}
			<button class:active={false} onclick={() => onDayFilter(day)} aria-pressed={false}>
				{DAY_LABELS[i]}
			</button>
		{/each}
	</div>
</div>

<style>
	.filter-bar {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		padding: 1rem;
		background: #f8f9fa;
		border-radius: 12px;
		margin-bottom: 1rem;
		flex-wrap: wrap;
	}
	input[type='search'] {
		flex: 1;
		min-width: 200px;
		padding: 0.5rem 1rem;
		border: 1px solid #ddd;
		border-radius: 8px;
		font-size: 1rem;
	}
	.filter-chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.35rem;
	}
	.filter-chips button {
		padding: 0.4rem 0.85rem;
		border: 1px solid #ddd;
		border-radius: 20px;
		background: #fff;
		color: #333;
		font-size: 0.85rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.15s;
		min-height: 40px;
	}
	.filter-chips button:hover {
		border-color: #1a73e8;
		background: #e8f0fe;
	}
	.filter-chips button.active {
		background: #1a73e8;
		color: #fff;
		border-color: #1a73e8;
	}
	.filter-chips button:focus-visible {
		outline: 3px solid #ffc107;
		outline-offset: 2px;
	}
</style>
