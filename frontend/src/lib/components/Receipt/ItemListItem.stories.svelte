<script module lang="ts">
	import { mockReceipts } from '$lib/mockData';
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import ItemListItem from './ItemListItem.svelte';

	const { Story } = defineMeta({
		title: 'Receipt/ItemListItem',
		component: ItemListItem,
		tags: ['autodocs'],
		parameters: {
			layout: 'fullscreen'
		}
	});
</script>

<Story name="Warranty" args={{ item: mockReceipts[2].items[0] }} />

<Story name="No Warranty" args={{ item: mockReceipts[2].items[1] }} />
