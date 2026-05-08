<script lang="ts">
	import '$lib/styles/layout.css';
	import { getCategorySpending, getMonthlySpending } from '$lib/types/common';
	import { mockReceipts } from '$lib/mockData';
	import { SummaryCard, SectionHeader } from '$lib/components/Common';
	import { PhilippinePeso, ShoppingBag, Store, TrendingUp } from '@lucide/svelte';
	import { BarChart, PieChart, LineChart, Ranking } from '$lib/components/Analytics';
	const receipts = mockReceipts;

	const totalSpending = receipts.reduce((sum, receipt) => sum + receipt.total, 0);
	const averageReceiptValue = totalSpending / receipts.length;
	const totalItems = receipts.reduce((sum, receipt) => sum + receipt.items.length, 0);
	const uniqueStores = new Set(receipts.map((r) => r.storeName)).size;
	const topMerchants = Object.entries(
		receipts.reduce(
			(acc, receipt) => {
				acc[receipt.storeName] = (acc[receipt.storeName] || 0) + receipt.total;
				return acc;
			},
			{} as Record<string, number>
		)
	)
		.map(([name, value]) => ({ name, value }))
		.sort((a, b) => b.value - a.value)
		.slice(0, 5);

	const summaries = [
		{
			title: 'Total Spending',
			value: `₱${totalSpending.toFixed(2)}`,
			subtitle: 'All time',
			Icon: PhilippinePeso,
			iconColor: 'forest-green'
		},
		{
			title: 'Avg. Cost',
			value: `₱${averageReceiptValue.toFixed(2)}`,
			subtitle: 'per transaction',
			Icon: TrendingUp,
			iconColor: 'blue'
		},
		{
			title: 'Total Items',
			value: `${totalItems}`,
			subtitle: `Purchased`,
			Icon: ShoppingBag,
			iconColor: 'purple'
		},
		{
			title: 'Stores',
			value: `${uniqueStores}`,
			subtitle: `Unique merchants`,
			Icon: Store,
			iconColor: 'orange'
		}
	];

	const format = (v: number) => `₱${v}`;
</script>

<div class="space-y-6 pb-20 md:pb-6">
	<SectionHeader title="Analytics & Insights" subtitle="Track your spending habits and trends" />
	<div class="grid grid-cols-1 gap-4 md:grid-cols-4">
		{#each summaries as summary (summary.title)}
			<SummaryCard {...summary} />
		{/each}
	</div>
	<div class="grid gap-6 md:grid-cols-2">
		<PieChart title="Spending by Category" data={getCategorySpending(receipts)} {format} />
		<BarChart title="Category Breakdown" data={getCategorySpending(receipts)} {format} />
		<LineChart title="Spending by Month" data={getMonthlySpending(receipts)} {format} />
		<Ranking title="Top Merchants" data={topMerchants} {format} />
	</div>
</div>
