import { describe, it, expect } from 'vitest';
import {
	normalizeService,
	normalizeServices,
	distinctCategories
} from '$lib/utils/services';
import { getHoursForDay, getOpenNowStatus } from '$lib/utils/hours';

describe('ragged pipeline data (3.3.0 shape)', () => {
	it('getHoursForDay returns null for null/string hours instead of throwing', () => {
		expect(getHoursForDay(null, 'mon')).toBeNull();
		expect(getHoursForDay(undefined, 'mon')).toBeNull();
		expect(getHoursForDay('Mon-Fri 09:00-17:00', 'mon')).toBeNull();
		expect(getOpenNowStatus(null)).toBe('unknown');
	});

	it('normalizeService defaults nulls and drops non-string entries', () => {
		const svc = normalizeService({
			id: 'x',
			name: 'X',
			hours: null,
			tags: null,
			services: null,
			category: null
		} as unknown as Record<string, unknown>);
		expect(svc.hours).toBeNull();
		expect(svc.tags).toBeNull();
		expect(svc.services).toBeNull();
		expect(svc.category).toBe('Uncategorised');
		expect(svc.dynamicActivities).toEqual([]);
	});

	it('normalizeService keeps dict hours and filters null day values', () => {
		const svc = normalizeService({
			id: 'x',
			name: 'X',
			hours: { monday: '09:00-17:00', sunday: null },
			tags: ['a', 1],
			services: ['b'],
			category: 'Health'
		} as unknown as Record<string, unknown>);
		expect(svc.hours).toEqual({ monday: '09:00-17:00' });
		expect(svc.tags).toEqual(['a']);
	});

	it('normalizeServices + distinctCategories handle the real dataset', async () => {
		const data = (await import('$lib/data/services.json')).default;
		const services = normalizeServices(
			data.services as unknown as Record<string, unknown>[]
		);
		expect(services).toHaveLength(14);
		// Every service renders without throwing on hours/tags/services access
		for (const s of services) {
			expect(() => getHoursForDay(s.hours, 'mon')).not.toThrow();
			expect(() => (s.tags ?? []).slice(0, 4)).not.toThrow();
			expect(() => (s.services ?? []).map(String)).not.toThrow();
		}
		expect(distinctCategories(services).length).toBeGreaterThan(0);
	});
});
