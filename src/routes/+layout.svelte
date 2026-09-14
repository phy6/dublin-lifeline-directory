<script lang="ts">
	let { children } = $props();
</script>

<nav class="top-nav">
	<a href="/">Home</a>
	<a href="/map">Map</a>
	<a href="/search">Search</a>
</nav>

{@render children()}

<style>
	.top-nav {
		display: flex;
		gap: 1rem;
		padding: 1rem;
		background: #1a73e8;
		border-radius: 0 0 12px 12px;
	}
	.top-nav a {
		color: #fff;
		text-decoration: none;
		font-weight: bold;
	}
	.top-nav a:hover {
		text-decoration: underline;
	}
</style>
