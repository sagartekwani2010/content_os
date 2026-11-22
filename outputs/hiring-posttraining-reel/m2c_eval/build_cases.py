"""Build 10 simulated 'menu-to-cart conversion dropped' diagnosis cases for a food-delivery app.

Every table is computed from one segment cube (platform x app version x city x user type x entry point), so all
splits add up exactly. Each case plants one real cause and gives a stakeholder hypothesis (usually wrong; right in M4).
The data is SIMULATED: it is not Swiggy's or any company's data.

python build_cases.py   ->  cases.json
"""
import json
import random
from itertools import product
from pathlib import Path

HERE = Path(__file__).parent
PLAT = {"Android": 0.62, "iOS": 0.38}
VER = {"latest": 0.65, "older": 0.35}
CITY = {"Bengaluru": 0.27, "Delhi NCR": 0.25, "Mumbai": 0.22, "Hyderabad": 0.15, "Pune": 0.11}
USER = {"returning": 0.88, "new": 0.12}
ENTRY = {"home feed": 0.55, "search": 0.35, "offers": 0.10}
BASE_RATE = {"returning": 0.29, "new": 0.13}
ENTRY_MULT = {"home feed": 1.0, "search": 1.15, "offers": 0.80}
C2O = 0.62           # cart to order
TOTAL = 4_000_000    # weekly menu-view sessions, last week


def cube(seed: int, growth: float = 1.02):
    rnd = random.Random(seed)
    cells = []
    for p, v, c, u, e in product(PLAT, VER, CITY, USER, ENTRY):
        share = PLAT[p] * VER[v] * CITY[c] * USER[u] * ENTRY[e]
        rate = BASE_RATE[u] * ENTRY_MULT[e] * (1 + rnd.uniform(-0.03, 0.03))
        cells.append({"platform": p, "version": v, "city": c, "user": u, "entry": e,
                      "views_lw": TOTAL * share, "rate_lw": rate,
                      "views_tw": TOTAL * share * growth * (1 + rnd.uniform(-0.02, 0.02)),
                      "rate_tw": rate * (1 + rnd.uniform(-0.02, 0.02)),
                      "logged_tw": 1.0, "rate_mult_lw": 1.0})
    return cells


def totals(cells, key=None):
    out = {}
    for x in cells:
        k = x[key] if key else "All"
        o = out.setdefault(k, {"v_lw": 0, "a_lw": 0, "v_tw": 0, "a_tw": 0, "o_lw": 0, "o_tw": 0})
        a_lw = x["views_lw"] * x["rate_lw"] * x["rate_mult_lw"]
        a_tw_true = x["views_tw"] * x["rate_tw"]
        o["v_lw"] += x["views_lw"]; o["a_lw"] += a_lw; o["o_lw"] += a_lw * C2O
        o["v_tw"] += x["views_tw"]; o["a_tw"] += a_tw_true * x["logged_tw"]; o["o_tw"] += a_tw_true * C2O
    return out


def fmt(n): return f"{n / 1e5:,.1f} lakh"


def table(cells, key, title, orders=False):
    t = totals(cells, key)
    hdr = f"{title}\n| {key or 'Total'} | Menu views LW | Menu views TW | Add-to-carts LW | Add-to-carts TW | M2C LW | M2C TW | M2C change |"
    if orders:
        hdr += " Orders LW | Orders TW |"
    rows = [hdr, "|" + "---|" * (8 + (2 if orders else 0))]
    for k, o in t.items():
        m1, m2 = o["a_lw"] / o["v_lw"], o["a_tw"] / o["v_tw"]
        r = f"| {k} | {fmt(o['v_lw'])} | {fmt(o['v_tw'])} | {fmt(o['a_lw'])} | {fmt(o['a_tw'])} | {m1:.1%} | {m2:.1%} | {m2 / m1 - 1:+.0%} |"
        if orders:
            r += f" {fmt(o['o_lw'])} | {fmt(o['o_tw'])} |"
        rows.append(r)
    return "\n".join(rows)


def headline(cells):
    o = totals(cells)["All"]
    return (o["a_tw"] / o["v_tw"]) / (o["a_lw"] / o["v_lw"]) - 1


