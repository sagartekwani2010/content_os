"""Iron Man-style (JARVIS HUD) hero visuals for Gym Jarvis Ep 3. Every overlay is drawn from measured pose data.

Data comes from pose_fx (cached YOLO keypoints) and judge/judge.py (rep table + Fable verdict).

  lockon  CLIP --t0 --dur          targeting brackets close in, 17 joints lock on, bones draw in
  wave    CLIP --t0 --dur          knee telemetry: glowing trail -> live angle graph -> rep counter; hidden joints flagged
  ghost   CLIP --best-rep --rep    best rep as a green hologram over the worst rep; gap fills red; verdict stamp
  sway    CLIP --t0 --dur          torso sway gauge (shoulder-hip line vs vertical); verdict stamp
  all     render the Ep 3 set (see EP3 below)

Outputs: demos/workout-hud/data/<stem>/hud/*.mp4, 1080x1920 30 fps. Bottom 20% kept clear for Instagram's overlay.
"""
import argparse, json, math, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "judge"))
import pose_fx as P  # noqa: E402
import judge as J    # noqa: E402

W, H, FPS = P.W, P.H, P.FPS
CYAN, CYAN_D = (53, 224, 255), (20, 120, 160)
AMBER, RED, GREEN, WHITE = (255, 178, 62), (255, 59, 48), (61, 255, 168), (235, 250, 255)
GREY = (110, 130, 140)
SAFE_BOTTOM = int(H * 0.80)
CROP = {"on": False, "y0": 0}   # panel mode: 1080x960 crop around the body


def panel_mode(kp):
    """Switch to the 1080x960 top-panel format, cropped around the body's median centre."""
    global H, SAFE_BOTTOM
    ys = []
    for f in kp:
        v = f[f[:, 2] >= P.CONF_MIN]
        if len(v):
            ys.append((v[:, 1].min() + v[:, 1].max()) / 2)
    cy = float(np.median(ys)) if ys else P.H / 2
    CROP.update(on=True, y0=int(min(max(cy - 450, 0), P.H - 960)))
    H = 960; SAFE_BOTTOM = 960 - 100; P.H = 960


def prep(img, f):
    """Crop the frame and shift keypoints when in panel mode."""
    if not CROP["on"]:
        return img, f
    g = f.copy(); g[:, 1] -= CROP["y0"]
    return img.crop((0, CROP["y0"], W, CROP["y0"] + 960)), g
F = P.FONTS


def hf(size, bold=True):
    try:
        return ImageFont.truetype(str(F / ("BarlowCondensed-ExtraBold.ttf" if bold else "BarlowCondensed-SemiBold.ttf")), size)
    except OSError:
        return ImageFont.load_default()


def ease(p):
    p = min(1, max(0, p)); return 1 - (1 - p) ** 3


def grade(img):
    """Cool HUD grade: darken, push to blue-teal, light scanlines."""
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    lum = a.mean(2, keepdims=True)
    a = 0.55 * a + 0.25 * lum * np.array([0.55, 0.85, 1.05])
    a[::4] *= 0.88
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def glow(layer, r=9):
    """Additive glow: blurred copy under the sharp layer."""
    g = layer.filter(ImageFilter.GaussianBlur(r))
    return Image.alpha_composite(g, layer)


def brackets(d, box, col, L=46, w=5, a=255):
    x0, y0, x1, y1 = box
    for (x, y, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(x, y), (x + dx * L, y)], fill=col + (a,), width=w); d.line([(x, y), (x, y + dy * L)], fill=col + (a,), width=w)


def panel(d, xy, lines, col=CYAN, size=58, sub=None):
    """HUD readout: thin frame with corner brackets, uppercase condensed text."""
    x, y = xy; f = hf(size); fs = hf(int(size * 0.5), bold=False)
    w = max(d.textlength(t, font=f) for t in lines) + 48
    h = len(lines) * (size + 6) + (int(size * 0.62) if sub else 0) + 26
    d.rectangle([x, y, x + w, y + h], fill=(4, 18, 28, 170), outline=col + (90,), width=2)
    brackets(d, (x, y, x + w, y + h), col, L=18, w=4)
    yy = y + 10
    if sub:
        d.text((x + 24, yy), sub.upper(), font=fs, fill=col + (200,)); yy += int(size * 0.62)
    for t in lines:
        d.text((x + 24, yy), t.upper(), font=f, fill=WHITE + (255,)); yy += size + 6
    return (x, y, x + w, y + h)


