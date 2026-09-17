<script lang="ts">
	import TextScaleToggle from '$lib/components/TextScaleToggle.svelte';
	import LowDataToggle from '$lib/components/LowDataToggle.svelte';
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';
	import { lang, setLang as onLang } from '$lib/stores/lang.svelte';

	let open = $state(false);
	const langCode = $derived(lang.current);
</script>

<button
	class="settings-fab"
	aria-haspopup="dialog"
	aria-expanded={open}
	aria-controls="settings-sheet"
	aria-label={langCode === 'ga' ? 'Socruithe' : 'Settings'}
	onclick={() => (open = true)}
>
	<span aria-hidden="true">⚙️</span>
</button>

{#if open}
	<div
		class="sheet-overlay"
		id="settings-sheet"
		role="dialog"
		aria-modal="true"
		aria-labelledby="settings-title"
	>
		<div class="sheet">
			<span class="grabber" aria-hidden="true"></span>
			<div class="sheet-header">
				<h3 id="settings-title">{langCode === 'ga' ? 'Socruithe' : 'Settings'}</h3>
				<button class="close" onclick={() => (open = false)} aria-label="Close settings">✕</button>
			</div>
			<div class="rows">
				<section class="row" aria-label={langCode === 'ga' ? 'Méid téacs' : 'Text size'}>
					<TextScaleToggle />
				</section>
				<section class="row" aria-label={langCode === 'ga' ? 'Téama' : 'Theme'}>
					<ThemeToggle />
				</section>
				<section class="row data-row" aria-label="Low data mode">
					<span class="row-label">{langCode === 'ga' ? 'Modh sonraí íseal' : 'Low data mode'}</span>
					<LowDataToggle />
				</section>
				<section class="row lang-row" aria-label="Language">
					<label for="settings-lang" class="row-label"
						>{langCode === 'ga' ? 'Teanga' : 'Language'}</label
					>
					<select
						id="settings-lang"
						value={langCode}
						onchange={(e) => onLang((e.target as HTMLSelectElement).value as 'en' | 'ga')}
					>
						<option value="en" selected={langCode === 'en'}>English</option>
						<option value="ga" selected={langCode === 'ga'}>Gaeilge</option>
					</select>
				</section>
			</div>
		</div>
	</div>
{/if}

<style>
	.settings-fab {
		position: fixed;
		right: max(var(--space-2), env(safe-area-inset-right));
		bottom: 76px;
		z-index: 1000;
		width: 48px;
		height: 48px;
		border-radius: 50%;
		border: 1px solid var(--color-border);
		background: var(--color-surface);
		color: var(--color-text-primary);
		font-size: 1.375rem;
		cursor: pointer;
		box-shadow: var(--shadow-md);
		display: inline-flex;
		align-items: center;
		justify-content: center;
	}
	.settings-fab:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
	}
	.sheet-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		z-index: 2201;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 16px;
	}
	.sheet {
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		padding: var(--space-3);
		max-width: 420px;
		width: 100%;
		max-height: 85dvh;
		overflow-y: auto;
	}
	.grabber {
		display: none;
	}
	.sheet-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: var(--space-2);
	}
	.sheet-header h3 {
		margin: 0;
		font-size: var(--text-lg);
	}
	.close {
		min-width: 44px;
		min-height: 44px;
		border: 0;
		background: transparent;
		color: var(--color-text-primary);
		font-size: var(--text-base);
		cursor: pointer;
		border-radius: var(--radius-md);
	}
	.rows {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}
	.row {
		border-top: 1px solid var(--color-border);
		padding-top: var(--space-2);
	}
	.row:first-child {
		border-top: 0;
		padding-top: 0;
	}
	/* Strip the floating-panel chrome off the embedded toggles — the sheet is the panel now. */
	.rows :global(.text-scale-panel),
	.rows :global(.theme-panel) {
		border: 0;
		box-shadow: none;
		padding: 0;
		flex-direction: column;
		align-items: flex-start;
		background: transparent;
	}
	.data-row,
	.lang-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-2);
	}
	.row-label {
		font-size: var(--text-sm);
		font-weight: 600;
	}
	.lang-row select {
		padding: var(--space-1) var(--space-2);
		border-radius: var(--radius-md);
		border: 2px solid var(--color-border-strong);
		background: var(--color-surface);
		color: var(--color-text-primary);
		font-size: var(--text-sm);
		font-weight: 600;
		min-height: 44px;
		font-family: var(--font-sans);
	}
	@media (max-width: 600px) {
		.settings-fab {
			bottom: calc(140px + env(safe-area-inset-bottom));
		}
		.sheet-overlay {
			padding: 0;
			align-items: flex-end;
		}
		.sheet {
			max-width: 100%;
			border-radius: var(--radius-lg) var(--radius-lg) 0 0;
			padding-bottom: calc(var(--space-3) + env(safe-area-inset-bottom));
		}
		.grabber {
			display: block;
			width: 40px;
			height: 4px;
			border-radius: 999px;
			background: var(--color-border-strong);
			margin: 0 auto var(--space-2);
		}
	}
</style>
