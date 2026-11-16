"""Meal photo -> items, grams (range), protein, kcal, confidence, totals, assumptions.

Two conditions:
  table  (default): step A, a vision model lists the foods and estimates grams only (no nutrients);
                    step B, local BM25 retrieval of candidate rows from USDA FoodData Central
                    (SR Legacy 2018-04 + FNDDS 2021-2023, data/fdc_compact.csv);
                    step C, a text-only model call picks the best candidate row per item (or none);
                    nutrients = grams x table value per 100 g. The model never states kcal or protein.
  direct (baseline): one vision call; the model states grams, kcal and protein itself.

The free ablation "table_bm25" (top-1 retrieval row, no step C) is computed from the same step A output.

Model calls go through the Claude Code CLI in headless mode (`claude -p`), which runs on the local
Claude Code login. No API key is needed. Every estimate is appended to the monitoring log
(see monitor/log.py): image SHA-256, never the image.

Usage:
  python estimate.py path/to/meal.jpg [--mode table|direct] [--model claude-fable-5-2] [--source real|eval]
"""
import argparse, csv, hashlib, json, math, re, subprocess, sys, tempfile, time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from monitor.log import append_estimate  # noqa: E402

DEFAULT_MODEL = "claude-fable-5-2"

ITEM_RULES = """Identify every distinct food item visible, including sauces, dressings, cooking oil or butter you can see
or that the preparation clearly implies, garnishes and drinks. Merge tiny garnishes into one item only if they weigh under 5 g.
For each item estimate the edible mass on the plate in grams as a range (grams_low, grams_high) and a best estimate (grams_best).
Use visual scale cues (plate, bowl, cutlery, hand, packaging) and say which you used. Give a confidence from 0 to 1 that
the item identity AND its grams_best (within +/-25%) are right."""

PROMPT_A = f"""You are the vision step of a food-logging pipeline. Use the Read tool to open the image path you are given.
{ITEM_RULES}
Do NOT estimate calories or protein: a separate step looks those up in the USDA FoodData Central table.
For each item write fdc_query: a description in USDA SR Legacy / FNDDS style, e.g.
"Chicken, broilers or fryers, breast, meat only, cooked, roasted" or "Rice, white, long-grain, regular, cooked" or "Lentils, mature seeds, cooked, boiled".
Reply with ONLY this JSON, no prose:
{{"items":[{{"name":str,"grams_low":num,"grams_best":num,"grams_high":num,"fdc_query":str,"preparation":str,"confidence":num}}],
"scale_cues":str,"assumptions":[str]}}"""

PROMPT_DIRECT = f"""You are a food-logging assistant. Use the Read tool to open the image path you are given.
{ITEM_RULES}
Then estimate, yourself, the calories (kcal) and protein (g) of each item at grams_best, and the totals.
Reply with ONLY this JSON, no prose:
{{"items":[{{"name":str,"grams_low":num,"grams_best":num,"grams_high":num,"kcal":num,"protein_g":num,"preparation":str,"confidence":num}}],
"total_kcal":num,"total_protein_g":num,"scale_cues":str,"assumptions":[str]}}"""

PROMPT_C = """You match foods to rows of the USDA FoodData Central table. For each item you get its description and
numbered candidate rows (description, kcal and protein per 100 g). Pick the candidate that best matches the food as it
appears on the plate, including preparation (cooked vs raw, fried, with sauce). If no candidate is a reasonable match, use -1.
Reply with ONLY JSON: {"picks":[{"item":int,"candidate":int,"why":str}]}"""


# ---------- model calls via Claude Code CLI ----------

