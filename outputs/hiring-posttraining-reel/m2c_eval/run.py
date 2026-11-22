"""Run one prompt version of the M2C diagnosis eval: 10 cases x RUNS runs, Fable 5.2 student, blind Opus 5.5 checker.

python run.py --version v0 --student-dir <empty dir>     (appends to results.json under that version)
Prompt versions live in PROMPTS; each new version adds the fix that the previous version's failures pointed to.
"""
import argparse
import concurrent.futures as cf
import json
import random
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
STUDENT, CHECKER, RUNS = "claude-fable-5-2", "claude-opus-5-5", 3
PROMPTS = json.loads((HERE / "prompts.json").read_text())


def run(prompt: str, model: str, cwd: str) -> str:
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "json", "--no-session-persistence", "--tools", ""]
    for _ in range(3):
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, cwd=cwd)
        try:
            out = json.loads(p.stdout[p.stdout.index("{"):])
            if not out.get("is_error"):
                return out["result"]
        except ValueError:
            pass
    raise RuntimeError(f"{model} failed: {p.stdout[-300:]} {p.stderr[-300:]}")


def js(t: str) -> dict:
    return json.loads(re.search(r"\{.*\}", t, re.S).group(0))


def checker_prompt(case: dict, answer: str) -> str:
    k = case["key"]
    checks = [f"I{i + 1}. MUST: {c}" for i, c in enumerate(k["must"])] + [f"N{i + 1}. MUST NOT: {c}" for i, c in enumerate(k["never"])]
    return (f"You are an independent examiner. You did not write this answer and do not know who did.\n\nTHE ASK: {case['ask']}\n\n"
            f"DATA (simulated):\n{case['data']}\n\nTHE TRUE CAUSE (answer key, written before any answer): {k['cause']}\n\nCHECKS:\n"
            + "\n".join(checks) + f"\n\nANSWER TO GRADE:\n{answer}\n\n"
            "Grade only what the leadership slide itself recommends and claims (text the author marks as notes outside the slide does "
            "not count as the recommendation). PASS only if every MUST is met and no MUST NOT is violated; meaning counts, not wording. "
            'JSON only: {"checks":[{"id":str,"ok":bool,"evidence":str}],"pass":bool,"failure":"<one plain sentence, or empty>",'
            '"hypothesis_followed":bool}')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--student-dir", required=True)
    ap.add_argument("--student", default=STUDENT)
    ap.add_argument("--data", default="data", choices=["data", "data_raw", "data_hard"])
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", default="results.json")
    a = ap.parse_args()
    cases = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())["cases"]}
    head = PROMPTS[a.version]
    tag = a.tag or a.version
    jobs = [(r, cid) for r in range(1, RUNS + 1) for cid in cases]
    prompt = lambda cid: (head + "\n\n" if head else "") + (cases[cid]["ask_hard"] if a.data == "data_hard" else cases[cid]["ask"]) + "\n\n" + cases[cid][a.data]
    with cf.ThreadPoolExecutor(8) as ex:
        ans = dict(zip(jobs, ex.map(lambda j: run(prompt(j[1]), a.student, a.student_dir), jobs)))
        order = list(jobs); random.shuffle(order)
        ex_ = dict(zip(order, ex.map(lambda j: js(run(checker_prompt(cases[j[1]], ans[j]), CHECKER, a.student_dir)), order)))
    rows = [{"version": tag, "student": a.student, "data": a.data, "run": r, "case": cid, "answer": ans[(r, cid)], "exam": ex_[(r, cid)]} for r, cid in jobs]
    path = HERE / a.out
    allr = json.loads(path.read_text()) if path.exists() else {"student": STUDENT, "checker": CHECKER, "rows": []}
    allr["rows"] = [x for x in allr["rows"] if x["version"] != tag] + rows
    path.write_text(json.dumps(allr, indent=1))
    per_run = [sum(bool(x["exam"].get("pass")) for x in rows if x["run"] == r) for r in range(1, RUNS + 1)]
    print(tag, "pass per run", per_run, "total", sum(per_run), "/", len(rows))
    for x in rows:
        if not x["exam"].get("pass"):
            print(f"  {x['case']} run{x['run']}: {x['exam'].get('failure')}")


if __name__ == "__main__":
    main()
