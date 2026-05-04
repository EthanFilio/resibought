<script lang="ts">
	import '$lib/styles/layout.css';
	import { mockReceipts } from '$lib/mockData';
	import { SectionHeader } from '$lib/components/Common';
	import { ReceiptImage, ReceiptText } from '$lib/components/Receipt';
	import type { Receipt } from '$lib/types/common';
	import UploadBin from '$lib/components/Upload/UploadBin.svelte';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';

	let files: FileList | null = $state(null);
	let uploadedImage: string | null = $state(null);
	let receipt: Receipt | null = $state(null);

	const processImage = (file: File) => {
		const reader = new FileReader();
		reader.onload = (e) => {
			const imageUrl = e.target?.result as string;
			uploadedImage = imageUrl;
			// TODO: call ML
			receipt = { ...mockReceipts[0], imageUrl };
		};
		reader.readAsDataURL(file);
	};

	const handleSaveReceipt = () => {
		// TODO: save to db
		goto(resolve(`/receipt/${receipt?.id}`));
	};

	const handleTryAgain = () => {
		files = null;
		uploadedImage = null;
		receipt = null;
	};

	const binArgs = {
		formats: ['jpg', 'png', 'heic'],
		maxSize: 10,
		title: 'Upload Receipt Image',
		processImage: processImage
	};
</script>

<div class="mx-auto max-w-4xl space-y-6 pb-20 md:pb-6">
	<SectionHeader
		title="Upload Receipt"
		subtitle="Scan or upload a receipt image for automatic processing"
	/>
	{#if !uploadedImage}
		<UploadBin {...binArgs} bind:files />
	{:else}
		<div class="space-y-6">
			<!--TODO Loading Component-->
			{#if receipt}
				<div class="grid gap-6 md:grid-cols-2">
					<ReceiptImage {...receipt} />
					<ReceiptText {...receipt} />
				</div>
				<div class="flex flex-col gap-3 sm:flex-row">
					<button
						onclick={handleSaveReceipt}
						class="flex-1 rounded-lg bg-forest-green-600 px-6 py-3 font-medium text-white transition-colors hover:bg-forest-green-700"
					>
						Save Receipt
					</button>
					<button
						onclick={handleTryAgain}
						class="flex-1 rounded-lg bg-gray-100 px-6 py-3 font-medium text-gray-700 transition-colors hover:bg-gray-200"
					>
						Try again
					</button>
				</div>
			{/if}
		</div>
	{/if}
</div>
