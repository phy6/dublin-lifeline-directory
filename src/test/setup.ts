import { vi } from 'vitest';
import '@testing-library/jest-dom';

vi.stubGlobal('localStorage', {
	getItem: vi.fn(),
	setItem: vi.fn(),
	removeItem: vi.fn(),
	clear: vi.fn()
});

// Mock navigator.connection
const mockConnection = {
	saveData: false,
	effectiveType: '4g',
	addEventListener: vi.fn(),
	removeEventListener: vi.fn(),
	dispatchEvent: vi.fn()
};

Object.defineProperty(navigator, 'connection', {
	writable: true,
	configurable: true,
	value: mockConnection
});

// Mock navigator.serviceWorker
const mockController = {
	postMessage: vi.fn()
};

Object.defineProperty(navigator, 'serviceWorker', {
	writable: true,
	configurable: true,
	value: {
		controller: mockController,
		ready: Promise.resolve({ active: mockController })
	}
});
