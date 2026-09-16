import { describe, it, expect } from 'vitest';
import {
	normalizeDayKey,
	getHoursForDay,
	isOpenOnDay,
	DAY_KEYS,
	DAY_LABELS
} from '$lib/utils/hours';

describe('hours utilities', () => {
	describe('normalizeDayKey', () => {
		it('normalizes full day names', () => {
			expect(normalizeDayKey('monday')).toBe('mon');
			expect(normalizeDayKey('tuesday')).toBe('tue');
			expect(normalizeDayKey('wednesday')).toBe('wed');
			expect(normalizeDayKey('thursday')).toBe('thu');
			expect(normalizeDayKey('friday')).toBe('fri');
			expect(normalizeDayKey('saturday')).toBe('sat');
			expect(normalizeDayKey('sunday')).toBe('sun');
		});

		it('normalizes abbreviated day names', () => {
			expect(normalizeDayKey('mon')).toBe('mon');
			expect(normalizeDayKey('tue')).toBe('tue');
			expect(normalizeDayKey('wed')).toBe('wed');
			expect(normalizeDayKey('thu')).toBe('thu');
			expect(normalizeDayKey('fri')).toBe('fri');
			expect(normalizeDayKey('sat')).toBe('sat');
			expect(normalizeDayKey('sun')).toBe('sun');
		});

		it('handles case insensitivity', () => {
			expect(normalizeDayKey('MONDAY')).toBe('mon');
			expect(normalizeDayKey('Monday')).toBe('mon');
			expect(normalizeDayKey('TuEsDaY')).toBe('tue');
		});

		it('returns null for invalid input', () => {
			expect(normalizeDayKey('invalid')).toBeNull();
			expect(normalizeDayKey('')).toBeNull();
			expect(normalizeDayKey('   ')).toBeNull();
		});
	});

	describe('getHoursForDay', () => {
		it('returns hours for exact day match', () => {
			const hours = { monday: '09:00-17:00', tuesday: '10:00-18:00' };
			expect(getHoursForDay(hours, 'mon')).toBe('09:00-17:00');
			expect(getHoursForDay(hours, 'tue')).toBe('10:00-18:00');
		});

		it('returns hours for mon-fri range', () => {
			const hours = { 'mon-fri': '09:00-17:00' };
			expect(getHoursForDay(hours, 'mon')).toBe('09:00-17:00');
			expect(getHoursForDay(hours, 'wed')).toBe('09:00-17:00');
			expect(getHoursForDay(hours, 'fri')).toBe('09:00-17:00');
			expect(getHoursForDay(hours, 'sat')).toBeNull();
			expect(getHoursForDay(hours, 'sun')).toBeNull();
		});

		it('returns null for closed days', () => {
			const hours = { monday: 'Closed', saturday: '09:00-13:00' };
			expect(getHoursForDay(hours, 'mon')).toBeNull();
			expect(getHoursForDay(hours, 'sat')).toBe('09:00-13:00');
		});

		it('returns null for missing days', () => {
			const hours = { monday: '09:00-17:00' };
			expect(getHoursForDay(hours, 'tue')).toBeNull();
		});
	});

	describe('isOpenOnDay', () => {
		it('returns true for open days', () => {
			const hours = { monday: '09:00-17:00', 'mon-fri': '09:00-17:00' };
			expect(isOpenOnDay(hours, 'mon')).toBe(true);
			expect(isOpenOnDay(hours, 'wed')).toBe(true);
		});

		it('returns false for closed days', () => {
			const hours = { monday: 'Closed', saturday: 'Closed' };
			expect(isOpenOnDay(hours, 'mon')).toBe(false);
			expect(isOpenOnDay(hours, 'sat')).toBe(false);
		});

		it('returns false for missing days', () => {
			const hours = { monday: '09:00-17:00' };
			expect(isOpenOnDay(hours, 'tue')).toBe(false);
		});
	});

	describe('DAY_KEYS and DAY_LABELS', () => {
		it('has correct day keys', () => {
			expect(DAY_KEYS).toEqual(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']);
		});

		it('has correct day labels', () => {
			expect(DAY_LABELS).toEqual(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);
		});

		it('has matching lengths', () => {
			expect(DAY_KEYS.length).toBe(DAY_LABELS.length);
		});
	});
});
