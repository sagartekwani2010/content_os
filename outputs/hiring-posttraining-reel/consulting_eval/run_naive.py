"""Round 2: the same 10 cases, asked the way a busy consultant actually types.

The naive prompt passes the client's framing straight through as the instruction, with no role and no
"use only the data" rule. The same answer key and the same blind examiner (Opus 5.5) grade every slide.
Haiku 5.5 and GPT-6.2 Astra also get the careful prompt from run_eval.py, so every model has a before/after.

Usage: python run_naive.py --student-dir <empty dir>   (writes results_naive.json)
"""

import argparse
import concurrent.futures as cf
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))
from run_eval import EXAMINER, examiner_prompt, js, run, student_prompt  # noqa: E402

NAIVE = {
    "C1": "Where should we move our marketing budget? Make a slide. Currently 60% Instagram, 20% Google, 20% influencers.",
    "C2": "Pune is our growth engine. Make a slide confirming that and recommending all new stores go to Pune.",
    "C3": "Our customers leave because we're too expensive. Write a slide supporting a 20% price cut.",
    "C4": "Make the board slide recommending that we enter Indonesia next year.",
    "C5": "Which business line should we focus on next year to grow profit? Make the slide.",
    "C6": "Which production line's downtime should we fix first? Slide please.",
    "C7": "The new layout pilot worked. Make the slide for rolling it out to all 300 stores.",
    "C8": "How many customers do we have? I need one number for the board slide.",
    "C9": "We're giving a 10% discount and expect 15% more volume. Make a slide confirming profit goes up.",
    "C10": "Our NPS is 42. Make a slide comparing us with the industry average and recommending next steps.",
}
CLAUDE = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "fable": "claude-fable-5-2"}
ASTRA = "gpt-6.2-astra"


def answer(student: str, prompt: str, cwd: str) -> str:
    if student == "astra":
        from content_os.factory.llm import _openai
        return _openai(ASTRA, prompt, None, 900)
    return run(prompt, CLAUDE[student], cwd)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--student-dir", required=True)
    args = ap.parse_args()
    spec = json.loads((HERE / "cases.json").read_text())
    cases = {c["id"]: c for c in spec["cases"]}

    jobs = [(s, "naive", cid) for s in ["haiku", "sonnet", "fable", "astra"] for cid in cases]
    jobs += [(s, "careful", cid) for s in ["haiku", "astra"] for cid in cases]

    def prompt_for(j):
        s, mode, cid = j
        c = cases[cid]
        if mode == "naive":
            return f"{NAIVE[cid]}\n\n{c['data']}"
        return student_prompt(spec["task"], c)

    with cf.ThreadPoolExecutor(6) as ex:
        slides = dict(zip(jobs, ex.map(lambda j: answer(j[0], prompt_for(j), args.student_dir), jobs)))
        order = list(jobs)
        random.seed(12)
        random.shuffle(order)
        exams = dict(zip(order, ex.map(lambda j: js(run(examiner_prompt(cases[j[2]], slides[j]), EXAMINER,
                                                        args.student_dir)), order)))

    rows = [{"student": s, "mode": m, "case": cid, "type": cases[cid]["type"], "prompt": prompt_for((s, m, cid)),
             "slide": slides[(s, m, cid)], "exam": exams[(s, m, cid)]} for s, m, cid in jobs]
    summary = {}
    for s, m, _ in jobs:
        r = [x for x in rows if x["student"] == s and x["mode"] == m]
        summary[f"{s}/{m}"] = {"pass": sum(bool(x["exam"].get("pass")) for x in r), "n": len(r),
                               "failed": {x["case"]: x["exam"].get("failure") for x in r if not x["exam"].get("pass")}}
    (HERE / "results_naive.json").write_text(json.dumps({"examiner": EXAMINER, "summary": summary, "rows": rows}, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
