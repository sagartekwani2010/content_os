"""Hero visuals for Gym Jarvis Ep 3, drawn from real pose data (nothing is animated by hand).

  keypoints  CLIP                      -> data/<stem>/kp.npz (17 joints x (x, y, conf) per frame, 30 fps)
  lockon     CLIP --t0 S --dur S        skeleton locks on: joints ping in one by one, bones draw like pen strokes
  wave       CLIP --t0 S --dur S        knee leaves a trail that unrolls into the knee-angle wave; reps counted
  ghost      CLIP --rep N --best CLIP2 --best-rep M   best rep as a green ghost over rep N; depth gap in red
  reps       CLIP                       print the cleaned rep table (guardrail applied)

Usage: demos/workout-hud/.venv/bin/python demos/workout-hud/visuals/pose_fx.py MODE CLIP [options]
Outputs go to demos/workout-hud/data/<stem>/fx/ (gitignored). 1080 x 1920, 30 fps, H.264.
"""
import argparse, json, math, subprocess, sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
WEIGHTS = ROOT / "pose" / "yolo11n-pose.pt"
FONTS = Path.home() / ".cache" / "content_os" / "fonts"
W, H, FPS = 1080, 1920, 30

# Series palette (content_os/visuals/palette.py, dark board), RGB
YELLOW, BLUE, GREEN, RED, ORANGE, PURPLE = (255, 212, 59), (77, 155, 255), (47, 214, 127), (255, 77, 61), (255, 159, 46), (183, 124, 255)
INK, GREY = (243, 240, 232), (140, 146, 158)

# COCO keypoints
NAMES = ["nose", "l_eye", "r_eye", "l_ear", "r_ear", "l_sh", "r_sh", "l_el", "r_el", "l_wr", "r_wr",
         "l_hip", "r_hip", "l_knee", "r_knee", "l_ank", "r_ank"]
BONES = [(5, 6), (5, 7), (7, 9), (6, 8), (8, 10), (5, 11), (6, 12), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
         (0, 1), (0, 2), (1, 3), (2, 4)]
LEFT = {1, 3, 5, 7, 9, 11, 13, 15}
LOCK_ORDER = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]  # head first, feet last
SIDES = {"left": (5, 11, 13, 15), "right": (6, 12, 14, 16)}
CONF_MIN = 0.4           # guardrail: below this a joint is "can't see"
KNEE_MIN_POSSIBLE = 30   # guardrail: a knee angle below this is physically impossible on these lifts


def font(size, kind="Kalam-Bold.ttf"):
    try:
        return ImageFont.truetype(str(FONTS / kind), size)
    except OSError:
        return ImageFont.load_default()


# ---------------------------------------------------------------- data
def keypoints(clip):
    """Run YOLO pose once per clip at 30 fps, 1080 x 1920; cache all 17 joints."""
    clip = Path(clip).resolve(); out = DATA / clip.stem; out.mkdir(parents=True, exist_ok=True)
    cache, video = out / "kp.npz", out / "src_1080.mp4"
    if cache.exists() and video.exists():
        return np.load(cache)["kp"], video
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-an", "-vf",
                    f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(video)], check=True)
    from ultralytics import YOLO
    model, cap, kps = YOLO(str(WEIGHTS)), cv2.VideoCapture(str(video)), []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        r = model(fr, verbose=False)[0]
        if r.keypoints is not None and len(r.keypoints) > 0:
            areas = (r.boxes.xywh[:, 2] * r.boxes.xywh[:, 3]).cpu().numpy()
            kps.append(r.keypoints.data[int(areas.argmax())].cpu().numpy())
        else:
            kps.append(np.zeros((17, 3), np.float32))
    kp = np.stack(kps); np.savez_compressed(cache, kp=kp)
    return kp, video


def smooth_kp(kp, k=5):
    """Centred moving average on x, y where the joint is visible; conf kept as is."""
    out = kp.copy(); n = len(kp)
    for j in range(17):
        vis = kp[:, j, 2] >= CONF_MIN
        for i in range(n):
            lo, hi = max(0, i - k // 2), min(n, i + k // 2 + 1)
            m = vis[lo:hi]
            if m.any():
                out[i, j, :2] = kp[lo:hi, j, :2][m].mean(0)
    return out


def angle(a, b, c):
    v1, v2 = a - b, c - b
    cos = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)
    return math.degrees(math.acos(float(np.clip(cos, -1, 1))))


