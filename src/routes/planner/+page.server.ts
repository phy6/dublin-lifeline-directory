import type { PageServerLoad } from './$types';
import servicesData from '$lib/data/services.json';
import mealsData from '$lib/data/meals.json';
import { normalizeServices } from '$lib/utils/services';
import type { MealEntry } from '$lib/types';

export const load: PageServerLoad = async () => {
	const services = normalizeServices(servicesData.services as unknown as Record<string, unknown>[]);
	return { services, meals: mealsData as MealEntry[] };
};
