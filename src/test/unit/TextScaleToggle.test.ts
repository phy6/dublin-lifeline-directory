import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/svelte';
import TextScaleToggle from '$lib/components/TextScaleToggle.svelte';

describe('TextScaleToggle', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		document.documentElement.style.fontSize = '';
		localStorage.getItem.mockReturnValue(null);
	});

	it('renders text scale panel with all size buttons', () => {
		const { container } = render(TextScaleToggle);

		expect(
			container.querySelector('[role="group"][aria-label="Text size controls"]')
		).toBeInTheDocument();
		expect(
			container.querySelector('button[aria-label="Set text size to 100%"]')
		).toBeInTheDocument();
		expect(
			container.querySelector('button[aria-label="Set text size to 125%"]')
		).toBeInTheDocument();
		expect(
			container.querySelector('button[aria-label="Set text size to 150%"]')
		).toBeInTheDocument();
		expect(
			container.querySelector('button[aria-label="Set text size to 175%"]')
		).toBeInTheDocument();
		expect(
			container.querySelector('button[aria-label="Set text size to 200%"]')
		).toBeInTheDocument();
	});

	it('sets font size on document when button clicked', async () => {
		const { container } = render(TextScaleToggle);

		const button150 = container.querySelector(
			'button[aria-label="Set text size to 150%"]'
		) as HTMLButtonElement;
		await button150.click();

		expect(document.documentElement.style.fontSize).toBe('150%');
		expect(localStorage.setItem).toHaveBeenCalledWith('dcs-text-scale', '150');
	});

	it('loads saved scale from localStorage on mount', () => {
		localStorage.getItem.mockReturnValue('175');

		render(TextScaleToggle);

		expect(document.documentElement.style.fontSize).toBe('175%');
		expect(localStorage.getItem).toHaveBeenCalledWith('dcs-text-scale');
	});

	it('marks active button with aria-pressed', async () => {
		const { container } = render(TextScaleToggle);

		const button150 = container.querySelector(
			'button[aria-label="Set text size to 150%"]'
		) as HTMLButtonElement;
		expect(button150).not.toHaveAttribute('aria-pressed', 'true');

		await button150.click();

		expect(button150).toHaveAttribute('aria-pressed', 'true');
		const button100 = container.querySelector(
			'button[aria-label="Set text size to 100%"]'
		) as HTMLButtonElement;
		expect(button100).toHaveAttribute('aria-pressed', 'false');
	});

	it('has proper focus styles for accessibility', () => {
		const { container } = render(TextScaleToggle);

		const button = container.querySelector(
			'button[aria-label="Set text size to 100%"]'
		) as HTMLButtonElement;
		button.focus();
		expect(button).toHaveStyle('outline: 3px solid rgb(255, 193, 7)');
	});
});
