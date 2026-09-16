<script lang="ts">
	import { onMount } from 'svelte';
	import type { ServiceLocation } from '$lib/types';
	import 'leaflet/dist/leaflet.css';

	let services = $state<ServiceLocation[]>([]);
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

		const res = await fetch('/services.json');
		const data = await res.json();
		services = data.services;

		if (mapEl) {
			map = L.map(mapEl, { preferCanvas: true }).setView([53.3496, -6.2687], 12);
			L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
				attribution: '&copy; OpenStreetMap contributors'
			}).addTo(map);

			services.forEach((s) => {
				if (s.latitude && s.longitude && map) {
					const marker = L.marker([s.latitude, s.longitude], { icon }).addTo(map);
					marker.bindPopup(
						`<b>${s.name}</b><br>${s.address}<br><a href="/service/${s.id}">View details</a>`
					);
				}
			});
			map.invalidateSize();
		}
	});
</script>

<main id="main-content">
	<h1>Map View</h1>
	<p>All Dublin City support services at a glance.</p>
	<div bind:this={mapEl} id="map" style="width: 100%; height: 600px;"></div>
</main>

<style>
	#map {
		width: 100%;
		min-height: 400px;
	}
	main {
		max-width: 100%;
		margin: 0 auto;
		padding: 1rem;
	}
	h1 {
		color: #1a73e8;
	}
</style>
