<script lang="ts">
	import '$lib/styles/layout.css';

	let { children } = $props();
</script>

<div class="space-y-6 pb-20 md:pb-6">
	{@render children()}
</div>
