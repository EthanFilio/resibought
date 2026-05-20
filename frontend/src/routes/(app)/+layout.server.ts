import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals: { supabase } }) => {
	const { data: claimsData, error } = await supabase.auth.getClaims();

	if (error || !claimsData?.claims) {
		redirect(303, '/');
	}

	return { claimsData: claimsData };
};
