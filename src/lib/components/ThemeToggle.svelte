<script lang="ts">
	import { onMount } from 'svelte';
	type Theme = 'light' | 'dark' | 'system';
	let theme = $state<Theme>('system');

	export function applyTheme(t: Theme) {
		theme = t;
		if (typeof document !== 'undefined') {
			if (t === 'system') document.documentElement.removeAttribute('data-theme');
			else document.documentElement.setAttribute('data-theme', t);
		}
		try {
			localStorage.setItem('dcs-theme', t);
		} catch {
			/* storage unavailable — theme still applies for the session */
		}
	}

	function loadTheme() {
		try {
			const saved = localStorage.getItem('dcs-theme');
			if (saved === 'light' || saved === 'dark' || saved === 'system') applyTheme(saved);
		} catch {
			/* ignore */
		}
	}

	onMount(loadTheme);
</script>

<div class="theme-panel" role="group" aria-labelledby="theme-label">
	<span id="theme-label">Theme:</span>
	<div class="theme-buttons">
		{#each [['light', 'Light'], ['dark', 'Dark'], ['system', 'System']] as [value, label] (value)}
			<button
				onclick={() => applyTheme(value as Theme)}
				aria-label="Use {label.toLowerCase()} theme"
				aria-pressed={theme === value}
				class:active={theme === value}
			>
				{label}
			</button>
		{/each}
	</div>
</div>

<style>
	.theme-panel {
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
	.theme-buttons {
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
