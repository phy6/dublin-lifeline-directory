import { describe, it, expect } from 'vitest';
import { mondayOf, dayKeyOf, todayKey, isToday, countsForDate } from '$lib/utils/week';
import type { PlannerAppointment } from '$lib/utils/planner';
import type { MealEntry } from '$lib/types';

describe('mondayOf', () => {
	it('normalises any day to its Monday without mutating input', () => {
		const wed = new Date(2026, 8, 16); // Wednesday
		const before = wed.getTime();
		const mon = mondayOf(wed);
		expect(mon.getDay()).toBe(1);
		expect(mon.getDate()).toBe(14);
		expect(wed.getTime()).toBe(before);
	});

	it('is idempotent on a Monday', () => {
		const mon = new Date(2026, 8, 14);
		expect(mondayOf(mon).getDate()).toBe(14);
	});
});

describe('dayKeyOf / todayKey', () => {
	it('maps Sunday to sun (Monday-first layout)', () => {
		expect(dayKeyOf(new Date(2026, 8, 13))).toBe('sun'); // a Sunday
		expect(dayKeyOf(new Date(2026, 8, 14))).toBe('mon');
	});

	it('todayKey honours the injected now', () => {
		expect(todayKey(new Date(2026, 8, 13))).toBe('sun');
		expect(todayKey(new Date(2026, 8, 16))).toBe('wed');
	});
});

describe('isToday', () => {
	it('matches same calendar day, honours injected now', () => {
		const now = new Date(2026, 8, 16, 12, 0);
		expect(isToday(new Date(2026, 8, 16, 8, 0), now)).toBe(true);
		expect(isToday(new Date(2026, 8, 17, 8, 0), now)).toBe(false);
	});
});

describe('countsForDate', () => {
	const meals = [{ id: 'm1', days: ['wed'] }] as MealEntry[];
	const plan: PlannerAppointment[] = [
		{
			id: 'a',
			title: 'Weekly',
			day: 'wed',
			start: '09:00',
			end: '10:00',
			location: '',
			notes: '',
			orgId: null,
			recurrence: 'weekly',
			source: 'personal',
			weekOf: '2026-09-14'
		},
		{
			id: 'b',
			title: 'Once',
			day: 'wed',
			start: '10:00',
			end: '10:30',
			location: '',
			notes: '',
			orgId: null,
			recurrence: 'once',
			source: 'personal',
			weekOf: '2026-09-16'
		}
	];

	it('counts meals + matching appts on the date', () => {
		expect(countsForDate(plan, meals, new Date(2026, 8, 16))).toEqual({ meals: 1, appts: 2 });
	});

	it('excludes once-appts from other weeks, keeps weekly ones', () => {
		expect(countsForDate(plan, meals, new Date(2026, 8, 23))).toEqual({ meals: 1, appts: 1 });
	});

	it('is zero on a day with nothing', () => {
		expect(countsForDate(plan, meals, new Date(2026, 8, 14))).toEqual({ meals: 0, appts: 0 });
	});
});
