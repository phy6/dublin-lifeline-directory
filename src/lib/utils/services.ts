import type { ServiceLocation } from '$lib/types';

type RawService = Record<string, unknown>;

function asString(value: unknown): string | null {
	return typeof value === 'string' ? value : null;
}

function asStringArray(value: unknown): string[] | null {
	if (!Array.isArray(value)) return null;
	return value.filter((item): item is string => typeof item === 'string');
}

function asHours(value: unknown): ServiceLocation['hours'] {
	if (typeof value === 'string') return value;
	if (value && typeof value === 'object' && !Array.isArray(value)) {
		const entries = Object.entries(value as Record<string, unknown>)
			.filter((entry): entry is [string, string] => typeof entry[1] === 'string')
			.map(([day, text]): [string, string | undefined] => [day, text]);
		return Object.fromEntries(entries);
	}
	return null;
}

/**
 * Map one ragged pipeline JSON entry onto ServiceLocation.
 * The scraper emits nulls and omits keys for unknown fields, so every
 * nullable field gets an explicit default here instead of in components.
 */
export function normalizeService(raw: RawService): ServiceLocation {
	return {
		id: String(raw.id ?? ''),
		name: String(raw.name ?? ''),
		address: asString(raw.address),
		phone: asString(raw.phone),
		email: asString(raw.email),
		website: asString(raw.website),
		hours: asHours(raw.hours),
		tags: asStringArray(raw.tags),
		services: asStringArray(raw.services),
		category: typeof raw.category === 'string' && raw.category ? raw.category : 'Uncategorised',
		latitude: typeof raw.latitude === 'number' ? raw.latitude : 0,
		longitude: typeof raw.longitude === 'number' ? raw.longitude : 0,
		description: asString(raw.description) ?? '',
		lastVerified: asString(raw.lastVerified) ?? '',
		dynamicActivities: asStringArray(raw.dynamicActivities) ?? [],
		activityMatchCount: typeof raw.activityMatchCount === 'number' ? raw.activityMatchCount : 0,
		dataSource: asString(raw.dataSource) ?? 'unknown',
		lastScraped: asString(raw.lastScraped) ?? '',
		scrapeSuccess: typeof raw.scrapeSuccess === 'boolean' ? raw.scrapeSuccess : undefined
	};
}

export function normalizeServices(raw: RawService[]): ServiceLocation[] {
	return raw.map(normalizeService);
}

export function distinctCategories(services: ServiceLocation[]): string[] {
	return [...new Set(services.map((s) => s.category))].sort();
}

/**
 * Curated needs taxonomy (03) — mirrors scraper/pipeline.py NEEDS.
 * Expand by adding a slug in both places. Chips use exact matching:
 * a service matches a need iff its services array contains the slug.
 */
export const NEEDS = [
	'food',
	'hygiene',
	'medical',
	'mental-health',
	'addiction-support',
	'shelter',
	'employment',
	'connectivity'
] as const;

export type Need = (typeof NEEDS)[number];

export function matchesNeed(service: ServiceLocation, need: string): boolean {
	return service.services?.includes(need) ?? false;
}

export function distinctNeeds(services: ServiceLocation[]): string[] {
	const seen = new Set<string>();
	for (const s of services) for (const n of s.services ?? []) if ((NEEDS as readonly string[]).includes(n)) seen.add(n);
	return [...seen].sort();
}
