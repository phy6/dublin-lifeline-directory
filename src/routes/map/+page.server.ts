import type { PageServerLoad } from './$types';
import servicesData from '$lib/data/services.json';

export const load: PageServerLoad = async () => {
	return { services: servicesData.services };
};
