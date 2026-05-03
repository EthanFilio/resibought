<script module lang="ts">
	import { mockReceipts } from '$lib/mockData';
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import ItemList from './ItemList.svelte';

	const { Story } = defineMeta({
		title: 'Receipt/ItemList',
		component: ItemList,
		tags: ['autodocs'],
		parameters: {
			layout: 'fullscreen'
		}
	});
</script>

<Story name="Item List" args={{ items: mockReceipts[2].items }} />
