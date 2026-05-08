<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import { mockReceipts } from '$lib/mockData';
	import { getCategorySpending } from '$lib/types/common';
	import PieChart from './PieChart.svelte';

	const { Story } = defineMeta({
		title: 'Analytics/PieChart',
		component: PieChart,
		tags: ['autodocs'],
		args: {
			title: 'Spending by Category',
			data: getCategorySpending(mockReceipts),
			format: (v) => `₱${v}`
		}
	});
</script>

<Story name="PieChart" />
