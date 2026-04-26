<script module>
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Header from './Header.svelte';
	import Logo from '../Logo/Logo.svelte';
	import { House, Upload, Shield, ChartColumnIncreasing, User } from '@lucide/svelte';

	const { Story } = defineMeta({
		title: 'Header/Header',
		component: Header,
		tags: ['autodocs'],
		parameters: {
			layout: 'fullscreen'
		},
		args: {
			title: 'Resibought',
			Logo: Logo,
			navItems: [
				{ id: 1, href: '/', Icon: House, label: 'Dashboard' },
				{ id: 2, href: '/upload', Icon: Upload, label: 'Upload' },
				{ id: 3, href: '/warranties', Icon: Shield, label: 'Warranties' },
				{ id: 4, href: '/analytics', Icon: ChartColumnIncreasing, label: 'Analytics' },
				{ id: 5, href: '/account', Icon: User, label: 'Account' }
			]
		}
	});
</script>

<Story name="On Page" />
