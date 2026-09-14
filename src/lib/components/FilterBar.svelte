<script lang="ts">
	let {
		categories,
		onFilter,
		onSearch
	}: { categories: string[]; onFilter: (cat: string) => void; onSearch: (q: string) => void } =
		$props();
	let query = $state('');
</script>

<div class="filter-bar">
	<input
		type="search"
		placeholder="Search services..."
		bind:value={query}
		oninput={() => onSearch(query)}
	/>
	<select onchange={(e) => onFilter(e.currentTarget.value)}>
		<option value="All">All Categories</option>
		{#each categories as cat (cat)}
			<option value={cat}>{cat}</option>
		{/each}
	</select>
</div>

<style>
	.filter-bar {
		display: flex;
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
	select {
		padding: 0.5rem 1rem;
		border: 1px solid #ddd;
		border-radius: 8px;
		font-size: 1rem;
		background: #fff;
	}
</style>
