#!/usr/bin/env python3
"""Generates templates/index.json, product.selo.json and product.abrelune.json.

Every product claim below is taken from the supplier listings researched on 2026-11-03
(see docs/PRODUCT-DATA.md). Store-specific promises (delivery time, warranty, returns)
are left as [bracketed placeholders] for the merchant to confirm.
Re-run after editing: python3 scripts/build-templates.py
"""
import json, os, itertools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_c = itertools.count(1)

def sec(type_, settings=None, blocks=None, name=None):
    s = {"type": type_, "settings": settings or {}}
    if blocks:
        ids = []
        s["blocks"] = {}
        for b in blocks:
            bid = f"{b['type'].strip('@')}_{next(_c)}"
            s["blocks"][bid] = {"type": b["type"], "settings": b.get("settings", {})}
            ids.append(bid)
        s["block_order"] = ids
    return s

def tmpl(sections, layout=None):
    d = {"sections": {}, "order": []}
    if layout:
        d["layout"] = layout
    for key, s in sections:
        d["sections"][key] = s
        d["order"].append(key)
    return d

def write(name, data):
    path = os.path.join(ROOT, "templates", name)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("wrote", path)

B = lambda t, **s: {"type": t, "settings": s}
P = lambda *ps: "".join(f"<p>{p}</p>" for p in ps)

SELO_ACCENT = "#d9531e"   # safety orange: matches the product's frame colour
ABR_ACCENT = "#4f6b2a"    # olive: matches the product's body colour

TIERS = [
    B("tier", label="Single unit", qty=1, pct=0, badge="", preselect=False),
    B("tier", label="Double pack", qty=2, pct=10, badge="Most popular", preselect=True),
    B("tier", label="Triple pack", qty=3, pct=15, badge="Best value", preselect=False),
]
TRUST = [
    B("trust", icon="lock", title="Secure checkout", text="Encrypted payment through Shopify Checkout"),
    B("trust", icon="truck", title="Delivery", text="[Add your confirmed delivery time]"),
    B("trust", icon="award", title="Warranty", text="[Confirm warranty terms with your supplier]"),
    B("trust", icon="return", title="Returns", text="[Summarise your refund policy]"),
]
SHIP_TEXT = P("[Add your confirmed dispatch and delivery times.]",
              "[Summarise your published refund policy and link to it.]")

