<script lang="ts">
	import '$lib/styles/layout.css';
	import { ContentCard } from '../Common';
	import { LineChart, Tooltip } from 'layerchart';
	import { timeMonth } from 'd3-time';

	interface Props {
		/** Title of the pie chart*/
		title: string;
		/** Data of the pie chart*/
		data: { month: string; value: number }[];
		/** How the value is formatted */
		format: (v: number) => string;
	}
	const { title, data, format }: Props = $props();
</script>

<ContentCard {title}>
	<div class="h-75 overflow-auto">
		<LineChart
			{data}
			x={(d) => new Date(d.month)}
			y="value"
			height={300}
			series={[{ key: 'value', color: 'var(--color-forest-green-600)' }]}
			props={{
				spline: { class: 'stroke-2' },
				xAxis: {
					classes: { tickLabel: 'text-sm font-normal text-gray-500' },
					ticks: { interval: timeMonth.every(1) }
				},
				yAxis: {
					classes: { tickLabel: 'text-sm font-normal text-gray-500' },
					rule: true,
					format: format
				}
			}}
			padding={{ top: 30, bottom: 30, right: 100, left: 100 }}
			points
		>
			{#snippet tooltip()}
				<Tooltip.Root
					>{#snippet children({ data })}
						<Tooltip.Header>
							{data.month}
						</Tooltip.Header>
						{format(data.value)}
					{/snippet}</Tooltip.Root
				>
			{/snippet}
		</LineChart>
	</div>
</ContentCard>
