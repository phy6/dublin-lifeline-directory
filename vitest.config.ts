import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';
import { playwright } from '@vitest/browser-playwright';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		browser: {
			enabled: true,
			provider: playwright(),
			instances: [{ browser: 'chromium', headless: true }]
		},
		setupFiles: ['./src/test/setup.ts'],
		include: [
			'src/test/unit/**/*.{test,spec}.{js,ts}',
			'src/test/integration/**/*.{test,spec}.{js,ts}'
		],
		globals: true,
		coverage: {
			provider: 'v8',
			reporter: ['text', 'json', 'html']
		}
	}
});
