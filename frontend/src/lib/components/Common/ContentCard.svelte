<script lang="ts">
	import '$lib/styles/layout.css';
	import type { Snippet } from 'svelte';

	interface Props {
		/** Title of the card */
		title: string;
		/** Content of the card */
		children: Snippet;
	}

	const { title, children }: Props = $props();
</script>

<div class="flex-col rounded-xl bg-white p-6 shadow-sm">
	<h2 class="mb-4 font-semibold text-gray-900">{title}</h2>
	{@render children()}
</div>
