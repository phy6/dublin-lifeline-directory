import type { PageServerLoad } from './$types';
import servicesData from '$lib/data/services.json';
import { normalizeService } from '$lib/utils/services';

export const load: PageServerLoad = async ({ params }) => {
	const raw = (servicesData.services as unknown as Record<string, unknown>[]).find(
		(s) => s.id === params.id
	);
	return { service: raw ? normalizeService(raw) : null };
};
