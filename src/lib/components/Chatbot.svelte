<script lang="ts">
	import { base } from '$app/paths';
	import tree from '$lib/data/chatbot-tree.json';
	import servicesData from '$lib/data/services.json';
	import ServiceCard from '$lib/components/ServiceCard.svelte';
	import { normalizeServices } from '$lib/utils/services';
	import {
		getNode,
		resolveText,
		resolveLabel,
		isLeaf,
		findServicesForTag,
		type ChatbotTree
	} from '$lib/utils/chatbot';
	import { lang as langStore } from '$lib/stores/lang.svelte';

	const chatbotTree = tree as unknown as ChatbotTree;
	const allServices = normalizeServices(
		servicesData.services as unknown as Record<string, unknown>[]
	);
	let open = $state(false);
	let fabRef: HTMLButtonElement | undefined = $state(undefined);
	let dialogRef: HTMLDialogElement | undefined = $state(undefined);
	let titleRef: HTMLHeadingElement | undefined = $state(undefined);
	const lang = $derived(langStore.current);
	let nodeKey = $state('start');
	let log = $state<{ who: 'bot' | 'user'; text: string }[]>([]);

	const node = $derived(getNode(chatbotTree, nodeKey));
	const inlineServices = $derived(
		node?.action?.type === 'filter' && node.action.tag
			? findServicesForTag(allServices, node.action.tag, 3)
			: []
	);

	function renderNode(key: string) {
		const n = getNode(chatbotTree, key);
		if (!n) {
			const fb = getNode(chatbotTree, 'no-match');
			if (fb) log = [...log, { who: 'bot', text: resolveText(fb, lang) }];
			return;
		}
		nodeKey = key;
		log = [...log, { who: 'bot', text: resolveText(n, lang) }];
	}

	function choose(label: string, next: string) {
		log = [...log, { who: 'user', text: label }];
		renderNode(next);
	}

	function startOver() {
		log = [];
		renderNode('start');
	}

	function syncDialog() {
		if (!dialogRef) return;
		if (open && !dialogRef.open) {
			dialogRef.showModal();
			// Heading first so screen-reader users land on context, not a button.
			requestAnimationFrame(() => titleRef?.focus());
		} else if (!open && dialogRef.open) {
			dialogRef.close();
		}
	}

	$effect(syncDialog);

	function openModal() {
		open = true;
		if (log.length === 0) startOver();
	}

	function closeModal() {
		dialogRef?.close();
		open = false;
		fabRef?.focus();
	}

	function onDialogClose() {
		// Native Escape/backdrop paths funnel here; keep state + focus in sync.
		if (open) {
			open = false;
			fabRef?.focus();
		}
	}

	function onOverlayClick(e: MouseEvent) {
		if (e.target === dialogRef) closeModal();
	}

	function actionHref(action: NonNullable<typeof node>['action']): string {
		if (!action) return `${base}/search`;
		if (action.type === 'tel') return `tel:${action.number}`;
		return `${base}/search?q=${encodeURIComponent(action.tag ?? '')}`;
	}
</script>

<button
	class="chatbot-fab"
	bind:this={fabRef}
	aria-haspopup="dialog"
	aria-expanded={open}
	aria-controls="chatbot-modal"
	onclick={openModal}
>
	<span aria-hidden="true"
		><svg
			class="fab-icon"
			viewBox="0 0 24 24"
			fill="none"
			stroke="currentColor"
			stroke-width="2"
			stroke-linecap="round"
			stroke-linejoin="round"
			><path
				d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"
			/></svg
		></span
	>
	{lang === 'ga' ? 'Cabhair? Comhrá' : 'Need help? Chat'}
</button>

