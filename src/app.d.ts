// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}

	interface NavigatorConnection {
		saveData: boolean;
		effectiveType: string;
		addEventListener: (type: string, listener: EventListener) => void;
		removeEventListener: (type: string, listener: EventListener) => void;
		dispatchEvent: (event: Event) => boolean;
	}

	interface Navigator {
		connection?: NavigatorConnection;
	}
}

export {};
