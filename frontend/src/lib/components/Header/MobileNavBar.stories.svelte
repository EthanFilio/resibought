<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import MobileNavBar from './MobileNavBar.svelte';
	import { House, Upload, Shield, ChartColumnIncreasing, User } from '@lucide/svelte';

	const { Story } = defineMeta({
		title: 'Header/MobileNavBar',
		component: MobileNavBar,
		tags: ['autodocs'],
		parameters: {
			layout: 'fullscreen'
		}
	});
</script>

<Story
	name="On Page"
	args={{
		navItems: [
			{ id: 1, href: '/', Icon: House, label: 'Dashboard' },
			{ id: 2, href: '/upload', Icon: Upload, label: 'Upload' },
			{ id: 3, href: '/warranties', Icon: Shield, label: 'Warranties' },
			{ id: 4, href: '/analytics', Icon: ChartColumnIncreasing, label: 'Analytics' },
			{ id: 5, href: '/account', Icon: User, label: 'Account' }
		]
	}}
/>

<Story
	name="Off Page"
	args={{
		navItems: [
			{ id: 1, href: '/upload', Icon: House, label: 'Dashboard' },
			{ id: 2, href: '/upload', Icon: Upload, label: 'Upload' },
			{ id: 3, href: '/warranties', Icon: Shield, label: 'Warranties' },
			{ id: 4, href: '/analytics', Icon: ChartColumnIncreasing, label: 'Analytics' },
			{ id: 5, href: '/account', Icon: User, label: 'Account' }
		]
	}}
/>