# ===================================================================== SELO
selo = tmpl([
  ("main", sec("ind-main-product", {
      "accent": SELO_ACCENT, "show_breadcrumbs": True, "media_badge": "",
      "eyebrow": "Scaffold material lift",
      "headline": "Professional lifting power: up to 500 kg to 6 metres, by remote control.",
      "short_desc": P("Move materials up safely and with less effort, right at the scaffold. Selo raises up to 500 kg to a height of up to 6 metres and is controlled by remote, saving your team heavy carrying and valuable working time."),
      "tiers_heading": "Choose your package", "show_buy_now": True, "show_dynamic_checkout": True,
      "stock_detail": "", "show_details": True, "shipping_text": SHIP_TEXT,
      "sticky": True, "sticky_mobile_scroll": False}, [
      B("highlight", icon="weight", text="Up to 500 kg load capacity"),
      B("highlight", icon="height", text="Up to 6 m lifting height"),
      B("highlight", icon="remote", text="Remote-control operation"),
      B("highlight", icon="shield", text="Automatic top and bottom limit stop"),
      *TIERS, *TRUST])),

  ("figures", sec("ind-stat-band", {"scheme": "ink", "accent": SELO_ACCENT, "heading": "Selo at a glance", "note": ""}, [
      B("stat", value="500", unit="kg", label="Maximum load capacity"),
      B("stat", value="6", unit="m", label="Maximum lifting height"),
      B("stat", value="360", unit="°", label="Swivel castors for positioning"),
      B("stat", value="2", unit="×", label="Automatic limit stops: top and bottom"),
  ])),

  ("benefits", sec("ind-feature-grid", {"scheme": "paper", "accent": SELO_ACCENT, "style": "numbered", "columns": 3, "row_mobile": False, "center": False, "tight": False,
      "eyebrow": "Why Selo", "heading": "Less carrying. More working.",
      "text": P("Selo takes material up to the scaffold so your team doesn't have to carry it up ladders and stairs."), "note": ""}, [
      B("feature", icon="weight", title="Lift heavy materials with less manual effort", text=P("Raise up to 500 kg of building material, tools and equipment on the platform instead of carrying it by hand.")),
      B("feature", icon="height", title="Reach elevated working areas", text=P("Up to 6 m lifting height, suitable for common scaffold heights.")),
      B("feature", icon="remote", title="Operate by remote control", text=P("The ergonomic remote lets you control lifting and lowering from a safe distance.")),
      B("feature", icon="stairs", title="Improve material handling", text=P("Fewer trips up and down ladders and stairs keeps the work on site moving.")),
      B("feature", icon="shield", title="Safety-oriented features", text=P("A braking system, automatic limit stops at the top and bottom, reinforced guard rails and a non-slip platform.")),
      B("feature", icon="rotate", title="Easy to position", text=P("360° swivel castors let you move Selo quickly to where it's needed on site.")),
  ])),

  ("lift", sec("ind-image-text", {"scheme": "sand", "accent": SELO_ACCENT, "reverse": False, "wide_media": False, "ratio": "square",
      "placeholder_label": "", "badge_value": "", "badge_label": "",
      "eyebrow": "Powerful electric lifting drive", "heading": "Raise and lower loads smoothly and precisely",
      "text": P("The powerful electric motor raises and lowers loads smoothly and precisely. That reduces physical strain, avoids unnecessary trips up ladders and stairs, and keeps the work on site moving."),
      "checks": "High-torque electric motor\nHigh-strength galvanised steel lifting cable\nControlled lifting and lowering by remote",
      "btn_label": "", "btn_link": "", "btn_style": "dark", "note": "Schematic illustration. Not to scale.",
      "diagram": "lift", "d_v1": "6 m", "d_l1": "max. lifting height", "d_v2": "500 kg", "d_l2": "max. load",
      "d_v3": "360°", "d_l3": "castors", "d_v4": "Remote", "d_l4": "control", "d_caption": ""})),

  ("features", sec("ind-feature-grid", {"scheme": "paper", "accent": SELO_ACCENT, "style": "cards", "columns": 4, "row_mobile": True, "center": True, "tight": False,
      "eyebrow": "Feature highlights", "heading": "Engineered for the job site", "text": "", "note": ""}, [
      B("feature", icon="motor", title="Electric lifting drive", text=P("High-torque motor for even, controlled lifting.")),
      B("feature", icon="remote", title="Ergonomic remote control", text=P("Operate the lift from a safe distance.")),
      B("feature", icon="shield", title="Automatic limit stop", text=P("Stops on its own at the upper and lower end positions.")),
      B("feature", icon="brake", title="Precise braking system", text=P("Holds the load securely.")),
      B("feature", icon="cable", title="Galvanised steel cable", text=P("High-strength lifting cable for long service life.")),
      B("feature", icon="layers", title="Reinforced steel frame", text=P("Built for stability in daily use.")),
      B("feature", icon="grip", title="Non-slip platform", text=P("Helps stop the load from sliding.")),
      B("feature", icon="rotate", title="360° swivel castors", text=P("Fast positioning on site.")),
  ])),

  ("action", sec("ind-tiles", {"scheme": "dark", "accent": SELO_ACCENT, "columns": 4, "wide": False, "center": False,
      "eyebrow": "Selo in action", "heading": "Ideal for work at height",
      "text": P("Selo is for moving materials only and is not approved for carrying people. Use photography that shows material, never people, on the platform.")}, [
      B("tile", icon="brick", title="Construction sites", text="Assembly and construction work"),
      B("tile", icon="tools", title="Painting & renovation", text="Material to the scaffold, where it's needed"),
      B("tile", icon="bolt", title="Technical installations", text="Electrical and mechanical systems"),
      B("tile", icon="wrench", title="Industrial maintenance", text="Maintenance and servicing at height"),
  ])),

  ("safety", sec("ind-image-text", {"scheme": "ink", "accent": SELO_ACCENT, "reverse": True, "wide_media": True, "ratio": "landscape",
      "placeholder_label": "Close-up: platform, guard rails, limit switch, remote", "badge_value": "500 kg", "badge_label": "Max. load",
      "eyebrow": "Construction & safety", "heading": "Safety you can rely on",
      "text": P("Selo is built for professional use, with several safety features for a controlled lift. A reinforced steel frame and a high-strength galvanised steel cable give stability and a long service life, even in daily use."),
      "checks": "Precise braking system holds the load securely\nAutomatic limit stop at the upper and lower positions\nReinforced guard rails keep the load in place\nNon-slip platform helps stop the load sliding",
      "btn_label": "", "btn_link": "", "btn_style": "accent",
      "note": "Selo is for transporting materials only and is not approved for carrying people. Always observe the maximum load capacity and the safety instructions in the operating manual.",
      "diagram": "none"})),

  ("compare", sec("ind-comparison", {"mode": "versus", "scheme": "sand", "accent": SELO_ACCENT,
      "eyebrow": "Traditional method vs. Selo", "heading": "Stop carrying material up ladders", "text": "",
      "label_col": "", "col_a": "Carrying by hand", "col_b": "With Selo", "note": ""}, [
      B("row", label="Getting material to height", a_mark="no", a="Carried up ladders or stairs", b_mark="yes", b="Lifted electrically, up to 6 m"),
      B("row", label="Load per lift", a_mark="none", a="What one person can carry", b_mark="yes", b="Up to 500 kg"),
      B("row", label="Control", a_mark="none", a="Physical effort on every trip", b_mark="yes", b="Remote control from a safe distance"),
      B("row", label="End positions", a_mark="none", a="—", b_mark="yes", b="Automatic limit stop at top and bottom"),
      B("row", label="Positioning", a_mark="none", a="—", b_mark="yes", b="360° swivel castors"),
  ])),

  ("specs", sec("ind-specs", {"scheme": "paper", "accent": SELO_ACCENT, "use_metafield": True,
      "eyebrow": "Technical data", "heading": "Selo specifications", "text": "", "visible_rows": 8,
      "note": "Selo is for transporting materials only, not people.",
      "media": "lift", "d_v1": "6 m", "d_l1": "max. lifting height", "d_v2": "500 kg", "d_l2": "max. load", "d_v3": "", "d_l3": "", "d_v4": "", "d_l4": "", "d_caption": "Schematic illustration. Not to scale."}, [
      B("row", label="Model", value="Selo"),
      B("row", label="Type", value="Scaffold material lift"),
      B("row", label="Load capacity", value="Up to 500 kg"),
      B("row", label="Maximum lifting height", value="Up to 6 m"),
      B("row", label="Motor", value="Professional high-torque electric motor"),
      B("row", label="Lifting cable", value="High-strength galvanised steel cable"),
      B("row", label="Frame", value="Reinforced steel construction"),
      B("row", label="Control", value="Ergonomic remote control"),
      B("row", label="Mobility", value="360° swivel castors"),
      B("row", label="Safety", value="Braking system; automatic limit stop at top and bottom; reinforced guard rails; non-slip platform"),
      B("row", label="Intended use", value="Materials only. Not approved for carrying people."),
  ])),

  ("included", sec("ind-included", {"scheme": "sand", "accent": SELO_ACCENT, "eyebrow": "In the box", "heading": "What's included", "text": "",
      "note": "[Confirm the full package contents with your supplier before publishing.]"}, [
      B("item", icon="layers", qty="1×", title="Selo material lift", text="With electric lifting drive"),
      B("item", icon="remote", qty="1×", title="Remote control", text="Ergonomic hand-held control"),
      B("item", icon="box", qty="1×", title="Operating manual", text="Including safety instructions"),
  ])),

  ("reviews", sec("ind-reviews", {"scheme": "paper", "accent": SELO_ACCENT, "eyebrow": "Customer reviews", "heading": "What customers say"})),

  ("faq", sec("ind-faq", {"scheme": "sand", "accent": SELO_ACCENT, "layout": "aside", "single": True, "open_first": True, "schema": True,
      "eyebrow": "FAQ", "heading": "Questions about Selo", "text": P("Can't find your answer? Contact our support team."), "btn_label": "", "btn_link": ""}, [
      B("qa", q="How much weight can Selo lift?", a=P("Up to 500 kg. Spread the load evenly across the platform.")),
      B("qa", q="How high can Selo lift?", a=P("Up to 6 metres, which suits common scaffold heights.")),
      B("qa", q="How is the lift operated?", a=P("With an ergonomic remote control, so you can control lifting from a safe distance.")),
      B("qa", q="What happens when the maximum height is reached?", a=P("The automatic limit stop stops the lift by itself at the upper and lower end positions.")),
      B("qa", q="Which safety features does Selo have?", a=P("A precise braking system, automatic limit stops at the top and bottom, reinforced guard rails and a non-slip platform. Selo is for materials only and is not approved for carrying people.")),
      B("qa", q="How is Selo installed and set up?", a=P("[Add set-up steps from the operating manual. Assembly, power supply and positioning.]")),
      B("qa", q="What maintenance does Selo need?", a=P("Follow the maintenance and safety instructions in the operating manual. [Add inspection intervals for the cable, brake and limit switches from the manual.]")),
      B("qa", q="How long does delivery take?", a=P("[Add your confirmed delivery times and carrier.]")),
      B("qa", q="Is there a warranty?", a=P("[Confirm warranty terms with your supplier. The supplier listing states 2 years on electrical and load-bearing components.]")),
      B("qa", q="Can I return Selo?", a=P("[Summarise your refund policy. The full policy is linked in the footer.]")),
  ])),

  ("cta", sec("ind-final-cta", {"scheme": "ink", "accent": SELO_ACCENT,
      "eyebrow": "Selo", "heading": "Lift higher. Work smarter.",
      "text": P("Up to 500 kg to 6 metres, by remote control, with safety features built in."),
      "checks": "Up to 500 kg load capacity\nUp to 6 m lifting height\nAutomatic top and bottom limit stop",
      "mode": "scroll", "btn_label": "Choose your package", "small": ""})),

  ("related", sec("ind-recommendations", {"scheme": "paper", "show_related": True, "heading_related": "Complete your equipment", "limit": 3, "show_recent": True, "heading_recent": "Recently viewed"})),
])

