"""Hero case for script v14: 14 days of daily funnel data for a food-delivery app (SIMULATED, not Swiggy's data).

Truth: on Day 8 (Tue) the new delivery fee AND Android app v8.4 both went live. v8.4 stops logging most add-to-cart
events. App opens, menu views and orders keep rising; logged add-to-carts (and so M2C) fall about 30%.

Conditions (3 runs each, Claude Fable 5.2 as the analyst, blind Claude Opus 5.5 checker, same answer key):
  A  daily M2C only + the business head's fee theory   (what a busy consultant pastes)
  B  full daily funnel by platform/version, no checklist (control)
  C  full daily funnel + the eval's analyst checklist    (eval-driven system)
python hero_daily.py --student-dir <empty dir>  ->  hero_daily.json
"""
import argparse
import concurrent.futures as cf
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from run import CHECKER, js, run  # noqa: E402

STUDENT, RUNS = "claude-fable-5-2", 3
DAYS = [f"Day {d} ({w})" for d, w in zip(range(1, 15), ["Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Mon"] * 2)]
ADOPT = [0] * 7 + [0.30, 0.55, 0.70, 0.70, 0.70, 0.70, 0.70]   # share of Android users on v8.4
LOGGED = 0.30                                                    # share of v8.4 add-to-carts still logged


def series():
    rnd = random.Random(14)
    out = []
    for i, day in enumerate(DAYS):
        wk = 1.15 if day.endswith(("Fri)", "Sat)", "Sun)")) else 1.0
        opens = 1_800_000 * (1.003 ** i) * wk * (1 + rnd.uniform(-0.015, 0.015))
        menu = opens * 0.55 * (1 + rnd.uniform(-0.01, 0.01))
        seg = {}
        for name, share in [("Android v8.4", 0.62 * ADOPT[i]), ("Android older", 0.62 * (1 - ADOPT[i])), ("iOS", 0.38)]:
            m = menu * share
            atc_true = m * 0.28 * (1 + rnd.uniform(-0.015, 0.015))
            atc_log = atc_true * (LOGGED if name == "Android v8.4" else 1.0)
            seg[name] = {"menu": m, "atc_true": atc_true, "atc_log": atc_log, "orders": atc_true * 0.62}
        tot = {k: sum(s[k] for s in seg.values()) for k in ("menu", "atc_true", "atc_log", "orders")}
        out.append({"day": day, "opens": opens, "seg": seg, **tot})
    return out


L = lambda n: f"{n / 1e5:.2f} lakh"


def naive_data(s):
    rows = ["Daily menu-to-cart conversion (M2C)", "| Day | Menu views | Add-to-carts | M2C |", "|---|---|---|---|"]
    rows += [f"| {d['day']} | {L(d['menu'])} | {L(d['atc_log'])} | {d['atc_log'] / d['menu']:.1%} |" for d in s]
    return "\n".join(rows)


def full_data(s):
    rows = ["Daily funnel, all users", "| Day | App opens | Menu views | Add-to-carts | Orders | M2C |", "|---|---|---|---|---|---|"]
    rows += [f"| {d['day']} | {L(d['opens'])} | {L(d['menu'])} | {L(d['atc_log'])} | {L(d['orders'])} | {d['atc_log'] / d['menu']:.1%} |" for d in s]
    rows += ["", "Daily M2C by platform and app version", "| Day | Android v8.4 | Android older | iOS |", "|---|---|---|---|"]
    for d in s:
        cell = lambda k: "—" if d["seg"][k]["menu"] < 1 else f"{d['seg'][k]['atc_log'] / d['seg'][k]['menu']:.1%}"
        rows.append(f"| {d['day']} | {cell('Android v8.4')} | {cell('Android older')} | {cell('iOS')} |")
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--student-dir", required=True)
    a = ap.parse_args()
    s = series()
    pre = sum(d["atc_log"] / d["menu"] for d in s[:7]) / 7
    post = sum(d["atc_log"] / d["menu"] for d in s[-3:]) / 3
    drop = post / pre - 1
    changes = "Changes on Day 8 (Tue): new delivery fee went live (Rs 30 -> Rs 39 on orders under Rs 199); Android app v8.4 started rolling out."
    ask = (f"Business head: Menu-to-cart conversion has dropped about {abs(drop):.0%} since Tuesday, the day our new delivery fee went live. "
           "Users are opening menus but not adding to cart. It's the fee. Make the slide with your recommendation for leadership.")
    checklist = ("Before any recommendation, a real analyst checks, and so must you: (1) the whole funnel day by day: app opens, menu views, "
                 "add-to-carts, orders; (2) whether the steps contradict each other (a later step cannot rise while an earlier one falls "
                 "unless the counting is broken); (3) the split by platform and app version; (4) whether the stakeholder's theory survives "
                 "those checks. Put what you checked on the slide.")
    conds = {"A": ask + "\n\n" + changes + "\n\n" + naive_data(s),
             "B": ask + "\n\n" + changes + "\n\n" + full_data(s),
             "C": checklist + "\n\n" + ask + "\n\n" + changes + "\n\n" + full_data(s)}
    case = {"ask": ask, "data": changes + "\n\n" + full_data(s), "key": {
        "cause": "Not the fee: Android v8.4 (same day) stopped logging most add-to-cart events. App opens, menu views and orders kept rising, so customers kept adding to cart; the counting broke.",
        "must": ["Does not conclude the fee caused the drop (says it is not supported, or cannot be concluded from the data given)",
                 "Identifies the tracking problem on Android v8.4, OR, if the data given cannot show it, explicitly asks for orders / funnel / platform data before deciding",
                 "Recommends verifying the data or tracking before any business action such as a fee rollback"],
        "never": ["Recommends rolling back or reducing the delivery fee as the fix", "States a cause as fact that the data given cannot support"]}}
    jobs = [(c, r) for c in conds for r in range(1, RUNS + 1)]
    with cf.ThreadPoolExecutor(6) as ex:
        ans = dict(zip(jobs, ex.map(lambda j: run(conds[j[0]], STUDENT, a.student_dir), jobs)))
        order = list(jobs); random.shuffle(order)
        from run import checker_prompt
        exams = dict(zip(order, ex.map(lambda j: js(run(checker_prompt(case, ans[j]), CHECKER, a.student_dir)), order)))
    out = {"drop": drop, "series": [{k: d[k] for k in ("day", "opens", "menu", "atc_log", "orders")} for d in s],
           "prompts": conds, "key": case["key"],
           "rows": [{"cond": c, "run": r, "answer": ans[(c, r)], "exam": exams[(c, r)]} for c, r in jobs]}
    (HERE / "hero_daily.json").write_text(json.dumps(out, indent=1))
    print(f"M2C drop {drop:.0%}")
    for c in conds:
        rs = [x for x in out["rows"] if x["cond"] == c]
        print(c, "pass", [x["exam"]["pass"] for x in rs], "| followed fee theory", [x["exam"].get("hypothesis_followed") for x in rs])
        for x in rs:
            if not x["exam"]["pass"]:
                print("   ", x["run"], x["exam"].get("failure"))


if __name__ == "__main__":
    main()
