"""Record the user's correction of a logged estimate: python -m monitor.correct <estimate_id> --kcal 520 --protein 31"""
import argparse
from monitor.log import append_correction

ap = argparse.ArgumentParser()
ap.add_argument("estimate_id"); ap.add_argument("--kcal", type=float); ap.add_argument("--protein", type=float)
ap.add_argument("--mass", type=float); ap.add_argument("--note")
a = ap.parse_args()
print(append_correction(a.estimate_id, a.kcal, a.protein, a.mass, a.note))
