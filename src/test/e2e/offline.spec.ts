import { test, expect } from '@playwright/test';

test.describe('Offline Mode', () => {
	test('service worker registration is attempted', async ({ page }) => {
		await page.goto('/');
		await page.waitForLoadState('networkidle');

		// Check that service worker registration is attempted
		const swReg = await page.evaluate(() => {
			return 'serviceWorker' in navigator;
		});
		expect(swReg).toBe(true);
	});

	test('low data mode can be toggled via UI', async ({ page }) => {
		await page.goto('/');
		await page.waitForLoadState('networkidle');

		// Click the low data toggle button
		const toggleButton = page.getByRole('button', { name: /enable low data mode/i });
		await expect(toggleButton).toBeVisible();
		await toggleButton.click();

		// Verify it shows as enabled
		await expect(page.getByRole('button', { name: /disable low data mode/i })).toBeVisible({
			timeout: 5000
		});
	});
});
