import { test, expect } from '@playwright/test';

test.describe('Text Scaling', () => {
	test('scales text from 100% to 200%', async ({ page }) => {
		await page.goto('/');
		await page.waitForLoadState('networkidle');

		const html = page.locator('html');
		await expect(html).toHaveCSS('font-size', '16px');

		await page.getByRole('button', { name: /set text size to 125%/i }).click();
		await expect(html).toHaveCSS('font-size', '20px');

		await page.getByRole('button', { name: /set text size to 150%/i }).click();
		await expect(html).toHaveCSS('font-size', '24px');

		await page.getByRole('button', { name: /set text size to 175%/i }).click();
		await expect(html).toHaveCSS('font-size', '28px');

		await page.getByRole('button', { name: /set text size to 200%/i }).click();
		await expect(html).toHaveCSS('font-size', '32px');
	});

	test('persists text scale preference across reloads', async ({ page }) => {
		await page.goto('/');
		await page.waitForLoadState('networkidle');

		await page.getByRole('button', { name: /set text size to 175%/i }).click();
		await expect(page.locator('html')).toHaveCSS('font-size', '28px');

		await page.reload();
		await page.waitForLoadState('networkidle');

		await expect(page.locator('html')).toHaveCSS('font-size', '28px');
		await expect(page.getByRole('button', { name: /set text size to 175%/i })).toHaveAttribute(
			'aria-pressed',
			'true'
		);
	});

	test('text scale buttons have proper accessibility attributes', async ({ page }) => {
		await page.goto('/');
		await page.waitForLoadState('networkidle');

		const panel = page.getByRole('group', { name: /text size controls/i });
		await expect(panel).toBeVisible();

		const buttons = page.getByRole('button', { name: /set text size to/i });
		await expect(buttons).toHaveCount(5);

		for (const label of ['100%', '125%', '150%', '175%', '200%']) {
			const button = page.getByRole('button', {
				name: new RegExp(`set text size to ${label}`, 'i')
			});
			await expect(button).toHaveAttribute('aria-label', `Set text size to ${label}`);
		}
	});

	test('text scaling works with low data mode enabled', async ({ page }) => {
		await page.goto('/');
		await page.waitForLoadState('networkidle');

		await page.getByRole('button', { name: /enable low data mode/i }).click();
		await expect(page.getByRole('button', { name: /disable low data mode/i })).toBeVisible();

		await page.getByRole('button', { name: /set text size to 200%/i }).click();
		await expect(page.locator('html')).toHaveCSS('font-size', '32px');
	});
});
