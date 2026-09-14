import type { PageServerLoad } from './$types';
import servicesData from '$lib/data/services.json';

export const load: PageServerLoad = async ({ params }) => {
	const service = servicesData.services.find((s) => s.id === params.id);
	return { service };
};
