<script module>
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import ReceiptLink from './ReceiptLink.svelte';

	const { Story } = defineMeta({
		title: 'Dashboard/ReceiptLink',
		component: ReceiptLink,
		tags: ['autodocs'],
		parameters: {
			layout: 'fullscreen'
		},
		args: {
			id: '3',
			storeName: 'ACE Hardware',
			date: new Date('2026-04-15'),
			total: 2340.56,
			imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
			itemCount: 4
		}
	});
</script>

<Story name="No Warranty" args={{ warranty: false }} />

<Story name="Warranty" args={{ warranty: true }} />
