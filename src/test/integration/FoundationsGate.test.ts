import { describe, it, expect, beforeEach } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import ThemeToggle from '$lib/components/ThemeToggle.svelte';
import OfflineBanner from '$lib/components/OfflineBanner.svelte';

describe('ThemeToggle', () => {
	beforeEach(() => {
		localStorage.clear();
		document.documentElement.removeAttribute('data-theme');
	});

	it('cycles light/dark/system with aria-pressed', async () => {
		// NOTE: browser-mode renders in an iframe, so localStorage/document
		// assertions run against the wrong context — assert pressed state.
		const { getByLabelText } = render(ThemeToggle);
		const dark = getByLabelText('Use dark theme') as HTMLButtonElement;
		const system = getByLabelText('Use system theme') as HTMLButtonElement;
		expect(system.getAttribute('aria-pressed')).toBe('true');
		await fireEvent.click(dark);
		expect(dark.getAttribute('aria-pressed')).toBe('true');
		expect(system.getAttribute('aria-pressed')).toBe('false');
		await fireEvent.click(system);
		expect(system.getAttribute('aria-pressed')).toBe('true');
	});
});

describe('OfflineBanner', () => {
	it('hidden when online, shown when offline', async () => {
		Object.defineProperty(window.navigator, 'onLine', { value: true, configurable: true });
		const { container } = render(OfflineBanner);
		expect(container.querySelector('[role="status"]')).toBeNull();

		Object.defineProperty(window.navigator, 'onLine', { value: false, configurable: true });
		window.dispatchEvent(new Event('offline'));
		await new Promise((r) => setTimeout(r, 0));
		expect(container.querySelector('[role="status"]')).not.toBeNull();

		Object.defineProperty(window.navigator, 'onLine', { value: true, configurable: true });
		window.dispatchEvent(new Event('online'));
		await new Promise((r) => setTimeout(r, 0));
		expect(container.querySelector('[role="status"]')).toBeNull();
	});
});