# ===================================================================== ABRELUNE
abr = tmpl([
  ("main", sec("ind-main-product", {
      "accent": ABR_ACCENT, "show_breadcrumbs": True, "media_badge": "",
      "eyebrow": "Electric compact transporter",
      "headline": "Move firewood, tools and building materials without straining.",
      "short_desc": P("Abrelune is a compact electric transporter for property maintenance, garden and outdoor work. It carries up to 450 kg on a spacious platform, is driven by a brushless 1000 W electric motor and handles grass, gravel and uneven ground."),
      "tiers_heading": "Choose your package", "show_buy_now": True, "show_dynamic_checkout": True,
      "stock_detail": "", "show_details": True, "shipping_text": SHIP_TEXT,
      "sticky": True, "sticky_mobile_scroll": False}, [
      B("highlight", icon="motor", text="Brushless 1000 W motor"),
      B("highlight", icon="weight", text="Up to 450 kg load"),
      B("highlight", icon="route", text="Approx. 24–27 km range*"),
      B("highlight", icon="width", text="79 cm wide"),
      *TIERS, *TRUST])),

  ("figures", sec("ind-stat-band", {"scheme": "accent", "accent": ABR_ACCENT, "heading": "",
      "note": "* Range depends on load, surface, gradient and battery condition."}, [
      B("stat", value="1000", unit="W", label="Brushless electric motor"),
      B("stat", value="450", unit="kg", label="Maximum load"),
      B("stat", value="24–27", unit="km", label="Range per charge*"),
      B("stat", value="79", unit="cm", label="Compact width"),
  ])),

  ("benefits", sec("ind-feature-grid", {"scheme": "sand", "accent": ABR_ACCENT, "style": "minimal", "columns": 3, "row_mobile": True, "center": True, "tight": False,
      "eyebrow": "Main benefits", "heading": "Load more. Carry less.", "text": "", "note": ""}, [
      B("feature", icon="bolt", title="Powered transportation", text=P("Electric drive does the pushing for you, round the property and the work site.")),
      B("feature", icon="weight", title="High carrying capacity", text=P("A stated maximum load of 450 kg, so firewood, stone, soil and tools can go in one trip.")),
      B("feature", icon="motor", title="Brushless motor", text=P("A 1000 W brushless electric motor with two-wheel drive.")),
      B("feature", icon="battery", title="Battery-powered convenience", text=P("A sealed 48 V battery system with a battery indicator that always shows the charge left.")),
      B("feature", icon="gauge", title="Manoeuvrability", text=P("Stepless twist throttle, two speed modes and reverse for precise driving in tight spaces.")),
      B("feature", icon="box", title="Fold-down side walls", text=P("Fold the side walls down or remove them completely to load from any side.")),
  ])),

  ("motor", sec("ind-image-text", {"scheme": "dark", "accent": "#9cc25a", "reverse": False, "wide_media": True, "ratio": "landscape",
      "placeholder_label": "Motor and drive close-up", "badge_value": "1000 W", "badge_label": "Brushless",
      "eyebrow": "Motor performance", "heading": "Full control on every surface",
      "text": P("Two-wheel drive gives traction on grass, gravel, paths and uneven ground. With the stepless twist throttle, two speed modes and reverse, you can drive slowly and precisely in tight spaces, or faster, up to about 24 km/h, on open stretches."),
      "checks": "Brushless 1000 W electric motor\nTwo-wheel drive\nStepless twist-grip throttle\nTwo speed modes, forward and reverse\nLED headlight and horn",
      "btn_label": "", "btn_link": "", "btn_style": "accent", "note": "", "diagram": "none"})),

  ("battery", sec("ind-image-text", {"scheme": "sand", "accent": ABR_ACCENT, "reverse": True, "wide_media": False, "ratio": "square",
      "placeholder_label": "Battery compartment opened for charging", "badge_value": "4–5 h", "badge_label": "Full charge",
      "eyebrow": "Battery technology", "heading": "Power and range for the whole working day",
      "text": P("The brushless motor is powered by a sealed 48 V lead-acid battery system. One charge gives about 24–27 km, depending on load and surface, enough for many work sessions around the property. A full charge takes about 4–5 hours."),
      "checks": "Sealed 48 V lead-acid battery system\nApprox. 24–27 km per charge*\nApprox. 4–5 hours charging time\nBattery indicator shows remaining charge\nBattery compartment for charging and maintenance",
      "btn_label": "", "btn_link": "", "btn_style": "dark",
      "note": "* Depends on load, surface, gradient and battery condition.", "diagram": "none"})),

  ("capacity", sec("ind-tiles", {"scheme": "paper", "accent": ABR_ACCENT, "columns": 5, "wide": False, "center": True,
      "eyebrow": "Carrying capacity", "heading": "Up to 450 kg, one trip",
      "text": P("The cargo platform sits at about 50 cm, a comfortable working height for loading.")}, [
      B("tile", icon="wood", title="Firewood", text=""),
      B("tile", icon="brick", title="Stone", text=""),
      B("tile", icon="layers", title="Building materials", text=""),
      B("tile", icon="leaf", title="Garden supplies & waste", text=""),
      B("tile", icon="tools", title="Tools & equipment", text=""),
  ])),

  ("manoeuvre", sec("ind-image-text", {"scheme": "paper", "accent": ABR_ACCENT, "reverse": False, "wide_media": False, "ratio": "square",
      "placeholder_label": "", "badge_value": "", "badge_label": "",
      "eyebrow": "Manoeuvrability", "heading": "Compact where it counts",
      "text": P("At about 165 cm long and 79 cm wide, Abrelune fits through gates, between flower beds and along narrow paths where a tractor or larger work vehicle won't fit. We recommend a passage at least 84 cm wide."),
      "checks": "79 cm overall width\nFits through passages from 84 cm\nApprox. 165 cm long",
      "btn_label": "", "btn_link": "", "btn_style": "dark", "note": "Schematic illustration. Not to scale.",
      "diagram": "gate", "d_v1": "79 cm", "d_l1": "vehicle width", "d_v2": "84 cm", "d_l2": "min. passage", "d_caption": ""})),

  ("specs", sec("ind-specs", {"scheme": "sand", "accent": ABR_ACCENT, "use_metafield": True,
      "eyebrow": "Technical data", "heading": "Abrelune specifications", "text": "", "visible_rows": 9,
      "note": "* Depends on load, surface, gradient and conditions of use.",
      "media": "transporter", "d_v1": "≈ 165 cm", "d_l1": "length", "d_v2": "≈ 50 cm", "d_l2": "platform height", "d_v3": "450 kg", "d_l3": "max. load", "d_v4": "150 × 80 cm", "d_l4": "Cargo platform", "d_caption": "Schematic illustration. Not to scale."}, [
      B("row", label="Model", value="Abrelune"),
      B("row", label="Motor", value="Brushless electric motor, 1000 W"),
      B("row", label="Drive", value="Two-wheel drive"),
      B("row", label="Battery", value="Sealed 48 V lead-acid battery"),
      B("row", label="Range", value="Approx. 24–27 km*"),
      B("row", label="Charging time", value="Approx. 4–5 hours"),
      B("row", label="Top speed", value="Approx. 24 km/h"),
      B("row", label="Maximum load", value="Up to 450 kg"),
      B("row", label="Cargo platform", value="150 × 80 cm"),
      B("row", label="Platform height", value="Approx. 50 cm"),
      B("row", label="Length × width", value="Approx. 165 × 79 cm"),
      B("row", label="Recommended passage width", value="At least 84 cm"),
      B("row", label="Weight", value="Approx. 150 kg"),
      B("row", label="Controls", value="Stepless twist-grip throttle, 2 speed modes, forward/reverse"),
      B("row", label="Equipment", value="Battery indicator, LED headlight, horn"),
      B("row", label="Side walls", value="Folding and removable"),
      B("row", label="Construction", value="Steel"),
  ])),

  ("included", sec("ind-included", {"scheme": "paper", "accent": ABR_ACCENT, "eyebrow": "In the box", "heading": "What's included", "text": "",
      "note": "The supplier lists a 110 V charger. [Confirm the charger voltage and plug type for your market before selling.]"}, [
      B("item", icon="truck", qty="1×", title="Abrelune electric transporter", text=""),
      B("item", icon="battery", qty="1×", title="48 V battery system", text=""),
      B("item", icon="plug", qty="1×", title="Charger", text="110 V per supplier listing"),
      B("item", icon="box", qty="1×", title="User manual", text="Including safety instructions"),
  ])),

  ("compare", sec("ind-comparison", {"mode": "versus", "scheme": "sand", "accent": ABR_ACCENT,
      "eyebrow": "Comparison", "heading": "Abrelune vs. manual transport", "text": "",
      "label_col": "", "col_a": "Wheelbarrow / hand cart", "col_b": "Abrelune", "note": ""}, [
      B("row", label="Load per trip", a_mark="none", a="What you can push", b_mark="yes", b="Up to 450 kg"),
      B("row", label="Drive", a_mark="no", a="Muscle power", b_mark="yes", b="1000 W brushless electric motor"),
      B("row", label="Grass, gravel, uneven ground", a_mark="none", a="Hard going under load", b_mark="yes", b="Two-wheel drive for traction"),
      B("row", label="Loading and unloading", a_mark="none", a="Lift or tip by hand", b_mark="yes", b="Fold-down, removable side walls"),
      B("row", label="Reversing", a_mark="none", a="By hand", b_mark="yes", b="Forward and reverse gear"),
      B("row", label="Narrow passages", a_mark="yes", a="Yes", b_mark="yes", b="79 cm wide; passages from 84 cm"),
  ])),

  ("reviews", sec("ind-reviews", {"scheme": "paper", "accent": ABR_ACCENT, "eyebrow": "Customer reviews", "heading": "What customers say"})),

  ("faq", sec("ind-faq", {"scheme": "paper", "accent": ABR_ACCENT, "layout": "stacked", "single": True, "open_first": True, "schema": True,
      "eyebrow": "FAQ", "heading": "Questions about Abrelune", "text": "", "btn_label": "", "btn_link": ""}, [
      B("qa", q="How much can Abrelune carry?", a=P("Up to 450 kg. On steep slopes and soft ground, reduce the load for safe driving.")),
      B("qa", q="What motor does it have?", a=P("A brushless 1000 W electric motor with two-wheel drive.")),
      B("qa", q="What battery does it use?", a=P("A sealed 48 V lead-acid battery system with a battery indicator.")),
      B("qa", q="How far can I drive on one charge?", a=P("About 24–27 km, depending on load, surface, gradient and battery condition.")),
      B("qa", q="How long does charging take?", a=P("A full charge takes about 4–5 hours.")),
      B("qa", q="What terrain can it handle?", a=P("Two-wheel drive gives traction on grass, gravel, paths and uneven ground. Reduce the load on steep slopes and soft ground.")),
      B("qa", q="Will it fit through my gate?", a=P("Abrelune is about 79 cm wide. We recommend a passage at least 84 cm wide.")),
      B("qa", q="Can I drive it on public roads?", a=P("Abrelune is intended for private land such as plots, farms and work areas. With a top speed of about 24 km/h, vehicle classification rules may apply. Always check local rules before driving outside private property.")),
      B("qa", q="What maintenance does it need?", a=P("Follow the user manual and safety instructions. [Add battery care and tyre and brake check guidance from the manual.]")),
      B("qa", q="What accessories are included?", a=P("The transporter, a 48 V battery system, a charger and the user manual with safety instructions.")),
      B("qa", q="How long does delivery take?", a=P("[Add your confirmed delivery times. This is a bulky item of approx. 150 kg.]")),
      B("qa", q="Is there a warranty?", a=P("[Confirm warranty terms with your supplier.]")),
  ])),

  ("cta", sec("ind-final-cta", {"scheme": "sand", "accent": ABR_ACCENT,
      "eyebrow": "Abrelune", "heading": "Heavy becomes light",
      "text": P("1000 W brushless power, up to 450 kg per trip, and a compact 79 cm body that goes where larger vehicles can't."),
      "checks": "Up to 450 kg load capacity\nApprox. 24–27 km per charge*\nFolding and removable side walls",
      "mode": "scroll", "btn_label": "Choose your package", "small": "* Depends on load, surface, gradient and battery condition."})),

  ("related", sec("ind-recommendations", {"scheme": "paper", "show_related": True, "heading_related": "Complete your equipment", "limit": 3, "show_recent": True, "heading_recent": "Recently viewed"})),
])