def knee_series(kp):
    """Knee angle per frame on the better-seen side, with the guardrail applied.
    Returns (angles with NaN where rejected, side, reasons per frame)."""
    side = max(SIDES, key=lambda s: kp[:, list(SIDES[s]), 2].mean())
    _, hip, knee, ank = SIDES[side]
    ang, why = np.full(len(kp), np.nan), [None] * len(kp)
    for i, f in enumerate(kp):
        hidden = [NAMES[j] for j in (hip, knee, ank) if f[j, 2] < CONF_MIN]
        if hidden:
            why[i] = "hidden: " + ", ".join(hidden); continue
        a = angle(f[hip, :2], f[knee, :2], f[ank, :2])
        if a < KNEE_MIN_POSSIBLE:
            why[i] = f"impossible: {a:.0f} deg"; continue
        ang[i] = a
    # short gaps (< 0.3 s) are interpolated for drawing; longer gaps stay NaN
    s = ang.copy(); idx = np.arange(len(s)); good = ~np.isnan(s)
    if good.sum() > 2:
        filled = np.interp(idx, idx[good], s[good])
        gap_start = None
        for i in range(len(s) + 1):
            g = i < len(s) and np.isnan(s[i])
            if g and gap_start is None:
                gap_start = i
            elif not g and gap_start is not None:
                if i - gap_start < 0.3 * FPS and gap_start > 0 and i < len(s):
                    s[gap_start:i] = filled[gap_start:i]
                gap_start = None
    k = 5; pad = np.pad(s, (k // 2, k // 2), mode="edge")
    sm = np.array([np.nanmean(pad[i:i + k]) if not np.isnan(s[i]) else np.nan for i in range(len(s))])
    return sm, side, why


def find_reps(ang, min_s=0.8):
    """Hysteresis rep counter on the cleaned knee angle. A rep must last >= min_s and reach the bottom band."""
    v = ang[~np.isnan(ang)]
    top, bot = np.percentile(v, 90), np.percentile(v, 10)
    down, up = top - 0.5 * (top - bot), top - 0.2 * (top - bot)
    reps, cur = [], None
    for i, a in enumerate(ang):
        if np.isnan(a):
            continue
        if cur is None and a < down:
            cur = {"i0": i, "imin": i, "min": a}
        elif cur is not None:
            if a < cur["min"]:
                cur["min"], cur["imin"] = a, i
            if a > up:
                cur["i1"] = i
                if (i - cur["i0"]) / FPS >= min_s:
                    reps.append(cur)
                cur = None
    for n, r in enumerate(reps, 1):
        r["n"] = n; r["t0"], r["t1"], r["t_bottom"] = r["i0"] / FPS, r["i1"] / FPS, r["imin"] / FPS
        r["depth"] = round(float(r["min"]), 1)
    return reps, (top, bot)


# ---------------------------------------------------------------- drawing
def px(f, j):
    return (float(f[j, 0]), float(f[j, 1]))


def rough_line(d, a, b, col, w, seed, p=1.0):
    """Two slightly offset strokes, drawn to fraction p: a hand-drawn marker line."""
    rng = np.random.default_rng(seed)
    ex = (a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p)
    for k in range(2):
        o = rng.normal(0, 1.6, 4)
        d.line([(a[0] + o[0], a[1] + o[1]), (ex[0] + o[2], ex[1] + o[3])], fill=col + (255 if k == 0 else 150,), width=w - 2 * k)


def near_side(f):
    l = f[[5, 11, 13, 15], 2].mean(); r = f[[6, 12, 14, 16], 2].mean()
    return LEFT if l >= r else set(range(17)) - LEFT - {0}


def draw_skeleton(d, f, col=BLUE, joint=YELLOW, alpha=255, w=9, bone_p=None, joints_on=None, seed=0):
    near = near_side(f) | {0}
    far = lambda j: j not in near
    for bi, (a, b) in enumerate(BONES):
        p = 1.0 if bone_p is None else bone_p[bi]
        if p <= 0:
            continue
        hidden = f[a, 2] < CONF_MIN or f[b, 2] < CONF_MIN
        c = GREY if hidden else col
        if (far(a) or far(b)) and a not in (5, 6) or alpha < 255:
            fa = min(alpha, 90) if (far(a) or far(b)) else alpha
            ex = (px(f, a)[0] + (px(f, b)[0] - px(f, a)[0]) * p, px(f, a)[1] + (px(f, b)[1] - px(f, a)[1]) * p)
            d.line([px(f, a), ex], fill=c + (fa,), width=max(3, w // 2) if fa < alpha else w)
        else:
            rough_line(d, px(f, a), px(f, b), c, w, seed + bi, p)
    for j in range(17):
        if joints_on is not None and j not in joints_on:
            continue
        x, y = px(f, j); hidden = f[j, 2] < CONF_MIN
        r = 8 if j in (1, 2, 3, 4) else 13
        a = min(alpha, 110) if far(j) else alpha
        d.ellipse([x - r, y - r, x + r, y + r], fill=(GREY if hidden else joint) + (a,), outline=(20, 20, 20, a), width=3)


def label(d, xy, text, col, size=54, bg=(15, 17, 23, 210), anchor="la"):
    f = font(size); bb = d.textbbox(xy, text, font=f, anchor=anchor)
    d.rounded_rectangle([bb[0] - 16, bb[1] - 10, bb[2] + 16, bb[3] + 12], 14, fill=bg)
    d.text(xy, text, font=f, fill=col, anchor=anchor)


class Writer:
    def __init__(self, path):
        self.p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                   "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                                   "-movflags", "+faststart", str(path)], stdin=subprocess.PIPE)

    def add(self, img):
        self.p.stdin.write(img.convert("RGB").tobytes())

    def close(self):
        self.p.stdin.close(); self.p.wait()


def frames(video, i0, n):
    cap = cv2.VideoCapture(str(video)); cap.set(cv2.CAP_PROP_POS_FRAMES, i0)
    for _ in range(n):
        ok, fr = cap.read()
        if not ok:
            break
        yield Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    cap.release()


def dim(img, k=0.62):
    return Image.blend(Image.new("RGBA", img.size, (10, 12, 18, 255)), img, k)


def ease(p):
    p = min(1, max(0, p)); return 1 - (1 - p) ** 3


# ---------------------------------------------------------------- effects
def fx_lockon(clip, t0, dur, out):
    kp, video = keypoints(clip); kp = smooth_kp(kp)
    i0, n = int(t0 * FPS), int(dur * FPS)
    lock_t, bones_t = 1.3, 1.0
    wr = Writer(out)
    for k, img in enumerate(frames(video, i0, n)):
        t = k / FPS; f = kp[i0 + k]
        img = dim(img, 0.55 + 0.45 * (1 - ease(t / 0.6)) if t < 0.6 else 0.55)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        on = [j for q, j in enumerate(LOCK_ORDER) if t >= 0.3 + q * lock_t / len(LOCK_ORDER)]
        bp = [ease((t - 0.3 - lock_t - bi * 0.05) / (bones_t * 0.6)) for bi in range(len(BONES))]
        draw_skeleton(d, f, bone_p=bp, joints_on=on, seed=i0 + k)
        for q, j in enumerate(LOCK_ORDER):  # ping rings as each joint lands
            tl = 0.3 + q * lock_t / len(LOCK_ORDER); a = (t - tl) / 0.45
            if 0 <= a < 1 and f[j, 2] >= CONF_MIN:
                x, y = px(f, j); r = 14 + 46 * ease(a)
                d.ellipse([x - r, y - r, x + r, y + r], outline=YELLOW + (int(255 * (1 - a)),), width=4)
        if len(on):
            label(d, (60, 120), f"{len(on)} / 17 joints", YELLOW, 64)
        if t > 0.3 + lock_t + bones_t:
            label(d, (60, 220), "every frame, 30 times a second", INK, 44)
        wr.add(Image.alpha_composite(img, ov))
    wr.close()


def fx_wave(clip, t0, dur, out):
    kp, video = keypoints(clip); kp = smooth_kp(kp)
    ang, side, why = knee_series(kp); reps, (top, bot) = find_reps(ang)
    _, hip, knee, ank = SIDES[side]
    i0, n = int(t0 * FPS), int(dur * FPS)
    gx0, gx1, gy0, gy1 = 70, W - 70, 1380, 1780     # graph box (bottom of frame)
    span = n                                           # graph shows the whole effect window
    amin, amax = max(KNEE_MIN_POSSIBLE, bot - 15), min(180, top + 10)
    gy = lambda a: gy0 + (amax - a) / (amax - amin) * (gy1 - gy0)
    gx = lambda i: gx0 + (i - i0) / span * (gx1 - gx0)
    wr = Writer(out); trail = []
    for k, img in enumerate(frames(video, i0, n)):
        i = i0 + k; f = kp[i]; img = dim(img, 0.6)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        draw_skeleton(d, f, alpha=110, w=6)
        # knee trail
        if f[knee, 2] >= CONF_MIN:
            trail.append(px(f, knee))
        trail = trail[-18:]
        for q in range(1, len(trail)):
            d.line([trail[q - 1], trail[q]], fill=ORANGE + (int(255 * q / len(trail)),), width=4 + q // 2)
        if f[knee, 2] >= CONF_MIN:
            x, y = px(f, knee); d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=ORANGE + (255,), outline=(20, 20, 20, 255), width=4)
            if not np.isnan(ang[i]):
                label(d, (x + 36, y - 30), f"{ang[i]:.0f}°", ORANGE, 58)
        # graph
        d.rounded_rectangle([gx0 - 30, gy0 - 90, gx1 + 30, gy1 + 40], 26, fill=(15, 17, 23, 215))
        d.text((gx0, gy0 - 76), "knee angle", font=font(42), fill=INK)
        pts = [(gx(j), gy(ang[j])) for j in range(i0, i + 1) if not np.isnan(ang[j])]
        for q in range(1, len(pts)):
            if pts[q][0] - pts[q - 1][0] < 12:
                d.line([pts[q - 1], pts[q]], fill=ORANGE + (255,), width=7)
        for j in range(i0, i + 1):  # guardrail: rejected frames marked grey
            if why[j]:
                d.line([(gx(j), gy0), (gx(j), gy1)], fill=GREY + (70,), width=3)
        if pts:
            d.ellipse([pts[-1][0] - 11, pts[-1][1] - 11, pts[-1][0] + 11, pts[-1][1] + 11], fill=ORANGE + (255,))
        counted = [r for r in reps if i0 <= r["imin"] and r["i1"] <= i]
        for r in counted:
            x, y = gx(r["imin"]), gy(r["min"])
            d.ellipse([x - 28, y + 8, x + 28, y + 64], fill=BLUE + (255,))
            d.text((x, y + 36), str(r["n"]), font=font(40, "PatrickHand-Regular.ttf"), fill=(255, 255, 255), anchor="mm")
        label(d, (60, 120), f"reps: {len(counted)}", BLUE, 76)
        if why[i]:
            label(d, (60, 240), f"can't see: {why[i].split(': ')[1]}" if why[i].startswith("hidden") else "impossible angle, thrown out", GREY, 46)
        wr.add(Image.alpha_composite(img, ov))
    wr.close()


def norm_pose(f, side):
    """Pose relative to the hip, scaled by thigh length, so two different clips can be overlaid."""
    _, hip, knee, _ = SIDES[side]
    o = f[hip, :2]; s = np.linalg.norm(f[knee, :2] - o) + 1e-6
    return (f[:, :2] - o) / s, o, s


def fx_ghost(clip, rep, best_clip, best_rep, out, hold_s=1.2):
    kp, video = keypoints(clip); kp = smooth_kp(kp)
    ang, side, _ = knee_series(kp); reps, _ = find_reps(ang)
    bkp, _ = keypoints(best_clip); bkp = smooth_kp(bkp)
    bang, bside, _ = knee_series(bkp); breps, _ = find_reps(bang)
    r, br = reps[rep - 1], breps[best_rep - 1]
    _, hip, knee, ank = SIDES[side]
    n = r["i1"] - r["i0"]; wr = Writer(out); last = None
    for k, img in enumerate(frames(video, r["i0"], n)):
        i = r["i0"] + k; f = kp[i]
        bi = br["i0"] + int(round(k / n * (br["i1"] - br["i0"])))  # time-normalised: same phase of the rep
        g, _, _ = norm_pose(bkp[bi], bside); _, o, s = norm_pose(f, side)
        if bside != side:
            g[:, 0] *= -1
        gf = np.concatenate([g * s + o, np.ones((17, 1))], 1)
        img = dim(img, 0.62); ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        draw_skeleton(d, gf, col=GREEN, joint=GREEN, alpha=130, w=14)
        draw_skeleton(d, f, w=8, seed=i)
        gap = ang[i] - bang[bi] if not (np.isnan(ang[i]) or np.isnan(bang[bi])) else 0
        if gap > 5:  # shallower than the best rep at the same phase: fill the gap red
            d.polygon([px(f, hip), px(f, knee), (gf[knee, 0], gf[knee, 1])], fill=RED + (140,))
        label(d, (60, 120), "ghost = my best rep", GREEN, 56)
        label(d, (60, 220), f"rep {rep}", INK, 56)
        if gap > 5:
            label(d, (60, 320), f"{gap:.0f}° short of my best", RED, 60)
        last = Image.alpha_composite(img, ov); wr.add(last)
    if last is not None:  # hold the last frame with the verdict stamp
        d = ImageDraw.Draw(last)
        gap_bottom = r["min"] - br["min"]
        for _ in range(int(hold_s * FPS)):
            wr.add(last)
    wr.close()
    return {"rep": rep, "depth": r["depth"], "best_depth": br["depth"], "gap_at_bottom": round(float(r["min"] - br["min"]), 1)}


def cmd_reps(clip):
    kp, _ = keypoints(clip); kp = smooth_kp(kp)
    ang, side, why = knee_series(kp); reps, (top, bot) = find_reps(ang)
    rejected = sum(1 for w in why if w)
    out = {"clip": Path(clip).name, "side": side, "reps": [{k: (round(v, 2) if isinstance(v, float) else v)
            for k, v in r.items() if k in ("n", "t0", "t1", "t_bottom", "depth")} for r in reps],
           "frames": len(kp), "rejected_frames": rejected, "rejected_pct": round(100 * rejected / len(kp), 1),
           "reject_reasons": {k: sum(1 for w in why if w and w.startswith(k)) for k in ("hidden", "impossible")}}
    (DATA / Path(clip).stem / "reps_clean.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["keypoints", "lockon", "wave", "ghost", "reps"])
    ap.add_argument("clip")
    ap.add_argument("--t0", type=float, default=0); ap.add_argument("--dur", type=float, default=6)
    ap.add_argument("--rep", type=int); ap.add_argument("--best"); ap.add_argument("--best-rep", type=int)
    a = ap.parse_args()
    fx = DATA / Path(a.clip).stem / "fx"; fx.mkdir(parents=True, exist_ok=True)
    if a.mode == "keypoints":
        kp, _ = keypoints(a.clip); print(kp.shape)
    elif a.mode == "reps":
        cmd_reps(a.clip)
    elif a.mode == "lockon":
        fx_lockon(a.clip, a.t0, a.dur, fx / f"lockon_{a.t0:g}.mp4"); print(fx / f"lockon_{a.t0:g}.mp4")
    elif a.mode == "wave":
        fx_wave(a.clip, a.t0, a.dur, fx / f"wave_{a.t0:g}.mp4"); print(fx / f"wave_{a.t0:g}.mp4")
    elif a.mode == "ghost":
        print(json.dumps(fx_ghost(a.clip, a.rep, a.best, a.best_rep, fx / f"ghost_rep{a.rep}.mp4")))
