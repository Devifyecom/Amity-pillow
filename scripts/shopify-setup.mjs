#!/usr/bin/env node
/**
 * Creates or updates the Selo and Abrelune products, the specs metafield definition, and the
 * automatic quantity / Black Friday discounts in a Shopify DEVELOPMENT store via the Admin GraphQL API.
 *
 *   SHOPIFY_STORE=your-dev-store.myshopify.com \
 *   SHOPIFY_ADMIN_TOKEN=shpat_xxx \
 *   node scripts/shopify-setup.mjs --selo-price 0000.00 --abrelune-price 0000.00 [--dry-run] [--publish]
 *
 * Token: Shopify admin → Settings → Apps → Develop apps → create app → Admin API scopes:
 *   write_products, read_products, write_discounts, read_discounts, write_publications (only for --publish)
 * The token is read from the environment only. It is never written to disk or logged.
 *
 * Safety:
 *  - Refuses to run unless the shop is a development store (override: --allow-non-dev, use with care).
 *  - Refuses to run without explicit prices. No price is invented.
 *  - Products are created as DRAFT unless --publish is passed.
 *  - Idempotent: products are matched by handle, discounts by title.
 */
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const API_VERSION = '2025-07';
const args = process.argv.slice(2);
const flag = (n) => args.includes(`--${n}`);
const opt = (n) => { const i = args.indexOf(`--${n}`); return i > -1 ? args[i + 1] : undefined; };

const STORE = process.env.SHOPIFY_STORE;
const TOKEN = process.env.SHOPIFY_ADMIN_TOKEN;
const DRY = flag('dry-run');
const PRICES = { selo: opt('selo-price'), abrelune: opt('abrelune-price') };
const COMPARE = { selo: opt('selo-compare-at'), abrelune: opt('abrelune-compare-at') };

const die = (m) => { console.error(`✖ ${m}`); process.exit(1); };
if (!STORE || !/^[a-z0-9-]+\.myshopify\.com$/.test(STORE)) die('Set SHOPIFY_STORE to your-dev-store.myshopify.com');
if (!TOKEN && !DRY) die('Set SHOPIFY_ADMIN_TOKEN in the environment (or use --dry-run)');
for (const h of Object.keys(PRICES)) {
  if (!PRICES[h] || !/^\d+(\.\d{1,2})?$/.test(PRICES[h])) die(`Pass a real price with --${h}-price (e.g. 1299.00). Prices are never guessed.`);
}

const here = path.dirname(fileURLToPath(import.meta.url));
const data = JSON.parse(await readFile(path.join(here, '..', 'data', 'products.json'), 'utf8'));

async function gql(query, variables = {}) {
  if (DRY) { console.log('  [dry-run]', query.trim().split('\n')[0].slice(0, 80), JSON.stringify(variables).slice(0, 160)); return {}; }
  const res = await fetch(`https://${STORE}/admin/api/${API_VERSION}/graphql.json`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Shopify-Access-Token': TOKEN },
    body: JSON.stringify({ query, variables }),
  });
  const json = await res.json();
  if (!res.ok || json.errors) die(`GraphQL error: ${JSON.stringify(json.errors || json).slice(0, 500)}`);
  return json.data;
}
const userErrors = (obj) => {
  const errs = obj && obj.userErrors;
  if (errs && errs.length) die(`Shopify rejected the request: ${JSON.stringify(errs)}`);
};

/* 1. Make sure this is a development store */
if (!DRY) {
  const { shop } = await gql(`query { shop { name myshopifyDomain plan { partnerDevelopment shopifyPlus } } }`);
  console.log(`Store: ${shop.name} (${shop.myshopifyDomain})`);
  if (!shop.plan.partnerDevelopment && !flag('allow-non-dev')) {
    die('This is not a development store. Refusing to change production data. Pass --allow-non-dev only if you are sure.');
  }
}

/* 2. Metafield definition for specifications (rendered by sections/ind-specs.liquid) */
console.log('→ Metafield definition ind.specifications');
{
  const d = await gql(`mutation($def: MetafieldDefinitionInput!) {
    metafieldDefinitionCreate(definition: $def) { createdDefinition { id } userErrors { field message code } }
  }`, { def: {
    name: 'Specifications', namespace: 'ind', key: 'specifications', type: 'json', ownerType: 'PRODUCT',
    description: 'Technical specifications: [{"label":"…","value":"…"}]', access: { storefront: 'PUBLIC_READ' },
  } });
  const errs = d.metafieldDefinitionCreate && d.metafieldDefinitionCreate.userErrors;
  if (errs && errs.length && !errs.every((e) => e.code === 'TAKEN')) die(JSON.stringify(errs));
}

