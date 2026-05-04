<script lang="ts">
	import '$lib/styles/layout.css';
	import ItemListItem from './ItemListItem.svelte';
	import type { ReceiptItem } from '$lib/types/common';

	interface Props {
		/** List of receipts */
		items: ReceiptItem[];
	}

	const { items }: Props = $props();
	const computeTotal = () => {
		return items.reduce((sum, item) => sum + item.price, 0);
	};
</script>

<div class="rounded-xl bg-white shadow-sm">
	<div class="border-b border-gray-200 p-6">
		<h2 class="text-xl font-bold text-gray-900">Itemized List</h2>
		<p class="mt-1 text-sm text-gray-600">
			Categories are automatically assigned using NLP. Click to edit.
		</p>
	</div>

	<div class="divide-y divide-gray-200">
		{#each items as item (item.id)}
			<ItemListItem {item} />
		{/each}
	</div>

	<div class="border-t border-gray-200 bg-gray-50 p-4">
		<div class="flex items-center justify-between">
			<span class="font-semibold text-gray-900">Total</span>
			<span class="text-2xl font-bold text-gray-900">₱{computeTotal().toFixed(2)}</span>
		</div>
	</div>
</div>
