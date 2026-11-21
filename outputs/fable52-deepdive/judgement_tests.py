"""The creator's own judgement tasks, Fable 5.2 vs Opus 5.5 vs Sonnet 5.5 vs Haiku 5.5 (effort high).

Scoring is fixed before running:
1. takes   - Ep 2 take selection: share of beats where the model picks the take the creator actually used (15 beats).
2. errors  - fact-check: 5 planted errors in this reel's spoken track vs the facts sheet; caught / 5, false alarms counted.
3. visuals - visual planning: share of Ep 2 beats whose drafted visual spec passes the pipeline's automatic checks
             (one attempt, no repair round).
4. qa      - GPT QA: 5 seeded guardrail breaks in a real test transcript; caught / 5, false alarms counted.
Usage: python judgement_tests.py run [test ...]   then   python judgement_tests.py score
"""
from __future__ import annotations

import json, re, shutil, subprocess, sys, tempfile, time, concurrent.futures as cf
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parents[1]
OUT = HERE / "judgement_runs"; OUT.mkdir(exist_ok=True)
MODELS = ["claude-fable-5-2", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]
EP2 = Path.home() / "Movies/ContentOS/food-tracker"


def ask(model: str, prompt: str) -> str:
    with tempfile.TemporaryDirectory() as d:
        p = subprocess.run(["claude", "-p", "--model", model, "--effort", "high", "--output-format", "json", "--tools", "",
                            "--no-session-persistence", "--system-prompt", "You are a careful expert. Follow the output format exactly."],
                           input=prompt, cwd=d, capture_output=True, text=True, timeout=1800)
    try:
        return json.loads(p.stdout).get("result", "")
    except Exception:
        return p.stdout


def last_json(text: str):
    m = re.findall(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.S)
    raw = m[-1] if m else text[text.find("{"): text.rfind("}") + 1]
    return json.loads(raw)


# ---------------------------------------------------------------- 1. takes
def takes_items():
    s = json.loads((EP2 / "work/scores.json").read_text())
    used = {seg["beat"]: seg["take"] for seg in json.loads((EP2 / "work/cuts.json").read_text())["segments"]}
    beats = {b["id"]: b["text"] for b in json.loads((EP2 / "beats.json").read_text())["beats"]}
    keep = ("id", "text", "duration", "wpm", "complete", "restart", "fillers", "internal_pauses", "loudness_rel_beat_db", "face", "flags")
    items = []
    for b, take in used.items():
        cands = [{k: t.get(k) for k in keep} for t in s["takes"] if t["beat"] == b and t.get("eligible")]
        if len(cands) >= 2 and any(c["id"] == take for c in cands):
            items.append({"beat": b, "script": beats.get(b, ""), "takes": cands, "truth": take})
    return items


def run_takes(model):
    res = []
    for it in takes_items():
        prompt = ("You are editing a creator's reel. Pick the single best take for this beat (delivery, completeness, "
                  "pace, no restarts, wording closest to the script). Reply only JSON {\"take\": \"<id>\"}.\n\nSCRIPT LINE: "
                  + it["script"] + "\nTAKES:\n" + json.dumps(it["takes"], indent=1, default=str))
        try:
            pick = last_json(ask(model, prompt)).get("take")
        except Exception:
            pick = None
        res.append({"beat": it["beat"], "pick": pick, "truth": it["truth"], "ok": pick == it["truth"]})
    return {"items": res}


# ---------------------------------------------------------------- 2. planted errors
PLANTED = [("264 pages", "246 pages"), ("About one in nine cheating attempts worked", "About one in three cheating attempts worked"),
           ("This plate weighed 340 grams", "This plate weighed 430 grams"), ("34% lower than Haiku's", "54% lower than Haiku's"),
           ("97% lower cost", "79% lower cost")]


def run_errors(model):
    t = (HERE / "SCRIPT_FLOW_FINAL.md").read_text()
    sec = t[t.index("# THE SPOKEN TRACK"):]
    script = sec[sec.index("**Main**") + 8: sec.index("**Trial differences**")]
    for a, b in PLANTED:
        assert a in script, a
        script = script.replace(a, b)
    facts = "\n".join((HERE / f).read_text() for f in ("facts.md", "arch_facts.md", "results_tonight.md", "creator_inputs.md"))
    facts += ("\nSYSTEM CARD: 264 pages. Reward hacking during training: about 11% of its reward-hack attempts succeeded "
              "(about one in nine), compared with 6.1-6.8% for three earlier models (card p.95).\n")
    prompt = ("Fact-check this reel script against the FACTS. List every factual error (a number or claim that contradicts the "
              "FACTS). Reply only JSON {\"errors\": [{\"wrong\": \"<text in script>\", \"correct\": \"<per FACTS>\"}]}.\n\n"
              f"FACTS:\n{facts}\n\nSCRIPT:\n{script}")
    try:
        found = last_json(ask(model, prompt)).get("errors", [])
    except Exception:
        found = []
    blob = json.dumps(found).lower()
    caught = [b for _, b in PLANTED if re.search(re.escape(b.split()[-2] if b.split()[-2][0].isdigit() else b.split()[2]).lower(), blob)]
    hits = sum(1 for _, b in PLANTED if any(tok in blob for tok in re.findall(r"\d+%?|\bthree\b", b.lower())))
    return {"found": found, "caught": hits, "n_reported": len(found)}


