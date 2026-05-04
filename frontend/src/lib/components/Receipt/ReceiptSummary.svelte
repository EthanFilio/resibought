<script lang="ts">
	import '$lib/styles/layout.css';
	import { PhilippinePeso, Calendar, FileText } from '@lucide/svelte';

	interface Props {
		/** Date of receipt */
		date: Date;
		/** Total cost of the receipt */
		total: number;
		/** Number of items*/
		itemAmount: number;
	}

	const { date, total, itemAmount }: Props = $props();
</script>

<div class="rounded-xl bg-white p-6 shadow-sm">
	<div class="grid gap-4 md:grid-cols-3">
		<div class="flex items-center gap-3">
			<Calendar class="h-5 w-5 text-blue-600" />
			<div>
				<p class="text-sm text-gray-600">Date</p>
				<p class="font-semibold text-gray-900">{date.toLocaleDateString()}</p>
			</div>
		</div>
		<div class="flex items-center gap-3">
			<PhilippinePeso class="h-5 w-5 text-forest-green-600" />
			<div>
				<p class="text-sm text-gray-600">Total</p>
				<p class="font-semibold text-gray-900">₱{total.toFixed(2)}</p>
			</div>
		</div>
		<div class="flex items-center gap-3">
			<FileText class="h-5 w-5 text-purple-600" />
			<div>
				<p class="text-sm text-gray-600">Items</p>
				<p class="font-semibold text-gray-900">{itemAmount}</p>
			</div>
		</div>
	</div>
</div>
