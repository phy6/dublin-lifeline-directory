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

<button
	onclick={toggle}
	aria-pressed={enabled}
	aria-label={enabled ? 'Disable low data mode' : 'Enable low data mode'}
	class:active={enabled}
>
	{enabled ? 'Low Data ON' : 'Low Data'}
</button>

<style>
	button {
		color: var(--color-text-on-accent);
		border: none;
		padding: var(--space-2) var(--space-3);
		border-radius: var(--radius-md);
		cursor: pointer;
		font-size: var(--text-sm);
		font-weight: 600;
		box-shadow: var(--shadow-md);
		background: var(--color-text-primary);
		min-height: 44px;
		min-width: 44px;
		font-family: var(--font-sans);
	}
	button.active {
		background: var(--color-warning);
		color: var(--color-warning-on-container);
	}
	button:hover:not(.active) {
		background: var(--color-text-secondary);
	}
	button:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
	}
</style>
