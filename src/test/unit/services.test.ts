import { describe, it, expect } from 'vitest';
import { applyFilters } from '$lib/utils/services';
import type { ServiceLocation } from '$lib/types';

function service(overrides: Partial<ServiceLocation> & { id: string }): ServiceLocation {
	return {
		name: 'Test',
		address: null,
		phone: null,
		email: null,
		website: null,
		hours: null,
		tags: null,
		services: null,
		category: 'Food',
		latitude: 0,
		longitude: 0,
		description: '',
		lastVerified: '',
		dynamicActivities: [],
		activityMatchCount: 0,
		dataSource: 'unknown',
		lastScraped: '',
		...overrides
	};
}

const services = [
	service({ id: 'a', name: 'Capuchin Breakfast', category: 'Food', hours: { mon: '07:30-11:30' } }),
	service({ id: 'b', name: 'Simon Shelter', category: 'Shelter', hours: { mon: 'closed' } }),
	service({
		id: 'c',
		name: 'Health Clinic',
		category: 'Medical',
		address: 'Capuchin Lane',
		tags: ['gp'],
		services: ['doctor-nurse'],
		hours: { mon: '09:00-17:00' }
	})
];

const all = { category: 'All', day: 'all', query: '' };

describe('applyFilters', () => {
	it('returns everything with neutral filters', () => {
		expect(applyFilters(services, all).map((s) => s.id)).toEqual(['a', 'b', 'c']);
	});

	it('filters by category', () => {
		expect(applyFilters(services, { ...all, category: 'Food' }).map((s) => s.id)).toEqual(['a']);
	});

	it('filters by open day', () => {
		expect(applyFilters(services, { ...all, day: 'mon' }).map((s) => s.id)).toEqual(['a', 'c']);
	});

	it('matches query across name, address, services, and tags', () => {
		expect(applyFilters(services, { ...all, query: 'capuchin' }).map((s) => s.id)).toEqual([
			'a',
			'c'
		]);
		expect(applyFilters(services, { ...all, query: 'GP' }).map((s) => s.id)).toEqual(['c']);
	});

	it('combines filters instead of dropping the query', () => {
		expect(
			applyFilters(services, { category: 'Medical', day: 'mon', query: 'capuchin' }).map(
				(s) => s.id
			)
		).toEqual(['c']);
		expect(
			applyFilters(services, { category: 'Food', day: 'mon', query: 'capuchin' }).map((s) => s.id)
		).toEqual(['a']);
	});
});
