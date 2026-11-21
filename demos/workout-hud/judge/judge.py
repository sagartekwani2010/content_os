"""Workout Analyser judge: pose numbers + 4 key frames -> Claude Fable 5.2 -> CONTINUE / HOLD / STOP.

Pipeline per clip (no labeller output is ever read here):
  1. Pose tool (YOLO11n-pose, cached kp.npz): 17 joints per frame at 30 fps.
  2. Safety check (code, before any model call): if the moving joint is hidden or impossible in more than
     CANT_SEE_PCT of frames, the verdict is CAN'T SEE with the fixed message below. Fable is not asked.
  3. Rep maths: the joint angle that moves most (knee, hip or elbow) is the rep signal; each rep gets its range,
     its end positions, lowering and lifting time, and torso sway.
  4. Baseline: the creator's best rep of this set (largest range of motion).
  5. Judge: Fable 5.2 reads the rep table and 4 key frames (best rep and worst rep, both ends) and returns one verdict.

Usage: demos/workout-hud/.venv/bin/python demos/workout-hud/judge/judge.py CLIP [CLIP ...]
Writes demos/workout-hud/data/<stem>/judge.json and judge_frames/*.jpg (gitignored).
"""
import json, re, subprocess, sys, tempfile, time
from pathlib import Path

import cv2
import numpy as np
from scipy.signal import find_peaks

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "visuals"))
import pose_fx as P  # noqa: E402

MODEL = "claude-fable-5-2"
CONF = 0.4
CANT_SEE_PCT = 25
CANT_SEE = "CAN'T SEE YOUR {joint}. NOT JUDGING THIS SET."

# (name, a, b, c) interior angle at b, per side
JOINTS = {"knee": (11, 13, 15), "hip": (5, 11, 13), "elbow": (5, 7, 9)}
RIGHT = {11: 12, 13: 14, 15: 16, 5: 6, 7: 8, 9: 10}

SYSTEM = """You are the judge agent in a lifter's Workout Analyser. You get measured numbers for one set from a pose
tool (30 frames per second) and four key frames: the lifter's best rep and worst rep, each at both ends of the movement.
The baseline is the lifter's own best rep in this set, not a textbook.

Decide one verdict for the set:
- CONTINUE: reps stay close to the best rep (range and control); nothing to fix.
- HOLD: a real but moderate drift from the best rep (range, tempo or sway); keep the load, fix it next set.
- STOP: the set has stopped doing its job or is unsafe: most reps fall clearly short of the best rep's range,
  the weight is being thrown or dropped, or form is breaking down. Stop the set and fix before the next one.
Use the frames to identify the lift and to confirm what the numbers say; do not judge anything the numbers and frames
cannot show. Use the Read tool to open the four frame paths.

Reply with JSON only:
{"lift": str, "verdict": "CONTINUE"|"HOLD"|"STOP", "reason": str (4 words max, plain gym words),
 "detail": str (one sentence a gym buddy would understand, with one number from the table),
 "worst_rep": int, "best_rep": int, "confidence": num 0-1}"""


def angle_series(kp, name, side):
    a, b, c = JOINTS[name]
    if side == "right":
        a, b, c = RIGHT[a], RIGHT[b], RIGHT[c]
    out = np.full(len(kp), np.nan)
    for i, f in enumerate(kp):
        if min(f[a, 2], f[b, 2], f[c, 2]) >= CONF:
            v = P.angle(f[a, :2], f[b, :2], f[c, :2])
            if v >= 20:  # physically impossible below this on these lifts
                out[i] = v
    return out


