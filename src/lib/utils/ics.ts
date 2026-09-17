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

function withTime(date: Date, time: string): Date {
	const [h, m] = time.split(':').map(Number);
	return new Date(date.getFullYear(), date.getMonth(), date.getDate(), h, m ?? 0, 0);
}

export function appointmentToICS(appt: PlannerAppointment, date: Date): string {
	const lines = [
		'BEGIN:VEVENT',
		`UID:${appt.id}@dublinlifeline`,
		`DTSTAMP:${formatFloating(new Date())}`,
		`DTSTART:${formatFloating(withTime(date, appt.start))}`,
		`DTEND:${formatFloating(withTime(date, appt.end))}`,
		`SUMMARY:${escapeICSText(appt.title)}`,
		`LOCATION:${escapeICSText(appt.location)}`,
		`DESCRIPTION:${escapeICSText(appt.notes)}`
	];
	if (appt.recurrence === 'weekly') lines.push('RRULE:FREQ=WEEKLY');
	lines.push('END:VEVENT');
	return lines.join('\r\n');
}

export function weekToICS(items: { appt: PlannerAppointment; date: Date }[]): string {
	const events = items.map((i) => appointmentToICS(i.appt, i.date));
	return [
		'BEGIN:VCALENDAR',
		'VERSION:2.0',
		'PRODID:-//DublinLifeline//Planner//EN',
		...events,
		'END:VCALENDAR'
	].join('\r\n');
}
