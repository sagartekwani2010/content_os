"""Fetch the Nutrition5k files this eval needs (metadata, official splits, overhead RGB) into a cache outside the repo.

Source: public GCS bucket gs://nutrition5k_dataset (CC BY 4.0), layout per github.com/google-research-datasets/Nutrition5k.
Sampling: SEED-fixed random sample of N dish ids from the official depth_test_ids.txt split
(the overhead RealSense RGB images exist only for the depth subset; depth_test is a subset of rgb_test).
"""
import argparse, csv, json, random, sys, urllib.request
from pathlib import Path

BASE = "https://storage.googleapis.com/nutrition5k_dataset/nutrition5k_dataset"
CACHE = Path.home() / ".cache/content_os/nutrition5k"


def get(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return True
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            dest.write_bytes(r.read())
        return True
    except Exception as e:
        print("FAIL", url, e, file=sys.stderr)
        return False


def load_meta():
    rows = {}
    for cafe in ("cafe1", "cafe2"):
        p = CACHE / f"metadata/dish_metadata_{cafe}.csv"
        get(f"{BASE}/metadata/dish_metadata_{cafe}.csv", p)
        for r in csv.reader(open(p)):
            ingrs = [{"name": r[i + 1], "grams": float(r[i + 2]), "kcal": float(r[i + 3]), "protein": float(r[i + 6])}
                     for i in range(6, len(r) - 6, 7)]
            # column order per official README: dish_id,total_calories,total_mass,total_fat,total_carb,total_protein
            rows[r[0]] = {"dish_id": r[0], "kcal": float(r[1]), "mass_g": float(r[2]), "fat_g": float(r[3]),
                          "carb_g": float(r[4]), "protein_g": float(r[5]), "ingredients": ingrs}
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20261116)
    a = ap.parse_args()
    split = CACHE / "splits/depth_test_ids.txt"
    get(f"{BASE}/dish_ids/splits/depth_test_ids.txt", split)
    ids = sorted(set(x.strip() for x in open(split) if x.strip()))
    meta = load_meta()
    rng = random.Random(a.seed)
    pool = [i for i in ids if i in meta and meta[i]["mass_g"] > 0]
    rng.shuffle(pool)
    chosen = []
    for d in pool:
        if len(chosen) == a.n:
            break
        if get(f"{BASE}/imagery/realsense_overhead/{d}/rgb.png", CACHE / f"overhead/{d}/rgb.png"):
            chosen.append(meta[d])
    out = Path(__file__).parent / "sample.json"
    json.dump({"seed": a.seed, "split": "dish_ids/splits/depth_test_ids.txt", "split_size": len(ids),
               "eligible": len(pool), "dishes": chosen}, open(out, "w"), indent=1)
    print(f"split ids={len(ids)} eligible={len(pool)} sampled={len(chosen)} -> {out}")


if __name__ == "__main__":
    main()
