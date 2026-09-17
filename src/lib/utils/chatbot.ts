export type Lang = 'en' | 'ga';
export interface LocalText {
	en: string;
	ga?: string;
}
export interface ChatbotOption {
	label: LocalText;
	next: string;
}
export interface ChatbotAction {
	type: 'tel' | 'filter';
	tag?: string;
	number?: string;
	label: LocalText;
}
export interface ChatbotNode {
	text: LocalText;
	options?: ChatbotOption[];
	action?: ChatbotAction;
	secondaryAction?: ChatbotAction;
}
export type ChatbotTree = Record<string, ChatbotNode>;

export function getNode(tree: ChatbotTree, key: string): ChatbotNode | undefined {
	return tree[key];
}

export function resolveText(node: ChatbotNode, lang: Lang): string {
	return lang === 'ga' && node.text.ga ? node.text.ga : node.text.en;
}

export function resolveLabel(text: LocalText, lang: Lang): string {
	return lang === 'ga' && text.ga ? text.ga : text.en;
}

export function isLeaf(node: ChatbotNode): boolean {
	return !node.options || node.options.length === 0;
}

export function validateTree(tree: ChatbotTree): string[] {
	const errors: string[] = [];
	for (const [key, node] of Object.entries(tree)) {
		if (!node.text?.en) errors.push(`${key}: missing en text`);
		for (const opt of node.options ?? []) {
			if (!opt.label?.en) errors.push(`${key}: option missing en label`);
			if (!tree[opt.next]) errors.push(`${key}: unknown next key "${opt.next}"`);
		}
	}
	return errors;
}

import type { ServiceLocation } from '$lib/types';

/** Map chatbot tags to real data vocabulary (tags, services slugs, categories). */
const TAG_SYNONYMS: Record<string, string[]> = {
	meal: ['food', 'meal'],
	parcel: ['parcel', 'food'],
	clothing: ['clothing', 'clothes', 'hygiene'],
	shower: ['shower', 'hygiene'],
	sleep: ['shelter', 'emergency shelter', 'housing'],
	health: ['health', 'healthcare', 'medical', 'doctor', 'nurse', 'dentist'],
	advice: ['advice', 'housing support', 'community support', 'welfare'],
	connectivity: ['connectivity', 'wifi', 'charging', 'phone charging'],
	shelter: ['shelter', 'emergency shelter', 'housing']
};

export function findServicesForTag(
	services: ServiceLocation[],
	tag: string,
	limit = 3
): ServiceLocation[] {
	const keys = [tag.toLowerCase(), ...(TAG_SYNONYMS[tag.toLowerCase()] ?? [])];
	const hay = (s: ServiceLocation) =>
		[...(s.tags ?? []), ...(s.services ?? []), s.category, s.name].join(' ').toLowerCase();
	return services.filter((s) => keys.some((k) => hay(s).includes(k))).slice(0, limit);
}
