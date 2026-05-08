<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import { mockReceipts } from '$lib/mockData';
	import { getCategorySpending } from '$lib/types/common';
	import BarChart from './BarChart.svelte';

	const { Story } = defineMeta({
		title: 'Analytics/BarChart',
		component: BarChart,
		tags: ['autodocs'],
		args: {
			title: 'Spending by Category',
			data: getCategorySpending(mockReceipts),
			format: (v) => `₱${v}`
		}
	});
</script>

<Story name="BarChart" />
