<script module lang="ts">
	import { mockReceipts } from '$lib/mockData';
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import ReceiptImage from './ReceiptImage.svelte';

	const { Story } = defineMeta({
		title: 'Receipt/ReceiptImage',
		component: ReceiptImage,
		tags: ['autodocs'],
		parameters: {
			layout: 'fullscreen'
		}
	});
</script>

<Story name="Image" args={{ ...mockReceipts[0] }} />
