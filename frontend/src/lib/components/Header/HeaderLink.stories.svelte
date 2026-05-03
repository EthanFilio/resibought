<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import { Search } from '@lucide/svelte';
	import Link from './HeaderLink.svelte';

	const { Story } = defineMeta({
		title: 'Header/Link',
		component: Link,
		tags: ['autodocs'],
		args: {
			Icon: Search,
			label: 'Button'
		}
	});
</script>

<Story name="Active" args={{ href: '/' }} />

<Story name="Inactive" args={{ href: '/nowhere' }} />
