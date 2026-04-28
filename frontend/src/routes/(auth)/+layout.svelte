<script lang="ts">
	import '$lib/styles/layout.css';
	import favicon from '$lib/assets/favicon.svg';
	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<main
	class="to-forest-green-100-100 flex min-h-screen items-center justify-center bg-linear-to-br from-green-50 p-4"
>
	{@render children()}
</main>
