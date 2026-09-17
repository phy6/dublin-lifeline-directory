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
	let modalRef: HTMLDivElement | undefined = $state(undefined);
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

	function focusables(): HTMLElement[] {
		if (!modalRef) return [];
		return [...modalRef.querySelectorAll('button, a[href]')].filter(
			(el) => el instanceof HTMLElement && !el.hasAttribute('disabled')
		) as HTMLElement[];
	}

	function focusFirst() {
		// Wait a tick so the {#if open} block has rendered.
		requestAnimationFrame(() => focusables()[0]?.focus());
	}

	function trapTab(e: KeyboardEvent) {
		if (e.key !== 'Tab') return;
		const items = focusables();
		if (items.length === 0) return;
		const first = items[0];
		const last = items[items.length - 1];
		if (e.shiftKey && document.activeElement === first) {
			e.preventDefault();
			last.focus();
		} else if (!e.shiftKey && document.activeElement === last) {
			e.preventDefault();
			first.focus();
		}
	}

	function openModal() {
		open = true;
		if (log.length === 0) startOver();
		focusFirst();
	}

	function closeModal() {
		open = false;
		fabRef?.focus();
	}

	function onOverlayClick(e: MouseEvent) {
		if (e.target === e.currentTarget) closeModal();
	}

	function onKeyDown(e: KeyboardEvent) {
		if (!open) return;
		if (e.key === 'Escape') closeModal();
		else trapTab(e);
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
	<span aria-hidden="true">💬</span>
	{lang === 'ga' ? 'Cabhair? Comhrá' : 'Need help? Chat'}
</button>

{#if open}
	<div
		class="modal-overlay active"
		id="chatbot-modal"
		role="dialog"
		aria-modal="true"
		aria-labelledby="chatbot-title"
		tabindex="-1"
		bind:this={modalRef}
		onkeydown={onKeyDown}
		onclick={onOverlayClick}
	>
		<div class="modal-box">
			<span class="grabber" aria-hidden="true"></span>
			<h3 id="chatbot-title">
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
				>↺ {lang === 'ga' ? 'Tosaigh arís' : 'Start over'}</button
			>
			<button class="close" onclick={closeModal} aria-label="Close chat">✕</button>
		</div>
	</div>
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
		border-radius: 999px;
		padding: 12px 16px;
		font-weight: 700;
		cursor: pointer;
		min-height: 48px;
		min-width: 48px;
		box-shadow: var(--shadow-md);
	}
	.modal-overlay {
		position: fixed;
		inset: 0;
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
		border-radius: var(--radius-lg);
		padding: var(--space-3);
		max-width: 420px;
		width: 100%;
		max-height: 90vh;
		overflow-y: auto;
		position: relative;
	}
	.crisis {
		font-size: var(--text-sm);
		font-weight: 700;
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
		border-radius: 12px;
		padding: 9px 12px;
		font-size: var(--text-sm);
		max-width: 88%;
	}
	.bubble.bot {
		background: var(--color-accent-container);
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
		border: 2px solid var(--color-accent);
		background: transparent;
		color: var(--color-accent);
		border-radius: 9px;
		padding: 9px 12px;
		text-align: left;
		font-weight: 700;
		cursor: pointer;
		text-decoration: none;
		font-size: var(--text-sm);
		min-height: 44px;
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
		display: block;
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
			border-radius: 999px;
			background: var(--color-border-strong);
			margin: 0 auto var(--space-2);
		}
		.chatbot-log {
			max-height: 40dvh;
		}
	}
</style>
