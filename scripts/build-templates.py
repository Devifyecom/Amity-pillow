#!/usr/bin/env python3
"""Generates templates/index.json, product.selo.json and product.abrelune.json.

Every product fact comes from the supplier listings researched on 2026-11-03
(see docs/PRODUCT-DATA.md). Store promises (delivery time, warranty length, return window)
are not stated as facts: copy points to checkout and to the store's published policies.
Re-run after editing: python3 scripts/build-templates.py
"""
import json, os, itertools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_c = itertools.count(1)

def sec(type_, settings=None, blocks=None):
    s = {"type": type_, "settings": settings or {}}
    if blocks:
        s["blocks"], s["block_order"] = {}, []
        for b in blocks:
            bid = f"{b['type']}_{next(_c)}"
            s["blocks"][bid] = {"type": b["type"], "settings": b.get("settings", {})}
            s["block_order"].append(bid)
    return s

def tmpl(sections):
    d = {"sections": {}, "order": []}
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

SELO = "#d9531e"     # safety orange, matches the Selo frame
ABR = "#4f6b2a"      # olive, matches the Abrelune body
ABR_LIGHT = "#9cc25a"

TIERS = [
    B("tier", label="Single unit", qty=1, pct=0, badge="", preselect=False),
    B("tier", label="Double pack", qty=2, pct=10, badge="Most popular", preselect=True),
    B("tier", label="Triple pack", qty=3, pct=15, badge="Best value", preselect=False),
]
TRUST = [
    B("trust", icon="lock", title="Secure checkout", text="Encrypted payment via Shopify"),
    B("trust", icon="truck", title="Delivery", text="Options and costs shown at checkout"),
    B("trust", icon="return", title="Returns", text="Under our published refund policy"),
    B("trust", icon="support", title="Real support", text="Questions before or after you buy"),
]
SHIP_TEXT = P(
    "Delivery options, costs and estimated delivery times are shown at checkout before you pay.",
    'Returns are handled under our <a href="/policies/refund-policy">refund policy</a>. Need help with an order? <a href="/pages/contact">Contact our team</a>.',
)
FAQ_DELIVERY = P("Available delivery options, costs and estimated delivery times are shown at checkout before you pay. You'll get a confirmation email as soon as your order ships.")
FAQ_RETURNS = P('Returns follow our <a href="/policies/refund-policy">refund policy</a>. Contact our team first and we\'ll guide you through the process.')
FAQ_WARRANTY = P('If anything isn\'t right, contact our support team with your order number and we\'ll help. The terms that apply to your purchase are set out in our <a href="/policies/terms-of-service">terms of service</a>.')

