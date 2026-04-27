<script lang="ts">
	import '$lib/styles/layout.css';
	import NavLink from './HeaderLink.svelte';
	import type { Component } from 'svelte';
	import type { Pathname } from '$app/types';
	interface Props {
		/** App name */
		title: string;
		/** App Logo*/
		Logo: Component;
		/** Nav Items*/
		navItems: { id: number; href: Pathname; Icon: Component; label: string }[];
	}

	const { title, Logo, navItems }: Props = $props();
</script>

<header class="sticky top-0 z-10 border-b border-gray-200 bg-white">
	<div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
		<div class="flex items-center gap-2">
			<Logo />
			<h1 class="text-xl font-bold text-gray-900">{title}</h1>
		</div>
		<nav class="hidden items-center gap-1 md:flex">
			{#each navItems as item (item.id)}
				<NavLink label={item.label} href={item.href} Icon={item.Icon} />
			{/each}
		</nav>
	</div>
</header>
