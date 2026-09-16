import { clientsClaim } from 'workbox-core';
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { NetworkOnly } from 'workbox-strategies';
import { offlineFallback } from 'workbox-recipes';

clientsClaim();

precacheAndRoute(self.__WB_MANIFEST);

offlineFallback({ pageFallback: '/offline.html' });

registerRoute({ request: ({ request }) => request.mode === 'navigate' }, new NetworkOnly());

self.addEventListener('message', async (event) => {
	if (event.data && event.data.type === 'DATA_UPDATE') {
		const clients = await self.clients.matchAll({ type: 'window' });
		clients.forEach((client) => {
			client.postMessage({
				type: 'DATA_UPDATE',
				version: event.data.version,
				lastUpdated: event.data.lastUpdated
			});
		});
	}
	if (event.data && event.data.type === 'TOGGLE_LOW_DATA') {
		const clients = await self.clients.matchAll({ type: 'window' });
		clients.forEach((client) => {
			client.postMessage({ type: 'LOW_DATA_MODE', enabled: event.data.enabled });
		});
	}
});
