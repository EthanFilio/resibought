<script lang="ts">
	import '$lib/styles/layout.css';
	import type { Component } from 'svelte';

	interface Props {
		/** Title of the card */
		title: string;
		/** Subtitle of the card */
		subtitle: string;
		/** Icon on the top right */
		Icon: Component;
		/** What the icon color should be */
		iconColor: string;
		/** Emphasized value */
		value: string;
	}
	const colorMap: Record<string, string> = {
		'forest-green': 'text-forest-green-600',
		blue: 'text-blue-600',
		purple: 'text-purple-600',
		yellow: 'text-yellow-600',
		orange: 'text-orange-600',
		red: 'text-red-600'
	};
	const { title, subtitle, Icon, iconColor, value }: Props = $props();
	const style = $derived(colorMap[iconColor]);
</script>

<div class="rounded-xl bg-white p-6 shadow-sm">
	<div class="mb-2 flex items-center justify-between">
		<span class="text-gray-600">{title}</span>
		<Icon class={['h-5 w-5', style].join(' ')} />
	</div>
	<p class="text-3xl font-bold text-gray-900">{value}</p>
	<p class="mt-1 text-sm text-gray-500">{subtitle}</p>
</div>
