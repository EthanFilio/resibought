<script module>
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Searchbar from './Searchbar.svelte';
	import { fn } from 'storybook/test';

	const { Story } = defineMeta({
		title: 'Common/Searchbar',
		component: Searchbar,
		tags: ['autodocs'],
		args: {
			onChange: fn(),
			placeholder: 'Search receipts, stores, or items...'
		}
	});
</script>

<Story name="Primary" />
