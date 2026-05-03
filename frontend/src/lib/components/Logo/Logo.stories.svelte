<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Logo from './Logo.svelte';

	// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
	const { Story } = defineMeta({
		title: 'Logo/Logo',
		component: Logo,
		tags: ['autodocs']
	});
</script>

<!-- More on writing stories with args: https://storybook.js.org/docs/writing-stories/args -->

<Story name="Large" args={{ size: 'large' }} />

<Story name="Medium" args={{ size: 'medium' }} />

<Story name="Small" args={{ size: 'small' }} />
