<script lang="ts">
	import '$lib/styles/layout.css';
	import { Tag, Pencil, Shield } from '@lucide/svelte';
	import { categories } from '$lib/types/common';
	import type { ReceiptItem } from '$lib/types/common';

	interface Props {
		/** List of receipts */
		item: ReceiptItem;
	}

	const { item }: Props = $props();
	let editingItemId: string | null = $state(null);
	let editingCategory: string = $state('');

	const handleEditCategory = (itemId: string, currentCategory: string) => {
		editingItemId = itemId;
		editingCategory = currentCategory;
	};

	const handleSaveCategory = () => {
		// TODO: update db and ml
		editingItemId = null;
	};
</script>

<div class="p-4 transition-colors hover:bg-gray-100">
	<div class="flex items-start justify-between gap-4">
		<div class="flex-1">
			<h3 class="font-semibold text-gray-900">{item.name}</h3>
			<div class="mt-2 flex items-center gap-4">
				{#if editingItemId}
					<div class="flex items-center gap-2">
						<select
							bind:value={editingCategory}
							class="rounded-lg border border-gray-300 px-3 py-1 text-sm outline-none focus:border-transparent focus:ring-2 focus:ring-forest-green-500"
						>
							{#each categories as category (category)}
								<option value={category}>
									{category}
								</option>
							{/each}
						</select>
						<button
							onclick={handleSaveCategory}
							class="rounded-lg bg-forest-green-600 px-3 py-1 text-white hover:bg-forest-green-700"
						>
							Save
						</button>
					</div>
				{:else}
					<button
						onclick={() => handleEditCategory(item.id, item.category)}
						class="flex items-center gap-1 rounded-full bg-forest-green-50 px-3 py-1 text-sm text-forest-green-700 transition-colors hover:bg-forest-green-100"
					>
						<Tag class="h-3 w-3" />
						{item.category}
						<Pencil class="ml-1 h-3 w-3" />
					</button>
				{/if}
				{#if item.warranty}
					<div
						class="flex items-center gap-1 rounded-full bg-green-50 px-3 py-1 text-sm text-green-700"
					>
						<Shield class="h-3 w-3" />
						{item.warranty.duration} warranty
					</div>
				{/if}
			</div>
			{#if item.warranty}
				<p class="mt-2 text-sm text-gray-600">
					Expires: {item.warranty.expiresAt.toLocaleDateString()}
				</p>
			{/if}
		</div>
		<div class="text-right">
			<p class="font-bold text-gray-900">₱{item.price.toFixed(2)}</p>
		</div>
	</div>
</div>
