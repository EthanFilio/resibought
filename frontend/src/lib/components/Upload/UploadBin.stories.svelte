<script module>
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import UploadBin from './UploadBin.svelte';

	const { Story } = defineMeta({
		title: 'Upload/UploadBin',
		component: UploadBin,
		tags: ['autodocs'],
		args: {
			formats: ['jpg', 'png', 'heic'],
			maxSize: 10,
			title: 'Upload Receipt Image'
		}
	});
</script>

<Story name="Section Header" />