def claude_call(system, prompt, model, image_dir=None, timeout=300):
    cmd = ["claude", "-p", prompt, "--system-prompt", system, "--model", model,
           "--output-format", "json", "--no-session-persistence"]
    if image_dir:
        cmd += ["--tools", "Read", "--allowedTools", "Read", "--add-dir", str(image_dir)]
    else:
        cmd += ["--tools", ""]
    t0 = time.time()
    with tempfile.TemporaryDirectory() as cwd:  # neutral cwd: no project CLAUDE.md is loaded
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    wall = time.time() - t0
    try:
        out = json.loads(p.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"CLI failed rc={p.returncode}: {p.stderr[-500:]} {p.stdout[-500:]}")
    if out.get("is_error"):
        raise RuntimeError(f"CLI error: {out.get('result')}")
    mu = out.get("modelUsage", {}).get(model, {})
    meta = {"wall_s": round(wall, 2), "duration_ms": out.get("duration_ms"), "num_turns": out.get("num_turns"),
            "cost_usd_cli": out.get("total_cost_usd"), "cost_basis": mu.get("costBasis"),
            "input_tokens": mu.get("inputTokens", 0) + mu.get("cacheReadInputTokens", 0) + mu.get("cacheCreationInputTokens", 0),
            "output_tokens": mu.get("outputTokens")}
    return out.get("result", ""), meta


def parse_json(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON in model reply: " + text[:300])
    return json.loads(m.group(0))


def call_json(system, prompt, model, image_dir=None, retries=1):
    metas, last = [], None
    for _ in range(retries + 1):
        try:
            text, meta = claude_call(system, prompt, model, image_dir)
            metas.append(meta)
            return parse_json(text), metas
        except (ValueError, RuntimeError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            last = e
    raise RuntimeError(f"failed after retries: {last}")


# ---------- nutrition table + BM25 retrieval ----------

_TOK = re.compile(r"[a-z]+")
STOP = {"and", "or", "with", "without", "the", "of", "in", "a", "nfs", "ns", "as", "to", "from", "made", "type"}


def toks(s):
    return [t for t in _TOK.findall(s.lower()) if t not in STOP and len(t) > 1]


class Table:
    def __init__(self, path=HERE / "data/fdc_compact.csv"):
        self.rows = list(csv.DictReader(open(path)))
        self.docs = [toks(r["description"]) for r in self.rows]
        self.df = Counter(t for d in self.docs for t in set(d))
        self.N = len(self.docs)
        self.avg = sum(map(len, self.docs)) / self.N
        self.inv = {}
        for i, d in enumerate(self.docs):
            for t in set(d):
                self.inv.setdefault(t, []).append(i)

    def search(self, query, k=8, k1=1.2, b=0.75):
        q = toks(query)
        scores = Counter()
        for t in set(q):
            idf = math.log(1 + (self.N - self.df.get(t, 0) + 0.5) / (self.df.get(t, 0) + 0.5))
            for i in self.inv.get(t, []):
                d = self.docs[i]
                tf = d.count(t)
                scores[i] += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(d) / self.avg))
        # tiny tie-break toward shorter (more generic) descriptions
        best = sorted(scores, key=lambda i: (-scores[i], len(self.docs[i])))[:k]
        return [dict(self.rows[i], score=round(scores[i], 2)) for i in best]


_TABLE = None


def table():
    global _TABLE
    if _TABLE is None:
        _TABLE = Table()
    return _TABLE


# ---------- pipeline ----------

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def nutrients(item, row):
    k, p = float(row["kcal_100g"]), float(row["protein_100g"])
    g = {x: float(item.get(f"grams_{x}") or item.get("grams_best") or 0) for x in ("low", "best", "high")}
    return {"kcal": round(g["best"] * k / 100, 1), "kcal_range": [round(g["low"] * k / 100), round(g["high"] * k / 100)],
            "protein_g": round(g["best"] * p / 100, 1),
            "protein_range": [round(g["low"] * p / 100, 1), round(g["high"] * p / 100, 1)]}


