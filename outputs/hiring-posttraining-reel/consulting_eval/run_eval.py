"""Consulting eval: does the AI write a client-ready so-what slide?

Students answer each case with no tools and no access to the answer key (they run from an empty directory).
Each student then grades its own slide, the way most people check AI today. A separate examiner (a different
model) grades every slide against the answer key without knowing which model wrote it.

Usage: python run_eval.py --student-dir <empty dir>   (writes results.json next to this file)
"""

import argparse
import concurrent.futures as cf
import json
import random
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
STUDENTS = {"fable": "claude-fable-5-2", "sonnet": "claude-sonnet-5-5"}
EXAMINER = "claude-opus-5-5"


def run(prompt: str, model: str, cwd: str) -> str:
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "json",
           "--no-session-persistence", "--tools", ""]
    for _ in range(3):
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=900, cwd=cwd)
        try:
            out = json.loads(p.stdout[p.stdout.index("{"):])
            if not out.get("is_error"):
                return out["result"]
        except ValueError:
            pass
    raise RuntimeError(f"{model} failed: {p.stdout[-300:]} {p.stderr[-300:]}")


def js(text: str) -> dict:
    return json.loads(re.search(r"\{.*\}", text, re.S).group(0))


def student_prompt(task: str, case: dict) -> str:
    return (f"You are a management consultant. {task}\n\nCLIENT BRIEF: {case['brief']}\n\nDATA:\n{case['data']}\n\n"
            "Write the slide now. Format:\nTITLE: <one sentence>\n- <bullet>\n- <bullet>\n- <bullet>")


def self_grade_prompt(case: dict, slide: str) -> str:
    return (f"You wrote this recommendation slide for a client.\n\nCLIENT BRIEF: {case['brief']}\n\nDATA:\n{case['data']}\n\n"
            f"YOUR SLIDE:\n{slide}\n\nGrade your own slide honestly. Is it correct and ready to show the client?\n"
            'Reply with JSON only: {"score": <0-10>, "client_ready": true|false, "reason": "<one sentence>"}')


def examiner_prompt(case: dict, slide: str) -> str:
    key = case["key"]
    checks = [f"I{i+1}. MUST INCLUDE: {c}" for i, c in enumerate(key["must_include"])]
    checks += [f"N{i+1}. MUST NOT: {c}" for i, c in enumerate(key["must_not"])]
    return (f"You are an independent examiner. You did not write this slide and do not know who did.\n\n"
            f"CLIENT BRIEF: {case['brief']}\n\nDATA:\n{case['data']}\n\nANSWER KEY (the correct so-what): {key['so_what']}\n\n"
            "CHECKS:\n" + "\n".join(checks) + f"\n\nSLIDE TO GRADE:\n{slide}\n\n"
            "For each check, decide met (for MUST INCLUDE) or violated (for MUST NOT), quoting the slide as evidence. "
            "The slide PASSES only if every MUST INCLUDE is met and no MUST NOT is violated. Be strict but fair: "
            "wording may differ from the key if the meaning is the same.\n"
            'JSON only: {"checks": [{"id": str, "ok": bool, "evidence": str}], "pass": bool, '
            '"failure": "<one plain sentence on what went wrong, or empty>"}')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--student-dir", required=True)
    args = ap.parse_args()
    spec = json.loads((HERE / "cases.json").read_text())
    cases = spec["cases"]

    jobs = [(s, c) for s in STUDENTS for c in cases]
    with cf.ThreadPoolExecutor(6) as ex:
        slides = dict(zip([(s, c["id"]) for s, c in jobs],
                          ex.map(lambda j: run(student_prompt(spec["task"], j[1]), STUDENTS[j[0]], args.student_dir), jobs)))
        selfg = dict(zip([(s, c["id"]) for s, c in jobs],
                         ex.map(lambda j: js(run(self_grade_prompt(j[1], slides[(j[0], j[1]["id"])]),
                                                 STUDENTS[j[0]], args.student_dir)), jobs)))
        order = list(jobs)
        random.seed(11)
        random.shuffle(order)  # examiner sees slides in a random order, with no model names
        exams = dict(zip([(s, c["id"]) for s, c in order],
                         ex.map(lambda j: js(run(examiner_prompt(j[1], slides[(j[0], j[1]["id"])]),
                                                 EXAMINER, args.student_dir)), order)))

    rows = []
    for s, c in jobs:
        k = (s, c["id"])
        rows.append({"student": s, "model": STUDENTS[s], "case": c["id"], "type": c["type"], "slide": slides[k],
                     "self": selfg[k], "exam": exams[k]})
    summary = {}
    for s in STUDENTS:
        r = [x for x in rows if x["student"] == s]
        summary[s] = {
            "model": STUDENTS[s],
            "self_client_ready": sum(bool(x["self"].get("client_ready")) for x in r),
            "self_mean_score": round(sum(float(x["self"].get("score", 0)) for x in r) / len(r), 1),
            "examiner_pass": sum(bool(x["exam"].get("pass")) for x in r),
            "n": len(r),
            "failed_cases": [x["case"] for x in r if not x["exam"].get("pass")],
            "self_ready_but_failed": [x["case"] for x in r if x["self"].get("client_ready") and not x["exam"].get("pass")],
        }
    (HERE / "results.json").write_text(json.dumps({"examiner": EXAMINER, "summary": summary, "rows": rows}, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
