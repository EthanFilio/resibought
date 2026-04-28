<script lang="ts">
	import '$lib/styles/layout.css';
	import Logo from '../Logo/Logo.svelte';

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

	<form class="space-y-2">
		<div>
			<input
				type="email"
				id="email"
				class="w-full rounded-lg border border-gray-300 px-4 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-forest-green-500"
				placeholder="Email"
				required
			/>
		</div>

		<div>
			<input
				type="password"
				id="password"
				class="w-full rounded-lg border border-gray-300 px-4 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-forest-green-500"
				placeholder="Password"
				required
			/>
		</div>

		<button
			type="submit"
			class="w-full rounded-lg bg-forest-green-600 px-4 py-2 font-medium text-white transition-colors hover:bg-forest-green-700"
		>
			{isSignup ? 'Sign Up' : 'Log In'}
		</button>
	</form>

	<div class="mt-6 text-center">
		<button
			onclick={() => (isSignup = !isSignup)}
			class="text-sm text-forest-green-600 hover:text-forest-green-700"
		>
			{isSignup ? 'Already have an account? Log in' : "Don't have an account? Sign up"}
		</button>
	</div>
</div>
