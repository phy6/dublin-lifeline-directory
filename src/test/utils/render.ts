import * as Svelte from 'svelte';
import * as DomTestingLibrary from '@testing-library/dom';
import { getQueriesForElement } from '@testing-library/dom';

export interface RenderResult<C> {
	container: HTMLElement;
	baseElement: HTMLElement;
	component: C;
	unmount: () => void;
	debug: (el?: HTMLElement) => void;
	[key: string]: unknown;
}

export function render<C extends Svelte.Component>(
	Component: new (options: { target: HTMLElement; props?: Record<string, unknown> }) => C,
	props: Record<string, unknown> = {},
	queries = DomTestingLibrary.queries
): RenderResult<C> {
	const container = document.createElement('div');
	document.body.appendChild(container);

	const component = new Component({ target: container, props });

	const boundQueries = getQueriesForElement(container, queries);

	return {
		container,
		baseElement: container,
		component,
		unmount: () => {
			component.$destroy();
			container.remove();
		},
		debug: (el = container) => console.log(DomTestingLibrary.prettyDOM(el)),
		...boundQueries
	};
}
