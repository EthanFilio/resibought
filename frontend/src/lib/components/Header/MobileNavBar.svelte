<script lang="ts">
	import '$lib/styles/layout.css';
	import type { Component } from 'svelte';
	import type { Pathname } from '$app/types';
	import MobileNavLink from './MobileNavLink.svelte';
	interface Props {
		/** Nav Items*/
		navItems: { id: number; href: Pathname; Icon: Component; label: string }[];
	}

	const { navItems }: Props = $props();
</script>

<nav class="fixed right-0 bottom-0 left-0 border-t border-gray-200 bg-white md:hidden">
	<div class="flex items-center justify-around py-2">
		{#each navItems as item (item.id)}
			<MobileNavLink {...item} />
		{/each}
	</div>
</nav>
