"""Metrics for eval/runs/<model>/<mode>/*.json against Nutrition5k labels.

Conditions: <model>/table (two-step, model picks table row), <model>/table_bm25 (ablation: top-1 retrieved row,
no picking call), <model>/direct (model states kcal/protein itself).
Metrics: MAE, MAPE (mean of per-dish |err|/truth), MAE as % of mean truth (the metric in Nutrition5k Table 3),
mean signed error (bias), with 95% percentile bootstrap CIs (10,000 resamples, seed 0). Paired bootstrap for
table minus direct on the same dishes.
Writes eval/results.json and eval/per_dish.csv.
"""
import csv, json, random, statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
B, SEED = 10000, 0
FIELDS = [("kcal", "kcal", "kcal"), ("mass_g", "grams", "mass"), ("protein_g", "protein_g", "protein")]


def boot(vals, fn, b=B, seed=SEED):
    rng = random.Random(seed)
    n = len(vals)
    xs = sorted(fn([vals[rng.randrange(n)] for _ in range(n)]) for _ in range(b))
    return [round(xs[int(0.025 * b)], 2), round(xs[int(0.975 * b) - 1], 2)]


def load():
    truth = {d["dish_id"]: d for d in json.load(open(HERE / "sample.json"))["dishes"]}
    conds = {}
    for model_dir in sorted((HERE / "runs").glob("*")):
        for mode_dir in sorted(model_dir.glob("*")):
            for f in sorted(mode_dir.glob("dish_*.json")):
                if f.name.endswith(".error.txt"):
                    continue
                r = json.load(open(f))
                did = f.stem
                conds.setdefault(f"{model_dir.name}/{mode_dir.name}", {})[did] = (r["totals"], r)
                if mode_dir.name in ("table",) and "ablation_table_bm25_top1" in r:
                    conds.setdefault(f"{model_dir.name}/table_bm25", {})[did] = (r["ablation_table_bm25_top1"]["totals"], r)
    return truth, conds


def metrics(truth, preds):
    ids = sorted(preds)
    res = {"n": len(ids)}
    for tk, pk, name in FIELDS:
        t = [truth[i][tk] for i in ids]
        p = [preds[i][0][pk] for i in ids]
        err = [pi - ti for pi, ti in zip(p, t)]
        ae = [abs(e) for e in err]
        ape = [abs(e) / ti * 100 for e, ti in zip(err, t)]
        pairs = list(zip(ae, t))
        res[name] = {
            "MAE": round(st.mean(ae), 1), "MAE_CI": boot(ae, st.mean),
            "MAPE": round(st.mean(ape), 1), "MAPE_CI": boot(ape, st.mean),
            "median_APE": round(st.median(ape), 1),
            "MAE_pct_of_mean": round(st.mean(ae) / st.mean(t) * 100, 1),
            "MAE_pct_of_mean_CI": boot(pairs, lambda s: st.mean(a for a, _ in s) / st.mean(x for _, x in s) * 100),
            "bias": round(st.mean(err), 1), "bias_CI": boot(err, st.mean),
            "within_20pct": round(sum(a <= 20 for a in ape) / len(ape) * 100, 1),
        }
    # decomposition: rescale the predicted kcal to the TRUE dish mass (removes portion error, keeps
    # identification + nutrient-density error). Not a deployable method: it uses the label.
    dens = [abs(preds[i][0]["kcal"] * truth[i]["mass_g"] / preds[i][0]["grams"] - truth[i]["kcal"])
            for i in ids if preds[i][0]["grams"]]
    res["kcal_if_true_mass_known"] = {"MAE": round(st.mean(dens), 1), "MAE_CI": boot(dens, st.mean), "n": len(dens)}
    rng_ok = [preds[i][0]["kcal_range"][0] <= truth[i]["kcal"] <= preds[i][0]["kcal_range"][1]
              for i in ids if preds[i][0].get("kcal_range")]
    if rng_ok:
        res["kcal_range_coverage_pct"] = round(sum(rng_ok) / len(rng_ok) * 100, 1)
    return res


def paired(truth, a, b, key="kcal", pk="kcal"):
    ids = sorted(set(a) & set(b))
    d = [abs(a[i][0][pk] - truth[i][key]) - abs(b[i][0][pk] - truth[i][key]) for i in ids]
    return {"n": len(ids), "mean_diff_abs_err": round(st.mean(d), 1), "CI": boot(d, st.mean)}


