<script lang="ts">
	import '$lib/styles/layout.css';
	import ContentCard from '../Common/ContentCard.svelte';

	interface Props {
		/** Image of the receipt */
		imageUrl: string;
		/** Store name on the receipt */
		storeName: string;
	}

	const { imageUrl, storeName }: Props = $props();
</script>

<ContentCard title="Receipt Image">
	<img src={imageUrl} alt={storeName} class="w-full rounded-lg border border-gray-200" />
</ContentCard>
