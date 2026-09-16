<script lang="ts">
	import { onMount } from 'svelte';
	let scale = $state(100);
	const sizes = [100, 125, 150, 175, 200];
	const labels = ['100%', '125%', '150%', '175%', '200%'];

	function setScale(s: number) {
		scale = s;
		document.documentElement.style.fontSize = s + '%';
		localStorage.setItem('dcs-text-scale', s.toString());
	}

	function loadScale() {
		const saved = localStorage.getItem('dcs-text-scale');
		if (saved) setScale(parseInt(saved));
	}

	onMount(loadScale);
</script>

<div class="text-scale-panel" role="group" aria-labelledby="scale-label">
	<span id="scale-label">Text size:</span>
	<div class="scale-buttons">
		{#each sizes as s, i (s)}
			<button
				onclick={() => setScale(s)}
				aria-label="Set text size to {labels[i]}"
				aria-pressed={scale === s}
				class:active={scale === s}
			>
				{labels[i]}
			</button>
		{/each}
	</div>
</div>

<style>
	.text-scale-panel {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: var(--space-2) var(--space-3);
		display: flex;
		align-items: center;
		gap: var(--space-2);
		font-size: var(--text-sm);
		box-shadow: var(--shadow-md);
	}
	.scale-buttons {
		display: flex;
		gap: var(--space-1);
	}
	button {
		padding: var(--space-1) var(--space-2);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		background: var(--color-surface);
		color: var(--color-text-primary);
		cursor: pointer;
		font-size: var(--text-xs);
		font-family: var(--font-sans);
		min-height: 36px;
		min-width: 36px;
	}
	button.active {
		background: var(--color-accent);
		color: var(--color-text-on-accent);
		border-color: var(--color-accent);
	}
	button:hover:not(.active) {
		background: var(--color-surface-hover);
	}
	button:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
	}
</style>
