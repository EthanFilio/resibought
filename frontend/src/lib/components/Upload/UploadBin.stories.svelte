<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import UploadBin from './UploadBin.svelte';
	import { fn } from 'storybook/test';

	const { Story } = defineMeta({
		title: 'Upload/UploadBin',
		component: UploadBin,
		tags: ['autodocs'],
		args: {
			formats: ['jpg', 'png', 'heic'],
			maxSize: 10,
			title: 'Upload Receipt Image',
			files: null,
			processImage: fn()
		}
	});
</script>

<Story name="Upload Bin" />
