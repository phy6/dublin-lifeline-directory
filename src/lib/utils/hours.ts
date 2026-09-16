export const DAY_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] as const;
export const DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as const;

export type DayKey = (typeof DAY_KEYS)[number];

export function normalizeDayKey(day: string): DayKey | null {
	const lower = day.toLowerCase().trim();
	if (lower.startsWith('mon')) return 'mon';
	if (lower.startsWith('tue')) return 'tue';
	if (lower.startsWith('wed')) return 'wed';
	if (lower.startsWith('thu')) return 'thu';
	if (lower.startsWith('fri')) return 'fri';
	if (lower.startsWith('sat')) return 'sat';
	if (lower.startsWith('sun')) return 'sun';
	return null;
}

export function getHoursForDay(hours: Record<string, string | undefined>, day: DayKey): string | null {
	for (const [key, value] of Object.entries(hours)) {
		const normalized = normalizeDayKey(key);
		if (normalized === day && value && value.toLowerCase() !== 'closed') {
			return value;
		}
		if (key.toLowerCase().includes('mon-fri') || key.toLowerCase().includes('monday-friday')) {
			if (day !== 'sat' && day !== 'sun' && value && value.toLowerCase() !== 'closed') {
				return value;
			}
		}
	}
	return null;
}

export function isOpenOnDay(hours: Record<string, string | undefined>, day: DayKey): boolean {
	const dayHours = getHoursForDay(hours, day);
	if (!dayHours) return false;
	const lower = dayHours.toLowerCase();
	return lower !== 'closed' && lower !== '' && lower !== 'null';
}

export function isOpenNow(hours: Record<string, string | undefined>): boolean {
	const now = new Date();
	const dayIndex = now.getDay();
	const dayMap: DayKey[] = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
	const today = dayMap[dayIndex];
	return isOpenOnDay(hours, today);
}

export function getOpenNowStatus(hours: Record<string, string | undefined>): 'open' | 'closed' | 'unknown' {
	const now = new Date();
	const dayIndex = now.getDay();
	const dayMap: DayKey[] = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
	const today = dayMap[dayIndex];
	const dayHours = getHoursForDay(hours, today);
	if (!dayHours) return 'unknown';
	const lower = dayHours.toLowerCase();
	if (lower === 'closed' || lower === '' || lower === 'null') return 'closed';
	return 'open';
}