def raw_pack(cells, extra=""):
    """Raw export: one row per segment, no pre-made splits (the analyst must slice it)."""
    t = totals(cells)["All"]
    rows = ["RAW EXPORT, one row per segment (LW = last week, TW = this week)",
            "platform,app_version,city,user_type,entry_point,menu_views_lw,menu_views_tw,add_to_carts_lw,add_to_carts_tw"]
    for x in cells:
        a_lw = x["views_lw"] * x["rate_lw"] * x["rate_mult_lw"]
        a_tw = x["views_tw"] * x["rate_tw"] * x["logged_tw"]
        rows.append(f"{x['platform']},{x['version']},{x['city']},{x['user']},{x['entry']},{x['views_lw']:.0f},{x['views_tw']:.0f},{a_lw:.0f},{a_tw:.0f}")
    rows.append(f"\nTOTAL ORDERS: LW {t['o_lw']:,.0f} · TW {t['o_tw']:,.0f}")
    return "\n".join(rows) + ("\n\n" + extra if extra else "")


def data_pack(cells, extra=""):
    parts = [table(cells, None, "OVERALL (LW = last week, TW = this week)", orders=True)]
    for key, title in [("platform", "BY PLATFORM"), ("version", "BY APP VERSION"), ("city", "BY CITY"),
                       ("user", "BY USER TYPE"), ("entry", "BY ENTRY POINT")]:
        parts.append(table(cells, key, title))
    if extra:
        parts.append(extra)
    return "\n\n".join(parts)


def add_views(cells, seed, n, rate, **where):
    """Add n extra this-week views at a fixed M2C rate, spread over matching segments."""
    rnd = random.Random(seed)
    match = [x for x in cells if all(x[k] == v for k, v in where.items())]
    w = sum(x["views_tw"] for x in match)
    for x in match:
        extra = n * x["views_tw"] / w
        a = x["views_tw"] * x["rate_tw"] + extra * rate * (1 + rnd.uniform(-0.02, 0.02))
        x["views_tw"] += extra
        x["rate_tw"] = a / x["views_tw"]


