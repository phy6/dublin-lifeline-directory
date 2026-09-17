import { describe, it, expect, beforeEach, vi } from 'vitest';
import { loadPlan, savePlan, STORAGE_KEY } from '$lib/utils/planner-store';

// src/test/setup.ts stubs localStorage with no-op vi.fn()s; replace with a
// minimal in-memory implementation so round-trip behaviour is testable.
const store = new Map<string, string>();
vi.stubGlobal('localStorage', {
	getItem: (key: string) => (store.has(key) ? store.get(key)! : null),
	setItem: (key: string, value: string) => {
		store.set(key, String(value));
	},
	removeItem: (key: string) => {
		store.delete(key);
	},
	clear: () => {
		store.clear();
	}
});

beforeEach(() => localStorage.clear());

describe('planner store', () => {
	it('round-trips appointments', () => {
		savePlan([{ id: 'a', title: 'T', day: 'mon', start: '09:00', end: '10:00', location: '', notes: '', orgId: null, recurrence: 'once', source: 'personal', weekOf: '2026-09-14' }]);
		expect(loadPlan()).toHaveLength(1);
		expect(JSON.parse(localStorage.getItem(STORAGE_KEY)!)).toHaveLength(1);
	});

	it('returns [] on corrupt data instead of throwing', () => {
		localStorage.setItem(STORAGE_KEY, '{broken');
		expect(loadPlan()).toEqual([]);
	});
});