def totals(items):
    t = {"grams": sum(float(i.get("grams_best") or 0) for i in items),
         "kcal": sum(i.get("kcal") or 0 for i in items), "protein_g": sum(i.get("protein_g") or 0 for i in items)}
    t["grams_range"] = [sum(float(i.get("grams_low") or 0) for i in items), sum(float(i.get("grams_high") or 0) for i in items)]
    if all("kcal_range" in i for i in items):
        t["kcal_range"] = [sum(i["kcal_range"][0] for i in items), sum(i["kcal_range"][1] for i in items)]
        t["protein_range"] = [round(sum(i["protein_range"][0] for i in items), 1), round(sum(i["protein_range"][1] for i in items), 1)]
    return {k: (round(v, 1) if isinstance(v, float) else v) for k, v in t.items()}


def estimate(image, mode="table", model=DEFAULT_MODEL, source="real", tag=None, log=True):
    image = Path(image).resolve()
    prompt = f"Image path: {image}"
    t0 = time.time()
    calls = []
    if mode == "direct":
        a, m = call_json(PROMPT_DIRECT, prompt, model, image.parent)
        calls += m
        items = a.get("items", [])
        for it in items:
            it["nutrient_source"] = "model estimate"
        result = {"items": items, "totals": totals(items),
                  "model_stated_totals": {"kcal": a.get("total_kcal"), "protein_g": a.get("total_protein_g")}}
    else:
        a, m = call_json(PROMPT_A, prompt, model, image.parent)
        calls += m
        items = a.get("items", [])
        cands = [table().search(f"{it.get('fdc_query', '')} {it.get('name', '')}") for it in items]
        lines = []
        for n, (it, cs) in enumerate(zip(items, cands)):
            lines.append(f"Item {n}: {it.get('name')} | {it.get('preparation', '')} | query: {it.get('fdc_query')}")
            lines += [f"  {j}: {c['description']} ({c['source']}; {c['kcal_100g']} kcal, {c['protein_100g']} g protein /100 g)"
                      for j, c in enumerate(cs)]
        picks = {}
        if items:
            c_out, m = call_json(PROMPT_C, "\n".join(lines), model)
            calls += m
            picks = {int(p["item"]): int(p["candidate"]) for p in c_out.get("picks", [])}
        bm25_items = []
        for n, (it, cs) in enumerate(zip(items, cands)):
            top = cs[0] if cs else None
            bm25_items.append({**it, **(nutrients(it, top) if top else {"kcal": 0, "protein_g": 0}),
                               "bm25_row": top["description"] if top else None})
            j = picks.get(n, -1)
            if 0 <= j < len(cs):
                row, flag = cs[j], None
            else:  # no acceptable candidate: retry retrieval on the plain name, flag as weak
                alt = table().search(it.get("name", ""), k=1)
                row, flag = (alt[0] if alt else top), "weak match"
            if row is None:
                it.update({"kcal": 0, "protein_g": 0, "match_flag": "no table row"})
                continue
            it.update(nutrients(it, row))
            it["fdc"] = {"fdc_id": row["fdc_id"], "description": row["description"], "source": row["source"],
                         "kcal_100g": float(row["kcal_100g"]), "protein_100g": float(row["protein_100g"])}
            it["nutrient_source"] = "USDA FoodData Central lookup"
            if flag:
                it["match_flag"] = flag
        result = {"items": items, "totals": totals(items),
                  "ablation_table_bm25_top1": {"totals": totals(bm25_items),
                                               "rows": [it.get("bm25_row") for it in bm25_items]}}
    result.update({"mode": mode, "model": model, "image_sha256": sha256(image), "scale_cues": a.get("scale_cues"),
                   "assumptions": a.get("assumptions", []),
                   "latency_s": round(time.time() - t0, 2), "calls": calls,
                   "cost_usd_cli": round(sum(c.get("cost_usd_cli") or 0 for c in calls), 5)})
    if log:
        result["log_id"] = append_estimate(result, source=source, tag=tag)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--mode", choices=["table", "direct"], default="table")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--source", choices=["real", "eval"], default="real")
    ap.add_argument("--no-log", action="store_true")
    a = ap.parse_args()
    print(json.dumps(estimate(a.image, a.mode, a.model, a.source, log=not a.no_log), indent=1))


if __name__ == "__main__":
    main()
