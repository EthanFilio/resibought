<script lang="ts">
	import '$lib/styles/layout.css';
	import { ContentCard } from '../Common';
	import { BarChart, Tooltip } from 'layerchart';

	interface Props {
		/** Title of the pie chart*/
		title: string;
		/** Data of the pie chart*/
		data: { name: string; value: number }[];
		/** How the value is formatted */
		format: (v: number) => string;
	}
	const { title, data, format }: Props = $props();
</script>

<ContentCard {title}>
	<div class="h-75 overflow-auto">
		<BarChart
			{data}
			x="name"
			y="value"
			height={300}
			props={{
				bars: { class: 'fill-forest-green-600 stroke-forest-green-600' },
				xAxis: { classes: { tickLabel: 'text-sm font-normal text-gray-500' } },
				yAxis: {
					classes: { tickLabel: 'text-sm font-normal text-gray-500' },
					rule: true,
					format: format
				}
			}}
			padding={{ top: 30, bottom: 30, right: 100, left: 100 }}
		>
			{#snippet tooltip()}
				<Tooltip.Root
					>{#snippet children({ data })}
						{data.name}: {format(data.value)}
					{/snippet}</Tooltip.Root
				>
			{/snippet}
		</BarChart>
	</div>
</ContentCard>
