import { DAY_KEYS, type DayKey } from '$lib/utils/hours';

export interface PlannerAppointment {
	id: string;
	title: string;
	day: DayKey;
	start: string;
	end: string;
	location: string;
	notes: string;
	orgId: string | null;
	recurrence: 'once' | 'weekly';
	source: 'meal' | 'personal';
	weekOf: string;
}

export function toISODate(date: Date): string {
	const y = date.getFullYear();
	const m = String(date.getMonth() + 1).padStart(2, '0');
	const d = String(date.getDate()).padStart(2, '0');
	return `${y}-${m}-${d}`;
}

export function dayIndexMondayFirst(day: DayKey): number {
	return DAY_KEYS.indexOf(day);
}

export function weekDates(weekMonday: Date): Date[] {
	const offset = (weekMonday.getDay() + 6) % 7;
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
