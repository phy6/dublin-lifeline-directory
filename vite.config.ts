import { sveltekit } from '@sveltejs/kit/vite';
import { SvelteKitPWA } from '@vite-pwa/sveltekit';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		sveltekit(),
		SvelteKitPWA({
			registerType: 'prompt',
			includeAssets: ['favicon.ico', 'icons/*.png', 'icons/*.svg', 'offline.html'],
			kit: {
				includeVersionFile: true
			},
			manifest: {
				name: 'Dublin City Support',
				short_name: 'Dublin Support',
				description: 'Find nearby support services in Dublin City',
				theme_color: '#1a73e8',
				background_color: '#ffffff',
				display: 'standalone',
				orientation: 'portrait',
				scope: '/',
				start_url: '/',
				categories: ['social'],
				icons: [
					{
						src: '/icons/icon-72x72.png',
						sizes: '72x72',
						type: 'image/png',
						purpose: 'any maskable'
					},
					{
						src: '/icons/icon-96x96.png',
						sizes: '96x96',
						type: 'image/png',
						purpose: 'any maskable'
					},
					{
						src: '/icons/icon-144x144.png',
						sizes: '144x144',
						type: 'image/png',
						purpose: 'any maskable'
					},
					{
						src: '/icons/icon-192x192.png',
						sizes: '192x192',
						type: 'image/png',
						purpose: 'any maskable'
					},
					{
						src: '/icons/icon-256x256.png',
						sizes: '256x256',
						type: 'image/png',
						purpose: 'any maskable'
					},
					{
						src: '/icons/icon-384x384.png',
						sizes: '384x384',
						type: 'image/png',
						purpose: 'any maskable'
					},
					{
						src: '/icons/icon-512x512.png',
						sizes: '512x512',
						type: 'image/png',
						purpose: 'any maskable'
					}
				]
			},
			workbox: {
				globPatterns: ['**/*.{js,css,html,ico,png,svg,webmanifest,ttf,woff,woff2,json}'],
				runtimeCaching: [
					// App shell — precache all build + static assets
					{
						urlPattern: /^https:\/\/dublin-city-support\.github\.io\//,
						handler: 'CacheFirst',
						options: {
							cacheName: 'app-shell',
							expiration: {
								maxEntries: 50,
								maxAgeSeconds: 30 * 24 * 60 * 60
							},
							cacheableResponse: { statuses: [0, 200] }
						}
					},
					// Static JSON data — stale-while-revalidate
					{
						urlPattern: /\/services\.json/,
						handler: 'StaleWhileRevalidate',
						options: {
							cacheName: 'data-json',
							expiration: {
								maxEntries: 10,
								maxAgeSeconds: 7 * 24 * 60 * 60
							}
						}
					},
					// Navigation — network first, cache fallback
					{
						urlPattern: ({ request }) => request.mode === 'navigate',
						handler: 'NetworkFirst',
						options: {
							cacheName: 'pages',
							networkTimeoutSeconds: 3,
							expiration: {
								maxEntries: 20,
								maxAgeSeconds: 1 * 24 * 60 * 60
							}
						}
					},
					// Existing OpenStreetMap rules
					{
						urlPattern: /^https:\/\/tile\.openstreetmap\.org\//,
						handler: 'CacheFirst'
					},
					{
						urlPattern: /^https:\/\/api\.openstreetmap\.org\//,
						handler: 'StaleWhileRevalidate'
					}
				]
			}
		})
	]
});
