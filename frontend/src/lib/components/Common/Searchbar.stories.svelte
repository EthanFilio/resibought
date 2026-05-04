<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Searchbar from './Searchbar.svelte';

	const { Story } = defineMeta({
		title: 'Common/Searchbar',
		component: Searchbar,
		tags: ['autodocs'],
		args: {
			placeholder: 'Search receipts, stores, or items...',
			value: ''
		}
	});
</script>

<Story name="Searchbar" />
