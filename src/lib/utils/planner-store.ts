import type { PlannerAppointment } from '$lib/utils/planner';

export const STORAGE_KEY = 'lifeline.planner.v1';

export function loadPlan(): PlannerAppointment[] {
	if (typeof localStorage === 'undefined') return [];
	try {
		const raw = localStorage.getItem(STORAGE_KEY);
		if (!raw) return [];
		const parsed: unknown = JSON.parse(raw);
		if (!Array.isArray(parsed)) return [];
		return parsed as PlannerAppointment[];
	} catch {
		return [];
	}
}

export function savePlan(appts: PlannerAppointment[]): void {
	if (typeof localStorage === 'undefined') return;
	try {
		localStorage.setItem(STORAGE_KEY, JSON.stringify(appts));
	} catch {
		// Storage full or unavailable — planner state stays in memory.
	}
}
