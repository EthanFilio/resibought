<script lang="ts">
	import '$lib/styles/layout.css';
	import { Calendar, List, Shield } from '@lucide/svelte';
	import type { SvelteDate } from 'svelte/reactivity';
	import { resolve } from '$app/paths';
	import type { Pathname } from '$app/types';

	interface Props {
		/** Interal id of the receipt */
		id: number;
		/** Image of the receipt */
		imageUrl: string;
		/** Name of the store that issued the receipt */
		storeName: string;
		/** Date the receipt was issued */
		date: SvelteDate;
		/** Total cost */
		total: number;
		/** Number of items in the reciept */
		itemCount: number;
		/** If the it has warranty */
		warranty: boolean;
	}
	let { id, imageUrl, storeName, date, total, itemCount, warranty }: Props = $props();
</script>

<a
	href={resolve(`/receipt/${id}` as Pathname)}
	class="flex items-center gap-4 p-4 transition-colors hover:bg-gray-100"
>
	<img src={imageUrl} alt={storeName} class="h-16 w-16 rounded-lg object-cover" />
	<div class="min-w-0 grow">
		<h3 class="font-semibold text-gray-900">{storeName}</h3>
		<div class="mt-1 flex items-center gap-3 text-sm text-gray-500">
			<div class="flex items-center gap-1">
				<Calendar class="h-4 w-4" />
				{date.toLocaleDateString()}
			</div>
			<div class="flex items-center gap-1">
				<List class="h-4 w-4" />
				{itemCount} items
			</div>
		</div>
	</div>
	<div class="items-right">
		<p class="font-bold text-gray-900">${total.toFixed(2)}</p>
		{#if warranty}
			<div class="mt-1 flex items-center gap-1 text-xs text-forest-green-600">
				<Shield class="h-3 w-3" />
				Warranty
			</div>
		{/if}
	</div>
</a>
