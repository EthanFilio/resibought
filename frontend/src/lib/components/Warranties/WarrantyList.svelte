<script lang="ts">
	import '$lib/styles/layout.css';
	import { resolve } from '$app/paths';
	import { getDaysUntilExpiry, type ReceiptItem } from '$lib/types/common';
	import {
		CircleCheck,
		Clock,
		Store,
		PhilippinePeso,
		Calendar,
		Shield,
		CircleAlert
	} from '@lucide/svelte';

	interface Props {
		/** List of warranties */
		warranties: Array<ReceiptItem & { receiptId: string; storeName: string; purchaseDate: Date }>;
		/** If the list is for expiring soon, active or expired warranties*/
		status: 'expiring-soon' | 'active' | 'expired';
	}

	let { warranties, status }: Props = $props();
</script>

<div class="rounded-xl bg-white shadow-sm">
	<div class="border-b border-gray-200 p-6">
		<h2 class="flex items-center gap-2 text-xl font-bold text-gray-900">
			{#if status === 'expiring-soon'}
				<CircleAlert class="h-5 w-5 text-yellow-600" />
				Expiring Soon
			{:else if status === 'active'}
				<CircleCheck class="h-5 w-5 text-forest-green-600" />
				Active Warranties
			{:else}
				<Clock class="h-5 w-5 text-red-600" />
				Expired Warranties
			{/if}
		</h2>
	</div>
	<div class="divide-y divide-gray-200">
		{#each warranties as item (item.id)}
			<a
				href={resolve(`/receipt/${item.receiptId}`)}
				class="block p-4 transition-colors hover:bg-gray-50"
			>
				<div class="flex items-start justify-between gap-4">
					<div class="flex-1">
						<h3 class="font-semibold text-gray-900">{item.name}</h3>
						<div class="mt-2 grid grid-cols-1 gap-2 text-sm text-gray-600 sm:grid-cols-2">
							<div class="flex items-center gap-1">
								<Store class="h-4 w-4" />
								{item.storeName}
							</div>
							<div class="flex items-center gap-1">
								<PhilippinePeso class="h-4 w-4" />
								${item.price.toFixed(2)}
							</div>
							<div class="flex items-center gap-1">
								<Calendar class="h-4 w-4" />
								Purchased: {item.purchaseDate.toLocaleDateString()}
							</div>
							<div class="flex items-center gap-1">
								<Shield class="h-4 w-4" />
								{item.warranty!.duration}
							</div>
						</div>
					</div>
					<div class="sm:flex-1"></div>
					<div class="text-center">
						{#if getDaysUntilExpiry(item.warranty!.expiresAt) <= 0}
							<span
								class="inline-block rounded-full bg-red-100 px-3 py-1 text-sm font-medium text-red-800"
							>
								Expired
							</span>
						{:else if getDaysUntilExpiry(item.warranty!.expiresAt) <= 7}
							<span
								class="inline-block rounded-full bg-orange-100 px-3 py-1 text-sm font-medium text-orange-800"
							>
								{getDaysUntilExpiry(item.warranty!.expiresAt)} days left
							</span>
						{:else if getDaysUntilExpiry(item.warranty!.expiresAt) <= 30}
							<span
								class="inline-block rounded-full bg-yellow-100 px-3 py-1 text-sm font-medium text-yellow-800"
							>
								{getDaysUntilExpiry(item.warranty!.expiresAt)} days left
							</span>
						{:else}
							<span
								class="inline-block rounded-full bg-forest-green-100 px-3 py-1 text-sm font-medium text-forest-green-800"
							>
								{getDaysUntilExpiry(item.warranty!.expiresAt)} days left
							</span>
						{/if}
						<p class="font-sm mt-3 text-gray-900">
							{item.warranty!.expiresAt.toLocaleDateString()}
						</p>
					</div>
				</div>
			</a>
		{/each}
	</div>
</div>
