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
		href === page.url.pathname ? 'text-forest-green-600 bg-forest-green-100' : 'text-gray-600'
	);
</script>

<a
	href={resolve(href)}
	class={['flex flex-col items-center gap-1 rounded-lg px-4 py-3', mode].join(' ')}
>
	<Icon class="h-5 w-5" />
	<span class="text-xs">{label}</span>
</a>
