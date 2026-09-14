<script lang="ts">
	import { onMount } from 'svelte';
	import type { ServiceLocation } from '$lib/types';

	let { data } = $props();
	let service = $state<ServiceLocation | null>(null);

	onMount(async () => {
		if (data.service) service = data.service as unknown as ServiceLocation;
	});
</script>

{#if service}
	<main>
		<a href="/">← Back</a>
		<div class="service-detail">
			<div class="category">{service.category}</div>
			<h1>{service.name}</h1>
			<p class="description">{service.description}</p>

			<section>
				<h2>Location</h2>
				<p>{service.address}</p>
				<p>Phone: <a href="tel:{service.phone}">{service.phone}</a></p>
				<p>Email: <a href="mailto:{service.email}">{service.email}</a></p>
				{#if service.website && service.website !== ''}
					<p><a href={service.website} target="_blank" rel="noopener">{service.website}</a></p>
				{/if}
			</section>

			<section>
				<h2>Hours</h2>
				{#each Object.entries(service.hours) as [day, hours] (day)}
					<div class="hours-row">
						<span class="day">{day}</span><span class="hours">{hours}</span>
					</div>
				{/each}
			</section>

			<section>
				<h2>Services</h2>
				<div class="tags">
					{#each service.services as srv (srv)}
						<span class="tag">{srv}</span>
					{/each}
				</div>
			</section>

			<section>
				<h2>Tags</h2>
				<div class="tags">
					{#each service.tags as tag (tag)}
						<span class="tag">{tag}</span>
					{/each}
				</div>
			</section>

			<footer>
				<small>Last verified: {service.lastVerified} · Data: {service.dataSource}</small>
			</footer>
		</div>
	</main>
{:else}
	<p>Service not found.</p>
{/if}

<style>
	main {
		max-width: 700px;
		margin: 0 auto;
		padding: 1rem;
	}
	a {
		color: #1a73e8;
		text-decoration: none;
	}
	.category {
		background: #1a73e8;
		color: #fff;
		padding: 4px 12px;
		border-radius: 4px;
		display: inline-block;
		font-size: 0.85rem;
		margin-bottom: 0.5rem;
	}
	h1 {
		color: #222;
	}
	.description {
		color: #444;
		line-height: 1.5;
	}
	section {
		margin: 1.5rem 0;
	}
	h2 {
		color: #1a73e8;
		font-size: 1.1rem;
		border-bottom: 1px solid #eee;
		padding-bottom: 0.5rem;
	}
	.hours-row {
		display: flex;
		justify-content: space-between;
		padding: 4px 0;
		border-bottom: 1px solid #f5f5f5;
	}
	.day {
		font-weight: bold;
	}
	.hours {
		color: #555;
	}
	.tags {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
	}
	.tag {
		background: #e8f0fe;
		color: #1a73e8;
		padding: 2px 8px;
		border-radius: 4px;
		font-size: 0.8rem;
	}
	footer {
		margin-top: 2rem;
		color: #999;
	}
</style>
