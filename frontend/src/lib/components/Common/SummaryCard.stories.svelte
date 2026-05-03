<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import SummaryCard from './SummaryCard.svelte';
	import { PhilippinePeso, Calendar } from '@lucide/svelte';

	const { Story } = defineMeta({
		title: 'Common/SummaryCard',
		component: SummaryCard,
		tags: ['autodocs']
	});
</script>

<Story
	name="Total Spending"
	args={{
		title: 'Total Spending',
		value: '₱22280.93',
		subtitle: 'All time',
		Icon: PhilippinePeso,
		iconColor: 'forest-green'
	}}
/>

<Story
	name="This Month"
	args={{
		title: 'This Month',
		value: '₱17780.94',
		subtitle: '4 receipts',
		Icon: Calendar,
		iconColor: 'blue'
	}}
/>
