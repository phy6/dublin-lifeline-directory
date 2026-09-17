import { describe, it, expect } from 'vitest';
import { getNode, resolveText, isLeaf, validateTree, findServicesForTag, type ChatbotTree } from '$lib/utils/chatbot';
import type { ServiceLocation } from '$lib/types';

const tree: ChatbotTree = {
	start: {
		text: { en: 'What do you need right now?', ga: 'Cad atá uait anois?' },
		options: [
			{ label: { en: 'A meal', ga: 'Béile' }, next: 'meal' },
			{ label: { en: 'Somewhere to sleep', ga: 'Áit codlata' }, next: 'sleep' }
		]
	},
	meal: {
		text: { en: 'Hot meals here.' },
		action: { type: 'filter', tag: 'meal', label: { en: 'Show meals' } }
	},
	sleep: {
		text: { en: 'Call DRHE first.', ga: 'Glaoigh ar DRHE.' },
		action: { type: 'tel', number: '1800707707', label: { en: 'Call DRHE' } }
	}
};

describe('chatbot tree renderer', () => {
	it('gets a node by key', () => {
		expect(getNode(tree, 'start')?.options).toHaveLength(2);
		expect(getNode(tree, 'missing')).toBeUndefined();
	});

	it('resolves text with English fallback', () => {
		expect(resolveText(tree.meal, 'ga')).toBe('Hot meals here.');
		expect(resolveText(tree.sleep, 'ga')).toBe('Glaoigh ar DRHE.');
	});

	it('detects leaf nodes', () => {
		expect(isLeaf(tree.start)).toBe(false);
		expect(isLeaf(tree.meal)).toBe(true);
	});

	it('validates next keys exist', () => {
		expect(validateTree(tree)).toEqual([]);
		const bad = { ...tree, start: { ...tree.start, options: [{ label: { en: 'x' }, next: 'nope' }] } };
		expect(validateTree(bad as ChatbotTree).length).toBeGreaterThan(0);
	});

	describe('findServicesForTag', () => {
		const svc = (over: Partial<ServiceLocation>): ServiceLocation => ({
			id: 'x', name: 'Test', address: null, phone: null, email: null, website: null,
			hours: null, tags: null, services: null, category: 'Food',
			latitude: 0, longitude: 0, description: '', lastVerified: '',
			dynamicActivities: [], activityMatchCount: 0, dataSource: 't', lastScraped: '', ...over
		});
		const services = [
			svc({ id: 'a', name: 'Capuchin', tags: ['food'], category: 'Food' }),
			svc({ id: 'b', name: 'Safetynet', tags: ['healthcare'], category: 'Health Support' }),
			svc({ id: 'c', name: 'Focus', category: 'Housing Support' })
		];
		it('matches tag synonyms and caps at 3', () => {
			expect(findServicesForTag(services, 'meal').map((s) => s.id)).toEqual(['a']);
			expect(findServicesForTag(services, 'health').map((s) => s.id)).toEqual(['b']);
			expect(findServicesForTag(services, 'shelter').map((s) => s.id)).toEqual(['c']);
			expect(findServicesForTag(services, 'meal', 3)).toHaveLength(1);
		});
		it('returns empty for no match so UI shows fallback', () => {
			expect(findServicesForTag(services, 'zzz')).toEqual([]);
		});
	});
});
