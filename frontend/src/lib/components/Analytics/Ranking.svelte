<script lang="ts">
	import '$lib/styles/layout.css';
	import { ContentCard } from '../Common';

	interface Props {
		/** Title of the pie chart*/
		title: string;
		/** Data of the pie chart*/
		data: { name: string; value: number }[];
		/** How the value is formatted */
		format: (v: number) => string;
	}
	const { title, data, format }: Props = $props();
	const total = $derived(data.reduce((sum, d) => sum + d.value, 0));
</script>

<ContentCard {title}>
	<div class="space-y-4">
		{#each data as d, index (d.name)}
			{@const percentage = (d.value * 100) / total}
			<div class="mb-1 flex items-center justify-between">
				<div class="flex items-center gap-2">
					<span
						class="flex h-6 w-6 items-center justify-center rounded-full bg-forest-green-100 text-sm font-semibold text-forest-green-600"
					>
						{index + 1}
					</span>
					<span class="font-medium text-gray-900">{d.name}</span>
				</div>
				<span class="font-semibold text-gray-900">{format(d.value)}</span>
			</div>
			<div class="h-2 w-full rounded-full bg-gray-200">
				<div
					class="h-2 rounded-full bg-forest-green-600 transition-all"
					style:width="{percentage}%"
				></div>
			</div>
			<p class="mt-1 text-xs text-gray-500">{percentage.toFixed(2)}% of total spending</p>
		{/each}
	</div>
</ContentCard>
