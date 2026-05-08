<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import { mockReceipts } from '$lib/mockData';
	import { getCategorySpending } from '$lib/types/common';
	import Ranking from './Ranking.svelte';
	import PageDecorator from '../PageDecorator.svelte';

	const { Story } = defineMeta({
		title: 'Analytics/Ranking',
		component: Ranking,
		tags: ['autodocs'],
		args: {
			title: 'Spending by Category',
			data: getCategorySpending(mockReceipts),
			format: (v) => `₱${v}`
		},
		// @ts-expect-error see https://github.com/storybookjs/storybook/issues/29951
		decorators: [() => PageDecorator]
	});
</script>

<Story name="Ranking" />
