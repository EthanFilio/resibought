<script lang="ts">
	import { Receipt } from '@lucide/svelte';

	interface Props {
		/** How large should the logo be? */
		size?: 'small' | 'medium' | 'large';
	}

	const { size = 'medium' }: Props = $props();
</script>

{#if size === 'small'}
	<div class="flex h-8 w-8 items-center justify-center rounded-md bg-forest-green-600">
		<Receipt class="h-5 w-5 text-white" />
	</div>
{:else if size === 'medium'}
	<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-forest-green-600">
		<Receipt class="h-6 w-6 text-white" />
	</div>
{:else}
	<div class="flex h-15 w-15 items-center justify-center rounded-xl bg-forest-green-600">
		<Receipt class="h-8 w-8 text-white" />
	</div>
{/if}
