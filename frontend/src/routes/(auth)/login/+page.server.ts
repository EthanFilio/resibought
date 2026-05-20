// src/routes/+page.server.ts
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad, RequestEvent } from './$types';

export const load: PageServerLoad = async ({ url, locals: { supabase } }) => {
	const { data, error } = await supabase.auth.getClaims();

	if (!error && data?.claims) {
		redirect(303, '/dashboard');
	}

	return { url: url.origin };
};

const logReg = async (event: RequestEvent, isReg: boolean) => {
	const {
		request,
		locals: { supabase }
	} = event;
	const formData = await request.formData();
	const email = formData.get('email') as string;
	const password = formData.get('password') as string;

	const validEmail = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email);
	if (!validEmail) {
		return fail(400, {
			errors: {
				email: 'Please enter a valid email address',
				password: null,
				passwordConfirm: null
			},
			email,
			password,
			passwordConfirm: ''
		});
	}

	if (password.length < 8) {
		return fail(400, {
			errors: {
				email: null,
				password: 'Please enter a password with at least 8 characters',
				passwordConfirm: null
			},
			email,
			password,
			passwordConfirm: ''
		});
	}

	if (isReg) {
		const passwordConfirm = formData.get('passwordConfirm') as string;
		if (passwordConfirm !== password) {
			return fail(400, {
				errors: { email: null, password: null, passwordConfirm: 'Please enter the same password' },
				email,
				password,
				passwordConfirm
			});
		}

		const { error } = await supabase.auth.signUp({ email, password });

		if (error) {
			return fail(400, {
				success: false,
				email,
				password,
				passwordConfirm,
				message: `Registration Failed`
			});
		}
	} else {
		const { error } = await supabase.auth.signInWithPassword({ email, password });

		if (error) {
			return fail(400, {
				success: false,
				email,
				password,
				passwordConfirm: '',
				message: `Account not found. Email or password incorrect`
			});
		}
	}

	redirect(303, '/dashboard');
};

export const actions: Actions = {
	login: async (event) => logReg(event, false),
	register: async (event) => logReg(event, true)
};
