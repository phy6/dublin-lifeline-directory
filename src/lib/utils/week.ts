import { DAY_KEYS, todayKey, type DayKey } from '$lib/utils/hours';
import type { MealEntry } from '$lib/types';
import type { PlannerAppointment } from '$lib/utils/planner';

/**
 * Deep week module: all Monday-first date math behind one seam.
 * Local-time semantics (on-device Dublin planner); documented, not UTC.
 */

/** 0-based Monday-first index of a date's weekday (Mon=0 … Sun=6). */
function mondayIndex(date: Date): number {
	return (date.getDay() + 6) % 7;
}

export function toISODate(date: Date): string {
	const y = date.getFullYear();
	const m = String(date.getMonth() + 1).padStart(2, '0');
	const d = String(date.getDate()).padStart(2, '0');
	return `${y}-${m}-${d}`;
}

export function mondayOf(base: Date): Date {
	const dow = mondayIndex(base);
	return new Date(base.getFullYear(), base.getMonth(), base.getDate() - dow);
}

export function dayKeyOf(date: Date): DayKey {
	return DAY_KEYS[mondayIndex(date)];
}

/** Injectable `now` keeps the interface the test surface (no clock-mocking). */
export { todayKey };

export function isToday(date: Date, now: Date = new Date()): boolean {
	return (
		date.getFullYear() === now.getFullYear() &&
		date.getMonth() === now.getMonth() &&
		date.getDate() === now.getDate()
	);
}

export function weekDates(weekMonday: Date): Date[] {
	const offset = mondayIndex(weekMonday);
	const monday = new Date(
		weekMonday.getFullYear(),
		weekMonday.getMonth(),
		weekMonday.getDate() - offset
	);
	return Array.from({ length: 7 }, (_, i) => {
		return new Date(monday.getFullYear(), monday.getMonth(), monday.getDate() + i);
	});
}

export interface ExpandedAppointment {
	appt: PlannerAppointment;
	date: Date;
}

export function expandWeek(appts: PlannerAppointment[], weekMonday: Date): ExpandedAppointment[] {
	const dates = weekDates(weekMonday);
	const out: ExpandedAppointment[] = [];
	for (const appt of appts) {
		const idx = DAY_KEYS.indexOf(appt.day);
		if (idx < 0) continue;
		const date = dates[idx];
		if (appt.recurrence === 'weekly') {
			out.push({ appt, date });
		} else {
			if (appt.weekOf === toISODate(date)) out.push({ appt, date });
		}
	}
	return out;
}

/** Counts of meals + appointments landing on a date (replaces page-local dotsFor). */
export function countsForDate(
	plan: PlannerAppointment[],
	meals: MealEntry[],
	date: Date
): { meals: number; appts: number } {
	const key = dayKeyOf(date);
	const iso = toISODate(date);
	const mealCount = meals.filter((m) => m.days.includes(key)).length;
	const apptCount = plan.filter((p) => {
		if (DAY_KEYS.indexOf(p.day) !== mondayIndex(date)) return false;
		return p.recurrence === 'weekly' || p.weekOf === iso;
	}).length;
	return { meals: mealCount, appts: apptCount };
}

export type { PlannerAppointment };