{#if open}
	<dialog
		class="modal-overlay active"
		id="chatbot-modal"
		aria-labelledby="chatbot-title"
		bind:this={dialogRef}
		onclose={onDialogClose}
		onclick={onOverlayClick}
	>
		<div class="modal-box">
			<span class="grabber" aria-hidden="true"></span>
			<h3 id="chatbot-title" bind:this={titleRef} tabindex="-1">
				{lang === 'ga' ? 'Faigh an tseirbhís cheart' : 'Find the right service'}
			</h3>
			<p class="crisis">
				🚨 {lang === 'ga' ? 'Éigeandáil? Glaoigh 112.' : 'Emergency? Call 112.'}
				<a href="tel:112">112</a>
			</p>
			<div class="chatbot-log" aria-live="polite">
				{#each log as entry (entry.text + entry.who)}
					<div class="bubble {entry.who}">{entry.text}</div>
				{/each}
			</div>
			{#if node}
				<div class="options">
					{#each node.options ?? [] as opt (opt.next)}
						<button
							class="option-btn"
							onclick={() => choose(resolveLabel(opt.label, lang), opt.next)}
						>
							{resolveLabel(opt.label, lang)}
						</button>
					{/each}
					{#if isLeaf(node)}
						{#if node.action?.type === 'tel'}
							<a class="option-btn" href={actionHref(node.action)}
								>{resolveLabel(node.action.label, lang)}</a
							>
						{/if}
						{#if inlineServices.length > 0}
							<div class="inline-cards">
								{#each inlineServices as service (service.id)}
									<ServiceCard {service} />
								{/each}
							</div>
							{#if node.action?.type === 'filter'}
								<a class="see-all" href={actionHref(node.action)}
									>{lang === 'ga' ? 'Féach gach ceann →' : 'See all →'}</a
								>
							{/if}
						{:else if node.action?.type === 'filter'}
							<p class="no-match">
								{lang === 'ga'
									? 'Níor aimsíodh meaitseáil — bain triail as cuardach.'
									: 'No exact match — try search.'}
							</p>
							<a class="option-btn" href={actionHref(node.action)}
								>{lang === 'ga' ? 'Cuardaigh →' : 'Search →'}</a
							>
						{/if}
						{#if node.secondaryAction}
							<a class="option-btn" href={actionHref(node.secondaryAction)}
								>{resolveLabel(node.secondaryAction.label, lang)}</a
							>
						{/if}
					{/if}
				</div>
			{/if}
			<button class="restart" onclick={startOver}
				><svg
					class="btn-icon"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					aria-hidden="true"
					><polyline points="1 4 1 10 7 10" /><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" /></svg
				>
				{lang === 'ga' ? 'Tosaigh arís' : 'Start over'}</button
			>
			<button class="close" onclick={closeModal} aria-label="Close chat"
				><svg
					class="btn-icon"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					aria-hidden="true"
					><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg
				></button
			>
		</div>
	</dialog>
{/if}

<style>
	.chatbot-fab {
		position: fixed;
		right: max(var(--space-2), env(safe-area-inset-right));
		bottom: max(var(--space-2), env(safe-area-inset-bottom));
		z-index: 2200;
		background: var(--color-accent);
		color: var(--color-text-on-accent);
		border: 0;
		border-radius: var(--radius-full);
		padding: 12px 20px;
		font-family: var(--font-sans);
		font-weight: 700;
		font-size: var(--text-sm);
		cursor: pointer;
		min-height: 48px;
		min-width: 48px;
		box-shadow: var(--shadow-md);
		display: inline-flex;
		align-items: center;
		gap: var(--space-2);
	}
	.chatbot-fab:hover {
		background: var(--color-accent-hover);
	}
	.chatbot-fab:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
	}
	.modal-overlay {
		position: fixed;
		inset: 0;
		border: 0;
		margin: 0;
		max-width: 100vw;
		max-height: 100dvh;
		background: rgba(0, 0, 0, 0.5);
		display: none;
		z-index: 2201;
		align-items: center;
		justify-content: center;
		padding: 16px;
	}
	.modal-overlay.active {
		display: flex;
	}
	.modal-box {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-xl);
		padding: var(--space-3);
		max-width: 420px;
		width: 100%;
		max-height: 90vh;
		overflow-y: auto;
		position: relative;
		box-shadow: var(--shadow-lg);
	}
	.modal-box h3 {
		font-family: var(--font-display);
		font-weight: 800;
		letter-spacing: -0.02em;
		color: var(--color-text-primary);
		font-size: var(--text-xl);
		line-height: var(--leading-tight);
		margin: 0 0 var(--space-2);
		padding-right: var(--space-5);
	}
	.crisis {
		font-size: var(--text-sm);
		font-weight: 700;
		background: var(--color-danger-container);
		color: var(--color-danger-on-container);
		border: 1px solid var(--color-danger);
		border-radius: var(--radius-md);
		padding: var(--space-2) var(--space-3);
		margin: 0 0 var(--space-2);
	}
	.chatbot-log {
		max-height: 280px;
		overflow-y: auto;
		margin: 10px 0;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}
	.bubble {
		border-radius: var(--radius-lg);
		padding: 9px 12px;
		font-size: var(--text-sm);
		line-height: var(--leading-normal);
		max-width: 88%;
		color: var(--color-text-primary);
	}
	.bubble.bot {
		background: var(--color-surface-hover);
		border: 1px solid var(--color-border);
		align-self: flex-start;
	}
	.bubble.user {
		background: var(--color-accent);
		color: var(--color-text-on-accent);
		align-self: flex-end;
	}
	.options {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}
	.option-btn {
		border: 1px solid var(--color-accent);
		background: var(--color-surface);
		color: var(--color-accent);
		border-radius: var(--radius-full);
		padding: 9px 16px;
		text-align: left;
		font-weight: 700;
		cursor: pointer;
		text-decoration: none;
		font-size: var(--text-sm);
		font-family: var(--font-sans);
		min-height: 44px;
	}
	.option-btn:hover {
		background: var(--color-surface-hover);
	}
	.inline-cards {
		display: flex;
		flex-direction: column;
		gap: 8px;
		margin: 8px 0;
	}
	.see-all {
		font-size: var(--text-sm);
		font-weight: 700;
		text-align: center;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-height: 44px;
		min-width: 44px;
		padding: 8px;
	}
	.no-match {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}
	.restart,
	.close {
		margin-top: 10px;
		min-height: 44px;
		min-width: 44px;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-1);
		border-radius: var(--radius-full);
		border: 1px solid var(--color-border);
		background: var(--color-surface);
		color: var(--color-text-secondary);
		font-family: var(--font-sans);
		font-size: var(--text-sm);
		font-weight: 600;
		cursor: pointer;
		padding: 8px 16px;
	}
	.restart:focus-visible,
	.close:focus-visible,
	.option-btn:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
	}
	.fab-icon,
	.btn-icon {
		width: 1.1em;
		height: 1.1em;
		flex-shrink: 0;
	}
	.grabber {
		display: none;
	}
	@media (max-width: 600px) {
		.chatbot-fab {
			bottom: calc(76px + env(safe-area-inset-bottom));
		}
		.modal-overlay {
			padding: 0;
			align-items: flex-end;
		}
		.modal-box {
			max-width: 100%;
			width: 100%;
			max-height: 85dvh;
			border-radius: var(--radius-lg) var(--radius-lg) 0 0;
			padding-bottom: calc(var(--space-3) + env(safe-area-inset-bottom));
		}
		.grabber {
			display: block;
			width: 40px;
			height: 4px;
			border-radius: var(--radius-full);
			background: var(--color-border-strong);
			margin: 0 auto var(--space-2);
		}
		.chatbot-log {
			max-height: 40dvh;
		}
	}
</style>
