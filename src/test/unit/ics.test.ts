import { describe, it, expect } from 'vitest';
import { appointmentToICS, weekToICS } from '$lib/utils/ics';

describe('appointmentToICS', () => {
	it('emits VEVENT with RRULE for weekly entries', () => {
		const ics = appointmentToICS(
			{
				id: 'a',
				title: 'Breakfast @ Capuchin',
				day: 'tue',
				start: '07:30',
				end: '11:30',
				location: '29 Bow St, Dublin 7',
				notes: '',
				orgId: 'capuchin-day-centre',
				recurrence: 'weekly',
				source: 'meal',
				weekOf: '2026-09-15'
			},
			new Date(2026, 8, 15)
		);
		expect(ics).toContain('BEGIN:VEVENT');
		expect(ics).toContain('SUMMARY:Breakfast @ Capuchin');
		expect(ics).toContain('DTSTART:20260915T073000');
		expect(ics).toContain('DTEND:20260915T113000');
		expect(ics).toContain('RRULE:FREQ=WEEKLY');
		expect(ics).toContain('LOCATION:29 Bow St\\, Dublin 7');
	});

	it('omits RRULE for once entries and escapes commas/semicolons', () => {
		const ics = appointmentToICS(
			{
				id: 'b',
				title: 'GP; follow-up, urgent',
				day: 'wed',
				start: '10:00',
				end: '10:30',
				location: '',
				notes: 'Bring; papers',
				orgId: null,
				recurrence: 'once',
				source: 'personal',
				weekOf: '2026-09-16'
			},
			new Date(2026, 8, 16)
		);
		expect(ics).not.toContain('RRULE');
		expect(ics).toContain('SUMMARY:GP\\; follow-up\\, urgent');
	});

	it('emits strict RFC 5545: UTC DTSTAMP, trailing CRLF, CALSCALE, folded long lines', () => {
		const appt = {
			id: 'c',
			title:
				'A very long appointment title that will definitely exceed seventy-five octets once prefixed',
			day: 'wed' as const,
			start: '10:00',
			end: '10:30',
			location: '',
			notes: '',
			orgId: null,
			recurrence: 'once' as const,
			source: 'personal' as const,
			weekOf: '2026-09-16'
		};
		const ics = weekToICS([{ appt, date: new Date(2026, 8, 16) }]);
		expect(ics).toMatch(/DTSTAMP:\d{8}T\d{6}Z/);
		expect(ics.endsWith('END:VCALENDAR\r\n')).toBe(true);
		expect(ics).toContain('CALSCALE:GREGORIAN');
		for (const line of ics.split('\r\n')) {
			expect(new TextEncoder().encode(line).length).toBeLessThanOrEqual(75);
		}
	});
});
