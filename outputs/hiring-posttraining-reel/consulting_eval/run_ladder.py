"""Round 3: the eval-driven climb, with consistency across runs.

Same model (Claude Fable 5.2), same 10 casual client asks (run_naive.NAIVE) and the same data every time. Only the
instructions around the ask change; each version adds the fix for what the eval caught in the version before.
Every version runs RUNS times; the blind examiner (Opus 5.5, answer key) grades every slide.

Usage: python run_ladder.py --student-dir <empty dir>   (writes results_ladder.json)
"""

import argparse
import concurrent.futures as cf
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from run_eval import EXAMINER, examiner_prompt, js, run  # noqa: E402
from run_naive import NAIVE  # noqa: E402

STUDENT = "claude-fable-5-2"
RUNS = 3
V1 = "You are a management consultant. Use only the data given; never invent a number."
V2 = (V1 + " If the data does not support what the client is asking for, say so in the slide title and recommend what the"
      " data does support. Never hide a warning in notes: the slide must stand on its own.")
V3 = (V2 + " Output only the slide, in exactly this format:\nTITLE: <one sentence that states the so-what>\n- <bullet>\n"
      "- <bullet>\n- <bullet>")
VERSIONS = {"v0": "", "v1": V1, "v2": V2, "v3": V3}


def prompt(version: str, cid: str, data: str) -> str:
    head = VERSIONS[version]
    return (f"{head}\n\n" if head else "") + f"{NAIVE[cid]}\n\n{data}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--student-dir", required=True)
    args = ap.parse_args()
    cases = {c["id"]: c for c in json.loads((HERE / "cases.json").read_text())["cases"]}
    jobs = [(v, r, cid) for v in VERSIONS for r in range(1, RUNS + 1) for cid in cases]

    with cf.ThreadPoolExecutor(8) as ex:
        slides = dict(zip(jobs, ex.map(lambda j: run(prompt(j[0], j[2], cases[j[2]]["data"]), STUDENT, args.student_dir),
                                       jobs)))
        order = list(jobs)
        random.seed(13)
        random.shuffle(order)
        exams = dict(zip(order, ex.map(lambda j: js(run(examiner_prompt(cases[j[2]], slides[j]), EXAMINER,
                                                        args.student_dir)), order)))

    rows = [{"version": v, "run": r, "case": cid, "slide": slides[(v, r, cid)], "exam": exams[(v, r, cid)]}
            for v, r, cid in jobs]
    summary = {}
    for v in VERSIONS:
        per_run = [sum(bool(x["exam"].get("pass")) for x in rows if x["version"] == v and x["run"] == r)
                   for r in range(1, RUNS + 1)]
        always = [cid for cid in cases if all(x["exam"].get("pass") for x in rows if x["version"] == v and x["case"] == cid)]
        flaky = [cid for cid in cases if len({bool(x["exam"].get("pass")) for x in rows
                                               if x["version"] == v and x["case"] == cid}) > 1]
        summary[v] = {"pass_per_run": per_run, "cases_pass_every_run": len(always), "flaky_cases": flaky,
                      "failures": {f"{x['case']}#run{x['run']}": x["exam"].get("failure") for x in rows
                                   if x["version"] == v and not x["exam"].get("pass")}}
    (HERE / "results_ladder.json").write_text(json.dumps({"student": STUDENT, "examiner": EXAMINER,
                                                          "versions": VERSIONS, "summary": summary, "rows": rows},
                                                         indent=1))
    print(json.dumps({v: {k: s[k] for k in ("pass_per_run", "cases_pass_every_run", "flaky_cases")}
                      for v, s in summary.items()}, indent=1))


if __name__ == "__main__":
    main()
