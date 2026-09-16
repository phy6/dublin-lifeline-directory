/// <reference types="vitest/globals" />
/// <reference types="@testing-library/jest-dom" />

declare const localStorage: Storage & {
	getItem: ReturnType<typeof vi.fn>;
	setItem: ReturnType<typeof vi.fn>;
	removeItem: ReturnType<typeof vi.fn>;
	clear: ReturnType<typeof vi.fn>;
};

declare const navigator: Navigator & {
	connection?: NavigatorConnection;
	serviceWorker: ServiceWorkerContainer & {
		controller: ServiceWorker | null;
		ready: Promise<ServiceWorkerRegistration>;
	};
};
