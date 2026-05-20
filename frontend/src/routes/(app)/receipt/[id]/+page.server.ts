import type { PageServerLoad } from './$types';
import { JSONtoReceipt } from '$lib/types/common';

export const load: PageServerLoad = async ({ locals: { supabase }, parent, params }) => {
	const { claimsData } = await parent();
	const { claims } = claimsData;
	const { id } = params;

	const { data: receiptData } = await supabase
		.from('receipts')
		.select(
			`
      id, 
      storeName: store_name, 
      date, 
      total, 
      imageUrl: 
      image_url, 
      extractedText: extracted_text, 
      items: receipt_items (id, name, price, category, warranty: warranties(duration, expiresAt: expires_at))
      `
		)
		.eq('user_id', claims.sub)
		.eq('id', id)
		.single();
	// @ts-expect-error warranty is treated as an array when its not
	const receipt = receiptData ? JSONtoReceipt(receiptData) : null;
	return { receipt };
};
