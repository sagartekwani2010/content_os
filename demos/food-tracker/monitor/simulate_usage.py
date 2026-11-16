"""SIMULATED usage log for demonstrating the monitoring dashboard. NOT real usage.

Every record carries "simulated": true and goes to a separate file (simulated_usage.jsonl), never into the real log.
Seeded and reproducible. Plausibility comes from measured numbers, not invention:
  - latency and CLI-reported cost are resampled from the real eval runs (eval/runs/<model>/table/*.json);
  - item confidences are resampled from the real eval runs;
  - meals are built from data/indian_reference.csv with assumed portion ranges;
  - "user corrections" are drawn on a fraction of alerted estimates.

  python monitor/simulate_usage.py --days 18 --seed 7 --model claude-fable-5-2
"""
import argparse, csv, json, random, sys, uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from monitor.log import LOG, alerts  # noqa: E402

OUT = LOG.parent / "simulated_usage.jsonl"

# (slot, items as (reference key, display name, grams low, grams high))
MEALS = [
    ("breakfast", [("besan_chilla", "Besan chilla x2", 140, 200), ("curd", "Curd", 80, 150), ("ketchup", "Ketchup", 10, 30)]),
    ("breakfast", [("oats_cooked", "Oats bowl (cooked in milk)", 200, 280), ("whey_shake", "Whey shake (1 scoop in water)", 280, 330)]),
    ("lunch", [("rice_white_cooked", "Rice", 150, 250), ("dal_mean", "Dal", 150, 230), ("bhindi_aloo", "Bhindi aloo", 90, 140)]),
    ("lunch", [("rice_white_cooked", "Rice", 150, 230), ("rajma", "Rajma", 150, 220), ("curd", "Curd", 80, 120)]),
    ("dinner", [("chicken_curry", "Chicken curry", 150, 220), ("roti", "Roti x2", 60, 90), ("aloo_sabzi", "Aloo sabzi", 90, 140)]),
    ("dinner", [("paneer_bhurji", "Paneer bhurji", 120, 190), ("roti", "Roti x2", 60, 90), ("dal_mean", "Dal", 150, 200)]),
    ("snack", [("greek_yogurt", "Greek yogurt", 85, 100)]),
]


def ref_table():
    t = {r["key"]: (float(r["kcal_100g"]), float(r["protein_100g"])) for r in csv.DictReader(open(HERE / "data/indian_reference.csv"))}
    # composite items (documented assumptions, same as the reference-estimate method)
    t["dal_mean"] = tuple((a + b) / 2 for a, b in zip(t["dal_fndds"], t["dal_indb"]))
    t["bhindi_aloo"] = tuple((a + b) / 2 for a, b in zip(t["bhindi_sabzi"], t["aloo_sabzi"]))
    t["besan_chilla"] = ((40 * 387 + 4 * 884) / 80, 40 * 22.39 / 80)          # 40 g besan + 4 g oil -> ~80 g chilla
    t["oats_cooked"] = ((40 * 389 + 200 * 61) / 240, (40 * 16.89 + 200 * 3.15) / 240)
    t["whey_shake"] = (30 * 352 / 300, 30 * 78.13 / 300)                     # 30 g scoop in ~270 ml water
    t["paneer_bhurji"] = ((100 * 299 + 8 * 884) / 140, 100 * 15.86 / 140)     # 100 g paneer + 8 g oil + veg
    return t


def measured(model):
    runs = [json.load(open(f)) for f in sorted((HERE / "eval/runs" / model / "table").glob("dish_*.json"))]
    if not runs:
        sys.exit("no eval runs to resample latency/cost/confidence from; run eval first")
    return ([r["latency_s"] for r in runs], [r["cost_usd_cli"] for r in runs],
            [i["confidence"] for r in runs for i in r["items"] if i.get("confidence") is not None])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=18)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--model", default="claude-fable-5-2")
    ap.add_argument("--end", default="2026-11-15")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    ref = ref_table()
    lat, cost, conf = measured(a.model)
    tz = timezone(timedelta(hours=5, minutes=30))
    end = datetime.fromisoformat(a.end).replace(tzinfo=tz)
    hours = {"breakfast": 8.5, "lunch": 13.5, "dinner": 20.5, "snack": 17}
    recs = []
    for d in range(a.days, 0, -1):
        day = end - timedelta(days=d)
        slots = ["breakfast", "lunch", "dinner"] + (["snack"] if rng.random() < 0.4 else [])
        for slot in slots:
            if rng.random() < 0.12:  # skipped logging this meal
                continue
            name, items = rng.choice([m for m in MEALS if m[0] == slot])
            ts = day + timedelta(hours=hours[slot] + rng.uniform(-0.75, 0.75))
            est_items, true_k = [], 0.0
            for key, label, lo, hi in items:
                g_true = rng.uniform(lo, hi)
                g_est = g_true * rng.lognormvariate(-0.08, 0.22)   # mild under-estimation, ~22% spread
                k100, p100 = ref[key]
                c = rng.choice(conf)
                est_items.append({"name": label, "grams_best": round(g_est), "kcal": round(g_est * k100 / 100, 1),
                                  "protein_g": round(g_est * p100 / 100, 1), "confidence": c,
                                  "kcal_range": [round(g_est * 0.75 * k100 / 100), round(g_est * 1.3 * k100 / 100)]})
                true_k += g_true * k100 / 100
            tot = {"kcal": round(sum(i["kcal"] for i in est_items), 1), "protein_g": round(sum(i["protein_g"] for i in est_items), 1),
                   "grams": sum(i["grams_best"] for i in est_items),
                   "kcal_range": [sum(i["kcal_range"][0] for i in est_items), sum(i["kcal_range"][1] for i in est_items)]}
            est = {"items": est_items, "totals": tot}
            al = alerts(est)
            rid = uuid.UUID(int=rng.getrandbits(128)).hex[:12]
            recs.append({"kind": "estimate", "id": rid, "ts": ts.strftime("%Y-%m-%dT%H:%M:%S%z"), "source": "real",
                         "simulated": True, "tag": f"sim-{slot}", "mode": "table", "model": a.model, "image_sha256": None,
                         "latency_s": rng.choice(lat), "cost_usd_cli": rng.choice(cost), "n_calls": 2,
                         "items": [{k: i[k] for k in ("name", "grams_best", "kcal", "protein_g", "confidence")} for i in est_items],
                         "totals": tot, "alerts": al, "needs_confirmation": bool(al)})
            if al and rng.random() < 0.45:  # user answers the confirmation prompt with a correction
                recs.append({"kind": "correction", "id": uuid.UUID(int=rng.getrandbits(128)).hex[:12], "simulated": True,
                             "ts": (ts + timedelta(minutes=rng.uniform(1, 30))).strftime("%Y-%m-%dT%H:%M:%S%z"),
                             "estimate_id": rid, "kcal": round(true_k), "protein_g": None, "mass_g": None,
                             "note": "simulated user correction"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    n_est = sum(r["kind"] == "estimate" for r in recs)
    print(f"{n_est} simulated estimates, {sum(r['kind']=='correction' for r in recs)} corrections, "
          f"{sum(r.get('needs_confirmation', False) for r in recs)} alerts -> {OUT}")


if __name__ == "__main__":
    main()
