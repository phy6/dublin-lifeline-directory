<script lang="ts">
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import type { ServiceLocation } from '$lib/types';
	import { t } from '$lib/stores/lang.svelte';
	import 'leaflet/dist/leaflet.css';

	const { data } = $props();
	const dataServices = data.services;
	let services = $state(dataServices);
	let mapEl: HTMLDivElement | null = null;
	let map: L.Map | null = null;

	onMount(async () => {
		const L = await import('leaflet');

		const icon = L.icon({
			iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
			shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
			iconSize: [25, 41],
			iconAnchor: [12, 41],
			popupAnchor: [1, -34]
		});

		if (mapEl) {
			map = L.map(mapEl, { preferCanvas: true }).setView([53.3496, -6.2687], 12);
			L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
				attribution: '&copy; OpenStreetMap contributors'
			}).addTo(map);

			services.forEach((s) => {
				if (s.latitude && s.longitude && map) {
					const marker = L.marker([s.latitude, s.longitude], { icon }).addTo(map);
					marker.bindPopup(
						`<b>${s.name}</b><br>${s.address}<br><a href="${base}/service/${s.id}">View details</a>`
					);

					const markerEl = marker.getElement();
					if (markerEl) {
						markerEl.setAttribute('tabindex', '0');
						markerEl.setAttribute('role', 'button');
						markerEl.setAttribute('aria-label', `View ${s.name} at ${s.address}`);
						markerEl.addEventListener('keydown', (e: KeyboardEvent) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								marker.openPopup();
								markerEl.focus();
							}
						});
					}
				}
			});
			map.invalidateSize();
		}
	});
</script>

<main id="main-content">
	<h1>{t('map-title')}</h1>
	<p>{t('map-intro')}</p>
	<p class="map-instructions">
		{t('map-help')}
	</p>
	<div bind:this={mapEl} id="map" style="width: 100%;"></div>
</main>

<style>
	#map {
		width: 100%;
		height: 50vh;
		min-height: 300px;
		max-height: 600px;
	}
	main {
		max-width: 100%;
		margin: 0 auto;
		padding: var(--space-3);
	}
	h1 {
		color: var(--color-accent);
		font-size: var(--text-2xl);
		line-height: var(--leading-tight);
		margin-bottom: var(--space-2);
		text-wrap: balance;
	}
	p {
		color: var(--color-text-secondary);
		font-size: var(--text-base);
		line-height: var(--leading-relaxed);
		margin-bottom: var(--space-2);
	}
	.map-instructions {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		font-style: italic;
		margin-bottom: var(--space-3);
	}
	@media (max-width: 600px) {
		#map {
			height: 40vh;
			min-height: 250px;
		}
		main {
			padding: var(--space-2);
		}
		h1 {
			font-size: var(--text-xl);
		}
		p {
			font-size: var(--text-sm);
		}
	}
</style>
