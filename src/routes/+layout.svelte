<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { base } from '$app/paths';
	import { lang, setLang, loadLang, t } from '$lib/stores/lang.svelte';
	import OfflineBanner from '$lib/components/OfflineBanner.svelte';
	import Chatbot from '$lib/components/Chatbot.svelte';
	import SettingsSheet from '$lib/components/SettingsSheet.svelte';
	import '$lib/styles/tokens.css';
	let { children } = $props();

	onMount(loadLang);
</script>

<svelte:head>
	{#if lang.current === 'ga'}
		<title>Seirbhísí Chathair Bhaile Átha Cliath</title>
	{/if}
</svelte:head>

<nav class="top-nav" aria-label="Main navigation">
	<a href="{base}/" aria-current={page.url.pathname === `${base}/` ? 'page' : undefined}
		>{t('directory')}</a
	>
	<a href="{base}/map" aria-current={page.url.pathname === `${base}/map` ? 'page' : undefined}
		>{t('map')}</a
	>
	<a href="{base}/search" aria-current={page.url.pathname === `${base}/search` ? 'page' : undefined}
		>{t('search')}</a
	>
</nav>

<div class="lang-pill" role="group" aria-label="Language">
	<button
		aria-pressed={lang.current === 'en'}
		class:active={lang.current === 'en'}
		onclick={() => setLang('en')}
	>
		EN
	</button>
	<button
		aria-pressed={lang.current === 'ga'}
		class:active={lang.current === 'ga'}
		onclick={() => setLang('ga')}
	>
		GA
	</button>
</div>

<SettingsSheet />

{@render children()}

<nav class="tab-bar" aria-label="Main navigation">
	<a href="{base}/" aria-current={page.url.pathname === `${base}/` ? 'page' : undefined}>
		<svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="8" y="2" width="8" height="4" rx="1" /><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" /><path d="M9 12h6M9 16h4" /></svg>
		<span class="tab-label">{t('directory')}</span>
	</a>
	<a href="{base}/map" aria-current={page.url.pathname === `${base}/map` ? 'page' : undefined}>
		<svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14.5 4.5 21 7v13l-6.5-2.5L9 20 3 17.5v-13L9 7l5.5-2.5Z" /><path d="M9 7v13M14.5 4.5v13" /></svg>
		<span class="tab-label">{t('map')}</span>
	</a>
	<a
		href="{base}/search"
		aria-current={page.url.pathname === `${base}/search` ? 'page' : undefined}
	>
		<svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg>
		<span class="tab-label">{t('search')}</span>
	</a>
</nav>

<OfflineBanner />
<Chatbot />

<style>
	.top-nav {
		display: flex;
		gap: var(--space-3);
		padding: var(--space-2) var(--space-3);
		background: var(--color-accent);
		flex-wrap: wrap;
		border-bottom: 1px solid rgba(0, 0, 0, 0.12);
	}
	.top-nav a {
		color: var(--color-text-on-accent);
		text-decoration: none;
		font-weight: 600;
		font-size: var(--text-sm);
		letter-spacing: 0.02em;
		padding: var(--space-1) var(--space-2);
		border-radius: var(--radius-sm);
	}
	@media (prefers-reduced-motion: no-preference) {
		.top-nav a {
			transition: background-color 0.15s;
		}
		.top-nav a:hover {
			background: rgba(255, 255, 255, 0.15);
			text-decoration: none;
		}
	}
	.top-nav a[aria-current='page'] {
		background: rgba(255, 255, 255, 0.25);
	}
	.lang-pill {
		position: fixed;
		top: max(var(--space-2), env(safe-area-inset-top));
		right: max(var(--space-2), env(safe-area-inset-right));
		z-index: 9998;
		display: flex;
		background: var(--color-surface);
		border: 2px solid var(--color-border-strong);
		border-radius: var(--radius-full);
		overflow: hidden;
	}
	.lang-pill button {
		border: 0;
		background: transparent;
		color: var(--color-text-secondary);
		font-size: var(--text-xs);
		font-weight: 700;
		padding: var(--space-1) var(--space-2);
		min-width: 44px;
		min-height: 44px;
		cursor: pointer;
		font-family: var(--font-sans);
	}
	.lang-pill button.active {
		background: var(--color-accent);
		color: var(--color-text-on-accent);
	}
	.lang-pill button:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: -3px;
	}
	.tab-bar {
		display: none;
	}
	@media (max-width: 600px) {
		:global(body) {
			padding-bottom: calc(72px + env(safe-area-inset-bottom));
		}
		.top-nav {
			display: none;
		}
		.tab-bar {
			display: flex;
			position: fixed;
			bottom: 0;
			left: 0;
			right: 0;
			z-index: 1500;
			background: var(--color-surface);
			border-top: 1px solid var(--color-border);
			padding-bottom: env(safe-area-inset-bottom);
			box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.12);
		}
		.tab-bar a {
			flex: 1;
			display: flex;
			flex-direction: column;
			align-items: center;
			gap: 2px;
			padding: var(--space-2) var(--space-1) calc(var(--space-1) + 2px);
			min-height: 56px;
			justify-content: center;
			color: var(--color-text-secondary);
			text-decoration: none;
			font-size: var(--text-xs);
			font-weight: 600;
		}
		.tab-bar a[aria-current='page'] {
			color: var(--color-accent);
		}
	.tab-icon {
		width: 22px;
		height: 22px;
		flex: none;
	}
		/* FABs stack above the tab bar */
		.lang-pill {
			top: max(var(--space-1), env(safe-area-inset-top));
			right: max(var(--space-1), env(safe-area-inset-right));
		}
	}
</style>
