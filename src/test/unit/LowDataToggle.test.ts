import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/svelte';
import LowDataToggle from '$lib/components/LowDataToggle.svelte';

interface NavigatorConnection {
	saveData: boolean;
	effectiveType: string;
}

describe('LowDataToggle', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		localStorage.getItem.mockReturnValue(null);
		(navigator.connection as NavigatorConnection).saveData = false;
		(navigator.connection as NavigatorConnection).effectiveType = '4g';
	});

	it('renders toggle button with initial state OFF', () => {
		const { container } = render(LowDataToggle);

		const button = container.querySelector('button') as HTMLButtonElement;
		expect(button).toBeInTheDocument();
		expect(button).toHaveTextContent('📶 Low Data');
		expect(button).not.toHaveClass('active');
	});

	it('toggles low data mode on click', async () => {
		const { container } = render(LowDataToggle);

		const button = container.querySelector('button') as HTMLButtonElement;
		await button.click();

		expect(button).toHaveAttribute('aria-pressed', 'true');
		expect(button).toHaveTextContent('📶 Low Data ON');
		expect(button).toHaveClass('active');
		expect(localStorage.setItem).toHaveBeenCalledWith('dcs-low-data', 'true');
	});

	it('sends message to service worker when toggled', async () => {
		const { container } = render(LowDataToggle);

		const button = container.querySelector('button') as HTMLButtonElement;
		await button.click();

		expect(navigator.serviceWorker.controller?.postMessage).toHaveBeenCalledWith({
			type: 'TOGGLE_LOW_DATA',
			enabled: true
		});
	});

	it('loads enabled state from localStorage on mount', () => {
		localStorage.getItem.mockReturnValue('true');

		const { container } = render(LowDataToggle);

		const button = container.querySelector('button') as HTMLButtonElement;
		expect(button).toHaveAttribute('aria-pressed', 'true');
		expect(button).toHaveClass('active');
		expect(navigator.serviceWorker.controller?.postMessage).toHaveBeenCalledWith({
			type: 'TOGGLE_LOW_DATA',
			enabled: true
		});
	});

	it('auto-enables based on saveData connection property', () => {
		(navigator.connection as NavigatorConnection).saveData = true;

		const { container } = render(LowDataToggle);

		const button = container.querySelector('button') as HTMLButtonElement;
		expect(button).toHaveAttribute('aria-pressed', 'true');
	});

	it('auto-enables based on 2g connection type', () => {
		(navigator.connection as NavigatorConnection).effectiveType = '2g';

		const { container } = render(LowDataToggle);

		const button = container.querySelector('button') as HTMLButtonElement;
		expect(button).toHaveAttribute('aria-pressed', 'true');
	});

	it('auto-enables based on slow-2g connection type', () => {
		(navigator.connection as NavigatorConnection).effectiveType = 'slow-2g';

		const { container } = render(LowDataToggle);

		const button = container.querySelector('button') as HTMLButtonElement;
		expect(button).toHaveAttribute('aria-pressed', 'true');
	});
});
