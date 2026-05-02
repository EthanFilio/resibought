<script lang="ts">
	import '$lib/styles/layout.css';
	import { Calendar, List, Shield } from '@lucide/svelte';
	import { resolve } from '$app/paths';
	import type { Pathname } from '$app/types';
	import type { Receipt } from '$lib/types/common';

	interface Props {
		/** Receipt associated with the link */
		receipt: Receipt;
	}
	const { receipt }: Props = $props();
</script>

<a
	href={resolve(`/receipt/${receipt.id}` as Pathname)}
	class="flex items-center gap-4 p-4 transition-colors hover:bg-gray-100"
>
	<img src={receipt.imageUrl} alt={receipt.storeName} class="h-16 w-16 rounded-lg object-cover" />
	<div class="min-w-0 grow">
		<h3 class="font-semibold text-gray-900">{receipt.storeName}</h3>
		<div class="mt-1 flex items-center gap-3 text-sm text-gray-500">
			<div class="flex items-center gap-1">
				<Calendar class="h-4 w-4" />
				{receipt.date.toLocaleDateString()}
			</div>
			<div class="flex items-center gap-1">
				<List class="h-4 w-4" />
				{receipt.items.length} items
			</div>
		</div>
	</div>
	<div class="items-right">
		<p class="font-bold text-gray-900">₱{receipt.total.toFixed(2)}</p>
		{#if receipt.items.some((item) => item.warranty)}
			<div class="mt-1 flex items-center gap-1 text-xs text-forest-green-600">
				<Shield class="h-3 w-3" />
				Warranty
			</div>
		{/if}
	</div>
</a>
