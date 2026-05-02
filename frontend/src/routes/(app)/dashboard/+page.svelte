<script lang="ts">
	import '$lib/styles/layout.css';
	import { getCategorySpending } from '$lib/types/common';
	import { mockReceipts } from '$lib/mockData';
	import Searchbar from '$lib/components/Dashboard/Searchbar.svelte';
	import SummaryCard from '$lib/components/Dashboard/SummaryCard.svelte';
	import ReceiptList from '$lib/components/Dashboard/ReceiptList.svelte';
	import { PhilippinePeso, Calendar, TrendingUp } from '@lucide/svelte';

	const receipts = mockReceipts;

	const totalSpending = receipts.reduce((sum, receipt) => sum + receipt.total, 0);
	const thisMonthReceipts = receipts.filter(
		(receipt) => receipt.date.getMonth() === new Date().getMonth()
	);
	const thisMonthSpending = thisMonthReceipts.reduce((sum, receipt) => sum + receipt.total, 0);
	const categorySpending = getCategorySpending(receipts);
	const topCategory = categorySpending.reduce((max, cat) => (cat.value > max.value ? cat : max));

	const summaries = [
		{
			title: 'Total Spending',
			value: `₱${totalSpending.toFixed(2)}`,
			subtitle: 'All time',
			Icon: PhilippinePeso,
			iconColor: 'forest-green'
		},
		{
			title: 'This Month',
			value: `₱${thisMonthSpending.toFixed(2)}`,
			subtitle: `${thisMonthReceipts.length} receipts`,
			Icon: Calendar,
			iconColor: 'blue'
		},
		{
			title: 'Top Category',
			value: `${topCategory.name}`,
			subtitle: `₱${topCategory.value.toFixed(2)} spent`,
			Icon: TrendingUp,
			iconColor: 'purple'
		}
	];
</script>

<div class="space-y-6 pb-20 md:pb-6">
	<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
		{#each summaries as summary (summary.title)}
			<SummaryCard {...summary} />
		{/each}
	</div>
	<Searchbar placeholder="Search receipts, stores, or items..." />
	<ReceiptList {receipts} />
</div>
