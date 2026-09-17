import { DAY_KEYS } from '$lib/utils/hours';
import type { PlannerAppointment } from '$lib/utils/planner';

const TIME_RE = /^([01]\d|2[0-3]):[0-5]\d$/;
const ISO_RE = /^\d{4}-\d{2}-\d{2}$/;

/**
 * Deep planner-io module: every planner serialisation concern behind one
 * seam. The store, the backup download, and the restore path all cross this
 * interface, so the full-field gate lives here — not in callers.
 */
export function validateAppt(e: unknown): e is PlannerAppointment {
	if (typeof e !== 'object' || e === null) return false;
	const o = e as Record<string, unknown>;
	if (typeof o.id !== 'string' || o.id.length === 0) return false;
	if (typeof o.title !== 'string' || o.title.trim().length === 0) return false;
	if (typeof o.day !== 'string' || !(DAY_KEYS as readonly string[]).includes(o.day)) return false;
	if (typeof o.start !== 'string' || !TIME_RE.test(o.start)) return false;
	if (typeof o.end !== 'string' || !TIME_RE.test(o.end)) return false;
	if (o.end <= o.start) return false;
	if (typeof o.location !== 'string' || typeof o.notes !== 'string') return false;
	if (typeof o.orgId !== 'string' && o.orgId !== null) return false;
	if (o.recurrence !== 'once' && o.recurrence !== 'weekly') return false;
	if (o.source !== 'meal' && o.source !== 'personal') return false;
	if (typeof o.weekOf !== 'string' || !ISO_RE.test(o.weekOf)) return false;
	return isRealCalendarDate(o.weekOf);
}

/** Strict calendar check: rejects overflow like 2026-02-30 that Date() normalises. */
function isRealCalendarDate(iso: string): boolean {
	const [y, m, d] = iso.split('-').map(Number);
	if (m < 1 || m > 12 || d < 1 || d > 31) return false;
	const dt = new Date(y, m - 1, d);
	return dt.getFullYear() === y && dt.getMonth() === m - 1 && dt.getDate() === d;
}

/** Parse restore text; null means "reject the whole file" (no partial import). */
export function parseBackup(text: string): PlannerAppointment[] | null {
	try {
		const parsed: unknown = JSON.parse(text);
		if (!Array.isArray(parsed) || !parsed.every(validateAppt)) return null;
		return parsed;
	} catch {
		return null;
	}
}

export function serializeBackup(plan: PlannerAppointment[]): string {
	return JSON.stringify(plan);
}
export function backupFilename(now: Date = new Date()): string {
	const stamp = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
	return `lifeline-planner-backup-${stamp}.json`;
}

export const STORAGE_KEY = 'lifeline.planner.v1';

/**
 * Lenient by design: localStorage may hold entries saved before the strict
 * gate existed. Never destroy user data on read — the form rewrites entries
 * cleanly on next save, so old data heals itself. Strictness lives on the
 * restore/import path (parseBackup), not here.
 */
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

export function downloadFile(filename: string, text: string, mime: string): void {
	const blob = new Blob([text], { type: mime });
	const url = URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = filename;
	document.body.appendChild(a);
	a.click();
	a.remove();
	URL.revokeObjectURL(url);
}
