<script lang="ts">
	import '$lib/styles/layout.css';
	import { List } from '@lucide/svelte';
	import ReceiptLink from './ReceiptLink.svelte';
	import type { SvelteDate } from 'svelte/reactivity';

	interface Receipt {
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

	interface Props {
		receipts: Receipt[];
	}
	let { receipts }: Props = $props();
</script>

<div class="rounded-xl bg-white shadow-sm">
	<div class="border-b border-gray-200 p-6">
		<div class="flex items-center justify-between">
			<h2 class="text-xl font-bold text-gray-900">Recent Receipts</h2>
			<span class="text-sm text-gray-500">{receipts.length} receipts</span>
		</div>
	</div>

	<div class="divide-y divide-gray-200">
		{#if receipts.length === 0}
			<div class="p-8 text-center text-gray-500">
				<List class="mx-auto mb-3 h-12 w-12 text-gray-400" />
				<p>No receipts found</p>
			</div>
		{:else}
			{#each receipts as receipt (receipt.id)}
				<ReceiptLink {...receipt} />
			{/each}
		{/if}
	</div>
</div>