def main():
    truth, conds = load()
    out = {"conditions": {c: metrics(truth, p) for c, p in conds.items()}, "paired": {}}
    models = sorted({c.split("/")[0] for c in conds})
    for m in models:
        for x, y in [("table", "direct"), ("table", "table_bm25")]:
            if f"{m}/{x}" in conds and f"{m}/{y}" in conds:
                for tk, pk, name in FIELDS:
                    out["paired"][f"{m}: {x} minus {y} ({name} abs err)"] = paired(truth, conds[f"{m}/{x}"], conds[f"{m}/{y}"], tk, pk)
    # test-retest: same model, same prompt, same image, run twice
    for m in models:
        a_, b_ = conds.get(f"{m}/table"), conds.get(f"{m}/table_repeat")
        if a_ and b_:
            ids = sorted(set(a_) & set(b_))
            dk = [abs(a_[i][0]["kcal"] - b_[i][0]["kcal"]) for i in ids]
            dp = [abs(a_[i][0]["kcal"] - b_[i][0]["kcal"]) / ((a_[i][0]["kcal"] + b_[i][0]["kcal"]) / 2) * 100 for i in ids]
            dg = [abs(a_[i][0]["grams"] - b_[i][0]["grams"]) for i in ids]
            out["test_retest"] = {"model": m, "n": len(ids), "mean_abs_kcal_diff": round(st.mean(dk), 1),
                                  "CI": boot(dk, st.mean), "median_abs_kcal_diff": round(st.median(dk), 1),
                                  "max_abs_kcal_diff": round(max(dk), 1), "mean_abs_pct_diff": round(st.mean(dp), 1),
                                  "mean_abs_grams_diff": round(st.mean(dg), 1)}
            print("test-retest", out["test_retest"])
    # latency / cost per image
    for c, p in conds.items():
        if c.endswith("table_bm25"):
            continue
        rs = [r for _, r in p.values()]
        out["conditions"][c]["latency_s"] = {"mean": round(st.mean(r["latency_s"] for r in rs), 1),
                                             "median": round(st.median(r["latency_s"] for r in rs), 1),
                                             "max": round(max(r["latency_s"] for r in rs), 1)}
        out["conditions"][c]["cost_usd_cli_per_image"] = round(st.mean(r["cost_usd_cli"] for r in rs), 4)
        out["conditions"][c]["cost_basis"] = sorted({str(cl.get("cost_basis")) for r in rs for cl in r["calls"]})
        out["conditions"][c]["calls_per_image"] = round(st.mean(len(r["calls"]) for r in rs), 2)
        out["conditions"][c]["tokens_in_per_image"] = round(st.mean(sum(cl["input_tokens"] for cl in r["calls"]) for r in rs))
        out["conditions"][c]["tokens_out_per_image"] = round(st.mean(sum(cl["output_tokens"] or 0 for cl in r["calls"]) for r in rs))
    json.dump(out, open(HERE / "results.json", "w"), indent=1)
    with open(HERE / "per_dish.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["condition", "dish_id", "true_kcal", "pred_kcal", "true_mass_g", "pred_mass_g", "true_protein_g", "pred_protein_g", "n_items"])
        for c, p in conds.items():
            for i, (t, r) in sorted(p.items()):
                d = truth[i]
                w.writerow([c, i, round(d["kcal"], 1), round(t["kcal"], 1), round(d["mass_g"], 1), round(t["grams"], 1),
                            round(d["protein_g"], 1), round(t["protein_g"], 1), len(r["items"])])
    for c, m in out["conditions"].items():
        print(f"{c:32s} n={m['n']:3d} kcal MAE {m['kcal']['MAE']} {m['kcal']['MAE_CI']} MAPE {m['kcal']['MAPE']} {m['kcal']['MAPE_CI']} "
              f"%mean {m['kcal']['MAE_pct_of_mean']} bias {m['kcal']['bias']} | mass MAE {m['mass']['MAE']} ({m['mass']['MAE_pct_of_mean']}%) "
              f"| protein MAE {m['protein']['MAE']} ({m['protein']['MAE_pct_of_mean']}%) MAPE {m['protein']['MAPE']} "
              f"| kcal MAE if true mass known {m['kcal_if_true_mass_known']['MAE']} | range cov {m.get('kcal_range_coverage_pct')}")
    for k, v in out["paired"].items():
        print(k, v)


if __name__ == "__main__":
    main()
