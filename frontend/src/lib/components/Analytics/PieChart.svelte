<script lang="ts">
	import '$lib/styles/layout.css';
	import { ContentCard } from '../Common';
	import { PieChart, Tooltip } from 'layerchart';

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
	<div class="h-75 overflow-auto">
		<PieChart
			{data}
			key="name"
			value="value"
			height={300}
			cRange={[
				'var(--color-forest-green-600)',
				'var(--color-forest-green-500)',
				'var(--color-forest-green-400)',
				'var(--color-forest-green-300)',
				'var(--color-forest-green-200)'
			]}
			labels={{
				placement: 'callout',
				calloutLineLength: 30,
				calloutPadding: 0,
				value: (d) => `${d.name}: ${((d.value * 100) / total).toFixed(2)}%`,
				class: 'text-gray-600 text-sm'
			}}
			props={{ arc: { class: 'stroke-white' } }}
			padding={40}
		>
			{#snippet tooltip()}
				<Tooltip.Root
					>{#snippet children({ data })}
						{data.name}: {format(data.value)}
					{/snippet}</Tooltip.Root
				>
			{/snippet}
		</PieChart>
	</div>
</ContentCard>
