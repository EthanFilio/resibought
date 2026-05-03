<script module lang="ts">
	import { mockReceipts } from '$lib/mockData';
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import ReceiptList from './ReceiptList.svelte';
	import PageDecorator from '../PageDecorator.svelte';

	const { Story } = defineMeta({
		title: 'Dashboard/ReceiptList',
		component: ReceiptList,
		tags: ['autodocs'],
		parameters: {
			layout: 'fullscreen'
		},
		// @ts-expect-error see https://github.com/storybookjs/storybook/issues/29951
		decorators: [() => PageDecorator]
	});
</script>

<Story
	name="Full"
	args={{
		receipts: mockReceipts
	}}
/>

<Story name="Empty" args={{ receipts: [] }} />
