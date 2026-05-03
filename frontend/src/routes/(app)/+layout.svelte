<script lang="ts">
	import '$lib/styles/layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { Header, MobileNavBar } from '$lib/components/Header';
	import Logo from '$lib/components/Logo/Logo.svelte';
	import { House, Upload, Shield, ChartColumnIncreasing, User } from '@lucide/svelte';
	import type { Pathname } from '$app/types';

	const args = {
		title: 'Resibought',
		Logo: Logo,
		navItems: [
			{ id: 1, href: '/dashboard' as Pathname, Icon: House, label: 'Dashboard' },
			{ id: 2, href: '/upload' as Pathname, Icon: Upload, label: 'Upload' },
			{ id: 3, href: '/warranties' as Pathname, Icon: Shield, label: 'Warranties' },
			{ id: 4, href: '/analytics' as Pathname, Icon: ChartColumnIncreasing, label: 'Analytics' },
			{ id: 5, href: '/account' as Pathname, Icon: User, label: 'Account' }
		]
	};

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<div class="min-h-screen bg-gray-50">
	<Header {...args} />
	<main class="mx-auto max-w-7xl px-4 py-6">
		{@render children()}
	</main>
	<MobileNavBar {...args} />
</div>
