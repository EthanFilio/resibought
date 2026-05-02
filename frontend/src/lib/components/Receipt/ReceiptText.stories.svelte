<script module>
	import { mockReceipts } from '$lib/mockData';
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import ReceiptText from './ReceiptText.svelte';

	const { Story } = defineMeta({
		title: 'Receipt/ReceiptText',
		component: ReceiptText,
		tags: ['autodocs'],
		parameters: {
			layout: 'fullscreen'
		}
	});
</script>

<Story name="Image" args={{ ...mockReceipts[0] }} />