/* 3. Products */
const productIds = {};
for (const p of data.products) {
  console.log(`→ Product ${p.title} (/products/${p.handle})`);
  const variant = {
    optionValues: [{ optionName: 'Title', name: 'Default Title' }],
    price: PRICES[p.handle],
    inventoryPolicy: 'DENY',
    inventoryItem: { tracked: true, requiresShipping: true, ...(p.weightKg ? { measurement: { weight: { unit: 'KILOGRAMS', value: p.weightKg } } } : {}) },
    taxable: true,
  };
  if (COMPARE[p.handle]) variant.compareAtPrice = COMPARE[p.handle];
  const input = {
    handle: p.handle,
    title: p.title,
    descriptionHtml: p.descriptionHtml,
    vendor: p.vendor,
    productType: p.productType,
    tags: p.tags,
    templateSuffix: p.templateSuffix,
    status: flag('publish') ? 'ACTIVE' : 'DRAFT',
    seo: p.seo,
    productOptions: [{ name: 'Title', values: [{ name: 'Default Title' }] }],
    variants: [variant],
    metafields: [{ namespace: 'ind', key: 'specifications', type: 'json', value: JSON.stringify(p.specifications) }],
  };
  const existing = DRY ? null : (await gql(`query($h: String!) { productByIdentifier(identifier: { handle: $h }) { id } }`, { h: p.handle })).productByIdentifier;
  const d = existing
    ? await gql(`mutation($input: ProductSetInput!, $id: ID!) {
        productSet(input: $input, identifier: { id: $id }, synchronous: true) {
          product { id handle title status variants(first: 1) { nodes { id price } } }
          userErrors { field message }
        }
      }`, { input, id: existing.id })
    : await gql(`mutation($input: ProductSetInput!) {
        productSet(input: $input, synchronous: true) {
          product { id handle title status variants(first: 1) { nodes { id price } } }
          userErrors { field message }
        }
      }`, { input });
  if (!DRY) {
    userErrors(d.productSet);
    const prod = d.productSet.product;
    productIds[p.handle] = prod.id;
    console.log(`  ✔ ${prod.title} ${prod.id} handle=${prod.handle} status=${prod.status} price=${prod.variants.nodes[0].price}`);
    if (prod.handle !== p.handle) console.warn(`  ⚠ handle is "${prod.handle}". Another product may already use "${p.handle}".`);
  } else {
    productIds[p.handle] = `gid://shopify/Product/DRY_${p.handle}`;
  }
}

/* 4. Publish to the Online Store sales channel (optional) */
if (flag('publish') && !DRY) {
  const pubs = await gql(`query { publications(first: 20) { nodes { id name } } }`);
  const online = pubs.publications.nodes.find((n) => /online store/i.test(n.name));
  if (!online) console.warn('  ⚠ Online Store publication not found. Publish manually.');
  else for (const id of Object.values(productIds)) {
    const r = await gql(`mutation($id: ID!, $pub: ID!) { publishablePublish(id: $id, input: { publicationId: $pub }) { userErrors { field message } } }`, { id, pub: online.id });
    userErrors(r.publishablePublish);
  }
  console.log('  ✔ Published to Online Store');
}

/* 5. Automatic discounts: per product, non-combinable, best one wins */
const existingTitles = new Set();
if (!DRY) {
  const d = await gql(`query { automaticDiscountNodes(first: 100) { nodes { automaticDiscount { ... on DiscountAutomaticBasic { title } } } } }`);
  d.automaticDiscountNodes.nodes.forEach((n) => n.automaticDiscount && n.automaticDiscount.title && existingTitles.add(n.automaticDiscount.title));
}
async function createDiscount({ title, productId, minQty, percent, startsAt, endsAt }) {
  if (existingTitles.has(title)) { console.log(`  • exists: ${title}`); return; }
  const d = await gql(`mutation($d: DiscountAutomaticBasicInput!) {
    discountAutomaticBasicCreate(automaticBasicDiscount: $d) { automaticDiscountNode { id } userErrors { field message } }
  }`, { d: {
    title,
    startsAt: startsAt || new Date().toISOString(),
    endsAt: endsAt || null,
    combinesWith: { productDiscounts: false, orderDiscounts: false, shippingDiscounts: true },
    minimumRequirement: { quantity: { greaterThanOrEqualToQuantity: String(minQty) } },
    customerGets: { value: { percentage: percent / 100 }, items: { products: { productsToAdd: [productId] } } },
  } });
  if (!DRY) userErrors(d.discountAutomaticBasicCreate);
  console.log(`  ✔ ${title}`);
}

console.log('→ Automatic discounts');
const bf = data.discounts.blackFriday;
for (const p of data.products) {
  const id = productIds[p.handle];
  for (const t of data.discounts.standard) {
    await createDiscount({ title: `${p.title}: buy ${t.minQty}+ save ${t.percent}%`, productId: id, minQty: t.minQty, percent: t.percent });
  }
  for (const t of bf.tiers) {
    await createDiscount({ title: `Black Friday ${p.title}: ${t.minQty}+ save ${t.percent}%`, productId: id, minQty: t.minQty, percent: t.percent, startsAt: bf.startsAt, endsAt: bf.endsAt });
  }
}

console.log('\nDone. Next steps:');
console.log('  • Upload real product photos to each product in Shopify admin (none are uploaded by this script).');
console.log('  • Online Store → Themes → Customize: check that product templates "selo" and "abrelune" are assigned.');
console.log('  • Place a test order with 1, 2 and 3 units and confirm the checkout totals match the product page.');
