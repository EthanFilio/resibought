export interface ReceiptItem {
	id: string;
	name: string;
	price: number;
	category: string;
	warranty?: {
		duration: string;
		expiresAt: Date;
	};
}

export interface Receipt {
	id: string;
	storeName: string;
	date: Date;
	total: number;
	items: ReceiptItem[];
	imageUrl: string;
	extractedText: string;
}

export const categories = [
	'Groceries',
	'Electronics',
	'Clothing',
	'Tools',
	'Home & Garden',
	'Health & Beauty',
	'Entertainment',
	'Transportation',
	'Dining',
	'Other'
];

export function getCategorySpending(receipts: Receipt[]) {
	const spending: Record<string, number> = {};
	receipts.forEach((receipt) => {
		receipt.items.forEach((item) => {
			spending[item.category] = (spending[item.category] || 0) + item.price;
		});
	});
	return Object.entries(spending).map(([name, value]) => ({ name, value }));
}

export function getMonthlySpending(receipts: Receipt[]) {
	const monthly: Record<string, number> = {};
	receipts.forEach((receipt) => {
		const monthKey = receipt.date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
		monthly[monthKey] = (monthly[monthKey] || 0) + receipt.total;
	});
	return Object.entries(monthly).map(([name, total]) => ({ name, total }));
}

export function getWarrantyItems(receipts: Receipt[]) {
	const items: Array<ReceiptItem & { receiptId: string; storeName: string; purchaseDate: Date }> =
		[];
	receipts.forEach((receipt) => {
		receipt.items.forEach((item) => {
			if (item.warranty) {
				items.push({
					...item,
					receiptId: receipt.id,
					storeName: receipt.storeName,
					purchaseDate: receipt.date
				});
			}
		});
	});
	return items.sort((a, b) => a.warranty!.expiresAt.getTime() - b.warranty!.expiresAt.getTime());
}

export function getDaysUntilExpiry(expiresAt: Date) {
	const now = new Date();
	return Math.ceil((expiresAt.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}
