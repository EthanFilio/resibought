<script lang="ts">
	import '$lib/styles/layout.css';
	import SectionHeader from '$lib/components/Common/SectionHeader.svelte';
	import SummaryCard from '$lib/components/Common/SummaryCard.svelte';
	import { Shield, CircleAlert, Clock } from '@lucide/svelte';

	const summaries = [
		{
			title: 'Total Warranties',
			value: '10',
			subtitle: 'Active Items',
			Icon: Shield,
			iconColor: 'forest-green'
		},
		{
			title: 'Expiring Soon',
			value: '3',
			subtitle: 'Within 7 days',
			Icon: CircleAlert,
			iconColor: 'yellow'
		},
		{
			title: 'Recently Expired',
			value: 'Acer Laptop',
			subtitle: '5 days ago',
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
</div>