# =============================================================================== SELO
selo = tmpl([
  ("main", sec("ind-main-product", {
      "accent": SELO, "show_breadcrumbs": True, "media_badge": "Up to 6 m",
      "eyebrow": "Scaffold material lift",
      "headline": "Take the heavy lifting off your team, all the way up to 6 metres.",
      "short_desc": P("Stop hauling material up ladders. Selo raises up to <strong>500 kg</strong> to a working height of up to <strong>6 metres</strong> at the touch of a remote, then stops automatically at the top. Your team stays on the scaffold, working, instead of carrying."),
      "tiers_heading": "Choose your package",
      "show_buy_now": True, "show_dynamic_checkout": True, "stock_detail": "",
      "show_details": True, "shipping_text": SHIP_TEXT,
      "sticky": True, "sticky_mobile_scroll": False}, [
      B("highlight", icon="weight", text="Lifts up to 500 kg"),
      B("highlight", icon="height", text="Up to 6 m lifting height"),
      B("highlight", icon="remote", text="Remote-control operation"),
      B("highlight", icon="shield", text="Auto stop at top and bottom"),
      *TIERS, *TRUST])),

  ("figures", sec("ind-stat-band", {"scheme": "ink", "accent": SELO, "heading": "Built to lift"}, [
      B("stat", value="500", unit="kg", label="Load capacity per lift"),
      B("stat", value="6", unit="m", label="Maximum lifting height"),
      B("stat", value="360", unit="°", label="Swivel castors"),
      B("stat", value="2", unit="×", label="Automatic limit stops"),
  ])),

  ("problem", sec("ind-image-text", {"scheme": "paper", "accent": SELO, "reverse": False, "wide_media": True, "ratio": "adapt",
      "placeholder_label": "Photo: Selo next to a scaffold, loaded with material",
      "badge_value": "500 kg", "badge_label": "In one lift",
      "eyebrow": "The problem with height",
      "heading": "Every trip up the ladder costs time and energy",
      "text": P("Plaster, tiles, tools, paint: on most sites, it all goes up by hand, one load and one climb at a time. It's slow, it's exhausting, and it pulls skilled people away from the work they're there to do.",
                "Selo changes the routine. Load the platform on the ground, press a button, and the material arrives at working height, up to 500 kg in a single lift."),
      "checks": "No more carrying material up ladders and stairs\nFewer trips, less strain on backs and shoulders\nYour team stays productive at height",
      "btn_label": "Choose your package", "btn_link": "#buy", "btn_style": "accent", "diagram": "none"})),

  ("how", sec("ind-feature-grid", {"scheme": "sand", "accent": SELO, "style": "numbered", "columns": 3, "row_mobile": False, "center": True,
      "eyebrow": "How it works", "heading": "Load. Lift. Get to work."}, [
      B("feature", icon="box", title="Load at ground level", text=P("Place material on the non-slip platform and spread the load evenly, up to 500 kg.")),
      B("feature", icon="remote", title="Lift by remote", text=P("Raise the platform smoothly from a safe distance using the ergonomic remote control.")),
      B("feature", icon="shield", title="Automatic stop", text=P("The limit stop halts the lift by itself at the top and bottom positions. Unload and carry on working.")),
  ])),

  ("lift", sec("ind-image-text", {"scheme": "paper", "accent": SELO, "reverse": True, "wide_media": False, "ratio": "adapt",
      "eyebrow": "Powerful electric lifting drive",
      "heading": "Smooth, controlled lifting, every time",
      "text": P("A high-torque electric motor raises and lowers the platform evenly and precisely, with no jerking and no guesswork. A high-strength galvanised steel cable carries the load, and a precise braking system holds it securely in position."),
      "checks": "High-torque electric motor\nHigh-strength galvanised steel cable\nPrecise braking system holds the load",
      "btn_style": "dark", "note": "Schematic illustration. Not to scale.",
      "diagram": "lift", "d_v1": "6 m", "d_l1": "max. lifting height", "d_v2": "500 kg", "d_l2": "max. load",
      "d_v3": "360°", "d_l3": "castors", "d_v4": "Remote", "d_l4": "control"})),

  ("features", sec("ind-feature-grid", {"scheme": "paper", "accent": SELO, "style": "cards", "columns": 4, "row_mobile": True, "center": True,
      "eyebrow": "Feature highlights", "heading": "Engineered for the job site",
      "text": P("Every detail of Selo is designed for daily professional use.")}, [
      B("feature", icon="motor", title="Electric lifting drive", text=P("High torque for even, controlled lifting and lowering.")),
      B("feature", icon="remote", title="Ergonomic remote", text=P("Control every lift from a safe distance.")),
      B("feature", icon="shield", title="Automatic limit stop", text=P("Stops by itself at the upper and lower end positions.")),
      B("feature", icon="brake", title="Precise brake", text=P("Holds the load securely at any height.")),
      B("feature", icon="cable", title="Galvanised steel cable", text=P("High-strength cable built for a long service life.")),
      B("feature", icon="layers", title="Reinforced steel frame", text=P("Stable and rigid, day after day.")),
      B("feature", icon="grip", title="Non-slip platform", text=P("Helps keep the load in place while lifting.")),
      B("feature", icon="rotate", title="360° swivel castors", text=P("Roll it into position quickly on site.")),
  ])),

  ("action", sec("ind-tiles", {"scheme": "dark", "accent": SELO, "columns": 4, "square": True,
      "eyebrow": "Selo in action", "heading": "Wherever work happens at height",
      "text": P("From renovation to industrial maintenance, Selo gets the material where it's needed.")}, [
      B("tile", icon="brick", title="Construction sites", text="Assembly and construction work at scaffold height"),
      B("tile", icon="tools", title="Painting & renovation", text="Paint, plaster and tools delivered to the scaffold"),
      B("tile", icon="bolt", title="Technical installations", text="Electrical and mechanical systems at height"),
      B("tile", icon="wrench", title="Industrial maintenance", text="Servicing and repair work above ground"),
  ])),

  ("safety", sec("ind-image-text", {"scheme": "ink", "accent": SELO, "reverse": False, "wide_media": True, "ratio": "adapt",
      "placeholder_label": "Close-up: platform, guard rails, limit switch, remote",
      "badge_value": "2×", "badge_label": "Auto limit stops",
      "eyebrow": "Construction & safety",
      "heading": "Safety built into every lift",
      "text": P("Selo is engineered for professional use, with several safety features working together for a controlled lift. Its reinforced steel frame and galvanised steel cable stay stable and dependable, even under daily use."),
      "checks": "Precise braking system holds the load securely\nAutomatic limit stop at the upper and lower positions\nReinforced guard rails keep the load in place\nNon-slip platform helps prevent sliding",
      "btn_style": "accent",
      "note": "Selo is designed for lifting materials only and is not approved for carrying people. Always observe the maximum load and the safety instructions in the operating manual.",
      "diagram": "none"})),

  ("compare", sec("ind-comparison", {"mode": "versus", "scheme": "sand", "accent": SELO,
      "eyebrow": "Traditional method vs. Selo", "heading": "The smarter way up",
      "text": P("Compare carrying material by hand with lifting it on Selo."),
      "col_a": "Carrying by hand", "col_b": "With Selo"}, [
      B("row", label="Getting material to height", a_mark="no", a="Up ladders or stairs", b_mark="yes", b="Lifted electrically, up to 6 m"),
      B("row", label="Load per trip", a_mark="no", a="What one person can carry", b_mark="yes", b="Up to 500 kg"),
      B("row", label="Effort", a_mark="no", a="Physical strain on every trip", b_mark="yes", b="One button on the remote"),
      B("row", label="Stopping at height", a_mark="none", a="—", b_mark="yes", b="Automatic limit stop, top and bottom"),
      B("row", label="Moving between spots", a_mark="none", a="—", b_mark="yes", b="360° swivel castors"),
  ])),

  ("specs", sec("ind-specs", {"scheme": "paper", "accent": SELO, "use_metafield": True,
      "eyebrow": "Technical data", "heading": "Selo specifications", "visible_rows": 8,
      "note": "For lifting materials only. Not approved for carrying people.",
      "media": "lift", "d_v1": "6 m", "d_l1": "max. lifting height", "d_v2": "500 kg", "d_l2": "max. load",
      "d_caption": "Schematic illustration. Not to scale."}, [
      B("row", label="Model", value="Selo"),
      B("row", label="Type", value="Scaffold material lift"),
      B("row", label="Load capacity", value="Up to 500 kg"),
      B("row", label="Maximum lifting height", value="Up to 6 m"),
      B("row", label="Motor", value="Professional high-torque electric motor"),
      B("row", label="Lifting cable", value="High-strength galvanised steel cable"),
      B("row", label="Frame", value="Reinforced steel construction"),
      B("row", label="Control", value="Ergonomic remote control"),
      B("row", label="Mobility", value="360° swivel castors"),
      B("row", label="Safety", value="Braking system, automatic limit stop at top and bottom, reinforced guard rails, non-slip platform"),
      B("row", label="Intended use", value="Materials only. Not approved for carrying people."),
  ])),

  ("included", sec("ind-included", {"scheme": "sand", "accent": SELO, "eyebrow": "In the box", "heading": "What's included",
      "text": P("Everything you need to start lifting.")}, [
      B("item", icon="layers", qty="1×", title="Selo material lift", text="With electric lifting drive"),
      B("item", icon="remote", qty="1×", title="Remote control", text="Ergonomic hand-held control"),
      B("item", icon="box", qty="1×", title="Operating manual", text="Including safety instructions"),
  ])),

  ("reviews", sec("ind-reviews", {"scheme": "paper", "accent": SELO, "eyebrow": "Customer reviews", "heading": "What professionals say"})),

  ("faq", sec("ind-faq", {"scheme": "sand", "accent": SELO, "layout": "aside", "single": True, "open_first": True, "schema": True,
      "eyebrow": "FAQ", "heading": "Questions about Selo",
      "text": P("Can't find what you're looking for? Our team is happy to help."),
      "btn_label": "Contact us", "btn_link": "shopify://pages/contact"}, [
      B("qa", q="How much weight can Selo lift?", a=P("Up to 500 kg per lift. Spread the load evenly across the platform for a stable, controlled lift.")),
      B("qa", q="How high can Selo lift?", a=P("Up to 6 metres, which suits common scaffold heights.")),
      B("qa", q="How is the lift operated?", a=P("With an ergonomic remote control, so you can raise and lower the platform from a safe distance.")),
      B("qa", q="What happens when it reaches the top?", a=P("The automatic limit stop halts the lift by itself at the upper and lower end positions, so there's no over-travel.")),
      B("qa", q="Which safety features does Selo have?", a=P("A precise braking system, automatic limit stops at the top and bottom, reinforced guard rails and a non-slip platform. Selo is for lifting materials only and is not approved for carrying people.")),
      B("qa", q="How do I set Selo up?", a=P("Follow the set-up steps and safety instructions in the operating manual supplied with Selo. Always position the lift on firm, level ground before lifting.")),
      B("qa", q="What maintenance does Selo need?", a=P("Inspect the steel cable, brake and limit stops regularly as described in the operating manual, and keep the platform clean and free of debris.")),
      B("qa", q="How long does delivery take?", a=FAQ_DELIVERY),
      B("qa", q="Is Selo covered if something goes wrong?", a=FAQ_WARRANTY),
      B("qa", q="Can I return Selo?", a=FAQ_RETURNS),
  ])),

  ("cta", sec("ind-final-cta", {"scheme": "ink", "accent": SELO,
      "eyebrow": "Selo scaffold material lift", "heading": "Lift higher. Work smarter.",
      "text": P("Up to 500 kg to 6 metres at the push of a button, with safety built into every lift. Save more when you equip your team with two or three units."),
      "checks": "Up to 500 kg load capacity\nUp to 6 m lifting height\nAutomatic top and bottom limit stop\nRemote-control operation",
      "mode": "scroll", "btn_label": "Choose your package", "small": "Multi-unit savings are applied automatically at checkout."})),

  ("related", sec("ind-recommendations", {"scheme": "paper", "show_related": True, "heading_related": "Complete your equipment", "limit": 3, "show_recent": True, "heading_recent": "Recently viewed"})),
])

