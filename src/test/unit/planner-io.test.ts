import { describe, it, expect } from 'vitest';
import { validateAppt, parseBackup, serializeBackup, backupFilename } from '$lib/utils/planner-io';
import type { PlannerAppointment } from '$lib/utils/planner';

const good: PlannerAppointment = {
	id: 'a',
	title: 'GP visit',
	day: 'wed',
	start: '10:00',
	end: '10:30',
	location: '',
	notes: '',
	orgId: null,
	recurrence: 'once',
	source: 'personal',
	weekOf: '2026-09-16'
};

describe('validateAppt', () => {
	it('accepts a well-formed entry', () => {
		expect(validateAppt(good)).toBe(true);
	});

	it.each([
		['unknown day', { ...good, day: 'funday' }],
		['bad start format', { ...good, start: '9am' }],
		['bad end format', { ...good, end: '25:00' }],
		['end before start', { ...good, start: '11:00', end: '10:00' }],
		['bad recurrence', { ...good, recurrence: 'monthly' }],
		['bad source', { ...good, source: 'imported' }],
		['bad weekOf shape', { ...good, weekOf: '16-09-2026' }],
		['impossible weekOf', { ...good, weekOf: '2026-13-99' }],
		['overflow weekOf (Feb 30 normalises)', { ...good, weekOf: '2026-02-30' }],
		['blank title', { ...good, title: '   ' }],
		['non-string orgId', { ...good, orgId: 42 }],
		['old 4-field entry (missing fields)', { id: 'x', title: 't', day: 'mon', start: '09:00' }]
	])('rejects %s', (_label, entry) => {
		expect(validateAppt(entry)).toBe(false);
	});
});

describe('parseBackup', () => {
	it('round-trips through serializeBackup', () => {
		expect(parseBackup(serializeBackup([good]))).toEqual([good]);
	});

	it('rejects malformed JSON, non-arrays, and arrays with one bad entry', () => {
		expect(parseBackup('not json')).toBeNull();
		expect(parseBackup('{"id":"a"}')).toBeNull();
		expect(parseBackup(serializeBackup([good, { ...good, day: 'funday' }]))).toBeNull();
	});
});

describe('backupFilename', () => {
	it('uses the injected date', () => {
		expect(backupFilename(new Date(2026, 8, 17))).toBe('lifeline-planner-backup-2026-09-17.json');
	});
});
