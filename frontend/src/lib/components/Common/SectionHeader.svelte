<script lang="ts">
	import '$lib/styles/layout.css';

	interface Props {
		/** Title of the section */
		title: string;
		/** Subtitle of the section */
		subtitle?: string;
	}

	const { title, subtitle }: Props = $props();
</script>

<div>
	<h1 class="text-3xl font-bold text-gray-900">{title}</h1>
	{#if subtitle}
		<p class="mt-2 text-gray-600">{subtitle}</p>
	{/if}
</div>
