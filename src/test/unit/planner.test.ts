import { describe, it, expect } from 'vitest';
import { weekDates, expandWeek, type PlannerAppointment } from '$lib/utils/planner';

const monday = new Date(2026, 8, 14); // a Monday

describe('weekDates', () => {
	it('returns 7 dates starting Monday without mutating input', () => {
		const before = monday.getTime();
		const days = weekDates(monday);
		expect(days).toHaveLength(7);
		expect(days[0].getDay()).toBe(1);
		expect(days[6].getDay()).toBe(0);
		expect(monday.getTime()).toBe(before);
	});
});

describe('expandWeek', () => {
	it('shows weekly entries every week and once entries only their week', () => {
		const weekly: PlannerAppointment = { id: 'a', title: 'Breakfast', day: 'tue', start: '07:30', end: '11:30', location: 'Capuchin', notes: '', orgId: 'capuchin-day-centre', recurrence: 'weekly', source: 'meal', weekOf: '2026-09-14' };
		const once: PlannerAppointment = { id: 'b', title: 'GP', day: 'wed', start: '10:00', end: '10:30', location: '', notes: '', orgId: null, recurrence: 'once', source: 'personal', weekOf: '2026-09-16' };
		const thisWeek = expandWeek([weekly, once], new Date(2026, 8, 14));
		expect(thisWeek.map((i) => i.appt.id).sort()).toEqual(['a', 'b']);
		const nextWeek = expandWeek([weekly, once], new Date(2026, 8, 21));
		expect(nextWeek.map((i) => i.appt.id)).toEqual(['a']);
	});
});
