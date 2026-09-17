import type { PageServerLoad } from './$types';
import servicesData from '$lib/data/services.json';
import { normalizeServices } from '$lib/utils/services';

export const load: PageServerLoad = async () => {
	return {
		services: normalizeServices(servicesData.services as unknown as Record<string, unknown>[])
	};
};
