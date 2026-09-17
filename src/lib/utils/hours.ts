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

export type HoursInput = Record<string, string | undefined> | string | null | undefined;

export function getHoursForDay(hours: HoursInput, day: DayKey): string | null {
	// Scraper data is ragged: hours can be null or a free-text string.
	// Only dict-shaped hours are day-resolvable; anything else is unknown.
	if (!hours || typeof hours !== 'object') return null;
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

export function isOpenOnDay(hours: HoursInput, day: DayKey): boolean {
	const dayHours = getHoursForDay(hours, day);
	if (!dayHours) return false;
	const lower = dayHours.toLowerCase();
	return lower !== 'closed' && lower !== '' && lower !== 'null';
}

/** Injectable `now` keeps the interface the test surface (no clock-mocking). */
export function todayKey(now: Date = new Date()): DayKey {
	const dayMap: DayKey[] = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
	return dayMap[now.getDay()];
}

export function isOpenNow(hours: HoursInput, now: Date = new Date()): boolean {
	return isOpenOnDay(hours, todayKey(now));
}

export function getOpenNowStatus(
	hours: HoursInput,
	now: Date = new Date()
): 'open' | 'closed' | 'unknown' {
	const dayHours = getHoursForDay(hours, todayKey(now));
	if (!dayHours) return 'unknown';
	const lower = dayHours.toLowerCase();
	if (lower === 'closed' || lower === '' || lower === 'null') return 'closed';
	return 'open';
}
