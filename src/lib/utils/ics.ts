import type { PlannerAppointment } from '$lib/utils/planner';

export function escapeICSText(value: string): string {
	return value
		.replace(/\\/g, '\\\\')
		.replace(/;/g, '\\;')
		.replace(/,/g, '\\,')
		.replace(/\r\n|\r|\n/g, '\\n');
}

function pad(n: number): string {
	return String(n).padStart(2, '0');
}

function formatFloating(date: Date): string {
	return (
		`${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}` +
		`T${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`
	);
}

function formatUTC(date: Date): string {
	return (
		`${date.getUTCFullYear()}${pad(date.getUTCMonth() + 1)}${pad(date.getUTCDate())}` +
		`T${pad(date.getUTCHours())}${pad(date.getUTCMinutes())}${pad(date.getUTCSeconds())}Z`
	);
}

/** Fold a content line to ≤75 octets per RFC 5545 §3.1 (byte-safe for ASCII; our output is ASCII post-escape). */
function foldLine(line: string): string {
	const bytes = line.length;
	if (bytes <= 75) return line;
	let out = '';
	let start = 0;
	while (start < line.length) {
		const chunk = line.slice(start, start + 74);
		out += (start === 0 ? '' : '\r\n ') + chunk;
		start += 74;
	}
	return out;
}

function joinCRLF(lines: string[]): string {
	return lines.map(foldLine).join('\r\n') + '\r\n';
}

function withTime(date: Date, time: string): Date {
	const [h, m] = time.split(':').map(Number);
	return new Date(date.getFullYear(), date.getMonth(), date.getDate(), h, m ?? 0, 0);
}

export function appointmentToICS(appt: PlannerAppointment, date: Date): string {
	const lines = [
		'BEGIN:VEVENT',
		`UID:${appt.id}@dublinlifeline`,
		`DTSTAMP:${formatUTC(new Date())}`,
		`DTSTART:${formatFloating(withTime(date, appt.start))}`,
		`DTEND:${formatFloating(withTime(date, appt.end))}`,
		`SUMMARY:${escapeICSText(appt.title)}`,
		`LOCATION:${escapeICSText(appt.location)}`,
		`DESCRIPTION:${escapeICSText(appt.notes)}`
	];
	if (appt.recurrence === 'weekly') lines.push('RRULE:FREQ=WEEKLY');
	lines.push('END:VEVENT');
	return joinCRLF(lines);
}

export function weekToICS(items: { appt: PlannerAppointment; date: Date }[]): string {
	const eventLines = items.flatMap((i) =>
		appointmentToICS(i.appt, i.date).split('\r\n').filter(Boolean)
	);
	return joinCRLF([
		'BEGIN:VCALENDAR',
		'VERSION:2.0',
		'PRODID:-//DublinLifeline//Planner//EN',
		'CALSCALE:GREGORIAN',
		...eventLines,
		'END:VCALENDAR'
	]);
}