def ring(d, c, r, t, col, a=220, w=4, gaps=3):
    """Rotating segmented ring around a joint."""
    x, y = c; seg = 360 / gaps
    for k in range(gaps):
        s = (t * 120 + k * seg) % 360
        d.arc([x - r, y - r, x + r, y + r], s, s + seg * 0.62, fill=col + (a,), width=w)


def skeleton(d, f, col=CYAN, alpha=255, w=6, bone_p=None, joints_on=None):
    near = P.near_side(f) | {0}
    for bi, (a, b) in enumerate(P.BONES):
        p = 1.0 if bone_p is None else bone_p[bi]
        if p <= 0:
            continue
        hidden = f[a, 2] < P.CONF_MIN or f[b, 2] < P.CONF_MIN
        far = a not in near or b not in near
        c = GREY if hidden else col; al = int(alpha * (0.35 if far else 1))
        A, B = P.px(f, a), P.px(f, b); E = (A[0] + (B[0] - A[0]) * p, A[1] + (B[1] - A[1]) * p)
        d.line([A, E], fill=c + (al,), width=w if not far else max(2, w // 2))
    for j in range(17):
        if joints_on is not None and j not in joints_on:
            continue
        x, y = P.px(f, j); hidden = f[j, 2] < P.CONF_MIN
        al = int(alpha * (0.4 if j not in near else 1)); r = 6 if j in (1, 2, 3, 4) else 10
        c = GREY if hidden else WHITE
        d.ellipse([x - r, y - r, x + r, y + r], outline=(GREY if hidden else col) + (al,), width=3, fill=c + (al // 2,))


def body_box(f):
    v = f[f[:, 2] >= P.CONF_MIN]
    if not len(v):
        return (W * .2, H * .2, W * .8, H * .7)
    return (v[:, 0].min() - 60, v[:, 1].min() - 80, v[:, 0].max() + 60, v[:, 1].max() + 60)


def stamp(img, verdict, reason, p):
    """Verdict stamp: STOP red, HOLD amber, CONTINUE green. p = 0..1 slam-in progress."""
    col = {"STOP": RED, "HOLD": AMBER, "CONTINUE": GREEN, "CHECK FOOTAGE": AMBER}.get(verdict, GREY)
    img = Image.alpha_composite(img, Image.new("RGBA", img.size, (0, 0, 0, int(110 * min(1, p)))))
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    base = 230
    while base > 60 and ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(verdict, font=hf(base)) > W - 200:
        base -= 10  # fit long verdicts (CHECK FOOTAGE) inside the frame
    s = 1.6 - 0.6 * ease(p); f = hf(int(base * s)); cx, cy = W // 2, int(H * 0.42)
    tw = d.textlength(verdict, font=f); th = int(base * s)
    box = (cx - tw / 2 - 50, cy - th / 2 - 30, cx + tw / 2 + 50, cy + th / 2 + 40)
    d.rectangle(box, outline=col + (255,), width=12, fill=(10, 0, 0, 120) if verdict == "STOP" else (0, 10, 6, 120))
    d.text((cx, cy), verdict, font=f, fill=col + (255,), anchor="mm")
    if p >= 1 and reason:
        f2 = hf(70); d.text((cx, box[3] + 70), reason.upper(), font=f2, fill=WHITE + (255,), anchor="mm")
    ov = ov.rotate(-6 if verdict == "STOP" else 0, center=(cx, cy), resample=Image.BICUBIC)
    return Image.alpha_composite(img, glow(ov, 12))


def write(out, gen):
    wr = P.Writer(out)
    for im in gen:
        wr.add(im)
    wr.close(); print(out, flush=True)


# ------------------------------------------------------------------ effects
def lockon(clip, t0, dur, out):
    kp, video = P.keypoints(clip); kp = P.smooth_kp(kp); i0 = int(t0 * FPS)
    def gen():
        for k, img in enumerate(P.frames(video, i0, int(dur * FPS))):
            t = k / FPS; img, f = prep(grade(img), kp[i0 + k])
            ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            bx = body_box(f); q = ease(t / 0.7)
            big = (40, 160, W - 40, SAFE_BOTTOM - 40)
            cur = tuple(big[i] + (bx[i] - big[i]) * q for i in range(4))
            brackets(d, cur, CYAN, L=70, w=6)
            if t < 0.7:
                y = 160 + (SAFE_BOTTOM - 200) * (t / 0.7); d.line([(40, y), (W - 40, y)], fill=CYAN + (160,), width=3)
            on = [j for n, j in enumerate(P.LOCK_ORDER) if t >= 0.7 + n * 0.07]
            bp = [ease((t - 0.7 - 17 * 0.07 - bi * 0.04) / 0.35) for bi in range(len(P.BONES))]
            skeleton(d, f, bone_p=bp, joints_on=on)
            for n, j in enumerate(P.LOCK_ORDER):
                a = (t - (0.7 + n * 0.07)) / 0.4
                if 0 <= a < 1 and f[j, 2] >= P.CONF_MIN:
                    x, y = P.px(f, j); r = 12 + 40 * ease(a)
                    d.ellipse([x - r, y - r, x + r, y + r], outline=CYAN + (int(255 * (1 - a)),), width=3)
            panel(d, (60, 110), [f"{len(on)} / 17 JOINTS"], sub="target acquired" if len(on) == 17 else "scanning")
            if t > 2.6:
                panel(d, (60, 300), ["30 FRAMES / SEC"], size=44, sub="tracking")
            yield Image.alpha_composite(img, glow(ov))
    write(out, gen())


def wave(clip, t0, dur, out):
    kp, video = P.keypoints(clip); kp = P.smooth_kp(kp)
    ang, side, why = P.knee_series(kp); reps, (top, bot) = P.find_reps(ang)
    _, hip, knee, ank = P.SIDES[side]; i0, n = int(t0 * FPS), int(dur * FPS)
    gx0, gx1, gy0, gy1 = 90, W - 90, SAFE_BOTTOM - 250, SAFE_BOTTOM - 40
    amin, amax = max(30, bot - 15), min(180, top + 10)
    gy = lambda a: gy0 + (amax - a) / (amax - amin) * (gy1 - gy0); gx = lambda i: gx0 + (i - i0) / n * (gx1 - gx0)
    def gen():
        trail = []
        for k, img in enumerate(P.frames(video, i0, n)):
            i = i0 + k; t = k / FPS; img, f = prep(grade(img), kp[i])
            ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            skeleton(d, f, alpha=150, w=4)
            if f[knee, 2] >= P.CONF_MIN:
                trail.append(P.px(f, knee))
            trail[:] = trail[-20:]
            for q in range(1, len(trail)):
                d.line([trail[q - 1], trail[q]], fill=CYAN + (int(255 * q / len(trail)),), width=3 + q // 3)
            if f[knee, 2] >= P.CONF_MIN:
                x, y = P.px(f, knee); ring(d, (x, y), 34, t, CYAN); ring(d, (x, y), 50, -t, AMBER, a=160, w=3, gaps=4)
                if not np.isnan(ang[i]):
                    d.text((x + 64, y - 40), f"{ang[i]:.0f}°", font=hf(72), fill=WHITE + (255,))
            # telemetry graph
            d.rectangle([gx0 - 30, gy0 - 80, gx1 + 30, gy1 + 30], fill=(4, 18, 28, 185), outline=CYAN + (90,), width=2)
            brackets(d, (gx0 - 30, gy0 - 80, gx1 + 30, gy1 + 30), CYAN, L=22, w=4)
            d.text((gx0, gy0 - 66), "KNEE ANGLE // LIVE", font=hf(40, False), fill=CYAN + (220,))
            for gl in range(5):
                yy = gy0 + gl * (gy1 - gy0) / 4; d.line([(gx0, yy), (gx1, yy)], fill=CYAN_D + (70,), width=1)
            for j in range(i0, i + 1):
                if why[j]:
                    d.line([(gx(j), gy0), (gx(j), gy1)], fill=RED + (55,), width=3)
            pts = [(gx(j), gy(ang[j])) for j in range(i0, i + 1) if not np.isnan(ang[j])]
            for q in range(1, len(pts)):
                if pts[q][0] - pts[q - 1][0] < 12:
                    d.line([pts[q - 1], pts[q]], fill=CYAN + (255,), width=6)
            counted = [r for r in reps if i0 <= r["imin"] and r["i1"] <= i]
            for r in counted:
                x, y = gx(r["imin"]), gy(r["min"])
                d.ellipse([x - 24, y + 10, x + 24, y + 58], outline=AMBER + (255,), width=4)
                d.text((x, y + 34), str(r["n"]), font=hf(36), fill=AMBER + (255,), anchor="mm")
            panel(d, (60, 110), [f"REPS {len(counted)}"], sub="rep counter")
            if why[i]:
                panel(d, (60, 330), [f"CAN'T SEE YOUR {why[i].split(': ')[1].split(',')[0].upper().replace('R_','').replace('L_','')}" if why[i].startswith("hidden") else "IMPOSSIBLE ANGLE: REJECTED"],
                      col=RED, size=46, sub="safety check")
            yield Image.alpha_composite(img, glow(ov, 7))
    write(out, gen())


def _judge_reps(clip):
    kp, video = P.keypoints(clip); kp = P.smooth_kp(kp); a = J.analyse(kp)
    return kp, video, a


def ghost(clip, rep, best_rep, out, verdict=None, reason=None, hold_s=2.0, slow=2, loops=2):
    kp, video, a = _judge_reps(clip); side = a["side"]; joint = a["joint"]
    reps = {r["rep"]: r for r in a["reps"]}; r, br = reps[rep], reps[best_rep]
    names = {"knee": (11, 13, 15), "hip": (5, 11, 13), "elbow": (5, 7, 9)}[joint]
    A_, B_, C_ = [J.RIGHT[x] if side == "right" else x for x in names]
    h0, _, h1 = r["_f"]; b0, _, b1 = br["_f"]; n = h1 - h0
    if CROP["on"]:  # crop from this rep's own extent so raised limbs stay in frame
        seg = kp[h0:h1 + 1]; ys = seg[:, :, 1][seg[:, :, 2] >= P.CONF_MIN]
        top = float(np.percentile(ys, 2)) if len(ys) else 0
        CROP["y0"] = int(min(max(top - 120, 0), 1920 - 960))
    def norm(f):
        o = f[B_, :2]; s = np.linalg.norm(f[A_, :2] - o) + 1e-6
        return (f[:, :2] - o) / s, o, s
    def gen():
        last = None
        src = list(P.frames(video, h0, n))
        seq = [k for _ in range(loops) for k in range(len(src)) for _ in range(slow)]
        for step, k in enumerate(seq):
            img = src[k]; i = h0 + k; f = kp[i]; t = step / FPS
            bi = b0 + int(round(k / max(1, n) * (b1 - b0)))
            img, f = prep(grade(img), f)
            g, _, _ = norm(kp[bi]); _, o, s = norm(f); gf = np.concatenate([g * s + o, np.ones((17, 1))], 1)
            ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            chain = [J.RIGHT[x] if side == "right" else x for x in (5, 11, 13, 15)] if joint in ("hip", "knee") else [A_, B_, C_]
            gview = gf.copy(); gview[[j for j in range(17) if j not in chain], 2] = 0  # ghost: moving chain only
            for a_, b_ in zip(chain, chain[1:]):
                d.line([P.px(gview, a_), P.px(gview, b_)], fill=GREEN + (200,), width=16)
            for j_ in chain:
                x_, y_ = P.px(gview, j_); d.ellipse([x_ - 12, y_ - 12, x_ + 12, y_ + 12], outline=GREEN + (230,), width=4)
            skeleton(d, f, w=6)
            real = J.angle_series(kp[i:i + 1], joint, side)[0]; best = J.angle_series(kp[bi:bi + 1], joint, side)[0]
            gap = abs(real - best) if not (np.isnan(real) or np.isnan(best)) else 0
            if gap > 6:
                d.polygon([P.px(f, B_), P.px(f, C_), (gf[C_, 0], gf[C_, 1])], fill=RED + (150,))
            panel(d, (60, 110), ["GHOST = MY BEST REP"], col=GREEN, size=50, sub=f"baseline: rep {best_rep}")
            panel(d, (60, 300), [f"REP {rep}"], size=50, sub="now")
            panel(d, (60, 470), [f"RANGE {r['range_deg']}° VS {br['range_deg']}°"], col=RED, size=50, sub="measured")
            last = Image.alpha_composite(img, glow(ov)); yield last
        if verdict and last is not None:
            for k in range(int(hold_s * FPS)):
                yield stamp(last, verdict, reason, k / (0.25 * FPS))
    write(out, gen())


def sway(clip, t0, dur, out, verdict=None, reason=None, hold_s=1.6):
    kp, video = P.keypoints(clip); kp = P.smooth_kp(kp); i0, n = int(t0 * FPS), int(dur * FPS)
    side = "left" if kp[:, [5, 11], 2].mean() >= kp[:, [6, 12], 2].mean() else "right"; S, Hh = (5, 11) if side == "left" else (6, 12)
    ln = J.lean_series(kp, side); seg = ln[i0:i0 + n]; sw = float(np.nanmax(seg) - np.nanmin(seg))
    def gen():
        last = None; lo, hi = 999, -999
        for k, img in enumerate(P.frames(video, i0, n)):
            i = i0 + k; t = k / FPS; img, f = prep(grade(img), kp[i])
            ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            skeleton(d, f, alpha=160, w=4)
            if min(f[S, 2], f[Hh, 2]) >= P.CONF_MIN:
                hs, hh = P.px(f, S), P.px(f, Hh)
                d.line([hh, (hh[0], hh[1] - 420)], fill=WHITE + (120,), width=3)
                d.line([hh, hs], fill=GREEN + (255,), width=10); ring(d, hh, 40, t, GREEN)
                if not np.isnan(ln[i]):
                    lo, hi = min(lo, ln[i]), max(hi, ln[i])
            panel(d, (60, 110), [f"TORSO SWAY {max(0, hi - lo):.0f}°"], col=GREEN, size=56, sub="shoulder-hip line")
            last = Image.alpha_composite(img, glow(ov)); yield last
        if verdict and last is not None:
            for k in range(int(hold_s * FPS)):
                yield stamp(last, verdict, reason, k / (0.25 * FPS))
    write(out, gen())
    return round(sw, 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["lockon", "wave", "ghost", "sway"])
    ap.add_argument("clip"); ap.add_argument("--t0", type=float, default=0); ap.add_argument("--dur", type=float, default=5)
    ap.add_argument("--rep", type=int); ap.add_argument("--best-rep", type=int)
    ap.add_argument("--verdict"); ap.add_argument("--reason"); ap.add_argument("--panel", action="store_true")
    ap.add_argument("--name")
    a = ap.parse_args(); d = P.DATA / Path(a.clip).stem / "hud"; d.mkdir(parents=True, exist_ok=True)
    if a.panel:
        kp0, _ = P.keypoints(a.clip); panel_mode(kp0)
    sfx = ("_panel" if a.panel else "") + (f"_{a.name}" if a.name else "")
    if a.mode == "lockon":
        lockon(a.clip, a.t0, a.dur, d / f"lockon{sfx}.mp4")
    elif a.mode == "wave":
        wave(a.clip, a.t0, a.dur, d / f"wave{sfx}.mp4")
    elif a.mode == "ghost":
        ghost(a.clip, a.rep, a.best_rep, d / f"ghost_rep{a.rep}{sfx}.mp4", a.verdict, a.reason)
    else:
        print("sway_deg", sway(a.clip, a.t0, a.dur, d / f"sway{sfx}.mp4", a.verdict, a.reason))