# =========================================================================== ABRELUNE
abr = tmpl([
  ("main", sec("ind-main-product", {
      "accent": ABR, "show_breadcrumbs": True, "media_badge": "450 kg capacity",
      "eyebrow": "Electric compact transporter",
      "headline": "Heavy loads, carried for you, across grass, gravel and rough ground.",
      "short_desc": P("Firewood, stone, soil, tools: move up to <strong>450 kg</strong> in a single trip without pushing a thing. A brushless <strong>1000 W</strong> motor and two-wheel drive do the work, and a compact <strong>79 cm</strong> body gets through the gates and paths where bigger vehicles can't."),
      "tiers_heading": "Choose your package",
      "show_buy_now": True, "show_dynamic_checkout": True, "stock_detail": "",
      "show_details": True, "shipping_text": SHIP_TEXT,
      "sticky": True, "sticky_mobile_scroll": False}, [
      B("highlight", icon="motor", text="Brushless 1000 W motor"),
      B("highlight", icon="weight", text="Carries up to 450 kg"),
      B("highlight", icon="route", text="Approx. 24–27 km range*"),
      B("highlight", icon="width", text="Just 79 cm wide"),
      *TIERS, *TRUST])),

  ("figures", sec("ind-stat-band", {"scheme": "accent", "accent": ABR,
      "note": "* Range depends on load, surface, gradient and battery condition."}, [
      B("stat", value="1000", unit="W", label="Brushless electric motor"),
      B("stat", value="450", unit="kg", label="Maximum load"),
      B("stat", value="24–27", unit="km", label="Range per charge*"),
      B("stat", value="79", unit="cm", label="Compact width"),
  ])),

  ("benefits", sec("ind-feature-grid", {"scheme": "sand", "accent": ABR, "style": "minimal", "columns": 3, "row_mobile": True, "center": True,
      "eyebrow": "Why Abrelune", "heading": "Load more. Carry less.",
      "text": P("Everything a wheelbarrow does, without the pushing, and with up to 450 kg on board.")}, [
      B("feature", icon="bolt", title="Powered transport", text=P("The electric drive does the pushing, all the way across the property and back.")),
      B("feature", icon="weight", title="High carrying capacity", text=P("Up to 450 kg per trip: firewood, stone, soil and tools in one go.")),
      B("feature", icon="motor", title="Brushless motor", text=P("1000 W of brushless power with two-wheel drive for real traction.")),
      B("feature", icon="battery", title="Battery-powered", text=P("Sealed 48 V battery system, with an indicator that always shows the charge left.")),
      B("feature", icon="gauge", title="Precise manoeuvring", text=P("Stepless twist throttle, two speed modes and reverse for tight spaces.")),
      B("feature", icon="box", title="Fold-down side walls", text=P("Fold them down, or take them off completely, to load and unload from any side.")),
  ])),

  ("how", sec("ind-feature-grid", {"scheme": "paper", "accent": ABR, "style": "numbered", "columns": 3, "row_mobile": False, "center": True,
      "eyebrow": "How it works", "heading": "Load it. Drive it. Drop it off."}, [
      B("feature", icon="box", title="Load the platform", text=P("A spacious 150 × 80 cm cargo platform at a comfortable height of about 50 cm.")),
      B("feature", icon="gauge", title="Drive with the throttle", text=P("Twist to go, choose your speed mode, and reverse when you need to.")),
      B("feature", icon="layers", title="Unload from any side", text=P("Fold down or remove the side walls and unload exactly where you need it.")),
  ])),

  ("motor", sec("ind-image-text", {"scheme": "dark", "accent": ABR_LIGHT, "reverse": False, "wide_media": True, "ratio": "adapt",
      "placeholder_label": "Photo: Abrelune driving across grass or gravel, loaded",
      "badge_value": "1000 W", "badge_label": "Brushless motor",
      "eyebrow": "Motor performance",
      "heading": "Real power on every surface",
      "text": P("Two-wheel drive delivers traction on grass, gravel, paths and uneven ground. Drive slowly and precisely with the stepless twist throttle in tight spots, or switch speed modes and travel at up to about 24 km/h on open stretches."),
      "checks": "Brushless 1000 W electric motor\nTwo-wheel drive for traction\nStepless twist-grip throttle\nTwo speed modes, forward and reverse\nLED headlight and horn",
      "btn_style": "accent", "diagram": "none"})),

  ("battery", sec("ind-image-text", {"scheme": "sand", "accent": ABR, "reverse": True, "wide_media": False, "ratio": "adapt",
      "placeholder_label": "Photo: battery compartment opened for charging",
      "badge_value": "4–5 h", "badge_label": "Full charge",
      "eyebrow": "Battery technology",
      "heading": "Power for the whole working day",
      "text": P("A sealed 48 V lead-acid battery system powers the motor. On one charge you'll cover about 24–27 km, depending on load and surface, which is enough for many work sessions around the property. Plug in overnight, or between jobs, and it's fully charged in about 4–5 hours."),
      "checks": "Sealed 48 V battery system\nApprox. 24–27 km per charge*\nApprox. 4–5 hours to full charge\nBattery indicator shows remaining charge\nAccessible battery compartment",
      "btn_style": "dark", "note": "* Depends on load, surface, gradient and battery condition.", "diagram": "none"})),

  ("capacity", sec("ind-tiles", {"scheme": "paper", "accent": ABR, "columns": 5, "center": True,
      "eyebrow": "Carrying capacity", "heading": "Up to 450 kg. One trip.",
      "text": P("The cargo platform sits at about 50 cm, a comfortable height to load without bending.")}, [
      B("tile", icon="wood", title="Firewood", text="Logs and kindling in bulk"),
      B("tile", icon="brick", title="Stone", text="Paving, rocks and gravel"),
      B("tile", icon="layers", title="Building materials", text="Bags, boards and supplies"),
      B("tile", icon="leaf", title="Garden supplies", text="Soil, compost and garden waste"),
      B("tile", icon="tools", title="Tools & equipment", text="Everything for the job, in one load"),
  ])),

  ("manoeuvre", sec("ind-image-text", {"scheme": "paper", "accent": ABR, "reverse": False, "wide_media": False, "ratio": "adapt",
      "eyebrow": "Manoeuvrability", "heading": "Goes where bigger vehicles can't",
      "text": P("At about 165 cm long and just 79 cm wide, Abrelune slips through garden gates, between flower beds and along narrow paths where a tractor or a larger work vehicle simply won't fit."),
      "checks": "79 cm overall width\nFits through passages from 84 cm\nApprox. 165 cm long\nReverse gear for tight turns",
      "btn_label": "Choose your package", "btn_link": "#buy", "btn_style": "accent",
      "note": "Schematic illustration. Not to scale.",
      "diagram": "gate", "d_v1": "79 cm", "d_l1": "vehicle width", "d_v2": "84 cm", "d_l2": "min. passage"})),

  ("compare", sec("ind-comparison", {"mode": "versus", "scheme": "sand", "accent": ABR,
      "eyebrow": "Comparison", "heading": "Abrelune vs. the wheelbarrow",
      "text": P("Compare manual transport with Abrelune."),
      "col_a": "Wheelbarrow / hand cart", "col_b": "Abrelune"}, [
      B("row", label="Load per trip", a_mark="no", a="Only what you can push", b_mark="yes", b="Up to 450 kg"),
      B("row", label="Power", a_mark="no", a="Your own muscle", b_mark="yes", b="1000 W brushless electric motor"),
      B("row", label="Grass, gravel, uneven ground", a_mark="no", a="Hard going under load", b_mark="yes", b="Two-wheel drive for traction"),
      B("row", label="Loading and unloading", a_mark="none", a="Lift or tip by hand", b_mark="yes", b="Fold-down, removable side walls"),
      B("row", label="Reversing", a_mark="none", a="Pull it back yourself", b_mark="yes", b="Built-in reverse gear"),
      B("row", label="Narrow passages", a_mark="yes", a="Yes", b_mark="yes", b="Yes: 79 cm wide"),
  ])),

  ("specs", sec("ind-specs", {"scheme": "paper", "accent": ABR, "use_metafield": True,
      "eyebrow": "Technical data", "heading": "Abrelune specifications", "visible_rows": 9,
      "note": "* Depends on load, surface, gradient and conditions of use.",
      "media": "transporter", "d_v1": "≈ 165 cm", "d_l1": "length", "d_v2": "≈ 50 cm", "d_l2": "platform height",
      "d_v3": "450 kg", "d_l3": "max. load", "d_v4": "150 × 80 cm", "d_l4": "Cargo platform",
      "d_caption": "Schematic illustration. Not to scale."}, [
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

  ("included", sec("ind-included", {"scheme": "sand", "accent": ABR, "eyebrow": "In the box", "heading": "What's included",
      "text": P("Ready to charge and go.")}, [
      B("item", icon="truck", qty="1×", title="Abrelune transporter", text="Electric compact transporter"),
      B("item", icon="battery", qty="1×", title="48 V battery system", text="Sealed lead-acid"),
      B("item", icon="plug", qty="1×", title="Charger", text="For the 48 V battery system"),
      B("item", icon="box", qty="1×", title="User manual", text="Including safety instructions"),
  ])),

  ("reviews", sec("ind-reviews", {"scheme": "paper", "accent": ABR, "eyebrow": "Customer reviews", "heading": "What owners say"})),

  ("faq", sec("ind-faq", {"scheme": "paper", "accent": ABR, "layout": "stacked", "single": True, "open_first": True, "schema": True,
      "eyebrow": "FAQ", "heading": "Questions about Abrelune",
      "text": P("Everything you need to know before you order."),
      "btn_label": "Contact us", "btn_link": "shopify://pages/contact"}, [
      B("qa", q="How much can Abrelune carry?", a=P("Up to 450 kg. On steep slopes and soft ground, reduce the load for safe driving.")),
      B("qa", q="What motor does it have?", a=P("A brushless 1000 W electric motor with two-wheel drive.")),
      B("qa", q="What battery does it use?", a=P("A sealed 48 V lead-acid battery system, with a battery indicator that always shows the charge left.")),
      B("qa", q="How far can I drive on one charge?", a=P("About 24–27 km, depending on load, surface, gradient and battery condition.")),
      B("qa", q="How long does charging take?", a=P("A full charge takes about 4–5 hours.")),
      B("qa", q="What terrain can it handle?", a=P("Two-wheel drive gives traction on grass, gravel, paths and uneven ground. Reduce the load on steep slopes and soft surfaces.")),
      B("qa", q="Will it fit through my gate?", a=P("Abrelune is about 79 cm wide. We recommend a passage of at least 84 cm.")),
      B("qa", q="Can I drive it on public roads?", a=P("Abrelune is intended for private land such as plots, farms and work areas. With a top speed of about 24 km/h, vehicle classification rules may apply. Always check local regulations before driving outside private property.")),
      B("qa", q="What maintenance does it need?", a=P("Keep the battery charged between uses, check the tyres and controls regularly, and follow the user manual supplied with Abrelune.")),
      B("qa", q="What's included?", a=P("The Abrelune transporter, a 48 V battery system, a charger, and the user manual with safety instructions.")),
      B("qa", q="How long does delivery take?", a=FAQ_DELIVERY),
      B("qa", q="Is Abrelune covered if something goes wrong?", a=FAQ_WARRANTY),
      B("qa", q="Can I return Abrelune?", a=FAQ_RETURNS),
  ])),

  ("cta", sec("ind-final-cta", {"scheme": "sand", "accent": ABR,
      "eyebrow": "Abrelune electric transporter", "heading": "Heavy work. Made light.",
      "text": P("1000 W of brushless power, up to 450 kg per trip, and a compact 79 cm body that goes where larger vehicles can't. Save more when you order two or three."),
      "checks": "Up to 450 kg load capacity\nApprox. 24–27 km per charge*\nFolding, removable side walls\nForward and reverse, two speed modes",
      "mode": "scroll", "btn_label": "Choose your package",
      "small": "* Depends on load, surface, gradient and battery condition. Multi-unit savings are applied automatically at checkout."})),

  ("related", sec("ind-recommendations", {"scheme": "paper", "show_related": True, "heading_related": "Complete your equipment", "limit": 3, "show_recent": True, "heading_recent": "Recently viewed"})),
])

# =============================================================================== HOME
home = tmpl([
  ("hero", sec("ind-hero", {"shade": 70, "height": 85, "height_mobile": 85,
      "eyebrow": "Professional lifting & transport equipment",
      "heading": "Lift higher. <em>Carry more.</em> Work smarter.",
      "text": P("Two electric machines that take the heavy lifting out of everyday work: Selo raises material to height, Abrelune moves heavy loads across the ground."),
      "btn1_label": "Shop Selo", "btn1_link": "shopify://products/selo",
      "btn2_label": "Shop Abrelune", "btn2_link": "shopify://products/abrelune"}, [
      B("stat", value="500 kg", label="Selo lifting capacity"),
      B("stat", value="6 m", label="Selo lifting height"),
      B("stat", value="450 kg", label="Abrelune load capacity"),
  ])),

  ("bf", sec("ind-bf-banner", {"show_upcoming": True, "kicker": "Limited-time campaign",
      "heading": "BLACK FRIDAY —", "heading_2": "BIGGER SAVINGS, SMARTER WORK",
      "text": P("Discover powerful equipment at exclusive Black Friday prices. Upgrade the way you work and save more when you purchase multiple units."),
      "show_tiers": True, "terms": "Discounts are applied automatically at checkout during the campaign and can't be combined with other offers.",
      "btn1_label": "Shop Selo", "btn1_link": "shopify://products/selo",
      "btn2_label": "Shop Abrelune", "btn2_link": "shopify://products/abrelune"})),

  ("intro", sec("ind-feature-grid", {"scheme": "paper", "style": "minimal", "columns": 3, "row_mobile": True,
      "eyebrow": "Our range", "heading": "Two machines. One goal: less strain, more done.",
      "text": P("We focus on equipment that takes heavy loads off people, both vertically at the scaffold and across the ground around your property.")}, [
      B("feature", icon="height", title="Vertical lifting", text=P("Selo raises up to 500 kg to as high as 6 m, by remote control.")),
      B("feature", icon="truck", title="Ground transport", text=P("Abrelune carries up to 450 kg across grass, gravel and uneven ground.")),
      B("feature", icon="shield", title="Built for daily use", text=P("Steel construction and practical safety features on both machines.")),
  ])),

  ("selo", sec("ind-featured-product", {"fallback_handle": "selo", "anchor": "selo", "scheme": "dark", "accent": SELO, "reverse": False,
      "eyebrow": "Scaffold material lift", "heading": "Selo",
      "text": P("Stop hauling material up ladders. Selo lifts up to 500 kg to 6 metres at the push of a button, then stops automatically at the top."),
      "btn_label": "Discover Selo", "show_atc": True}, [
      B("spec", value="500 kg", label="Load capacity"),
      B("spec", value="6 m", label="Lifting height"),
      B("spec", value="Remote", label="Control"),
      B("spec", value="360°", label="Swivel castors"),
  ])),

  ("abrelune", sec("ind-featured-product", {"fallback_handle": "abrelune", "anchor": "abrelune", "scheme": "sand", "accent": ABR, "reverse": True,
      "eyebrow": "Electric compact transporter", "heading": "Abrelune",
      "text": P("Move firewood, stone and tools without pushing a thing. 1000 W of brushless power, up to 450 kg per trip, and a 79 cm body that fits through the gate."),
      "btn_label": "Discover Abrelune", "show_atc": True}, [
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
      "text": P("Selo moves material up. Abrelune moves material along.")}, [
      B("row", label="Main task", a="Lifting material to height", b="Transporting loads on the ground"),
      B("row", label="Capacity", a="Up to 500 kg", b="Up to 450 kg"),
      B("row", label="Reach", a="Up to 6 m lifting height", b="Approx. 24–27 km per charge"),
      B("row", label="Drive", a="High-torque electric motor", b="Brushless 1000 W, two-wheel drive"),
      B("row", label="Control", a="Ergonomic remote control", b="Twist throttle, 2 speeds, reverse"),
      B("row", label="Mobility", a="360° swivel castors", b="79 cm wide, passages from 84 cm"),
      B("row", label="Ideal for", a="Scaffolds, renovation, installations", b="Firewood, stone, garden, construction"),
  ])),

  ("why", sec("ind-feature-grid", {"scheme": "sand", "style": "numbered", "columns": 4, "center": True,
      "eyebrow": "Why choose our equipment", "heading": "Made to take the load"}, [
      B("feature", icon="layers", title="Steel construction", text=P("Reinforced steel frames for stability in daily use.")),
      B("feature", icon="shield", title="Safety features", text=P("Limit stops, brakes and guard rails on Selo; battery indicator, LED headlight and horn on Abrelune.")),
      B("feature", icon="remote", title="Easy control", text=P("Remote-controlled lifting and stepless twist-throttle driving.")),
      B("feature", icon="lock", title="Secure checkout", text=P("Encrypted payment through Shopify Checkout.")),
  ])),

  ("applications", sec("ind-tiles", {"scheme": "paper", "columns": 4,
      "eyebrow": "Real-world applications", "heading": "Where our machines work"}, [
      B("tile", icon="brick", title="Construction & renovation", text="Selo lifts material to the scaffold", link="shopify://products/selo"),
      B("tile", icon="wrench", title="Installation & maintenance", text="Selo for technical work at height", link="shopify://products/selo"),
      B("tile", icon="wood", title="Firewood & stone", text="Abrelune moves heavy loads in one trip", link="shopify://products/abrelune"),
      B("tile", icon="leaf", title="Property & garden", text="Abrelune on grass, gravel and narrow paths", link="shopify://products/abrelune"),
  ])),

  ("quality", sec("ind-image-text", {"scheme": "dark", "reverse": True, "wide_media": True, "ratio": "adapt",
      "placeholder_label": "Photo: detail of steel frame or workshop",
      "eyebrow": "Quality & reliability", "heading": "Robust where it matters",
      "text": P("Selo uses a reinforced steel frame and a high-strength galvanised steel cable for a long service life. Abrelune is built from steel, with folding, removable side walls and a sealed 48 V battery system."),
      "checks": "Reinforced steel construction\nGalvanised steel lifting cable (Selo)\nSealed 48 V battery system (Abrelune)",
      "btn_style": "accent", "diagram": "none"})),

  ("reviews", sec("ind-reviews", {"scheme": "paper", "eyebrow": "Customer reviews", "heading": "What customers say"})),

  ("faq", sec("ind-faq", {"scheme": "sand", "layout": "aside", "single": True, "open_first": False, "schema": True,
      "eyebrow": "FAQ", "heading": "Frequently asked questions",
      "btn_label": "Contact us", "btn_link": "shopify://pages/contact"}, [
      B("qa", q="Which product do I need?", a=P("Choose Selo to raise materials to height: up to 500 kg and up to 6 m. Choose Abrelune to move heavy loads across the ground: up to 450 kg per trip.")),
      B("qa", q="Can Selo carry people?", a=P("No. Selo is for lifting materials only and is not approved for carrying people.")),
      B("qa", q="How do multi-unit savings work?", a=P("Choose a Double or Triple pack on the product page. The discount is applied automatically, and your cart shows the final price before you pay.")),
      B("qa", q="How long does delivery take?", a=FAQ_DELIVERY),
      B("qa", q="What is your return policy?", a=FAQ_RETURNS),
      B("qa", q="Which payment methods can I use?", a=P("All payment methods available in our checkout are shown in the footer of every page.")),
  ])),

  ("newsletter", sec("ind-newsletter", {"scheme": "dark", "eyebrow": "Newsletter", "heading": "Product news and campaign alerts",
      "text": P("Be the first to hear about new equipment and seasonal offers."), "disclaimer": "You can unsubscribe at any time."})),
])

write("product.selo.json", selo)
write("product.abrelune.json", abr)
write("index.json", home)
