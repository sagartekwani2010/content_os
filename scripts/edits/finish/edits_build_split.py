"""Frame-exact Edits build: 30 fps project, one import, splitAt the section times, verify zero drift, transitions.
Usage: python3 edits_build_split.py <clean_mp4> <plan.json> <cuts.json>"""
import json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ed import call  # noqa: E402

clean, plan_p, cuts_p = sys.argv[1:4]
plan = json.load(open(plan_p)); cuts = json.load(open(cuts_p))
seg = {s["beat"]: s for s in cuts["segments"]}
FPS = 30


def step(name, args=None):
    r = call(name, args or {})
    if isinstance(r, dict) and r.get("error"):
        raise SystemExit(f"{name} failed: {r}")
    return r


step("newProject"); time.sleep(2)
step("setFrameRate", {"fps": FPS})
step("seek", {"seconds": 0})
cid = step("importMedia", {"path": clean})["id"]
bounds = sorted({t["between_beats"][1] for t in plan["transitions"]})
times = [round(round(seg[b]["out_start"] * FPS) / FPS, 6) for b in bounds]
step("splitAt", {"id": cid, "times": times, "snap": "projectFrame"})
clips = sorted(step("clips")["clips"], key=lambda c: c["startTime"])
drift = max(abs(c["startTime"] - c["sourceInPoint"]) for c in clips)
edge = max(abs(c["startTime"] - t) for c, t in zip(clips[1:], times))
print(json.dumps({"clips": len(clips), "split_times": times, "max_drift_s": round(drift, 4), "max_edge_err_s": round(edge, 4),
                  "end": round(clips[-1]["endTime"], 4), "expected_end": round(cuts["duration"], 4)}))
if drift > 0.001 or edge > 0.017:
    raise SystemExit("alignment check failed; not adding transitions")
by_start = {round(c["startTime"], 3): c["id"] for c in clips}
order = [c["id"] for c in clips]
for t, b in zip(sorted(plan["transitions"], key=lambda t: t["between_beats"][1]), bounds):
    i = order.index(by_start[round(times[bounds.index(t["between_beats"][1])], 3)])
    step("addTransition", {"fromId": order[i - 1], "toId": order[i], "filterId": t["id"], "durationSeconds": t["duration_s"]})
clips2 = sorted(step("clips")["clips"], key=lambda c: c["startTime"])
print("after transitions, max drift:", round(max(abs(c["startTime"] - c["sourceInPoint"]) for c in clips2), 4),
      "| transitions:", len(plan["transitions"]))
