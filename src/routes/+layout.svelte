<script lang="ts">
	import { onMount } from 'svelte';
	import TextScaleToggle from '$lib/components/TextScaleToggle.svelte';
	import LowDataToggle from '$lib/components/LowDataToggle.svelte';
	let { children } = $props();
	let lang = $state('en');

	function toggleLang() {
		lang = lang === 'en' ? 'ga' : 'en';
		document.documentElement.lang = lang;
		localStorage.setItem('dcs-language', lang);
	}

	function loadLang() {
		if (typeof window !== 'undefined') {
			const saved = localStorage.getItem('dcs-language');
			if (saved) lang = saved;
			else lang = navigator.language.startsWith('ga') ? 'ga' : 'en';
			document.documentElement.lang = lang;
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
	<a href="/">Home</a>
	<a href="/map">Map</a>
	<a href="/search">Search</a>
</nav>

<div id="emergency-fab" role="complementary" aria-label="Emergency contacts">
	<a href="tel:112" aria-label="Call emergency services">112</a>
</div>

<div id="lang-fab">
	<button onclick={toggleLang} aria-label="Switch language">{lang === 'en' ? '🇮🇪 Gaeilge' : '🇬🇧 English'}</button>
</div>

{@render children()}

<div class="a11y-fab">
	<TextScaleToggle />
	<LowDataToggle />
</div>

<style>
	.top-nav {
		display: flex;
		gap: 1rem;
		padding: 1rem;
		background: #1a73e8;
		border-radius: 0 0 12px 12px;
	}
	.top-nav a {
		color: #fff;
		text-decoration: none;
		font-weight: bold;
	}
	.top-nav a:hover {
		text-decoration: underline;
	}
	#emergency-fab {
		position: fixed;
		top: 0.5rem;
		right: 9rem;
		z-index: 9999;
	}
	#emergency-fab a {
		background: #167f3d;
		color: white;
		padding: 0.5rem 1rem;
		border-radius: 8px;
		text-decoration: none;
		font-weight: bold;
		font-size: 1.2rem;
		border: 2px solid #ffc900;
	}
	#emergency-fab a:hover {
		background: #126b32;
	}
	#lang-fab button {
		position: fixed;
		top: 0.5rem;
		right: 0.5rem;
		z-index: 9998;
		padding: 0.4rem 0.8rem;
		border-radius: 8px;
		border: 2px solid #ffc900;
		background: #1a73e8;
		color: white;
		cursor: pointer;
		font-size: 0.85rem;
		font-weight: bold;
	}
	.a11y-fab {
		position: fixed;
		bottom: 0.5rem;
		right: 0.5rem;
		z-index: 1000;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
</style>
