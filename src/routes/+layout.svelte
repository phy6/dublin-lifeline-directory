<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { base } from '$app/paths';
	import OfflineBanner from '$lib/components/OfflineBanner.svelte';
	import Chatbot from '$lib/components/Chatbot.svelte';
	import SettingsSheet from '$lib/components/SettingsSheet.svelte';
	import '$lib/styles/tokens.css';
	let { children } = $props();
	let lang = $state('en');

	function loadLang() {
		if (typeof window !== 'undefined') {
			const saved = localStorage.getItem('dcs-language');
			if (saved) lang = saved;
			else lang = navigator.language.startsWith('ga') ? 'ga' : 'en';
			document.documentElement.lang = lang;
		}
	}

	function setLang(v: 'en' | 'ga') {
		lang = v;
		if (typeof window !== 'undefined') {
			document.documentElement.lang = v;
			localStorage.setItem('dcs-language', v);
		}
	}

	onMount(loadLang);
</script>

<svelte:head>
	{#if lang === 'ga'}
		<title>Seirbhísí Chathair Bhaile Átha Cliath</title>
	{/if}
</svelte:head>

<nav class="top-nav" aria-label="Main navigation">
	<a href="{base}/" aria-current={page.url.pathname === `${base}/` ? 'page' : undefined}
		>Directory</a
	>
	<a href="{base}/map" aria-current={page.url.pathname === `${base}/map` ? 'page' : undefined}
		>Map</a
	>
	<a href="{base}/search" aria-current={page.url.pathname === `${base}/search` ? 'page' : undefined}
		>Search</a
	>
</nav>

<div id="emergency-fab" role="complementary" aria-label="Emergency contacts">
	<a href="tel:112" aria-label="Call emergency services 112">112</a>
</div>

<SettingsSheet {lang} onLang={setLang} />

{@render children()}

<nav class="tab-bar" aria-label="Main navigation">
	<a href="{base}/" aria-current={page.url.pathname === `${base}/` ? 'page' : undefined}>
		<span aria-hidden="true" class="tab-icon">📋</span>
		<span class="tab-label">Directory</span>
	</a>
	<a href="{base}/map" aria-current={page.url.pathname === `${base}/map` ? 'page' : undefined}>
		<span aria-hidden="true" class="tab-icon">🗺️</span>
		<span class="tab-label">Map</span>
	</a>
	<a
		href="{base}/search"
		aria-current={page.url.pathname === `${base}/search` ? 'page' : undefined}
	>
		<span aria-hidden="true" class="tab-icon">🔍</span>
		<span class="tab-label">Search</span>
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
		transition: background-color 0.15s;
	}
	@media (prefers-reduced-motion: no-preference) {
		.top-nav a:hover {
			background: rgba(255, 255, 255, 0.15);
			text-decoration: none;
		}
	}
	.top-nav a[aria-current='page'] {
		background: rgba(255, 255, 255, 0.25);
	}
	#emergency-fab {
		position: fixed;
		top: max(var(--space-2), env(safe-area-inset-top));
		right: max(var(--space-2), env(safe-area-inset-right));
		z-index: 9999;
	}
	#emergency-fab a {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-width: 44px;
		min-height: 44px;
		background: var(--color-success);
		color: var(--color-text-on-accent);
		padding: var(--space-2) var(--space-3);
		border-radius: var(--radius-md);
		text-decoration: none;
		font-weight: 700;
		font-size: var(--text-lg);
		border: 2px solid var(--color-warning);
		box-shadow: var(--shadow-lg);
	}
	@media (prefers-reduced-motion: no-preference) {
		#emergency-fab a:hover {
			background: var(--color-success-container);
			color: var(--color-success-on-container);
		}
		#emergency-fab a:active {
			transform: scale(0.96);
		}
	}
	#emergency-fab a:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
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
			font-size: 1.375rem;
			line-height: 1;
		}
		/* FABs stack above the tab bar */
		#emergency-fab {
			top: max(var(--space-1), env(safe-area-inset-top));
			right: max(var(--space-1), env(safe-area-inset-right));
		}
		#emergency-fab a {
			font-size: var(--text-base);
			padding: var(--space-1) var(--space-2);
			min-width: 44px;
			min-height: 44px;
		}
	}
</style>