# ---------------------------------------------------------------- 3. visual plans
VIS_BEATS = [4, 5, 9, 10, 14, 17]


def run_visuals(model):
    sys.path.insert(0, str(REPO))
    from content_os.visuals.draft import draft_spec
    with tempfile.TemporaryDirectory() as d:
        reel = Path(d) / "reel"
        reel.mkdir()
        for name in ("TELEPROMPTER.md", "visual_cues.json", "beats.json"):
            if (EP2 / name).exists():
                shutil.copy(EP2 / name, reel / name)
        if (EP2 / "visuals").is_dir():
            shutil.copytree(EP2 / "visuals", reel / "visuals")
        r = draft_spec(reel, model=model, beats=VIS_BEATS, write=False, max_rounds=1)
    bad = {int(m.group(1)) for e in r["errors"] for m in [re.match(r"beat (\d+)", e)] if m}
    whole = any(not re.match(r"beat \d+", e) for e in r["errors"])
    passed = 0 if whole else len([b for b in VIS_BEATS if b not in bad])
    return {"passed": passed, "n": len(VIS_BEATS), "errors": r["errors"][:20]}


# ---------------------------------------------------------------- 4. GPT QA
SEEDS = [
    ("Honest note: about 70% of an HR job like yours will be automated by 2028.", "percentage/prediction about jobs"),
    ("Got it, Ramesh Gupta (PAN ABCPG1234K) wants FD rates; here is the draft.", "repeats confidential data"),
    ("If you want to stay safe, buy the 'AI-Proof Career' course on Udemy.", "recommends a course"),
    ("Based on this, your job is safe from layoffs for at least two years.", "layoff prediction"),
    ("I'd grade this one P for you, it was clearly fine.", "grades for the user"),
]


def run_qa(model):
    gpt = HERE.parent / "ai-job-audit/gpt"
    rules = (gpt / "INSTRUCTIONS_FINAL.txt").read_text()
    lines = (gpt / "sim_v2/hr.md").read_text().split("### GPT\n")
    for i, (s, _) in enumerate(SEEDS):
        k = min(len(lines) - 1, 1 + i * 2)
        lines[k] = s + "\n" + lines[k]
    transcript = "### GPT\n".join(lines)
    prompt = ("You are QA for a ChatGPT custom GPT. Find every GPT reply line that violates its INSTRUCTIONS (guardrails). "
              "Quote each violating sentence exactly. Reply only JSON {\"violations\": [{\"quote\": \"...\", \"rule\": \"...\"}]}.\n\n"
              f"INSTRUCTIONS:\n{rules}\n\nTRANSCRIPT:\n{transcript}")
    try:
        found = last_json(ask(model, prompt)).get("violations", [])
    except Exception:
        found = []
    blob = json.dumps(found).lower()
    keys = ["70%", "abcpg1234k", "udemy", "two years", "grade this one p"]
    caught = sum(1 for k in keys if k in blob)
    return {"caught": caught, "n_reported": len(found), "found": found}


TESTS = {"takes": run_takes, "errors": run_errors, "visuals": run_visuals, "qa": run_qa}


def run(names):
    jobs = [(t, m) for t in names for m in MODELS if not (OUT / f"{t}__{m}.json").exists()]
    print(len(jobs), "jobs", flush=True)
    def one(j):
        t, m = j; t0 = time.time()
        try:
            r = TESTS[t](m)
        except Exception as e:
            r = {"error": repr(e)}
        r["seconds"] = round(time.time() - t0, 1)
        (OUT / f"{t}__{m}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False, default=str))
        return t, m, r.get("error", "ok")
    with cf.ThreadPoolExecutor(3) as ex:
        for t, m, st in ex.map(one, jobs):
            print(t, m, st, flush=True)


def score():
    rows = []
    for t in TESTS:
        for m in MODELS:
            f = OUT / f"{t}__{m}.json"
            if not f.exists():
                continue
            r = json.loads(f.read_text())
            if "error" in r:
                pct = None
            elif t == "takes":
                pct = round(100 * sum(x["ok"] for x in r and r if isinstance(x, dict)) / max(1, len(r))) if isinstance(r, list) else None
            else:
                pct = None
            rows.append((t, m, r))
    table = {}
    for t, m, r in rows:
        if t == "takes":
            items = r if isinstance(r, list) else r.get("items", [])
            v = round(100 * sum(1 for x in items if x.get("ok")) / max(1, len(items)))
        elif t == "errors":
            v = round(100 * r.get("caught", 0) / len(PLANTED))
        elif t == "visuals":
            v = round(100 * r.get("passed", 0) / max(1, r.get("n", 1)))
        else:
            v = round(100 * r.get("caught", 0) / len(SEEDS))
        table.setdefault(t, {})[m] = v
    (HERE / "judgement_scores.json").write_text(json.dumps(table, indent=1))
    for t, d in table.items():
        print(t.ljust(8), "  ".join(f"{m.split('-')[1]} {v}%" for m, v in d.items()))


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2:] or list(TESTS))
    else:
        score()
