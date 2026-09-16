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

<div class="text-scale-panel" role="group" aria-label="Text size controls">
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
		position: fixed;
		bottom: 1rem;
		right: 1rem;
		background: white;
		border: 2px solid #1a73e8;
		border-radius: 8px;
		padding: 0.5rem 1rem;
		z-index: 1000;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.9rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
	}
	.scale-buttons {
		display: flex;
		gap: 0.25rem;
	}
	button {
		padding: 0.25rem 0.5rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		background: white;
		cursor: pointer;
		font-size: 0.85rem;
	}
	button.active {
		background: #1a73e8;
		color: white;
		border-color: #1a73e8;
	}
	button:focus-visible {
		outline: 3px solid #ffc107;
		outline-offset: 2px;
	}
</style>
