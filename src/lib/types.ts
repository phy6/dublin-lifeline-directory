export interface ServiceLocation {
	id: string;
	name: string;
	address: string | null;
	phone: string | null;
	email: string | null;
	website: string | null;
	hours: Record<string, string | undefined> | string | null;
	tags: string[] | null;
	services: string[] | null;
	category: string;
	latitude: number;
	longitude: number;
	description: string;
	lastVerified: string;
	dynamicActivities: string[];
	activityMatchCount: number;
	dataSource: string;
	lastScraped: string;
	scrapeSuccess?: boolean;
}

export interface ServicesData {
	version: string;
	lastUpdated: string;
	generatedBy: string;
	services: ServiceLocation[];
	metadata: {
		source: string;
		totalServices: number;
		categories: string[];
		coverage: string;
		nextSync: string;
		pipelineRun: string;
		differencesDetected: number;
		additions: number;
		updates: number;
		deletions: number;
	};
}
