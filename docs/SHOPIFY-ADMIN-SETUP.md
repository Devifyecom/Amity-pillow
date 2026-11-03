# Shopify admin setup: what the theme cannot do by itself

Do these in your **development store**. Allow about 30 minutes.

## 1. Create the products (pick one route)

**A. Script (recommended).** Needs a custom-app Admin API token with `write_products`, `write_discounts`
(plus `write_publications` if you use `--publish`).

```bash
export SHOPIFY_STORE=your-dev-store.myshopify.com
export SHOPIFY_ADMIN_TOKEN=shpat_...        # keep it in your shell, never commit it
node scripts/shopify-setup.mjs --dry-run --selo-price 0.00 --abrelune-price 0.00   # preview
node scripts/shopify-setup.mjs --selo-price <REAL> --abrelune-price <REAL> [--publish]
```
The script refuses to run on a non-development store and refuses to run without explicit prices.
It creates products `selo` and `abrelune` (template suffixes set, specs metafield set, status DRAFT unless
`--publish`), the `ind.specifications` metafield definition, and 10 automatic discounts.

**B. CSV import.** Open `data/products.csv` and fill **Variant Price**. Then go to Products → Import.
Afterwards, for each product: Theme template = `selo` / `abrelune`, and set Status = Active.
(To import the Specifications column, first create the product metafield definition `ind.specifications`, type JSON.
Otherwise the theme falls back to the spec rows in the template, which hold the same data.)

Then **upload real photos** to each product (Products → Media). Add alt text.
Set **Product category**: Selo → *Hardware › Tools › Lifts & Hoists* (or nearest); Abrelune → *Vehicles & Parts* / *Lawn & Garden › Carts* (nearest match).

## 2. Discounts (must match what the theme displays)

| Title | Applies to | Min qty | % | Dates |
|---|---|---|---|---|
| Selo: buy 2+ save 10% | Selo | 2 | 10 | always |
| Selo: buy 3+ save 15% | Selo | 3 | 15 | always |
| Abrelune: buy 2+ save 10% | Abrelune | 2 | 10 | always |
| Abrelune: buy 3+ save 15% | Abrelune | 3 | 15 | always |
| Black Friday {product}: 1+ save 10% | each product | 1 | 10 | 23 Nov 2026 00:00 → 1 Dec 2026 23:59 (UTC+1) |
| Black Friday {product}: 2+ save 15% | each product | 2 | 15 | same |
| Black Friday {product}: 3+ save 20% | each product | 3 | 20 | same |

Type: *Amount off products → Automatic*. Combinations: **none** with product or order discounts.
When several qualify, Shopify applies the one with the biggest saving, so tiers never stack.
If you change a percentage, change it in the theme too: product template → *Package tier* blocks
(standard %) and Theme settings → *Black Friday campaign* (campaign %, dates, UTC offset).

**Verify:** add 1, 2 and 3 units of each product and check that the cart drawer and checkout totals equal
the package prices on the product page. Repeat with the campaign preview dates.

## 3. Theme settings to review
- Theme settings → **Black Friday campaign**: enabled, start/end, UTC offset (must equal the discount time zone).
  "Preview in editor" shows the campaign only inside the theme editor.
- Product templates: replace every `[bracketed placeholder]` (delivery, warranty, returns, set-up, maintenance).
- Footer → Customer support: enter your real email, phone and address (blank fields stay hidden).
- Settings → **Policies**: publish Shipping, Refund, Privacy and Terms. The footer lists whatever is published.
- Navigation: `main-menu` (e.g. Selo, Abrelune, FAQ, Contact) and `footer`.

## 4. Languages
- The Selo page is authored in **English** (primary). UI strings are translated to German in `locales/de.json`.
- To serve German too: Settings → Languages → add German → Translate & Adapt app → translate the product
  title, description, SEO fields and the template section texts.
- Infographics are SVG/HTML with text from section settings, so they translate the same way. There are no image files to redo.

## 5. Cart drawer changes made in this theme
- Disabled the "Cart reserved for 5:00" timer (nothing was actually reserved).
- Disabled the free-shipping progress bar (no confirmed threshold). Re-enable it only with your real threshold.
- Enabled the discount line in the drawer subtotal, so customers see Shopify's applied discounts.
