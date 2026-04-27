<script module>
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import ReceiptList from './ReceiptList.svelte';
	import PageDecorator from '../PageDecorator.svelte';
	import { SvelteDate } from 'svelte/reactivity';

	const { Story } = defineMeta({
		title: 'Dashboard/ReceiptList',
		component: ReceiptList,
		tags: ['autodocs'],
		parameters: {
			// More on how to position stories at: https://storybook.js.org/docs/configure/story-layout
			layout: 'fullscreen'
		},
		// @ts-expect-error see https://github.com/storybookjs/storybook/issues/29951
		decorators: [() => PageDecorator]
	});
</script>

<Story name="Empty" args={{ receipts: [] }} />

<Story
	name="Full"
	args={{
		receipts: [
			{
				id: 1,
				storeName: 'Best Electronics',
				date: new SvelteDate('2026-04-20'),
				total: 1299.99,
				imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
				itemCount: 1,
				warranty: true
			},
			{
				id: 2,
				storeName: 'SuperMart',
				date: new SvelteDate('2026-04-18'),
				total: 87.42,
				imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
				itemCount: 8,
				warranty: false
			},
			{
				id: 3,
				storeName: 'Home Depot',
				date: new SvelteDate('2026-04-15'),
				total: 234.56,
				imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
				itemCount: 6,
				warranty: true
			},
			{
				id: 4,
				storeName: 'Fashion Outlet',
				date: new SvelteDate('2026-04-10'),
				total: 156.97,
				imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
				itemCount: 3,
				warranty: false
			},
			{
				id: 5,
				storeName: 'Tech Store',
				date: new SvelteDate('2026-03-28'),
				total: 449.99,
				imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
				itemCount: 6,
				warranty: true
			}
		]
	}}
/>
