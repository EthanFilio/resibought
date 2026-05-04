<script lang="ts">
	import '$lib/styles/layout.css';
	import ContentCard from '../Common/ContentCard.svelte';
	import { ThumbsUp, ThumbsDown } from '@lucide/svelte';

	interface Props {
		/** Store name on the receipt */
		extractedText: string;
		/** Wwas the text rated already*/
		rated?: boolean;
	}

	let rating: 'yes' | 'no' | null = $state(null);

	const { extractedText, rated = false }: Props = $props();

	// TODO: Attatch to ML feed back
	const handleYes = () => {
		rating = 'yes';
	};
	const handleNo = () => {
		rating = 'no';
	};

	let yesMode = $derived(
		rating ? (rating === 'yes' ? 'text-forest-green-700' : '') : 'hover:text-forest-green-700'
	);

	let noMode = $derived(rating ? (rating === 'no' ? 'text-red-700' : '') : 'hover:text-red-700');
</script>

<ContentCard title="Extracted Text">
	<pre
		class="max-h-96 overflow-auto rounded-lg border border-gray-200 bg-gray-50 p-4 font-mono text-sm whitespace-pre-wrap text-gray-700">{extractedText}</pre>
	{#if !rated}
		<div class="mt-3 flex items-center gap-1">
			<div class="text-sm text-gray-900">Is the extracted text accurate?</div>
			<button disabled={rating !== null} onclick={handleYes}
				><ThumbsUp class={['h-5 w-5', yesMode].join(' ')} /></button
			>
			<button disabled={rating !== null} onclick={handleNo}
				><ThumbsDown class={['h-5 w-5', noMode].join(' ')} /></button
			>
		</div>
		{#if rating}
			<div class="mt-1 ml-1 text-xs text-gray-900">Feedback sent to the model</div>
		{/if}
	{/if}
</ContentCard>
