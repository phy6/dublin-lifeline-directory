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
	<select onchange={(e) => { lang = (e.target as HTMLSelectElement).value; document.documentElement.lang = lang; localStorage.setItem('dcs-language', lang); }} aria-label="Select language">
		<option value="en" selected={lang === 'en'}>English</option>
		<option value="ga" selected={lang === 'ga'}>Gaeilge</option>
	</select>
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
		padding: 0.75rem 1rem;
		background: #1a73e8;
		border-radius: 0 0 12px 12px;
		flex-wrap: wrap;
	}
	.top-nav a {
		color: #fff;
		text-decoration: none;
		font-weight: bold;
		font-size: 1rem;
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
		font-size: 1.1rem;
		border: 2px solid #ffc900;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
	}
	#emergency-fab a:hover {
		background: #126b32;
	}
	#lang-fab select {
		position: fixed;
		top: 0.5rem;
		right: 0.5rem;
		z-index: 9998;
		padding: 0.4rem 0.6rem;
		border-radius: 8px;
		border: 2px solid #ffc900;
		background: white;
		color: #333;
		cursor: pointer;
		font-size: 0.85rem;
		font-weight: bold;
		min-width: 100px;
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
	@media (max-width: 600px) {
		.top-nav {
			gap: 0.5rem;
			padding: 0.5rem;
			font-size: 0.9rem;
		}
		.top-nav a {
			font-size: 0.85rem;
			padding: 0.25rem 0.5rem;
		}
		#emergency-fab {
			top: 0.25rem;
			right: 7rem;
		}
		#emergency-fab a {
			font-size: 0.9rem;
			padding: 0.3rem 0.6rem;
		}
		#lang-fab select {
			top: 0.25rem;
			right: 0.25rem;
			font-size: 0.8rem;
			min-width: 80px;
		}
		.a11y-fab {
			bottom: 0.25rem;
			right: 0.25rem;
		}
	}
</style>
