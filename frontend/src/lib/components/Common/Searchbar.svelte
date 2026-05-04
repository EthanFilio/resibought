<script lang="ts">
	import '$lib/styles/layout.css';
	import { Search } from '@lucide/svelte';

	interface Props {
		/** Placeholder value */
		placeholder: string;
		/** Value to bind to */
		value: string;
	}

	let { value = $bindable(), ...props }: Props = $props();
</script>

<div class="rounded-xl bg-white p-4 shadow-sm">
	<div class="relative">
		<Search class="absolute top-1/2 left-3 h-5 w-5 -translate-y-1/2 text-gray-400" />
		<input
			type="text"
			{...props}
			bind:value
			class="w-full rounded-lg border border-gray-300 py-2 pr-4 pl-10 outline-none focus:border-transparent focus:ring-2 focus:ring-forest-green-500"
		/>
	</div>
</div>
