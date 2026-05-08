<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import { mockReceipts } from '$lib/mockData';
	import { getMonthlySpending } from '$lib/types/common';
	import LineChart from './LineChart.svelte';

	const { Story } = defineMeta({
		title: 'Analytics/LineChart',
		component: LineChart,
		tags: ['autodocs'],
		args: {
			title: 'Spending by Category',
			data: getMonthlySpending(mockReceipts),
			format: (v) => `₱${v}`
		}
	});
</script>

<Story name="LineChart" />
