# Selo & Abrelune: product data record

Researched 2026-11-03 from the supplier listings:

- Selo: https://pelaorina.com/de/products/selo (German)
- Abrelune: https://bellavorait.com/sv/products/abrelune (Swedish)

The facts used in the theme and in `data/products.json` come only from those listings. Copy was
rewritten in English. It was not copied verbatim.

## What was *not* carried over, and why

| Item | Reason |
|---|---|
| Prices (both listed at €69.90, "was" €233.90) | Not credible for a 500 kg lift or a 150 kg 1000 W vehicle, and identical across both stores. Set your real cost-based price. Set a compare-at price only if you have genuinely sold at it. |
| Ratings ("4.6 (324)", "4.8 (311)") | No review text available, and the products were only weeks old. The theme shows ratings only from a reviews app's metafields. |
| Product images (5 + 5) | AI-generated renders that differ from image to image. 3 Selo images show a person standing on the platform, which contradicts the listing's own "not for carrying people" note. They also belong to other stores. Use supplier-licensed or your own photography. |
| Delivery time, warranty, returns | These are store promises. They're left as `[bracketed placeholders]` in the templates for you to confirm. |

## Selo: verified from listing
Up to 500 kg · up to 6 m lifting height · high-torque electric motor · high-strength galvanised steel cable ·
reinforced steel frame · ergonomic remote control · 360° swivel castors · braking system · automatic limit
stop top and bottom · reinforced guard rails · non-slip platform · **materials only, not for carrying people**.
Supplier claims a 2-year warranty on electrical and load-bearing components (confirm before you promise it).

**Missing (ask the supplier):** motor power, voltage, dimensions, weight, lifting speed, platform size, package contents.

## Abrelune: verified from listing
Brushless 1000 W · two-wheel drive · sealed 48 V lead-acid battery · approx. 24–27 km range* · 4–5 h charge ·
approx. 24 km/h · up to 450 kg · platform 150 × 80 cm at approx. 50 cm · approx. 165 × 79 cm · passage ≥ 84 cm ·
approx. 150 kg · twist throttle, 2 speeds, forward/reverse · battery indicator, LED headlight, horn ·
folding and removable side walls · steel. *Depends on load, surface, gradient and battery condition.
In the box: transporter, 48 V battery system, charger (**110 V** as listed; confirm for EU/UK), manual and safety instructions.
For private land; public-road rules may apply.

**Missing (ask the supplier):** battery Ah, tyre size, brake type, charger spec for your market.

## Image brief (for the photographer / supplier)
Each product needs: a clean hero on a neutral background, 3–4 detail close-ups (Selo: remote, limit switch,
cable drum, castor, platform surface; Abrelune: handlebar and throttle, battery compartment, side-wall hinge,
tyre, LED light), 2–3 in-use shots, and a "what's in the box" flat-lay.
Rules: show the real unit; Selo carries **material only** (no people on the platform). Keep any text off the
photos: the theme renders all labels and infographics as translatable HTML/SVG.
