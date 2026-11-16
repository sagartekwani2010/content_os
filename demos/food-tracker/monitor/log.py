"""Append-only JSONL monitoring log for every estimate (eval or real use).

Default location is OUTSIDE the repo (real meals are personal data): ~/.cache/content_os/food-tracker/estimates.jsonl
Override with FOOD_TRACKER_LOG. The image itself is never stored, only its SHA-256.
Record kinds: "estimate", "ground_truth" (eval label or weighed meal), "correction" (user fixes an estimate).
"""
import json, os, time, uuid
from pathlib import Path

LOG = Path(os.environ.get("FOOD_TRACKER_LOG", Path.home() / ".cache/content_os/food-tracker/estimates.jsonl"))

# Alert rule: ask the user to confirm instead of silently logging.
KCAL_PLAUSIBLE = (30, 1800)   # per photo
MIN_ITEM_CONF = 0.5
MAX_RANGE_RATIO = 0.8         # (kcal_high - kcal_low) / kcal_best


def alerts(est):
    out = []
    t = est.get("totals", {})
    k = t.get("kcal") or 0
    if not KCAL_PLAUSIBLE[0] <= k <= KCAL_PLAUSIBLE[1]:
        out.append(f"total kcal {k:.0f} outside plausible {KCAL_PLAUSIBLE}")
    for it in est.get("items", []):
        c = it.get("confidence")
        if c is not None and c < MIN_ITEM_CONF:
            out.append(f"low confidence {c:.2f}: {it.get('name')}")
        if it.get("match_flag"):
            out.append(f"{it['match_flag']}: {it.get('name')}")
    kr = t.get("kcal_range")
    if kr and k and (kr[1] - kr[0]) / k > MAX_RANGE_RATIO:
        out.append(f"wide kcal range {kr[0]}-{kr[1]}")
    return out


def _append(rec):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec["id"]


def append_estimate(est, source="real", tag=None):
    a = alerts(est)
    rec = {"kind": "estimate", "id": uuid.uuid4().hex[:12], "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "source": source, "tag": tag, "mode": est.get("mode"), "model": est.get("model"),
           "image_sha256": est.get("image_sha256"), "latency_s": est.get("latency_s"),
           "cost_usd_cli": est.get("cost_usd_cli"), "n_calls": len(est.get("calls", [])),
           "tokens_in": sum(c.get("input_tokens") or 0 for c in est.get("calls", [])),
           "tokens_out": sum(c.get("output_tokens") or 0 for c in est.get("calls", [])),
           "items": [{"name": i.get("name"), "grams": i.get("grams_best"), "kcal": i.get("kcal"),
                      "protein_g": i.get("protein_g"), "confidence": i.get("confidence"),
                      "fdc": (i.get("fdc") or {}).get("description"), "flag": i.get("match_flag")}
                     for i in est.get("items", [])],
           "totals": est.get("totals"), "alerts": a, "needs_confirmation": bool(a)}
    return _append(rec)


def append_ground_truth(tag, kcal, protein_g, mass_g, source="eval", note=None):
    return _append({"kind": "ground_truth", "id": uuid.uuid4().hex[:12], "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "source": source, "tag": tag, "kcal": kcal, "protein_g": protein_g, "mass_g": mass_g, "note": note})


def append_correction(estimate_id, kcal=None, protein_g=None, mass_g=None, note=None):
    return _append({"kind": "correction", "id": uuid.uuid4().hex[:12], "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "estimate_id": estimate_id, "kcal": kcal, "protein_g": protein_g, "mass_g": mass_g, "note": note})


def read():
    if not LOG.exists():
        return []
    return [json.loads(l) for l in open(LOG) if l.strip()]
