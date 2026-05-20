<script lang="ts">
	import '$lib/styles/layout.css';
	import Logo from '$lib/components/Logo/Logo.svelte';
	import { enhance } from '$app/forms';
	import type { ActionData, SubmitFunction } from './$types.js';
	interface Props {
		form: ActionData;
	}
	let { form }: Props = $props();
	let loading = $state(false);
	const handleSubmit: SubmitFunction = () => {
		loading = true;
		return async ({ update }) => {
			update();
			loading = false;
		};
	};

	let isSignup = $state(false);
</script>

<div class="w-full max-w-md rounded-2xl bg-white p-8 shadow-xl">
	<div class="mb-8 text-center">
		<div class="mb-4 inline-flex">
			<Logo size="large" />
		</div>

		<h1 class="text-3xl font-bold text-gray-900">Resibought</h1>
		<p class="mt-2 text-gray-600">AI-powered receipt mangment</p>
	</div>

	<form
		class="space-y-2"
		method="POST"
		use:enhance={handleSubmit}
		action={isSignup ? '?/register' : '?/login'}
	>
		<div>
			<input
				//type="email"
				id="email"
				name="email"
				class="w-full rounded-lg border border-gray-300 px-4 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-forest-green-500"
				placeholder="Email"
				value={form?.email ?? ''}
				required
			/>
			{#if form?.errors?.email}
				<div class="mt-0 items-center pl-5 text-sm text-red-400">{form?.errors?.email}</div>
			{/if}
		</div>
		<div>
			<input
				type="password"
				id="password"
				name="password"
				class="w-full rounded-lg border border-gray-300 px-4 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-forest-green-500"
				placeholder="Password"
				value={form?.password ?? ''}
				required
			/>
			{#if form?.errors?.password}
				<div class="mt-0 items-center pl-5 text-sm text-red-400">
					{form?.errors?.password}
				</div>
			{/if}
		</div>

		{#if isSignup}
			<div>
				<input
					type="password"
					id="passwordConfirm"
					name="passwordConfirm"
					class="w-full rounded-lg border border-gray-300 px-4 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-forest-green-500"
					placeholder="Confirm Password"
					value={form?.passwordConfirm ?? ''}
					required
				/>
				{#if form?.errors?.passwordConfirm}
					<div class="mt-0 items-center pl-5 text-sm text-red-400">
						{form?.errors?.passwordConfirm}
					</div>
				{/if}
			</div>
		{/if}
		{#if form?.message !== undefined}
			<div class="text-center text-red-400">{form?.message}</div>
		{/if}

		<button
			type="submit"
			class="w-full rounded-lg bg-forest-green-600 px-4 py-2 font-medium text-white transition-colors hover:bg-forest-green-700"
			disabled={loading}
		>
			{loading ? 'Loading...' : isSignup ? 'Sign Up' : 'Log In'}
		</button>
	</form>

	<div class="mt-6 text-center">
		<button
			onclick={() => (isSignup = !isSignup)}
			class="text-sm text-forest-green-400 hover:text-forest-green-600"
		>
			{isSignup ? 'Already have an account? Log in' : "Don't have an account? Sign up"}
		</button>
	</div>
</div>
