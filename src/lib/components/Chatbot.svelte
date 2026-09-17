<script lang="ts">
	import { base } from '$app/paths';
	import tree from '$lib/data/chatbot-tree.json';
	import servicesData from '$lib/data/services.json';
	import ServiceCard from '$lib/components/ServiceCard.svelte';
	import { normalizeServices } from '$lib/utils/services';
	import { getNode, resolveText, resolveLabel, isLeaf, findServicesForTag, type ChatbotTree, type Lang } from '$lib/utils/chatbot';

	const chatbotTree = tree as unknown as ChatbotTree;
	const allServices = normalizeServices(servicesData.services as unknown as Record<string, unknown>[]);
	let open = $state(false);
	let lang: Lang = $state('en');
	let nodeKey = $state('start');
	let log = $state<{ who: 'bot' | 'user'; text: string }[]>([]);

	const node = $derived(getNode(chatbotTree, nodeKey));
	const inlineServices = $derived(
		node?.action?.type === 'filter' && node.action.tag ? findServicesForTag(allServices, node.action.tag, 3) : []
	);

	function detectLang() {
		if (typeof window !== 'undefined') {
			const saved = localStorage.getItem('dcs-language');
			lang = saved === 'ga' ? 'ga' : 'en';
		}
	}

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

	function openModal() {
		detectLang();
		open = true;
		if (log.length === 0) startOver();
	}

	function actionHref(action: NonNullable<typeof node>['action']): string {
		if (!action) return `${base}/search`;
		if (action.type === 'tel') return `tel:${action.number}`;
		return `${base}/search?q=${encodeURIComponent(action.tag ?? '')}`;
	}
</script>

<button class="chatbot-fab" aria-haspopup="dialog" aria-expanded={open} aria-controls="chatbot-modal" onclick={openModal}>
	<span aria-hidden="true">💬</span> {lang === 'ga' ? 'Cabhair? Comhrá' : 'Need help? Chat'}
</button>

{#if open}
	<div class="modal-overlay active" id="chatbot-modal" role="dialog" aria-modal="true" aria-labelledby="chatbot-title">
		<div class="modal-box">
			<h3 id="chatbot-title">{lang === 'ga' ? 'Faigh an tseirbhís cheart' : 'Find the right service'}</h3>
			<p class="crisis">🚨 {lang === 'ga' ? 'Éigeandáil? Glaoigh 112.' : 'Emergency? Call 112.'} <a href="tel:112">112</a></p>
			<div class="chatbot-log" aria-live="polite">
				{#each log as entry (entry.text + entry.who)}
					<div class="bubble {entry.who}">{entry.text}</div>
				{/each}
			</div>
			{#if node}
				<div class="options">
					{#each node.options ?? [] as opt (opt.next)}
						<button class="option-btn" onclick={() => choose(resolveLabel(opt.label, lang), opt.next)}>
							{resolveLabel(opt.label, lang)}
						</button>
					{/each}
					{#if isLeaf(node)}
						{#if node.action?.type === 'tel'}
							<a class="option-btn" href={actionHref(node.action)}>{resolveLabel(node.action.label, lang)}</a>
						{/if}
						{#if inlineServices.length > 0}
							<div class="inline-cards">
								{#each inlineServices as service (service.id)}
									<ServiceCard {service} />
								{/each}
							</div>
							{#if node.action?.type === 'filter'}
								<a class="see-all" href={actionHref(node.action)}>{lang === 'ga' ? 'Féach gach ceann →' : 'See all →'}</a>
							{/if}
						{:else if node.action?.type === 'filter'}
							<p class="no-match">{lang === 'ga' ? 'Níor aimsíodh meaitseáil — bain triail as cuardach.' : 'No exact match — try search.'}</p>
							<a class="option-btn" href={actionHref(node.action)}>{lang === 'ga' ? 'Cuardaigh →' : 'Search →'}</a>
						{/if}
						{#if node.secondaryAction}
							<a class="option-btn" href={actionHref(node.secondaryAction)}>{resolveLabel(node.secondaryAction.label, lang)}</a>
						{/if}
					{/if}
				</div>
			{/if}
			<button class="restart" onclick={startOver}>↺ {lang === 'ga' ? 'Tosaigh arís' : 'Start over'}</button>
			<button class="close" onclick={() => (open = false)} aria-label="Close chat">✕</button>
		</div>
	</div>
{/if}

<style>
	.chatbot-fab { position: fixed; right: 14px; bottom: 14px; z-index: 2200; background: var(--color-accent); color: var(--color-text-on-accent); border: 0; border-radius: 999px; padding: 12px 16px; font-weight: 700; cursor: pointer; min-height: 44px; }
	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: none; z-index: 2201; align-items: center; justify-content: center; padding: 16px; }
	.modal-overlay.active { display: flex; }
	.modal-box { background: var(--color-surface); border-radius: var(--radius-lg); padding: var(--space-3); max-width: 420px; width: 100%; max-height: 90vh; overflow-y: auto; position: relative; }
	.crisis { font-size: var(--text-sm); font-weight: 700; }
	.chatbot-log { max-height: 280px; overflow-y: auto; margin: 10px 0; display: flex; flex-direction: column; gap: 8px; }
	.bubble { border-radius: 12px; padding: 9px 12px; font-size: var(--text-sm); max-width: 88%; }
	.bubble.bot { background: var(--color-accent-container); align-self: flex-start; }
	.bubble.user { background: var(--color-accent); color: var(--color-text-on-accent); align-self: flex-end; }
	.options { display: flex; flex-direction: column; gap: 6px; }
	.option-btn { border: 2px solid var(--color-accent); background: transparent; color: var(--color-accent); border-radius: 9px; padding: 9px 12px; text-align: left; font-weight: 700; cursor: pointer; text-decoration: none; font-size: var(--text-sm); min-height: 44px; }
	.inline-cards { display: flex; flex-direction: column; gap: 8px; margin: 8px 0; }
	.see-all { font-size: var(--text-sm); font-weight: 700; text-align: center; display: block; padding: 8px; }
	.no-match { font-size: var(--text-sm); color: var(--color-text-muted); }
	.restart, .close { margin-top: 10px; min-height: 44px; }
</style>
