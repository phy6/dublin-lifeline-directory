<script lang="ts">
	import { onMount } from 'svelte';
	let online = $state(true);

	function update() {
		online = typeof navigator === 'undefined' ? true : navigator.onLine;
	}

	onMount(() => {
		update();
		window.addEventListener('online', update);
		window.addEventListener('offline', update);
		return () => {
			window.removeEventListener('online', update);
			window.removeEventListener('offline', update);
		};
	});
</script>

{#if !online}
	<div class="offline-banner" role="status">
		You are offline. Showing saved information — some details may be out of date.
	</div>
{/if}

<style>
	.offline-banner {
		background: var(--color-warning-container);
		color: var(--color-warning-on-container);
		border-bottom: 2px solid var(--color-warning);
		padding: var(--space-2) var(--space-3);
		text-align: center;
		font-size: var(--text-sm);
		font-weight: 600;
	}
</style>
