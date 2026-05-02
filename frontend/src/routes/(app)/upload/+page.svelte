<script lang="ts">
	import '$lib/styles/layout.css';
	import { SectionHeader } from '$lib/components/Common';
	import UploadBin from '$lib/components/Upload/UploadBin.svelte';

	const binArgs = {
		formats: ['jpg', 'png', 'heic'],
		maxSize: 10,
		title: 'Upload Receipt Image'
	};
</script>

<div class="mx-auto max-w-4xl space-y-6 pb-20 md:pb-6">
	<SectionHeader
		title="Upload Receipt"
		subtitle="Scan or upload a receipt image for automatic processing"
	/>
	<UploadBin {...binArgs} />
</div>
