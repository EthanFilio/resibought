<script module>
	import { mockReceipts } from '$lib/mockData';
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import ReceiptSummary from './ReceiptSummary.svelte';

	const { Story } = defineMeta({
		title: 'Receipt/ReceiptSummary',
		component: ReceiptSummary,
		tags: ['autodocs'],
		parameters: {
			layout: 'fullscreen'
		}
	});
</script>

<Story name="Summary" args={{ ...mockReceipts[0], itemAmount: mockReceipts[0].items.length }} />
