import type { PageServerLoad } from './$types';
import servicesData from '$lib/data/services.json';
import { normalizeServices, distinctCategories } from '$lib/utils/services';

export const load: PageServerLoad = async () => {
	const services = normalizeServices(servicesData.services as unknown as Record<string, unknown>[]);
	return {
		services,
		categories: distinctCategories(services)
	};
};
