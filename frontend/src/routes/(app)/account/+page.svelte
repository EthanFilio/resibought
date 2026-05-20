<script lang="ts">
	import '$lib/styles/layout.css';
	import type { SubmitFunction } from '@sveltejs/kit';
	import { Save, LogOut } from '@lucide/svelte';
	import { SectionHeader } from '$lib/components/Common';
	import { enhance } from '$app/forms';

	let loading = $state(false);

	const handleSave: SubmitFunction = () => {
		loading = true;
		return async ({ update }) => {
			loading = false;
			update();
		};
	};
	const handleLogOut: SubmitFunction = () => {
		loading = true;
		return async ({ update }) => {
			loading = false;
			update();
		};
	};
</script>

<div class="mx-auto max-w-4xl space-y-6 pb-20 md:pb-6">
	<SectionHeader title="Account Settings" subtitle="Manage your profile and preferences" />
	<div class="flex flex-col gap-3 sm:flex-row">
		<button
			//onclick={handleSave}
			class="flex flex-1 items-center justify-center gap-2 rounded-lg bg-forest-green-600 px-6 py-3 font-medium text-white transition-colors hover:bg-forest-green-700"
		>
			<Save class="h-5 w-5" />
			Save Changes
		</button>
		<form method="post" action="?/signout" use:enhance={handleLogOut} class="flex flex-1">
			<button
				class="flex flex-1 items-center justify-center gap-2 rounded-lg bg-gray-100 px-6 py-3 font-medium text-gray-700 transition-colors hover:bg-gray-200"
				disabled={loading}
			>
				<LogOut class="h-5 w-5" />
				{loading ? 'Loading...' : 'Log Out'}
			</button>
		</form>
	</div>
</div>
