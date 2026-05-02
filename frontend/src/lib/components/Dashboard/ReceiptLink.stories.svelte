<script module>
	import { mockReceipts } from '$lib/mockData';
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import ReceiptLink from './ReceiptLink.svelte';

	const { Story } = defineMeta({
		title: 'Dashboard/ReceiptLink',
		component: ReceiptLink,
		tags: ['autodocs'],
		parameters: {
			layout: 'fullscreen'
		}
	});
</script>

<Story name="No Warranty" args={{ receipt: mockReceipts[1] }} />

<Story name="Warranty" args={{ receipt: mockReceipts[0] }} />
