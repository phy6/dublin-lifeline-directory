<script lang="ts">
	import { onMount } from 'svelte';
	import { t } from '$lib/stores/lang.svelte';

	interface InstallEvent extends Event {
		prompt: () => Promise<void>;
		userChoice: Promise<{ outcome: string }>;
	}

	let deferred = $state<InstallEvent | null>(null);
	let dismissed = $state(false);

	onMount(() => {
		if (sessionStorage.getItem('dcs-install-dismissed') === '1') dismissed = true;
		const onPrompt = (e: Event) => {
			e.preventDefault();
			deferred = e as InstallEvent;
		};
		const onInstalled = () => {
			deferred = null;
		};
		window.addEventListener('beforeinstallprompt', onPrompt);
		window.addEventListener('appinstalled', onInstalled);
		return () => {
			window.removeEventListener('beforeinstallprompt', onPrompt);
			window.removeEventListener('appinstalled', onInstalled);
		};
	});

	function dismiss() {
		dismissed = true;
		sessionStorage.setItem('dcs-install-dismissed', '1');
	}

	async function install() {
		if (!deferred) return;
		deferred.prompt();
		await deferred.userChoice;
		deferred = null;
	}
</script>

{#if deferred && !dismissed}
	<div class="install-banner" role="region" aria-label={t('install-app')}>
		<p>{t('install-app-blurb')}</p>
		<div class="actions">
			<button class="primary" onclick={install}>{t('install-app')}</button>
			<button class="ghost" onclick={dismiss}>{t('not-now')}</button>
		</div>
	</div>
{/if}

<style>
	.install-banner {
		position: fixed;
		left: var(--space-2);
		right: var(--space-2);
		bottom: calc(var(--space-2) + env(safe-area-inset-bottom));
		z-index: 2100;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lg);
		padding: var(--space-3);
	}
	.install-banner p {
		margin: 0 0 var(--space-2);
		font-size: var(--text-sm);
		color: var(--color-text-primary);
	}
	.actions {
		display: flex;
		gap: var(--space-2);
	}
	.actions button {
		min-height: 48px;
		padding: var(--space-2) var(--space-3);
		border-radius: var(--radius-full);
		font-size: var(--text-sm);
		font-weight: 700;
		cursor: pointer;
		font-family: var(--font-sans);
	}
	.actions .primary {
		border: 0;
		background: var(--color-accent);
		color: var(--color-text-on-accent);
		flex: 1;
	}
	.actions .ghost {
		border: 1px solid var(--color-border-strong);
		background: transparent;
		color: var(--color-text-primary);
	}
	.actions button:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
	}
	@media (max-width: 600px) {
		.install-banner {
			bottom: calc(140px + env(safe-area-inset-bottom));
		}
	}
</style>
