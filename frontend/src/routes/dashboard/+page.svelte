<script lang="ts">
	import '$lib/styles/layout.css';
	import Searchbar from '$lib/components/Dashboard/Searchbar.svelte';
	import SummaryCard from '$lib/components/Dashboard/SummaryCard.svelte';
	import ReceiptList from '$lib/components/Dashboard/ReceiptList.svelte';
	import { DollarSign, Calendar, TrendingUp } from '@lucide/svelte';
	import { SvelteDate } from 'svelte/reactivity';

	const summaries = [
		{
			title: 'Total Spending',
			value: '₱22280.93',
			subtitle: 'All time',
			Icon: DollarSign,
			iconColor: 'forest-green'
		},
		{
			title: 'This Month',
			value: '₱17780.94',
			subtitle: '4 receipts',
			Icon: Calendar,
			iconColor: 'blue'
		},
		{
			title: 'Top Category',
			value: 'Electronics',
			subtitle: '₱17490.98 spent',
			Icon: TrendingUp,
			iconColor: 'purple'
		}
	];

	const receipts = [
		{
			id: 1,
			storeName: 'Abenson',
			date: new SvelteDate('2026-04-20'),
			total: 12990.99,
			imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
			itemCount: 1,
			warranty: true
		},
		{
			id: 2,
			storeName: 'Puregold',
			date: new SvelteDate('2026-04-18'),
			total: 870.42,
			imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
			itemCount: 8,
			warranty: false
		},
		{
			id: 3,
			storeName: 'Ace Hardware',
			date: new SvelteDate('2026-04-15'),
			total: 2340.56,
			imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
			itemCount: 6,
			warranty: true
		},
		{
			id: 4,
			storeName: 'Uniqlo',
			date: new SvelteDate('2026-04-10'),
			total: 1560.97,
			imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
			itemCount: 3,
			warranty: false
		},
		{
			id: 5,
			storeName: 'DataBlitz',
			date: new SvelteDate('2026-03-28'),
			total: 4490.99,
			imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
			itemCount: 6,
			warranty: true
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
