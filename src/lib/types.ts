export interface ServiceLocation {
	id: string;
	name: string;
	address: string;
	phone: string;
	email: string;
	website: string;
	hours: Record<string, string>;
	tags: string[];
	services: string[];
	category: string;
	latitude: number;
	longitude: number;
	description: string;
	lastVerified: string;
	dynamicActivities: string[];
	activityMatchCount: number;
	dataSource: string;
	lastScraped: string;
	scrapeSuccess: boolean;
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