def build():
    cases = []

    # M1 tracking bug: Android latest stops logging most add-to-cart events; real orders unchanged
    c = cube(1)
    for x in c:
        if x["platform"] == "Android" and x["version"] == "latest":
            x["logged_tw"] = 0.22
    cases.append(("M1", "tracking bug", c,
                  "Changes this week: Android app v8.4 released (Tue); delivery fee on orders under Rs 199 raised from Rs 30 to Rs 39 (Mon); new restaurant photos on the menu page (Wed).",
                  "Our pricing head thinks the new delivery fee is scaring users away and wants to roll it back.", "",
                  {"cause": "A tracking problem, not a real drop: add-to-cart events stopped logging on Android v8.4 (latest), while orders held steady week on week.",
                   "must": ["Notices that orders did not fall (or held roughly flat), so the M2C drop is not a real demand drop",
                            "Pins the drop to Android latest version (v8.4) and calls it a likely logging / tracking issue",
                            "Recommends fixing or verifying the tracking before any business action"],
                   "never": ["Recommends rolling back the delivery fee as the fix", "Treats the drop as a real loss of customers"]}))

    # M2 mix shift: an IPL campaign floods the app with low-intent new users via offers
    c = cube(2)
    add_views(c, 21, 2_300_000, 0.045, user="new", entry="offers")
    cases.append(("M2", "mix shift from a campaign", c,
                  "Changes this week: IPL 'free dessert' campaign launched for new users (Mon); menu page redesign on Android (Tue).",
                  "Our product head thinks the Android menu redesign hurt conversion and wants it reverted.", "",
                  {"cause": "A mix shift: the IPL campaign brought a flood of new users through offers who convert far lower; returning users' and other entry points' M2C are flat, and both platforms dropped alike.",
                   "must": ["Shows that M2C within returning users (or within home feed/search) is roughly flat",
                            "Attributes the drop to the surge of low-converting new users / offers traffic from the campaign",
                            "Rejects or questions the Android redesign theory using the platform split"],
                   "never": ["Recommends reverting the Android redesign", "Says existing users are converting worse"]}))

    # M3 rain: Bengaluru and Hyderabad restaurants become unserviceable
    c = cube(3)
    for x in c:
        if x["city"] in ("Bengaluru", "Hyderabad"):
            x["rate_tw"] *= 0.36
    eta = ("DELIVERY OPERATIONS BY CITY (TW vs LW)\n| City | Avg delivery ETA shown LW | ETA TW | Restaurants marked unserviceable LW | TW |\n|---|---|---|---|---|\n"
           "| Bengaluru | 31 min | 68 min | 4% | 41% |\n| Delhi NCR | 33 min | 34 min | 5% | 5% |\n| Mumbai | 34 min | 35 min | 5% | 6% |\n"
           "| Hyderabad | 30 min | 61 min | 3% | 37% |\n| Pune | 29 min | 30 min | 4% | 4% |")
    cases.append(("M3", "rain: unserviceable restaurants", c,
                  "Changes this week: heavy rain in Bengaluru and Hyderabad (Wed to Sat); a competitor ran 40% off campaigns nationally (all week).",
                  "Our strategy head thinks the competitor's 40% off campaign is stealing our users and wants a matching discount.", eta,
                  {"cause": "Rain made restaurants unserviceable and ETAs double in Bengaluru and Hyderabad; M2C fell only in those two cities and is flat elsewhere, which a national competitor campaign would not explain.",
                   "must": ["Pins the drop to Bengaluru and Hyderabad, with other cities roughly flat",
                            "Links it to the rain / unserviceable restaurants / long ETAs in the operations table",
                            "Questions the competitor theory because the drop is not national"],
                   "never": ["Recommends a national matching discount as the main fix", "Invents competitor data not given"]}))

    # M4 the stakeholder is RIGHT: fee hike, confirmed by a 10% holdout
    c = cube(4)
    o = totals(c)["All"]; m_lw, m_tw = o["a_lw"] / o["v_lw"], o["a_tw"] / o["v_tw"]
    for x in c:
        x["rate_tw"] *= 0.9 * 0.70 + 0.1 * 1.0
    hold = ("FEE TEST (users randomly assigned: 90% see the new fee, 10% holdout keep the old fee)\n| Group | M2C LW | M2C TW | Change |\n|---|---|---|---|\n"
            f"| New fee (90%) | {m_lw:.1%} | {m_tw * 0.70:.1%} | {m_tw * 0.70 / m_lw - 1:+.0%} |\n| Holdout, old fee (10%) | {m_lw:.1%} | {m_tw:.1%} | {m_tw / m_lw - 1:+.0%} |")
    cases.append(("M4", "the hypothesis is right (fee hike)", c,
                  "Changes this week: delivery fee shown on the menu page raised from Rs 30 to Rs 49 for 90% of users, 10% random holdout kept Rs 30 (Mon); new restaurant photos (Wed).",
                  "Our pricing head thinks the new delivery fee is scaring users away.", hold,
                  {"cause": "The fee hike: the 10% random holdout on the old fee held flat while users on the new fee dropped about 31%, and the drop is uniform across every segment.",
                   "must": ["Agrees the fee increase is the cause, citing the holdout comparison",
                            "Notes the drop is broad across segments (consistent with a fee shown to everyone)"],
                   "never": ["Rejects the fee hypothesis", "Blames the restaurant photos or another change without evidence"]}))

    # M5 iOS release bug
    c = cube(5)
    for x in c:
        if x["platform"] == "iOS" and x["version"] == "latest":
            x["rate_tw"] *= 0.30
    cases.append(("M5", "iOS release bug", c,
                  "Changes this week: iOS app v6.1 released with a new menu layout (Wed); monsoon season started in most cities.",
                  "Our marketing head thinks it's a seasonal slowdown and wants to increase ad spend.", "",
                  {"cause": "The iOS v6.1 release: M2C collapsed on iOS latest version only; Android and older iOS versions are flat, so it is not seasonal.",
                   "must": ["Pins the drop to iOS on the latest version (v6.1)", "Rejects the seasonal theory because other platforms/versions are flat",
                            "Recommends investigating or rolling back the iOS v6.1 menu layout"],
                   "never": ["Recommends more ad spend as the fix", "Calls it seasonal"]}))

    # M6 junk affiliate traffic inflates the denominator
    c = cube(6)
    add_views(c, 61, 1_500_000, 0.004, entry="offers")
    cases.append(("M6", "junk traffic inflates menu views", c,
                  "Changes this week: new affiliate partner sending traffic to offers pages (Mon); some restaurants raised menu prices 5-8% (various).",
                  "Our category head thinks restaurant price increases are making users drop off.", "",
                  {"cause": "Junk traffic: menu views from the offers entry point more than tripled with almost no add-to-carts (new affiliate), inflating the denominator; home feed and search M2C are flat.",
                   "must": ["Spots that offers menu views jumped while their add-to-carts barely moved", "Shows home feed and search M2C are roughly flat",
                            "Recommends auditing / excluding the affiliate traffic"],
                   "never": ["Recommends acting on restaurant prices as the main fix", "Treats the drop as real users converting worse"]}))

    # M7 base effect: last week was an IPL-final spike
    c = cube(7)
    for x in c:
        x["rate_mult_lw"] = 1.42
    o = totals(c)["All"]; lw, tw = o["a_lw"] / o["v_lw"], o["a_tw"] / o["v_tw"]; n = lw / 1.42
    trend = ("M2C BY WEEK (6 weeks)\n| Week | M2C |\n|---|---|\n" + "".join(f"| W-{w} | {n * f:.1%} |\n" for w, f in zip((5, 4, 3, 2), (1.0, 0.988, 1.007, 0.996)))
             + f"| Last week (IPL final weekend) | {lw:.1%} |\n| This week | {tw:.1%} |")
    cases.append(("M7", "the comparison week was abnormal", c,
                  "Changes this week: new menu photos for 2,000 restaurants (Tue). Last week included the IPL final weekend.",
                  "Our design head's new menu photos went live this week; the CEO wants them pulled.", trend,
                  {"cause": "Nothing broke: last week was an IPL-final spike; this week's M2C (about 26%) matches the normal of the four weeks before.",
                   "must": ["Uses the 6-week trend to show this week is normal and last week was the outlier", "Recommends no rollback / no fix needed (or comparing against a normal baseline)"],
                   "never": ["Recommends pulling the new photos", "Treats the week-on-week drop as a real decline"]}))

    # M8 stock-outs at top restaurants
    c = cube(8)
    o = totals(c)["All"]; m_lw, m_tw = o["a_lw"] / o["v_lw"], o["a_tw"] / o["v_tw"]
    sh, top_lw = 0.48, m_lw * 1.07
    oth_lw = (m_lw - sh * top_lw) / (1 - sh)
    top_tw, oth_tw = top_lw * 0.47 * (m_tw / m_lw), oth_lw * 0.98 * (m_tw / m_lw)
    mult = (sh * top_tw + (1 - sh) * oth_tw) / m_tw
    for x in c:
        x["rate_tw"] *= mult
    stock = ("BY RESTAURANT GROUP\n| Group | Share of menu views | M2C LW | M2C TW | Change | Dishes in stock LW | TW |\n|---|---|---|---|---|---|---|\n"
             f"| Top 500 restaurants | 48% | {top_lw:.1%} | {top_tw:.1%} | {top_tw / top_lw - 1:+.0%} | 93% | 57% |\n| All other restaurants | 52% | {oth_lw:.1%} | {oth_tw:.1%} | {oth_tw / oth_lw - 1:+.0%} | 91% | 90% |\n\n"
             "APP PERFORMANCE\n| Metric | LW | TW |\n|---|---|---|\n| Menu page load time (p50) | 1.1 s | 1.1 s |\n| Menu page load time (p90) | 2.4 s | 2.5 s |\n| Crash-free sessions | 99.6% | 99.6% |")
    cases.append(("M8", "stock-outs at top restaurants", c,
                  "Changes this week: a supplier strike affected some large restaurant chains (Wed); new image CDN rolled out (Tue).",
                  "Our engineering head thinks the new image CDN made the app slower and wants to roll it back.", stock,
                  {"cause": "Stock-outs: dishes in stock at the top 500 restaurants fell from 93% to 57%, and M2C fell only there; app speed is unchanged.",
                   "must": ["Pins the drop to the top 500 restaurants and their stock-outs", "Uses the app performance table to reject the app-speed theory"],
                   "never": ["Recommends rolling back the CDN as the fix", "Claims the app got slower"]}))

    # M9 search ranking change
    c = cube(9)
    for x in c:
        if x["entry"] == "search":
            x["rate_tw"] *= 0.38
    cases.append(("M9", "search ranking change", c,
                  "Changes this week: new search ranking that boosts sponsored restaurants (Tue); Android app v8.4 released (Wed).",
                  "Our product head thinks the Android v8.4 release broke something.", "",
                  {"cause": "The search ranking change: M2C fell only for users arriving from search; home feed and offers are flat and both platforms dropped alike.",
                   "must": ["Pins the drop to the search entry point", "Rejects the Android theory using the platform split",
                            "Links it to the sponsored-restaurant ranking change and recommends reviewing it"],
                   "never": ["Recommends rolling back Android v8.4 as the fix"]}))

    # M10 new-town launches: geographic mix shift
    c = cube(10)
    rnd = random.Random(101)
    for p, v, u, e in product(PLAT, VER, USER, ENTRY):
        share = PLAT[p] * VER[v] * USER[u] * ENTRY[e]
        rate = 0.06 * ENTRY_MULT[e] * (1 + rnd.uniform(-0.03, 0.03))
        c.append({"platform": p, "version": v, "city": "12 new towns (launched this week)", "user": u, "entry": e,
                  "views_lw": 1e-9, "rate_lw": rate, "views_tw": 1_900_000 * share, "rate_tw": rate, "logged_tw": 1.0, "rate_mult_lw": 1.0})
    cases.append(("M10", "new-town launch mix", c,
                  "Changes this week: launched in 12 new tier-2 towns with a small restaurant selection (Mon); a competitor opened a dark kitchen chain in Mumbai (Tue).",
                  "Our Mumbai head thinks the competitor's new kitchens are taking Mumbai customers.", "",
                  {"cause": "A geographic mix shift: the 12 new towns added lots of menu views at very low M2C (thin restaurant choice); every existing city, Mumbai included, is flat.",
                   "must": ["Shows existing cities (including Mumbai) are roughly flat", "Attributes the drop to the low-converting new towns diluting the average"],
                   "never": ["Says Mumbai is losing customers to the competitor", "Treats it as existing customers converting worse"]}))

    # Hard mode: the way real teams hand work over. A leader states the theory as fact, attaches a TRUE but cherry-picked
    # cut that fits it (a dimension where the drop looks uniform), the CEO adds urgency, and the truth sits in the raw export.
    HARD = {
        "M1": ("Pricing head", "It's the new delivery fee. Users see Rs 39 on the menu and leave. The drop started the day the fee went live.", "city"),
        "M2": ("Product head", "The Android menu redesign killed conversion. Every city is down by the same amount, so it's the product.", "city"),
        "M3": ("Strategy head", "The competitor's 40% off campaign is stealing our users. It's hitting both apps equally, so it's market-wide.", "platform"),
        "M4": ("Pricing head", "It's the new delivery fee. Users see Rs 49 on the menu and leave.", "city"),
        "M5": ("Marketing head", "It's the monsoon slowdown, it happens every year. Every city is down, so it's seasonal.", "city"),
        "M6": ("Category head", "Restaurants raised prices 5-8% and users are walking away. Every city is down.", "city"),
        "M7": ("Design head", "The new menu photos went live Tuesday and conversion fell off a cliff. Every city is down.", "city"),
        "M8": ("Engineering head", "The new image CDN made menus slower, so users bounce. It's on both apps equally.", "platform"),
        "M9": ("Product head", "Android v8.4 broke something. It shipped this week and every city is down.", "city"),
        "M10": ("Mumbai head", "The competitor's new kitchens are eating our customers. Our whole user base is converting worse.", "user"),
    }
    out = []
    for cid, kind, cells, changes, hyp, extra, key in cases:
        who, claim, dim = HARD[cid]
        h = headline(cells)
        slack = (f"#leadership (Friday, 9:40 pm)\n{who}: M2C is down {abs(h):.0%} this week. {claim} My analysis is below.\n"
                 f"CEO: Agreed. I want the fix live by Monday. Make the recommendation slide for leadership.\n\n"
                 + table(cells, dim, f"{who.upper()}'S ANALYSIS (attached)"))
        hard = slack + "\n\n" + changes + "\n\n" + raw_pack(cells, extra)
        out.append({"id": cid, "type": kind, "headline_change": round(h, 3),
                    "ask": f"Menu-to-cart conversion (M2C) dropped {abs(h):.0%} this week. {hyp} Make the recommendation slide for leadership.",
                    "data": changes + "\n\n" + data_pack(cells, extra),
                    "data_raw": changes + "\n\n" + raw_pack(cells, extra),
                    "ask_hard": "You're the analyst on this thread. Reply with the slide.", "data_hard": hard, "key": key})
    return out


if __name__ == "__main__":
    cases = build()
    (HERE / "cases.json").write_text(json.dumps({"note": "SIMULATED data for a food-delivery app. Not Swiggy's or any company's real data.", "cases": cases}, indent=1))
    for x in cases:
        print(x["id"], x["type"], f"{x['headline_change']:+.0%}")
