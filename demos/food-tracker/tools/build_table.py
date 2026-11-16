"""Build data/fdc_compact.csv: kcal and protein per 100 g for USDA FoodData Central SR Legacy (April 2018)
and FNDDS 2021-2023 (released 2024-10-31). Both are public domain / CC0 1.0 (fdc.nal.usda.gov).

Download (outside the repo, to ~/.cache/content_os/fdc):
  https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip
  https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_survey_food_csv_2024-10-31.zip
"""
import csv, io, urllib.request, zipfile
from pathlib import Path

CACHE = Path.home() / ".cache/content_os/fdc"
OUT = Path(__file__).resolve().parent.parent / "data/fdc_compact.csv"
SOURCES = {
    "SR Legacy 2018-04": ("FoodData_Central_sr_legacy_food_csv_2018-04.zip", {"1008": "kcal", "1003": "protein"}),
    # FNDDS food_nutrient.csv uses legacy nutrient numbers: 208 = Energy (kcal), 203 = Protein (g)
    "FNDDS 2021-2023": ("FoodData_Central_survey_food_csv_2024-10-31.zip", {"208": "kcal", "203": "protein"}),
}


def rows(z, suffix):
    name = next(n for n in z.namelist() if n.endswith("/" + suffix))
    return csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8"))


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    out = []
    for label, (fname, nmap) in SOURCES.items():
        p = CACHE / fname
        if not p.exists():
            urllib.request.urlretrieve("https://fdc.nal.usda.gov/fdc-datasets/" + fname, p)
        z = zipfile.ZipFile(p)
        foods = {r["fdc_id"]: r["description"] for r in rows(z, "food.csv")}
        vals = {}
        for r in rows(z, "food_nutrient.csv"):
            k = nmap.get(r["nutrient_id"])
            if k and r["fdc_id"] in foods:
                vals.setdefault(r["fdc_id"], {})[k] = float(r["amount"])
        for fid, v in vals.items():
            if "kcal" in v and "protein" in v:
                out.append({"source": label, "fdc_id": fid, "description": foods[fid],
                            "kcal_100g": v["kcal"], "protein_100g": v["protein"]})
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader(); w.writerows(out)
    print(len(out), "foods ->", OUT)


if __name__ == "__main__":
    main()
