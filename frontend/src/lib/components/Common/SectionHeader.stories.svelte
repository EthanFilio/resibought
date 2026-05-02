<script module>
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import SectionHeader from './SectionHeader.svelte';

	const { Story } = defineMeta({
		title: 'Common/SectionHeader',
		component: SectionHeader,
		tags: ['autodocs'],
		args: {
			title: 'Upload Receipt',
			subtitle: 'Scan or upload a receipt image for automatic processing'
		}
	});
</script>

<Story name="Section Header" />
