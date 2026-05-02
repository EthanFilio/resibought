<script lang="ts">
	import '$lib/styles/layout.css';
	import ContentCard from '../Common/ContentCard.svelte';

	interface Props {
		/** Store name on the receipt */
		extractedText: string;
	}

	const { extractedText }: Props = $props();
</script>

<ContentCard title="Extracted Text">
	<pre
		class="max-h-96 overflow-auto rounded-lg border border-gray-200 bg-gray-50 p-4 font-mono text-sm whitespace-pre-wrap text-gray-700">{extractedText}</pre>
</ContentCard>
