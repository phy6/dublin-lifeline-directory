import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import FilterBar from '$lib/components/FilterBar.svelte';

describe('FilterBar', () => {
	const categories = ['Health', 'Housing', 'Food', 'Legal'];
	let onFilter: ReturnType<typeof vi.fn>;
	let onSearch: ReturnType<typeof vi.fn>;
	let onDayFilter: ReturnType<typeof vi.fn>;

	beforeEach(() => {
		onFilter = vi.fn();
		onSearch = vi.fn();
		onDayFilter = vi.fn();
	});

	it('renders search input and category chips', () => {
		const { container } = render(FilterBar, { categories, onFilter, onSearch, onDayFilter });

		expect(container.querySelector('input[id="search-input"]')).toBeInTheDocument();
		expect(container.querySelector('label[for="search-input"]')).toBeInTheDocument();
		expect(container.querySelectorAll('.filter-chips').length).toBe(2);
	});

	it('shows All Categories as default active chip', () => {
		const { container } = render(FilterBar, { categories, onFilter, onSearch, onDayFilter });

		const allChip = container.querySelector('.filter-chips button') as HTMLButtonElement;
		expect(allChip).toHaveTextContent('All Categories');
		expect(allChip).toHaveClass('active');
	});

	it('shows all provided categories as chips', () => {
		const { container } = render(FilterBar, { categories, onFilter, onSearch, onDayFilter });

		const categoryChips = container.querySelectorAll('.filter-chips')[0].querySelectorAll('button');
		expect(categoryChips.length).toBe(5);
		expect(categoryChips[0]).toHaveTextContent('All Categories');
		expect(categoryChips[1]).toHaveTextContent('Health');
		expect(categoryChips[2]).toHaveTextContent('Housing');
		expect(categoryChips[3]).toHaveTextContent('Food');
		expect(categoryChips[4]).toHaveTextContent('Legal');
	});

	it('shows day chips', () => {
		const { container } = render(FilterBar, { categories, onFilter, onSearch, onDayFilter });

		const dayChips = container.querySelectorAll('.filter-chips')[1].querySelectorAll('button');
		expect(dayChips.length).toBe(8); // All Days + 7 days
		expect(dayChips[0]).toHaveTextContent('All Days');
		expect(dayChips[1]).toHaveTextContent('Mon');
		expect(dayChips[2]).toHaveTextContent('Tue');
		expect(dayChips[3]).toHaveTextContent('Wed');
		expect(dayChips[4]).toHaveTextContent('Thu');
		expect(dayChips[5]).toHaveTextContent('Fri');
		expect(dayChips[6]).toHaveTextContent('Sat');
		expect(dayChips[7]).toHaveTextContent('Sun');
	});

	it('calls onSearch when typing in search input', () => {
		const { container } = render(FilterBar, { categories, onFilter, onSearch, onDayFilter });

		const input = container.querySelector('input[id="search-input"]') as HTMLInputElement;
		fireEvent.input(input, { target: { value: 'doctor' } });

		expect(onSearch).toHaveBeenCalledWith('doctor');
	});

	it('calls onFilter when clicking category chip', () => {
		const { container } = render(FilterBar, { categories, onFilter, onSearch, onDayFilter });

		const healthChip = container.querySelectorAll('.filter-chips')[0].querySelectorAll('button')[1];
		fireEvent.click(healthChip);

		expect(onFilter).toHaveBeenCalledWith('Health');
	});

	it('calls onDayFilter when clicking day chip', () => {
		const { container } = render(FilterBar, { categories, onFilter, onSearch, onDayFilter });

		const monChip = container.querySelectorAll('.filter-chips')[1].querySelectorAll('button')[1];
		fireEvent.click(monChip);

		expect(onDayFilter).toHaveBeenCalledWith('mon');
	});

	it('works with empty categories array', () => {
		const { container } = render(FilterBar, { categories: [], onFilter, onSearch, onDayFilter });

		const categoryChips = container.querySelectorAll('.filter-chips')[0].querySelectorAll('button');
		expect(categoryChips.length).toBe(1); // Only "All Categories"
		expect(categoryChips[0]).toHaveTextContent('All Categories');
	});

	it('handles rapid search input changes', () => {
		const { container } = render(FilterBar, { categories, onFilter, onSearch, onDayFilter });

		const input = container.querySelector('input[id="search-input"]') as HTMLInputElement;
		fireEvent.input(input, { target: { value: 'h' } });
		fireEvent.input(input, { target: { value: 'he' } });
		fireEvent.input(input, { target: { value: 'hea' } });

		expect(onSearch).toHaveBeenCalledTimes(3);
		expect(onSearch).toHaveBeenLastCalledWith('hea');
	});
});
