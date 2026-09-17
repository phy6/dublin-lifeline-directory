import { DAY_KEYS, type DayKey } from '$lib/utils/hours';

// Week math lives in the deep week module; re-exported here so existing
// importers keep working through one seam.
export {
	weekDates,
	expandWeek,
	toISODate,
	type ExpandedAppointment
} from '$lib/utils/week';

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

export function dayIndexMondayFirst(day: DayKey): number {
	return DAY_KEYS.indexOf(day);
}

/** Monday-first month grid: rows of 7 cells, null for padding days outside the month. */
export function monthGrid(year: number, monthIndex: number): (Date | null)[][] {
	const first = new Date(year, monthIndex, 1);
	const lead = (first.getDay() + 6) % 7;
	const total = new Date(year, monthIndex + 1, 0).getDate();
	const cells: (Date | null)[] = [];
	for (let i = 0; i < lead; i++) cells.push(null);
	for (let d = 1; d <= total; d++) cells.push(new Date(year, monthIndex, d));
	while (cells.length % 7 !== 0) cells.push(null);
	const rows: (Date | null)[][] = [];
	for (let i = 0; i < cells.length; i += 7) rows.push(cells.slice(i, i + 7));
	return rows;
}
