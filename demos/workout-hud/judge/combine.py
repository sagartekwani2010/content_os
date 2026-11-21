"""Final verdict = judge agent (pose numbers + key frames) AND coach agent (frames only) must agree before STOP.

Rule (fixed after the lunge false alarm on 20 Nov 2026, IMG_2650):
  judge STOP + coach BAD      -> STOP
  judge STOP + coach not BAD  -> CHECK FOOTAGE   (the two AIs disagree; a human looks)
  judge CAN'T SEE             -> CAN'T SEE        (safety check, no verdict)
  otherwise                   -> the judge's verdict
Usage: demos/workout-hud/.venv/bin/python demos/workout-hud/judge/combine.py
Writes demos/workout-hud/data/verdicts.json and prints the table.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def final(j, c):
    if j == "CAN'T SEE":
        return "CAN'T SEE"
    if j == "STOP":
        return "STOP" if c == "bad" else "CHECK FOOTAGE"
    return j


def main():
    rows = []
    for d in sorted(DATA.glob("IMG_*")):
        if not (d / "judge.json").exists() or not (d / "label.json").exists():
            continue
        jd, lb = json.loads((d / "judge.json").read_text()), json.loads((d / "label.json").read_text())
        sets = lb["label"].get("sets") or []
        coach = sets[0]["verdict"] if sets else "unclear"
        v = jd.get("verdict", {})
        rows.append({"clip": d.name, "lift": lb["label"].get("lift"), "judge": v.get("verdict"), "judge_reason": v.get("reason"),
                     "coach": coach, "coach_issue": (sets[0]["issues"][0]["what"] if sets and sets[0]["issues"] else None),
                     "final": final(v.get("verdict"), coach)})
    judged = [r for r in rows if r["judge"] != "CAN'T SEE" and r["coach"] != "unclear"]
    agree = sum(1 for r in judged if (r["judge"] in ("STOP", "HOLD")) == (r["coach"] == "bad"))
    summary = {"sets": len(rows), "final_counts": {k: sum(1 for r in rows if r["final"] == k)
               for k in ("CONTINUE", "HOLD", "STOP", "CHECK FOOTAGE", "CAN'T SEE")},
               "judge_vs_coach_agree": f"{agree} of {len(judged)} sets both could judge (flag vs no flag)"}
    (DATA / "verdicts.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1))
    for r in rows:
        print(f"{r['clip']:9} {r['final']:13} judge={r['judge']:9} coach={r['coach']:8} {r['lift'][:40] if r['lift'] else ''}")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
