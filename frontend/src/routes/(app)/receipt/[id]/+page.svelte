<script lang="ts">
	import '$lib/styles/layout.css';
	import { mockReceipts } from '$lib/mockData';
	import { BackButton, SectionHeader } from '$lib/components/Common';
	import { ReceiptSummary, ReceiptImage, ReceiptText, ItemList } from '$lib/components/Receipt';
	import { page } from '$app/state';

	const receipt = mockReceipts.find((r) => r.id === page.params.id);
	console.log(page.params.id);
	console.log(receipt);
</script>

<div class="mx-auto max-w-4xl space-y-6 pb-20 md:pb-6">
	<div class="flex items-center gap-4">
		<BackButton />
		{#if !receipt}
			<SectionHeader title="Receipt not found" />
		{:else}
			<SectionHeader title={receipt!.storeName} subtitle="Receipt Details" />
		{/if}
	</div>
	{#if receipt}
		<ReceiptSummary {...receipt!} itemAmount={receipt!.items.length} />
		<div class="grid gap-6 md:grid-cols-2">
			<ReceiptImage {...receipt!} />
			<ReceiptText {...receipt!} />
		</div>
		<ItemList items={receipt!.items} />
	{/if}
</div>
