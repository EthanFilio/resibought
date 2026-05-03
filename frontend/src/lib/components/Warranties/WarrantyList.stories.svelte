<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import WarrantyList from './WarrantyList.svelte';
	import type { ReceiptItem } from '$lib/types/common';

	// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
	const { Story } = defineMeta({
		title: 'Warranties/WarrantyList',
		component: WarrantyList,
		tags: ['autodocs']
	});

	const expired: Array<ReceiptItem & { receiptId: string; storeName: string; purchaseDate: Date }> =
		[
			{
				id: '1-1',
				name: 'Acer Laptop',
				price: 12990.99,
				category: 'Electronics',
				warranty: {
					duration: '1 day',
					expiresAt: new Date(Date.now() - 86400000)
				},
				receiptId: '1',
				storeName: 'Abenson',
				purchaseDate: new Date(Date.now() - 2 * 86400000)
			}
		];
	const soon: Array<ReceiptItem & { receiptId: string; storeName: string; purchaseDate: Date }> = [
		{
			id: '1-1',
			name: 'Acer Laptop',
			price: 12990.99,
			category: 'Electronics',
			warranty: {
				duration: '1 day',
				expiresAt: new Date(Date.now() + 86400000)
			},
			receiptId: '1',
			storeName: 'Abenson',
			purchaseDate: new Date(Date.now())
		}
	];
	const activeOrange: Array<
		ReceiptItem & { receiptId: string; storeName: string; purchaseDate: Date }
	> = [
		{
			id: '1-1',
			name: 'Acer Laptop',
			price: 12990.99,
			category: 'Electronics',
			warranty: {
				duration: '14 days',
				expiresAt: new Date(Date.now() + 14 * 86400000)
			},
			receiptId: '1',
			storeName: 'Abenson',
			purchaseDate: new Date(Date.now())
		}
	];
	const activeGreen: Array<
		ReceiptItem & { receiptId: string; storeName: string; purchaseDate: Date }
	> = [
		{
			id: '1-1',
			name: 'Acer Laptop',
			price: 12990.99,
			category: 'Electronics',
			warranty: {
				duration: '60 days',
				expiresAt: new Date(Date.now() + 60 * 86400000)
			},
			receiptId: '1',
			storeName: 'Abenson',
			purchaseDate: new Date(Date.now())
		}
	];
</script>

<Story name="Expired" args={{ warranties: expired, status: 'expired' }} />

<Story name="Expiring Soon" args={{ warranties: soon, status: 'expiring-soon' }} />

<Story name="Active Orange" args={{ warranties: activeOrange, status: 'active' }} />

<Story name="Active Green" args={{ warranties: activeGreen, status: 'active' }} />
