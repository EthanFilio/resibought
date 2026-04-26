<script lang="ts">
	import '$lib/styles/layout.css';
	import { page } from '$app/state';
	import type { Component } from 'svelte';
	import { resolve } from '$app/paths';
	import type { Pathname } from '$app/types';

	interface Props {
		/** Button contents */
		label: string;
		/** Route */
		href: Pathname;
		/** Lucide Icon*/
		Icon: Component;
	}

	const { label, href = '/', Icon }: Props = $props();

	let mode = $derived(
		href === page.url.pathname
			? 'bg-forest-green-100 text-forest-green-600'
			: 'text-gray-600 hover:bg-gray-100'
	);
</script>

<a
	class={['flex items-center gap-2 rounded-lg px-4 py-2 transition-colors', mode].join(' ')}
	href={resolve(href)}
>
	<Icon class="h-4 w-4" />
	<span>{label}</span>
</a>
