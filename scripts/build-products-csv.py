#!/usr/bin/env python3
"""Builds data/products.csv (Shopify product import format) from data/products.json.
Variant Price is left EMPTY on purpose: fill in your real prices before importing.
Usage: python3 scripts/build-products-csv.py
"""
import csv, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, 'data', 'products.json')))
cols = ['Handle','Title','Body (HTML)','Vendor','Product Category','Type','Tags','Published','Option1 Name','Option1 Value',
        'Variant SKU','Variant Grams','Variant Inventory Tracker','Variant Inventory Qty','Variant Inventory Policy',
        'Variant Fulfillment Service','Variant Price','Variant Compare At Price','Variant Requires Shipping','Variant Taxable',
        'Image Src','Image Position','Image Alt Text','SEO Title','SEO Description','Variant Weight Unit','Status',
        'Specifications (product.metafields.ind.specifications)']
with open(os.path.join(ROOT, 'data', 'products.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for p in data['products']:
        w.writerow({
            'Handle': p['handle'], 'Title': p['title'], 'Body (HTML)': p['descriptionHtml'], 'Vendor': p['vendor'],
            'Product Category': '', 'Type': p['productType'], 'Tags': ', '.join(p['tags']), 'Published': 'TRUE',
            'Option1 Name': 'Title', 'Option1 Value': 'Default Title', 'Variant SKU': '',
            'Variant Grams': int(p.get('weightKg', 0) * 1000) or '', 'Variant Inventory Tracker': 'shopify',
            'Variant Inventory Qty': '', 'Variant Inventory Policy': 'deny', 'Variant Fulfillment Service': 'manual',
            'Variant Price': '', 'Variant Compare At Price': '', 'Variant Requires Shipping': 'TRUE', 'Variant Taxable': 'TRUE',
            'Image Src': '', 'Image Position': '', 'Image Alt Text': '',
            'SEO Title': p['seo']['title'], 'SEO Description': p['seo']['description'], 'Variant Weight Unit': 'kg',
            'Status': 'draft', 'Specifications (product.metafields.ind.specifications)': json.dumps(p['specifications'], ensure_ascii=False),
        })
print('wrote data/products.csv')
