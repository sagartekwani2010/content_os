"""Small eval on the creator's own meal photos against a REFERENCE ESTIMATE (portion assumed), NOT weighed truth.

Input: a JSON file OUTSIDE the repo (photos are personal), e.g. ~/.cache/content_os/food-tracker/indian_meals.json:
  [{"meal": "lunch-1", "photo": "/abs/path/lunch.jpg",
    "items": [{"key": "rice_white_cooked", "grams": 200, "basis": "1 katori ~ 150 g; plate looked like 1.3 katori"}, ...]}]
`key` refers to data/indian_reference.csv (per-100 g values with a source URL per row); composite keys
(dal_mean, bhindi_aloo, besan_chilla, ...) are defined in monitor/simulate_usage.ref_table with their recipe assumptions.

Output: eval/indian_reference_results.json (numbers + photo SHA-256 only) and a printed table.
Every number this produces must be labelled "reference estimate (portion assumed), not weighed".
"""
import argparse, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from estimate import estimate  # noqa: E402
from monitor.simulate_usage import ref_table  # noqa: E402
from monitor.log import append_correction  # noqa: E402

LABEL = "reference estimate (portion assumed), not weighed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("meals_json")
    ap.add_argument("--model", default="claude-fable-5-2")
    ap.add_argument("--modes", nargs="+", default=["table", "direct"])
    a = ap.parse_args()
    ref = ref_table()
    out = []
    for m in json.load(open(a.meals_json)):
        r_k = sum(ref[i["key"]][0] * i["grams"] / 100 for i in m["items"])
        r_p = sum(ref[i["key"]][1] * i["grams"] / 100 for i in m["items"])
        row = {"meal": m["meal"], "reference": {"kcal": round(r_k), "protein_g": round(r_p, 1),
                                               "grams": sum(i["grams"] for i in m["items"]), "label": LABEL,
                                               "items": m["items"]}}
        for mode in a.modes:
            e = estimate(m["photo"], mode=mode, model=a.model, source="real", tag=m["meal"])
            append_correction(e["log_id"], kcal=round(r_k), protein_g=round(r_p, 1), note=LABEL)
            row[mode] = {"kcal": e["totals"]["kcal"], "protein_g": e["totals"]["protein_g"], "grams": e["totals"]["grams"],
                         "items": [(i["name"], i.get("grams_best"), i.get("kcal"), i.get("confidence")) for i in e["items"]],
                         "image_sha256": e["image_sha256"], "latency_s": e["latency_s"]}
            print(f"{m['meal']:12s} {mode:6s} est {e['totals']['kcal']:6.0f} kcal {e['totals']['protein_g']:5.1f} g P | "
                  f"ref {r_k:6.0f} kcal {r_p:5.1f} g P  [{LABEL}]")
        out.append(row)
    json.dump({"label": LABEL, "model": a.model, "meals": out}, open(HERE / "indian_reference_results.json", "w"), indent=1)


if __name__ == "__main__":
    main()