# ===================================================================== HOME
home = tmpl([
  ("hero", sec("ind-hero", {"shade": 70, "height": 85, "height_mobile": 85,
      "eyebrow": "Professional lifting & transport equipment",
      "heading": "Lift higher. <em>Carry more.</em> Work smarter.",
      "text": P("Two electric machines that take the heavy lifting out of everyday work: Selo for raising material to height, Abrelune for moving heavy loads across the ground."),
      "btn1_label": "Shop Selo", "btn1_link": "shopify://products/selo",
      "btn2_label": "Shop Abrelune", "btn2_link": "shopify://products/abrelune"}, [
      B("stat", value="500 kg", label="Selo lifting capacity"),
      B("stat", value="6 m", label="Selo lifting height"),
      B("stat", value="450 kg", label="Abrelune load capacity"),
  ])),

  ("bf", sec("ind-bf-banner", {"show_upcoming": True, "kicker": "Limited-time campaign",
      "heading": "BLACK FRIDAY —", "heading_2": "BIGGER SAVINGS, SMARTER WORK",
      "text": P("Discover powerful equipment at exclusive Black Friday prices. Upgrade the way you work and save more when you purchase multiple units."),
      "show_tiers": True, "terms": "Discounts are applied automatically at checkout during the campaign and cannot be combined with other offers.",
      "btn1_label": "Shop Selo", "btn1_link": "shopify://products/selo",
      "btn2_label": "Shop Abrelune", "btn2_link": "shopify://products/abrelune"})),

  ("intro", sec("ind-feature-grid", {"scheme": "paper", "style": "minimal", "columns": 3, "row_mobile": True, "center": False, "tight": False,
      "eyebrow": "Our range", "heading": "Two machines. One goal: less strain, more work done.",
      "text": P("We focus on equipment that takes heavy loads off people: vertical lifting at the scaffold and powered transport around the property."), "note": ""}, [
      B("feature", icon="height", title="Vertical lifting", text=P("Selo raises up to 500 kg to as high as 6 m, by remote control.")),
      B("feature", icon="truck", title="Ground transport", text=P("Abrelune carries up to 450 kg on grass, gravel and uneven ground.")),
      B("feature", icon="shield", title="Built for daily use", text=P("Steel construction and practical safety features on both machines.")),
  ])),

  ("selo", sec("ind-featured-product", {"fallback_handle": "selo", "anchor": "selo", "scheme": "dark", "accent": SELO_ACCENT, "reverse": False,
      "eyebrow": "Scaffold material lift", "heading": "Selo",
      "text": P("Professional lifting power for the job site. Move materials up safely and with less effort, right at the scaffold, controlled by remote."),
      "badge": "", "btn_label": "Discover Selo", "show_atc": True}, [
      B("spec", value="500 kg", label="Load capacity"),
      B("spec", value="6 m", label="Lifting height"),
      B("spec", value="Remote", label="Control"),
      B("spec", value="360°", label="Swivel castors"),
  ])),

  ("abrelune", sec("ind-featured-product", {"fallback_handle": "abrelune", "anchor": "abrelune", "scheme": "sand", "accent": ABR_ACCENT, "reverse": True,
      "eyebrow": "Electric compact transporter", "heading": "Abrelune",
      "text": P("Powerful transport, high carrying capacity and the manoeuvrability to go where larger vehicles can't."),
      "badge": "", "btn_label": "Discover Abrelune", "show_atc": True}, [
      B("spec", value="1000 W", label="Brushless motor"),
      B("spec", value="450 kg", label="Max. load"),
      B("spec", value="24–27 km", label="Range*"),
      B("spec", value="79 cm", label="Width"),
  ])),

  ("benefits", sec("ind-stat-band", {"scheme": "ink", "heading": "Main benefits",
      "note": "* Abrelune range depends on load, surface, gradient and battery condition."}, [
      B("stat", value="500", unit="kg", label="Lifted to height with Selo"),
      B("stat", value="6", unit="m", label="Maximum Selo lifting height"),
      B("stat", value="450", unit="kg", label="Carried per trip with Abrelune"),
      B("stat", value="24–27", unit="km", label="Abrelune range per charge*"),
  ])),

  ("compare", sec("ind-comparison", {"mode": "products", "scheme": "paper",
      "eyebrow": "Product comparison", "heading": "Which machine fits your work?",
      "text": P("Selo moves material up. Abrelune moves material along."), "label_col": "", "col_a": "", "col_b": "", "note": ""}, [
      B("row", label="Main task", a="Lifting material to height", b="Transporting loads on the ground"),
      B("row", label="Capacity", a="Up to 500 kg", b="Up to 450 kg"),
      B("row", label="Reach", a="Up to 6 m lifting height", b="Approx. 24–27 km per charge"),
      B("row", label="Drive", a="High-torque electric motor", b="Brushless 1000 W, two-wheel drive"),
      B("row", label="Control", a="Ergonomic remote control", b="Twist throttle, 2 speeds, reverse"),
      B("row", label="Mobility", a="360° swivel castors", b="79 cm wide, passages from 84 cm"),
      B("row", label="Ideal for", a="Scaffolds, renovation, installations", b="Firewood, stone, garden, construction"),
  ])),

  ("why", sec("ind-feature-grid", {"scheme": "sand", "style": "numbered", "columns": 4, "row_mobile": False, "center": True, "tight": False,
      "eyebrow": "Why choose our equipment", "heading": "Made to take the load", "text": "", "note": ""}, [
      B("feature", icon="layers", title="Steel construction", text=P("Reinforced steel frames for stability in daily use.")),
      B("feature", icon="shield", title="Safety features", text=P("Limit stops, brakes and guard rails on Selo; a battery indicator, LED headlight and horn on Abrelune.")),
      B("feature", icon="remote", title="Easy control", text=P("Remote-controlled lifting and stepless twist-throttle driving.")),
      B("feature", icon="lock", title="Secure checkout", text=P("Encrypted payment through Shopify Checkout.")),
  ])),

  ("applications", sec("ind-tiles", {"scheme": "paper", "columns": 4, "wide": False, "center": False,
      "eyebrow": "Real-world applications", "heading": "Where our machines work", "text": ""}, [
      B("tile", icon="brick", title="Construction & renovation", text="Selo lifts material to the scaffold", link="shopify://products/selo"),
      B("tile", icon="wrench", title="Installation & maintenance", text="Selo for technical and industrial work at height", link="shopify://products/selo"),
      B("tile", icon="wood", title="Firewood & stone", text="Abrelune moves heavy loads in one trip", link="shopify://products/abrelune"),
      B("tile", icon="leaf", title="Property & garden", text="Abrelune on grass, gravel and narrow paths", link="shopify://products/abrelune"),
  ])),

  ("quality", sec("ind-image-text", {"scheme": "dark", "reverse": True, "wide_media": True, "ratio": "landscape",
      "placeholder_label": "Workshop or detail photography", "badge_value": "", "badge_label": "",
      "eyebrow": "Quality & reliability", "heading": "Robust where it matters",
      "text": P("Selo uses a reinforced steel frame and a high-strength galvanised steel cable for long service life. Abrelune is built from steel, with folding and removable side walls."),
      "checks": "Reinforced steel construction\nGalvanised steel lifting cable (Selo)\nSealed 48 V battery system (Abrelune)",
      "btn_label": "", "btn_link": "", "btn_style": "accent", "note": "", "diagram": "none"})),

  ("reviews", sec("ind-reviews", {"scheme": "paper", "eyebrow": "Customer reviews", "heading": "What customers say"})),

  ("faq", sec("ind-faq", {"scheme": "sand", "layout": "aside", "single": True, "open_first": False, "schema": True,
      "eyebrow": "FAQ", "heading": "Frequently asked questions", "text": "", "btn_label": "", "btn_link": ""}, [
      B("qa", q="Which product do I need?", a=P("Choose Selo to raise materials to height, up to 500 kg and up to 6 m. Choose Abrelune to move heavy loads across the ground, up to 450 kg.")),
      B("qa", q="Can Selo carry people?", a=P("No. Selo is for transporting materials only and is not approved for carrying people.")),
      B("qa", q="How do multi-unit savings work?", a=P("Choose a Double or Triple pack on the product page. The discount is applied automatically at checkout, and your cart shows the final price before you pay.")),
      B("qa", q="How long does delivery take?", a=P("[Add your confirmed delivery times.]")),
      B("qa", q="What is your return policy?", a=P("[Summarise your refund policy. The full policy is linked in the footer.]")),
      B("qa", q="Which payment methods can I use?", a=P("All payment methods enabled in our checkout are shown in the footer.")),
  ])),

  ("newsletter", sec("ind-newsletter", {"scheme": "dark", "eyebrow": "Newsletter", "heading": "Product news and campaign alerts",
      "text": P("Be the first to hear about new equipment and seasonal offers."), "disclaimer": "You can unsubscribe at any time."})),
])

write("product.selo.json", selo)
write("product.abrelune.json", abr)
write("index.json", home)
