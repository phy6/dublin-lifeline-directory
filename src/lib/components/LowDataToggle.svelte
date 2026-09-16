<script lang="ts">
	import { onMount } from 'svelte';
	let enabled = $state(false);

	function toggle() {
		enabled = !enabled;
		localStorage.setItem('dcs-low-data', enabled ? 'true' : 'false');
		if (navigator.serviceWorker.controller) {
			navigator.serviceWorker.controller.postMessage({
				type: 'TOGGLE_LOW_DATA',
				enabled
			});
		}
	}

	function load() {
		const saved = localStorage.getItem('dcs-low-data');
		if (saved === 'true') {
			enabled = true;
			if (navigator.serviceWorker.controller) {
				navigator.serviceWorker.controller.postMessage({ type: 'TOGGLE_LOW_DATA', enabled: true });
			}
		}
		if ('connection' in navigator) {
			const conn = navigator.connection as NavigatorConnection | null;
			if (conn?.saveData || conn?.effectiveType === '2g' || conn?.effectiveType === 'slow-2g') {
				enabled = true;
			}
		}
	}

	onMount(load);
</script>

<button onclick={toggle} aria-pressed={enabled} aria-label="{enabled ? 'Disable' : 'Enable'} low data mode" class:active={enabled}>
	{enabled ? '📶 Low Data ON' : '📶 Low Data'}
</button>

<style>
	button {
		position: fixed;
		bottom: 1rem;
		left: 1rem;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 8px;
		cursor: pointer;
		font-size: 0.9rem;
		font-weight: bold;
		z-index: 1000;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
		background: #333;
	}
	button.active {
		background: #ff9800;
	}
	button:focus-visible {
		outline: 3px solid #1a73e8;
		outline-offset: 2px;
	}
</style>
