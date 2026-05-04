<script lang="ts">
	import '$lib/styles/layout.css';
	import { getWarrantyItems, getDaysUntilExpiry, type ReceiptItem } from '$lib/types/common';
	import { mockReceipts } from '$lib/mockData';
	import { SectionHeader, Searchbar, SummaryCard } from '$lib/components/Common';
	import WarrantyList from '$lib/components/Warranties/WarrantyList.svelte';
	import { Shield, CircleAlert, Clock } from '@lucide/svelte';

	let searchValue = $state('');

	const warrantyItems = getWarrantyItems(mockReceipts);

	const soon = warrantyItems.filter((item) => {
		const days = getDaysUntilExpiry(item.warranty!.expiresAt);
		return days <= 7 && days > 0;
	});

	const active = warrantyItems.filter((item) => {
		const days = getDaysUntilExpiry(item.warranty!.expiresAt);
		return days > 7;
	});

	const expired = warrantyItems.filter((item) => {
		const days = getDaysUntilExpiry(item.warranty!.expiresAt);
		return days <= 0;
	});

	const warrantyFilter = (
		items: (ReceiptItem & {
			receiptId: string;
			storeName: string;
			purchaseDate: Date;
		})[]
	) => {
		return items.filter(
			(item) =>
				searchValue === '' ||
				item.storeName.toLowerCase().includes(searchValue.toLowerCase()) ||
				item.name.toLocaleLowerCase().includes(searchValue.toLocaleLowerCase())
		);
	};

	let filteredSoon = $derived(warrantyFilter(soon));
	let filteredActive = $derived(warrantyFilter(active));
	let filteredExpired = $derived(warrantyFilter(expired));

	const summaries = [
		{
			title: 'Total Warranties',
			value: `${active.length + soon.length}`,
			subtitle: 'Active Items',
			Icon: Shield,
			iconColor: 'forest-green'
		},
		{
			title: 'Expiring Soon',
			value: `${soon.length}`,
			subtitle: 'Within 7 days',
			Icon: CircleAlert,
			iconColor: 'yellow'
		},
		{
			title: 'Recently Expired',
			value: expired.length > 0 ? expired[0].name : 'None',
			subtitle:
				expired.length > 0
					? `${-1 * getDaysUntilExpiry(expired[0].warranty!.expiresAt)} days ago`
					: 'No expired warranties',
			Icon: Clock,
			iconColor: 'red'
		}
	];
</script>

<div class="space-y-6 pb-20 md:pb-6">
	<SectionHeader
		title="Warranty Management"
		subtitle="Track your warranties and expiration dates"
	/>
	<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
		{#each summaries as summary (summary.title)}
			<SummaryCard {...summary} />
		{/each}
	</div>
	<Searchbar placeholder="Search stores or items..." bind:value={searchValue} />
	{#if soon.length > 0}
		<WarrantyList status="expiring-soon" warranties={filteredSoon} />
	{/if}
	{#if active.length > 0}
		<WarrantyList status="active" warranties={filteredActive} />
	{/if}
	{#if expired.length > 0}
		<WarrantyList status="expired" warranties={filteredExpired} />
	{/if}
</div>
