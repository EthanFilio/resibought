<script lang="ts">
	import '$lib/styles/layout.css';
	import { browser } from '$app/environment';
	import { ArrowLeft } from '@lucide/svelte';

	const goBack = () => {
		if (browser) window.history.back();
	};
</script>

<button onclick={goBack} class="rounded-lg p-2 transition-colors hover:bg-gray-100">
	<ArrowLeft class="h-5 w-5" />
</button>