def smooth(x, k=7):
    s = x.copy(); n = len(x)
    for i in range(n):
        w = x[max(0, i - k // 2): i + k // 2 + 1]
        if not np.isnan(x[i]) and (~np.isnan(w)).any():
            s[i] = np.nanmean(w)
    return s


def lean_series(kp, side):
    S, H = (5, 11) if side == "left" else (6, 12)
    return np.array([abs(np.degrees(np.arctan2(f[S, 0] - f[H, 0], f[H, 1] - f[S, 1])))
                     if min(f[S, 2], f[H, 2]) >= CONF else np.nan for f in kp])


def rhythm(s):
    """Peak autocorrelation at a rep-like period (0.7 to 4 s): about 1 for clean repeated reps, near 0 for jitter."""
    x = np.where(np.isnan(s), np.nanmedian(s), s); x = x - x.mean()
    if x.std() < 1e-6:
        return 0.0
    ac = np.correlate(x, x, "full")[len(x) - 1:] / (x.var() * len(x))
    lo, hi = 21, min(120, len(ac) - 1)
    return float(max(0.0, ac[lo:hi].max())) if hi > lo else 0.0


def analyse(kp):
    side = "left" if kp[:, [5, 11, 13, 15], 2].mean() >= kp[:, [6, 12, 14, 16], 2].mean() else "right"
    best = None
    for name in JOINTS:
        s = smooth(angle_series(kp, name, side))
        v = s[~np.isnan(s)]
        if len(v) < 0.5 * len(s):
            continue
        rng = np.percentile(v, 95) - np.percentile(v, 5)
        score = rng * rhythm(s)  # reps repeat; tracking jitter does not
        if best is None or score > best[3]:
            best = (name, s, rng, score)
    if best is None:
        return {"side": side, "joint": "knee", "hidden_pct": 100.0}
    name, s, rng, _ = best
    hidden = round(100 * float(np.isnan(s).mean()), 1)
    x = np.where(np.isnan(s), np.nanmedian(s), s)
    hi, _ = find_peaks(x, prominence=0.35 * rng, distance=15)
    lo, _ = find_peaks(-x, prominence=0.35 * rng, distance=15)
    lean = lean_series(kp, side)
    reps = []
    for n, l in enumerate(lo):  # a rep = one low turn between two high turns
        before, after = hi[hi < l], hi[hi > l]
        if not len(before) or not len(after):
            continue
        h0, h1 = before[-1], after[0]
        top = float(min(x[h0], x[h1])); bottom = float(x[l]); seg = lean[h0:h1 + 1]
        reps.append({"rep": len(reps) + 1, "t": round(l / 30, 2), "open_deg": round(top), "closed_deg": round(bottom),
                     "range_deg": round(top - bottom), "into_s": round((l - h0) / 30, 2), "out_of_s": round((h1 - l) / 30, 2),
                     "torso_sway_deg": None if np.isnan(seg).all() else round(float(np.nanmax(seg) - np.nanmin(seg))),
                     "_f": (int(h0), int(l), int(h1))})
    return {"side": side, "joint": name, "hidden_pct": hidden, "reps": reps,
            "range_p5_p95": [round(float(np.percentile(x, 5))), round(float(np.percentile(x, 95)))]}


def save_frame(video, i, path, label):
    cap = cv2.VideoCapture(str(video)); cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, fr = cap.read(); cap.release()
    if ok:
        fr = cv2.resize(fr, (540, 960))
        cv2.rectangle(fr, (0, 0), (540, 44), (0, 0, 0), -1)
        cv2.putText(fr, label, (10, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 220, 255), 2)
        cv2.imwrite(str(path), fr)


def claude(prompt, image_dir, timeout=900):
    cmd = ["claude", "-p", prompt, "--system-prompt", SYSTEM, "--model", MODEL, "--output-format", "json",
           "--no-session-persistence", "--tools", "Read", "--allowedTools", "Read", "--add-dir", str(image_dir)]
    with tempfile.TemporaryDirectory() as cwd:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    out = json.loads(p.stdout)
    if out.get("is_error"):
        raise RuntimeError(out.get("result"))
    return out["result"], out.get("total_cost_usd")


def judge(clip):
    clip = Path(clip).resolve(); d = P.DATA / clip.stem
    kp, video = P.keypoints(clip); kp = P.smooth_kp(kp)
    a = analyse(kp)
    rec = {"clip": clip.name, "analysis": {k: v for k, v in a.items() if k != "reps"},
           "reps": [{k: v for k, v in r.items() if k != "_f"} for r in a.get("reps", [])],
           "judge": {"model": MODEL, "inputs": "rep table + 4 key frames; never the labeller's output"}}
    if a["hidden_pct"] > CANT_SEE_PCT or len(a.get("reps", [])) < 2:
        rec["verdict"] = {"verdict": "CAN'T SEE", "reason": "joint hidden",
                          "detail": CANT_SEE.format(joint=a["joint"].upper()), "by": "safety check (code), no model call"}
    else:
        reps = a["reps"]; b = max(reps, key=lambda r: r["range_deg"]); w = min(reps, key=lambda r: r["range_deg"])
        fd = d / "judge_frames"; fd.mkdir(exist_ok=True)
        paths = []
        for tag, r in (("best", b), ("worst", w)):
            for end, idx in (("open", r["_f"][0]), ("closed", r["_f"][1])):
                p = fd / f"{tag}_rep{r['rep']}_{end}.jpg"; save_frame(video, idx, p, f"{tag.upper()} rep {r['rep']} {end}")
                paths.append(str(p))
        table = json.dumps({k: v for k, v in rec["analysis"].items()} | {"reps": rec["reps"]}, indent=0)
        prompt = (f"Clip {clip.name}. Moving joint: {a['joint']} angle in degrees (open = most extended, closed = most bent). "
                  f"Best rep (baseline) = rep {b['rep']}, worst = rep {w['rep']}.\nREP TABLE:\n{table}\n\nKEY FRAMES:\n" + "\n".join(paths))
        t0 = time.time()
        for _ in range(2):
            try:
                text, cost = claude(prompt, fd)
                rec["verdict"] = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
                rec["verdict"]["by"] = MODEL; rec["run"] = {"wall_s": round(time.time() - t0, 1), "cost_usd": cost}
                break
            except Exception as e:  # noqa: BLE001
                rec["error"] = str(e)
    (d / "judge.json").write_text(json.dumps(rec, indent=1))
    v = rec.get("verdict", {})
    print(f"{clip.stem}: {v.get('verdict')} | {v.get('reason')} | {v.get('detail')}", flush=True)


if __name__ == "__main__":
    for c in sys.argv[1:]:
        try:
            judge(c)
        except Exception as e:  # noqa: BLE001
            print(f"{Path(c).stem}: ERROR {e}", flush=True)
