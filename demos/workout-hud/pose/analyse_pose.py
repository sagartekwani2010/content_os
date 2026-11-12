"""Turn a side-on lifting clip into pose data for the Workout HUD.

Usage: python analyse.py CLIP.mp4 OUT_DIR [--weights yolo11n-pose.pt]
Writes OUT_DIR/set-1.mp4 (web-ready H.264, 720 px wide max) and OUT_DIR/pose.json.

Everything in pose.json is measured from the clip. Nothing is estimated by hand.
"""
import json, math, subprocess, sys
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

# COCO keypoint indices: (shoulder, hip, knee, ankle, ear) for left and right
SIDES = {"left": (5, 11, 13, 15, 3), "right": (6, 12, 14, 16, 4)}


def angle(a, b, c):
    """Interior angle at b, in degrees."""
    v1, v2 = np.subtract(a, b), np.subtract(c, b)
    cos = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)
    return math.degrees(math.acos(float(np.clip(cos, -1, 1))))


def lean(shoulder, hip):
    """Torso angle from vertical, in degrees (0 = upright)."""
    dx, dy = shoulder[0] - hip[0], hip[1] - shoulder[1]
    return abs(math.degrees(math.atan2(dx, dy + 1e-9)))


def smooth(x, k=5):
    pad = np.pad(np.asarray(x, float), (k // 2, k // 2), mode="edge")
    return np.convolve(pad, np.ones(k) / k, mode="valid")


def main(clip, out_dir, weights="yolo11n-pose.pt"):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    web = out / "set-1.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", clip, "-an", "-vf", "scale='min(720,iw)':-2,fps=30",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26", "-movflags", "+faststart", str(web)], check=True)

    cap = cv2.VideoCapture(str(web))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w, h = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    model = YOLO(weights)
    raw, conf_sum = [], {"left": 0.0, "right": 0.0}
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        r = model(frame, verbose=False)[0]
        kp = None
        if r.keypoints is not None and len(r.keypoints) > 0:
            # keep the largest person in frame
            areas = (r.boxes.xywh[:, 2] * r.boxes.xywh[:, 3]).cpu().numpy()
            kp = r.keypoints.data[int(areas.argmax())].cpu().numpy()  # 17 x (x, y, conf)
            for s, idx in SIDES.items():
                conf_sum[s] += float(kp[list(idx[:4]), 2].mean())
        raw.append((i / fps, kp)); i += 1
    cap.release()

    side = max(conf_sum, key=conf_sum.get)
    S, H, K, A, E = SIDES[side]
    frames, missed = [], 0
    for t, kp in raw:
        if kp is None or kp[[S, H, K, A], 2].min() < 0.3:
            missed += 1
            continue
        p = lambda n: [float(kp[n, 0] / w), float(kp[n, 1] / h)]
        px = lambda n: (kp[n, 0], kp[n, 1])
        frames.append({"t": round(t, 3), "knee": angle(px(H), px(K), px(A)), "lean": lean(px(S), px(H)),
                       "j": {"ankle": p(A), "knee": p(K), "hip": p(H), "shoulder": p(S), "head": p(E)}})
    if len(frames) < 10:
        sys.exit(f"Pose not found reliably: {len(frames)} usable frames of {len(raw)}.")

    knee = smooth([f["knee"] for f in frames]); ln = smooth([f["lean"] for f in frames])
    top, bottom = float(np.percentile(knee, 90)), float(np.percentile(knee, 10))
    down_at, up_at = top - 0.5 * (top - bottom), top - 0.2 * (top - bottom)
    reps, rep, in_rep, cur = [], 0, False, None
    for f, k, l in zip(frames, knee, ln):
        f["knee"], f["lean"] = round(float(k), 1), round(float(l), 1)
        if not in_rep and k < down_at:
            in_rep, rep = True, rep + 1
            cur = {"n": rep, "knee_min": 999.0, "lean_max": 0.0, "t0": f["t"]}
        if in_rep:
            cur["knee_min"] = min(cur["knee_min"], float(k)); cur["lean_max"] = max(cur["lean_max"], float(l))
            if k > up_at:
                in_rep = False; cur["t1"] = f["t"]
                reps.append({a: (round(b, 1) if isinstance(b, float) else b) for a, b in cur.items()})
        f["rep"] = max(1, rep)
    if in_rep and cur:  # clip ended mid-rep
        reps.append({a: (round(b, 1) if isinstance(b, float) else b) for a, b in cur.items()})

    result = {"fps": fps, "side": side, "frames": frames, "reps": reps,
              "quality": {"frames_total": len(raw), "frames_missed": missed,
                          "missed_pct": round(100 * missed / max(1, len(raw)), 1)}}
    (out / "pose.json").write_text(json.dumps(result))
    print(json.dumps({"side": side, "reps": reps, "quality": result["quality"],
                      "knee_range": [round(bottom, 1), round(top, 1)]}, indent=1))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    wts = sys.argv[sys.argv.index("--weights") + 1] if "--weights" in sys.argv else "yolo11n-pose.pt"
    main(args[0], args[1], wts)
