"""Run the estimator on the fixed Nutrition5k sample. Resumable: skips dishes that already have a result file.

  python eval/run_eval.py --model claude-fable-5-2 --modes table direct --workers 4
Raw outputs: eval/runs/<model>/<mode>/<dish_id>.json  (model outputs only; no images)
"""
import argparse, json, sys, traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from estimate import estimate  # noqa: E402
from monitor.log import append_ground_truth, read  # noqa: E402

IMG = Path.home() / ".cache/content_os/nutrition5k/overhead"


def run_one(d, mode, model, suffix=""):
    out = HERE / "runs" / model / (mode + suffix) / f"{d['dish_id']}.json"
    if out.exists():
        return "skip"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = estimate(IMG / d["dish_id"] / "rgb.png", mode=mode, model=model, source="eval", tag=d["dish_id"])
        out.write_text(json.dumps(r, indent=1))
        return f"ok {d['dish_id']} {mode} {r['totals']['kcal']:.0f} vs {d['kcal']:.0f} kcal {r['latency_s']}s"
    except Exception as e:
        (out.parent / f"{d['dish_id']}.error.txt").write_text(traceback.format_exc())
        return f"ERR {d['dish_id']} {mode}: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-fable-5-2")
    ap.add_argument("--modes", nargs="+", default=["table", "direct"])
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--suffix", default="", help="e.g. _repeat to store a test-retest run separately")
    a = ap.parse_args()
    dishes = json.load(open(HERE / "sample.json"))["dishes"][: a.n]
    have = {r["tag"] for r in read() if r["kind"] == "ground_truth"}
    for d in dishes:
        if d["dish_id"] not in have:
            append_ground_truth(d["dish_id"], d["kcal"], d["protein_g"], d["mass_g"], note="Nutrition5k label")
    jobs = [(d, m) for d in dishes for m in a.modes]
    with ThreadPoolExecutor(a.workers) as ex:
        for msg in ex.map(lambda j: run_one(j[0], j[1], a.model, a.suffix), jobs):
            print(msg, flush=True)


if __name__ == "__main__":
    main()
