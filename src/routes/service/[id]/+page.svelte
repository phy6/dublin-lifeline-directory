<script lang="ts">
	import { base } from '$app/paths';
	import { t } from '$lib/stores/lang.svelte';

	const { data } = $props();
	let service = $state(data.service ?? null);
</script>

{#if service}
	<main id="main-content">
		<a href="{base}/" class="back-link">← {t('back')}</a>
		<div class="service-detail">
			<div class="category">{service.category}</div>
			<h1>{service.name}</h1>
			<p class="description">{service.description}</p>

			<section>
				<h2>{t('location')}</h2>
				{#if service.address}<p>{service.address}</p>{/if}
				{#if service.phone}
					<p>
						<a href="tel:{service.phone}" aria-label="Call {service.name} at {service.phone}"
							>{service.phone}</a
						>
					</p>
				{/if}
				{#if service.email}
					<p>
						<a href="mailto:{service.email}" aria-label="Email {service.name}">{service.email}</a>
					</p>
				{/if}
				{#if service.website && service.website !== ''}
					<p>
						<a
							href={service.website}
							target="_blank"
							rel="noopener"
							aria-label="Visit {service.name} website">{service.website}</a
						>
					</p>
				{/if}
			</section>

			<section>
				<h2>{t('opening-hours')}</h2>
				{#if typeof service.hours === 'string'}
					<p>{service.hours}</p>
				{:else if service.hours && typeof service.hours === 'object'}
					<dl class="hours-list">
						{#each Object.entries(service.hours) as [day, hours] (day)}
							<div class="hours-row">
								<dt class="day">{day}</dt>
								<dd class="hours">{hours}</dd>
							</div>
						{/each}
					</dl>
				{:else}
					<p>{t('no-hours')}</p>
				{/if}
			</section>

			<section>
				<h2>{t('services-offered')}</h2>
				<div class="tags">
					{#each service.services ?? [] as srv (srv)}
						<span class="tag">{srv}</span>
					{/each}
				</div>
			</section>

			<section>
				<h2>{t('categories')}</h2>
				<div class="tags">
					{#each service.tags ?? [] as tag (tag)}
						<span class="tag">{tag}</span>
					{/each}
				</div>
			</section>

			<footer>
				<small
					>{t('last-verified')}: {service.lastVerified} · {t('source')}: {service.dataSource}</small
				>
			</footer>
		</div>
	</main>
{:else}
	<div class="not-found">
		<h2>{t('not-found')}</h2>
		<p>{t('not-found-body')}</p>
		<nav>
			<a href="{base}/search">{t('search-another')}</a>
			<span aria-hidden="true"> or </span>
			<a href="{base}/">return to directory</a>
		</nav>
	</div>
{/if}

<style>
	main {
		max-width: 700px;
		margin: 0 auto;
		padding: var(--space-4);
	}
	.back-link {
		display: inline-block;
		margin-bottom: var(--space-3);
		color: var(--color-accent);
		text-decoration: none;
		font-weight: 500;
		font-size: var(--text-sm);
	}
	.back-link:hover {
		text-decoration: underline;
	}
	.back-link:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
		border-radius: var(--radius-sm);
	}
	.category {
		background: var(--color-accent-container);
		color: var(--color-accent-on-container);
		padding: var(--space-1) var(--space-2);
		border-radius: var(--radius-sm);
		display: inline-block;
		font-size: var(--text-sm);
		font-weight: 600;
		margin-bottom: var(--space-2);
	}
	h1 {
		color: var(--color-text-primary);
		font-size: var(--text-3xl);
		line-height: var(--leading-tight);
		margin-bottom: var(--space-2);
		text-wrap: balance;
	}
	.description {
		color: var(--color-text-secondary);
		line-height: var(--leading-relaxed);
		font-size: var(--text-base);
		margin-bottom: var(--space-4);
	}
	section {
		margin: var(--space-5) 0;
	}
	h2 {
		color: var(--color-accent);
		font-size: var(--text-xl);
		font-weight: 600;
		border-bottom: 1px solid var(--color-border);
		padding-bottom: var(--space-2);
		margin-bottom: var(--space-3);
	}
	.hours-list {
		margin: 0;
	}
	.hours-row {
		display: flex;
		justify-content: space-between;
		padding: var(--space-1) 0;
		border-bottom: 1px solid var(--color-border);
	}
	.hours-row:last-child {
		border-bottom: none;
	}
	.day {
		font-weight: 600;
		color: var(--color-text-primary);
		font-size: var(--text-sm);
	}
	.hours {
		color: var(--color-text-secondary);
		font-size: var(--text-sm);
		margin: 0;
	}
	.tags {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-1);
	}
	.tag {
		background: var(--color-accent-container);
		color: var(--color-accent-on-container);
		padding: var(--space-1) var(--space-2);
		border-radius: var(--radius-sm);
		font-size: var(--text-xs);
	}
	footer {
		margin-top: var(--space-6);
		padding-top: var(--space-4);
		border-top: 1px solid var(--color-border);
	}
	footer small {
		color: var(--color-text-muted);
		font-size: var(--text-xs);
	}
	.not-found {
		max-width: 700px;
		margin: 0 auto;
		padding: var(--space-6) var(--space-4);
		text-align: center;
	}
	.not-found h2 {
		font-size: var(--text-2xl);
		color: var(--color-text-primary);
		margin-bottom: var(--space-2);
	}
	.not-found p {
		color: var(--color-text-secondary);
		margin-bottom: var(--space-4);
		font-size: var(--text-base);
		line-height: var(--leading-relaxed);
	}
	.not-found nav {
		display: flex;
		justify-content: center;
		gap: var(--space-2);
		flex-wrap: wrap;
	}
	.not-found a {
		color: var(--color-accent);
		font-weight: 600;
		text-decoration: none;
	}
	.not-found a:hover {
		text-decoration: underline;
	}
	a {
		color: var(--color-accent);
		text-decoration: none;
	}
	a:hover {
		text-decoration: underline;
	}
	a:focus-visible {
		outline: 3px solid var(--color-focus-ring);
		outline-offset: 2px;
		border-radius: var(--radius-sm);
	}
	@media (max-width: 600px) {
		main {
			padding: var(--space-3);
		}
		h1 {
			font-size: var(--text-2xl);
		}
		h2 {
			font-size: var(--text-lg);
		}
		.day,
		.hours {
			font-size: var(--text-xs);
		}
	}
</style>
