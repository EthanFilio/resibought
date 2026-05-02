import type { Receipt } from './types/common';

export const mockReceipts: Receipt[] = [
	{
		id: '1',
		storeName: 'Abenson',
		date: new Date('2026-04-20'),
		total: 12990.99,
		imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
		extractedText: 'Abenson\n123 Tech Street\nLaptop - $1299.99\n1 Year Warranty\nTotal: $1299.99',
		items: [
			{
				id: '1-1',
				name: 'Acer Laptop',
				price: 12990.99,
				category: 'Electronics',
				warranty: {
					duration: '1 year',
					expiresAt: new Date('2027-04-20')
				}
			}
		]
	},
	{
		id: '2',
		storeName: 'Puregold',
		date: new Date('2026-04-18'),
		total: 870.42,
		imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
		extractedText: '',
		items: [
			{ id: '2-1', name: 'Organic Milk', price: 40.99, category: 'Groceries' },
			{ id: '2-2', name: 'Bread', price: 20.99, category: 'Groceries' },
			{ id: '2-3', name: 'Apples (2lb)', price: 50.98, category: 'Groceries' },
			{ id: '2-4', name: 'Chicken Breast', price: 120.99, category: 'Groceries' },
			{ id: '2-5', name: 'Pasta', price: 10.99, category: 'Groceries' },
			{ id: '2-6', name: 'Olive Oil', price: 80.99, category: 'Groceries' },
			{ id: '2-7', name: 'Yogurt (6pk)', price: 40.99, category: 'Groceries' },
			{ id: '2-8', name: 'Bananas', price: 20.5, category: 'Groceries' }
		]
	},
	{
		id: '3',
		storeName: 'Ace Hardware',
		date: new Date('2026-04-15'),
		total: 2340.56,
		imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
		extractedText: '',
		items: [
			{
				id: '3-1',
				name: 'Power Drill',
				price: 890.99,
				category: 'Tools',
				warranty: {
					duration: '90 days',
					expiresAt: new Date('2026-07-14')
				}
			},
			{ id: '3-2', name: 'Drill Bits Set', price: 240.99, category: 'Tools' },
			{ id: '3-3', name: 'Safety Glasses', price: 120.99, category: 'Tools' },
			{ id: '3-4', name: 'Work Gloves', price: 150.99, category: 'Tools' },
			{ id: '3-5', name: 'Extension Cord', price: 180.99, category: 'Tools' },
			{ id: '3-6', name: 'Toolbox', price: 710.61, category: 'Tools' }
		]
	},
	{
		id: '4',
		storeName: 'Uniqlo',
		date: new Date('2026-04-10'),
		total: 1560.97,
		imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
		extractedText: '',
		items: [
			{ id: '4-1', name: 'Blue Jeans', price: 490.99, category: 'Clothing' },
			{ id: '4-2', name: 'T-Shirt (2)', price: 390.98, category: 'Clothing' },
			{ id: '4-3', name: 'Sneakers', price: 670.0, category: 'Clothing' }
		]
	},
	{
		id: '5',
		storeName: 'DataBlitz',
		date: new Date('2026-03-28'),
		total: 4490.99,
		imageUrl: 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400',
		extractedText: '',
		items: [
			{
				id: '5-1',
				name: 'Wireless Headphones',
				price: 199.99,
				category: 'Electronics',
				warranty: {
					duration: '2 years',
					expiresAt: new Date('2028-03-28')
				}
			},
			{ id: '5-2', name: 'Phone Case', price: 290.99, category: 'Electronics' },
			{ id: '5-3', name: 'USB-C Cable', price: 190.99, category: 'Electronics' },
			{ id: '5-4', name: 'Screen Protector', price: 140.99, category: 'Electronics' },
			{ id: '5-5', name: 'Charging Pad', price: 390.99, category: 'Electronics' },
			{ id: '5-6', name: 'Bluetooth Speaker', price: 1450.04, category: 'Electronics' }
		]
	}
];
