import { describe, it, expect } from 'vitest';
import meals from '$lib/data/meals.json';
import { DAY_KEYS } from '$lib/utils/hours';

describe('meals data', () => {
	it('every meal has what/when/where and a verification date', () => {
		expect(meals.length).toBeGreaterThan(0);
		for (const m of meals) {
			expect(['breakfast', 'lunch', 'dinner']).toContain(m.mealType);
			expect(m.days.length).toBeGreaterThan(0);
			for (const d of m.days) expect(DAY_KEYS as readonly string[]).toContain(d);
			expect(/^([01]\d|2[0-3]):[0-5]\d$/.test(m.start)).toBe(true);
			expect(/^([01]\d|2[0-3]):[0-5]\d$/.test(m.end)).toBe(true);
			expect(m.orgId.length).toBeGreaterThan(0);
			expect(m.address.length).toBeGreaterThan(0);
			expect(m.verifiedDate.length).toBeGreaterThan(0);
		}
	});

	it('every meal orgId exists in services.json', async () => {
		const services = (await import('$lib/data/services.json')).default;
		const ids = new Set(services.services.map((s: { id: string }) => s.id));
		for (const m of meals) expect(ids.has(m.orgId)).toBe(true);
	});
});
