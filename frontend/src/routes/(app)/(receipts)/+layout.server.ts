import type { LayoutServerLoad } from './$types';
import { JSONtoReceipts } from '$lib/types/common';

export const load: LayoutServerLoad = async ({ locals: { supabase }, parent }) => {
	const { claimsData } = await parent();
	const { claims } = claimsData;

	const { data: receiptsData } = await supabase
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
		.eq('user_id', claims.sub);
	// @ts-expect-error warranty is treated as an array when its not
	const receipts = JSONtoReceipts(receiptsData).sort((a, b) => b.date.getTime() - a.date.getTime());
	return { receipts };
};
