"""Render every Gym Jarvis Ep 3 HUD visual as 1080x960 top-panel clips into outputs/.../visuals/.

All data comes from demos/workout-hud/data (pose keypoints, judge.json, label.json, verdicts.json).
Usage: demos/workout-hud/.venv/bin/python demos/workout-hud/visuals/ep3_render.py [name ...]
"""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "judge"))

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hud_fx as X  # noqa: E402
import pose_fx as P  # noqa: E402

OUT = HERE.parents[2] / "outputs" / "workout-analyser-reel" / "visuals"
DL = Path.home() / "Downloads"
W, PH = 1080, 960
V = json.loads((P.DATA / "verdicts.json").read_text())
COL = {"STOP": X.RED, "HOLD": X.AMBER, "CONTINUE": X.GREEN, "CHECK FOOTAGE": X.AMBER, "CAN'T SEE": X.GREY}


def fresh(clip):
    """Panel mode needs per-clip crop; reset globals then set them for this clip."""
    X.H, X.SAFE_BOTTOM, P.H = 1920, int(1920 * .8), 1920; X.CROP.update(on=False, y0=0)
    kp, _ = P.keypoints(DL / f"{clip}.MOV"); X.panel_mode(kp)
    return DL / f"{clip}.MOV"


def judge(clip):
    return json.loads((P.DATA / clip / "judge.json").read_text())["verdict"]


def blank():
    return Image.new("RGBA", (W, PH), (3, 12, 20, 255))


def strike_stamp(img, p):
    """STOP gets struck through and replaced by CHECK FOOTAGE."""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    cx, cy = W // 2, int(PH * 0.42)
    d.line([(cx - 330, cy + 120), (cx - 330 + 660 * X.ease(p), cy + 120 - 240 * X.ease(p))], fill=X.WHITE + (255,), width=14)
    return Image.alpha_composite(img, ov)


# ------------------------------------------------------------------ clips
def ghost_stop():
    c = fresh("IMG_2661"); j = judge("IMG_2661")
    X.ghost(c, j["worst_rep"], j["best_rep"], OUT / "ghost_stop.mp4", "STOP", j["reason"], hold_s=2.0)


def lockon():
    X.lockon(fresh("IMG_2650"), 0.6, 3.6, OUT / "lockon.mp4")


def wave():
    X.wave(fresh("IMG_2650"), 0.5, 8.0, OUT / "wave.mp4")


def false_alarm():
    """The lunge: live knee readout on the rep where I face the camera, judge STOP, struck, CHECK FOOTAGE."""
    c = fresh("IMG_2650"); kp, video = P.keypoints(c); kp = P.smooth_kp(kp); ang, side, _ = P.knee_series(kp)
    knee = P.SIDES[side][2]; i0, n = int(24.0 * X.FPS), int(2.2 * X.FPS)
    def gen():
        last = None
        for k, img in enumerate(P.frames(video, i0, n)):
            i = i0 + k; img, f = X.prep(X.grade(img), kp[i]); t = k / X.FPS
            ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); X.skeleton(d, f, w=5)
            if f[knee, 2] >= P.CONF_MIN and not np.isnan(ang[i]):
                x, y = P.px(f, knee); X.ring(d, (x, y), 34, t, X.AMBER); d.text((x + 56, y - 40), f"{ang[i]:.0f}°", font=X.hf(70), fill=X.WHITE + (255,))
            X.panel(d, (60, 60), ["JUDGE: 5 OF 17 REPS DEEP"], col=X.RED, size=44, sub="numbers + frames")
            last = Image.alpha_composite(img, X.glow(ov)); yield last
        for k in range(int(0.9 * X.FPS)):
            yield X.stamp(last, "STOP", "", k / (0.25 * X.FPS))
        st = X.stamp(last, "STOP", "", 1)
        for k in range(int(0.6 * X.FPS)):
            yield strike_stamp(st, k / (0.4 * X.FPS))
        base = strike_stamp(st, 1)
        for k in range(int(1.8 * X.FPS)):
            im = base.copy(); d = ImageDraw.Draw(im)
            X.panel(d, (60, 640), ["COACH: DEPTH CONSISTENT"], col=X.GREEN, size=44, sub="video only")
            im = X.stamp(Image.alpha_composite(im, Image.new("RGBA", im.size, (0, 0, 0, 90))), "CHECK FOOTAGE", "", k / (0.25 * X.FPS)) if k > 6 else im
            yield im
    X.write(OUT / "false_alarm.mp4", gen())


def cant_see():
    """A set the safety check refused: joints greyed, fixed message, no AI call."""
    clip = "IMG_2655"; c = fresh(clip); kp, video = P.keypoints(c); kp = P.smooth_kp(kp)
    msg = judge(clip)["detail"]
    def gen():
        for k, img in enumerate(P.frames(video, 0, int(2.6 * X.FPS))):
            img, f = X.prep(X.grade(img), kp[k]); ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            X.skeleton(d, f, w=5)
            if (k // 6) % 2 == 0:
                X.panel(d, (60, 60), [msg.split(". ")[0] + "."], col=X.RED, size=50, sub="safety check")
            X.panel(d, (60, 220), ["NOT JUDGING THIS SET."], col=X.WHITE, size=44)
            yield Image.alpha_composite(img, X.glow(ov))
    X.write(OUT / "cant_see.mp4", gen())


def sway_red():
    c = fresh("IMG_2785"); j = judge("IMG_2785")
    X.sway(c, 2.0, 4.5, OUT / "sway_continue.mp4", "CONTINUE", j["reason"], hold_s=1.6)


def wall():
    """23 sets tiled; a scan sweeps; each tile gets its final verdict; all but STOP fade."""
    rows = V["rows"]; cols, rws = 6, 4; tw, th = W // cols, (PH - 220) // rws
    thumbs = []
    for r in rows:
        src = P.DATA / r["clip"] / "sheets" / "sheet_01.jpg"
        sh = Image.open(src); fw, fh = sh.width // 4, sh.height // 3
        thumbs.append(sh.crop((fw, 0, 2 * fw, fh)).resize((tw - 8, th - 8)))
    stop_i = next(i for i, r in enumerate(rows) if r["final"] == "STOP")
    X.H, X.SAFE_BOTTOM, P.H = PH, PH - 100, PH
    def gen():
        n = int(4.2 * X.FPS)
        for k in range(n):
            t = k / X.FPS; im = blank(); d = ImageDraw.Draw(im)
            scan = min(1, t / 2.2)
            for i, (r, th_) in enumerate(zip(rows, thumbs)):
                x, y = (i % cols) * tw + 4, 150 + (i // cols) * th + 4
                done = (i + 1) / len(rows) <= scan
                faded = t > 3.0 and i != stop_i
                tile = X.grade(th_.convert("RGBA"))
                if faded:
                    tile = Image.blend(Image.new("RGBA", tile.size, (3, 12, 20, 255)), tile, 0.25)
                im.paste(tile, (x, y))
                if done:
                    c = COL[r["final"]]; d.rectangle([x, y, x + tw - 9, y + th - 9], outline=c + (255,), width=5 if r["final"] == "STOP" else 3)
                    lab = {"CHECK FOOTAGE": "CHECK", "CAN'T SEE": "CAN'T SEE"}.get(r["final"], r["final"])
                    d.rectangle([x, y + th - 44, x + tw - 9, y + th - 9], fill=(0, 0, 0, 200))
                    d.text((x + (tw - 9) / 2, y + th - 27), lab, font=X.hf(30), fill=c + (255,), anchor="mm")
            ys = 150 + scan * (rws * th)
            if scan < 1:
                d.line([(0, ys), (W, ys)], fill=X.CYAN + (220,), width=4)
            counted = int(scan * len(rows))
            X.panel(d, (40, 20), [f"{counted} SETS WATCHED"], size=52, sub="2 sessions · 15 + 28 aug")
            if t > 2.4:
                X.panel(d, (640, 20), ["1 STOP"], col=X.RED, size=52, sub="flagged")
            yield im
    X.write(OUT / "wall_of_sets.mp4", gen())


def arch(stage):
    """HUD schematic of the system, revealed up to `stage` (1-5); the newest node pulses."""
    nodes = [("CLIP", "my set, 30 fps", 1), ("POSE", "17 joints / frame", 1), ("REP MATHS", "range · speed · sway", 2),
             ("SAFETY CHECK", "can't see? no verdict", 2), ("MY BEST REP", "the baseline", 3),
             ("JUDGE", "Fable 5.2 · numbers + frames", 3), ("COACH", "Fable 5.2 · video only", 4),
             ("BOTH AGREE?", "STOP · else CHECK FOOTAGE", 4), ("VERDICT", "CONTINUE · HOLD · STOP", 5)]
    pos = [(180, 120), (540, 120), (900, 120), (900, 300), (540, 300), (720, 480), (220, 480), (470, 680), (870, 680)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 5), (4, 5), (0, 6), (5, 7), (6, 7), (7, 8)]
    def gen():
        for k in range(int(2.4 * X.FPS)):
            t = k / X.FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            for gx in range(0, W, 60):
                d.line([(gx, 0), (gx, PH)], fill=X.CYAN_D + (25,), width=1)
            for gy in range(0, PH, 60):
                d.line([(0, gy), (W, gy)], fill=X.CYAN_D + (25,), width=1)
            for a, b in edges:
                if nodes[a][2] <= stage and nodes[b][2] <= stage:
                    new = max(nodes[a][2], nodes[b][2]) == stage; p = X.ease(t / 0.8) if new else 1
                    A, B = pos[a], pos[b]; E = (A[0] + (B[0] - A[0]) * p, A[1] + (B[1] - A[1]) * p)
                    d.line([A, E], fill=X.CYAN + (200,), width=4)
                    if p >= 1:  # data packet travelling the edge
                        q = (t * 0.8 + a * 0.13) % 1; d.ellipse([A[0] + (B[0] - A[0]) * q - 7, A[1] + (B[1] - A[1]) * q - 7, A[0] + (B[0] - A[0]) * q + 7, A[1] + (B[1] - A[1]) * q + 7], fill=X.WHITE + (255,))
            for (name, sub, st), (x, y) in zip(nodes, pos):
                if st > stage:
                    continue
                new = st == stage; a = int(255 * X.ease((t - 0.3) / 0.5)) if new else 255
                col = X.RED if name == "BOTH AGREE?" else (X.GREEN if name == "MY BEST REP" else X.CYAN)
                w2, h2 = 150, 62
                d.rectangle([x - w2, y - h2, x + w2, y + h2], fill=(4, 22, 34, min(a, 230)), outline=col + (a,), width=3)
                X.brackets(d, (x - w2, y - h2, x + w2, y + h2), col, L=16, w=4, a=a)
                d.text((x, y - 16), name, font=X.hf(46), fill=X.WHITE + (a,), anchor="mm")
                d.text((x, y + 28), sub.upper(), font=X.hf(26, False), fill=col + (a,), anchor="mm")
                if new:
                    X.ring(d, (x + w2 - 4, y - h2 + 4), 18, t, col, a=a, w=3)
            yield Image.alpha_composite(im, X.glow(ov, 6))
    X.H, X.SAFE_BOTTOM, P.H = PH, PH - 100, PH
    X.write(OUT / f"arch_{stage}.mp4", gen())


def countdown_blast(step=0.45, blast=0.75):
    """3-2-1 arc-reactor countdown, then a blast: white flash + shockwave + WORKOUT ANALYSER ONLINE (about 3.4 s)."""
    import math
    X.H, X.SAFE_BOTTOM, P.H = PH, PH - 100, PH
    cx, cy = W // 2, 430
    def gen():
        cd = 3 * step; n = int((cd + blast) * X.FPS)
        for k in range(n):
            t = k / X.FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            if t < cd:  # countdown: one number per 0.8 s, rings spin up
                num = 3 - int(t / step); ph = (t % step) / step; spin = 1 + (cd - t)
                for r, gaps, col, w in ((300, 3, X.CYAN, 6), (250, 6, X.CYAN_D, 4), (200, 4, X.AMBER, 5)):
                    X.ring(d, (cx, cy), r, t * (4 / spin) * (1 if gaps != 6 else -1), col, a=230, w=w, gaps=gaps)
                for a_ in range(0, 360, 10):  # tick marks
                    rr = 330; x0, y0 = cx + rr * math.cos(math.radians(a_)), cy + rr * math.sin(math.radians(a_))
                    x1, y1 = cx + (rr + (18 if a_ % 30 == 0 else 9)) * math.cos(math.radians(a_)), cy + (rr + (18 if a_ % 30 == 0 else 9)) * math.sin(math.radians(a_))
                    d.line([(x0, y0), (x1, y1)], fill=X.CYAN + (160,), width=3)
                sc = 1.35 - 0.35 * X.ease(ph / 0.35)
                d.text((cx, cy), str(num), font=X.hf(int(300 * sc)), fill=X.WHITE + (int(255 * (1 - max(0, ph - 0.8) / 0.2)),), anchor="mm")
                d.text((cx, 820), "INITIALISING WORKOUT ANALYSER", font=X.hf(44, False), fill=X.CYAN + (220,), anchor="mm")
                d.rectangle([140, 770, 140 + (W - 280) * (t / cd), 776], fill=X.CYAN + (230,))
                yield Image.alpha_composite(im, X.glow(ov, 10))
            else:  # blast
                b = (t - cd) / blast
                fl = max(0.0, 1 - b / 0.25)
                for k2 in range(3):
                    rr = 40 + 900 * X.ease(min(1, b * 1.4 - k2 * 0.12))
                    if rr > 40:
                        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(X.WHITE if k2 == 0 else X.CYAN) + (int(255 * max(0, 1 - b)),), width=14 - 4 * k2)
                for a_ in range(0, 360, 15):  # debris streaks
                    r0, r1 = 120 + 700 * X.ease(b), 160 + 820 * X.ease(b)
                    d.line([(cx + r0 * math.cos(math.radians(a_)), cy + r0 * math.sin(math.radians(a_))),
                            (cx + r1 * math.cos(math.radians(a_)), cy + r1 * math.sin(math.radians(a_)))], fill=X.AMBER + (int(200 * max(0, 1 - b)),), width=4)
                if b > 0.15:
                    a = int(255 * X.ease((b - 0.15) / 0.3))
                    d.text((cx, cy - 40), "WORKOUT ANALYSER", font=X.hf(120), fill=X.WHITE + (a,), anchor="mm")
                    d.text((cx, cy + 70), "ONLINE", font=X.hf(90), fill=X.CYAN + (a,), anchor="mm")
                im = Image.alpha_composite(im, X.glow(ov, 12))
                if fl > 0:
                    im = Image.alpha_composite(im, Image.new("RGBA", im.size, (255, 255, 255, int(255 * fl))))
                yield im
    X.write(OUT / "countdown_blast.mp4", gen())


def raw_label(clip, t0, dur, label, out, col=None):
    """Raw footage (graded, no skeleton) with one plain label, so viewers spot the fault themselves."""
    c = fresh(clip); kp, video = P.keypoints(c)
    def gen():
        for k, img in enumerate(P.frames(video, int(t0 * X.FPS), int(dur * X.FPS))):
            img, _ = X.prep(X.grade(img), kp[int(t0 * X.FPS) + k]); d = ImageDraw.Draw(img)
            X.panel(d, (60, 60), [label], col=col or X.AMBER, size=56, sub="watch")
            yield img
    X.write(OUT / out, gen())


def sample_result():
    """What the FORM download returns: one real coach result for the STOP set (label.json, IMG_2661)."""
    lb = json.loads((P.DATA / "IMG_2661" / "label.json").read_text())["label"]; st = lb["sets"][0]
    lines = [f"VERDICT: {st['verdict'].upper()}", "REPS 4, 5, 9 CUT SHORT", "SWUNG, NOT CONTROLLED", "FIX: LOWER IN 2-3 S"]
    X.H, X.SAFE_BOTTOM, P.H = PH, PH - 100, PH
    def gen():
        for k in range(int(2.6 * X.FPS)):
            t = k / X.FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            shown = lines[:1 + int(t / 0.35)]
            X.panel(d, (90, 150), shown, col=X.RED if t > 0.2 else X.CYAN, size=64, sub="form coach · sample result · my reverse crunch")
            d.text((W // 2, 760), "COMMENT FORM", font=X.hf(96), fill=X.CYAN + (int(255 * X.ease((t - 1.4) / 0.4)),), anchor="mm")
            yield Image.alpha_composite(im, X.glow(ov, 6))
    X.write(OUT / "sample_result.mp4", gen())


def labelled_lunge():
    """Re-render the lunge clips with the set name so replays are never confused with the crunch."""
    orig = X.panel
    def panel_with_tag(d, xy, lines, **kw):
        r = orig(d, xy, lines, **kw)
        if xy == (60, 110) or xy == (60, 60):
            orig(d, (60, 760), ["LUNGE: WATCH ME TURN"], col=X.AMBER, size=40)
        return r
    X.panel = panel_with_tag
    try:
        false_alarm()
    finally:
        X.panel = orig


def dual_wave(left=("IMG_2650", 0.5, "LEGS · KNEE", "knee"), right=("IMG_2783", 0.5, "BACK · ELBOW", "elbow"), dur=7.0):
    """Two exercises side by side (blue legs, red back): footage + skeleton + live joint angle wave. No rep totals."""
    import judge as J
    X.H, X.SAFE_BOTTOM, P.H = PH, PH - 100, PH; X.CROP.update(on=False, y0=0)
    halves = []
    for clip, t0, title, joint in (left, right):
        kp, video = P.keypoints(DL / f"{clip}.MOV"); kp = P.smooth_kp(kp)
        side = "left" if kp[:, [5, 11, 13, 15], 2].mean() >= kp[:, [6, 12, 14, 16], 2].mean() else "right"
        ang = J.smooth(J.angle_series(kp, joint, side))
        names = {"knee": (11, 13, 15), "hip": (5, 11, 13), "elbow": (5, 7, 9)}[joint]
        mid = J.RIGHT[names[1]] if side == "right" else names[1]
        win = kp[int(t0 * X.FPS): int((t0 + dur) * X.FPS)]  # crop from the frames actually shown
        vis = win[:, :, 2] >= P.CONF_MIN
        hv = vis[:, [11, 12]]; hx = win[:, [11, 12], 0][hv]
        cx = float(np.median(hx)) if len(hx) else float(np.median(win[:, :, 0][vis]))
        tops = [f[f[:, 2] >= P.CONF_MIN][:, 1].min() for f in win if (f[:, 2] >= P.CONF_MIN).any()]
        top = float(np.percentile(tops, 5)) if tops else 300.0
        cw, ch = 720, 1280  # crop 720x1280 around the body, scale to 540x960
        x0 = int(min(max(cx - cw / 2, 0), 1080 - cw)); y0 = int(min(max(top - 90, 0), 1920 - ch))
        halves.append(dict(kp=kp, video=video, t0=t0, title=title, ang=ang, mid=mid, x0=x0, y0=y0, sc=540 / cw,
                           frames=list(P.frames(video, int(t0 * X.FPS), int(dur * X.FPS)))))
    n = min(len(h["frames"]) for h in halves)
    def gen():
        for k in range(n):
            t = k / X.FPS; im = blank()
            for hi, h in enumerate(halves):
                i = int(h["t0"] * X.FPS) + k
                fr = X.grade(h["frames"][k]).crop((h["x0"], h["y0"], h["x0"] + 720, h["y0"] + 1280)).resize((540, 960))
                f = h["kp"][i].copy(); f[:, 0] = (f[:, 0] - h["x0"]) * h["sc"]; f[:, 1] = (f[:, 1] - h["y0"]) * h["sc"]
                ov = Image.new("RGBA", fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
                X.skeleton(d, f, w=4)
                if f[h["mid"], 2] >= P.CONF_MIN:
                    x, y = P.px(f, h["mid"]); X.ring(d, (x, y), 26, t, X.AMBER, w=3)
                    if not np.isnan(h["ang"][i]):
                        d.text((x + 34, y - 30), f"{h['ang'][i]:.0f}°", font=X.hf(48), fill=X.WHITE + (255,))
                # graph
                gx0, gx1, gy0, gy1 = 30, 510, 690, 840
                d.rectangle([gx0 - 14, gy0 - 50, gx1 + 14, gy1 + 14], fill=(4, 18, 28, 200), outline=X.CYAN + (90,), width=2)
                d.text((gx0, gy0 - 42), h["title"] + " // LIVE", font=X.hf(30, False), fill=X.CYAN + (230,))
                seg = h["ang"][int(h["t0"] * X.FPS): int(h["t0"] * X.FPS) + n]
                lo, hi_ = np.nanmin(seg) - 5, np.nanmax(seg) + 5
                pts = [(gx0 + j / n * (gx1 - gx0), gy0 + (hi_ - v) / (hi_ - lo) * (gy1 - gy0)) for j, v in enumerate(seg[:k + 1]) if not np.isnan(v)]
                for q in range(1, len(pts)):
                    if pts[q][0] - pts[q - 1][0] < 10:
                        d.line([pts[q - 1], pts[q]], fill=X.CYAN + (255,), width=5)
                X.brackets(d, (6, 6, 534, 954), X.CYAN if hi == 0 else X.RED, L=30, w=4)
                fr = Image.alpha_composite(fr, X.glow(ov, 6)); im.paste(fr, (hi * 540, 0))
            d2 = ImageDraw.Draw(im); d2.line([(540, 0), (540, PH)], fill=X.CYAN + (200,), width=3)
            X.panel(d2, (300, 30), ["EVERY DIP = ONE REP"], size=44, sub="2 sessions · 2 lifts")
            yield im
    X.write(OUT / "dual_wave.mp4", gen())


def wait_is_over():
    """THE WAIT IS OVER slam (0.9 s) -> then countdown_blast follows in the edit."""
    X.H, X.SAFE_BOTTOM, P.H = PH, PH - 100, PH
    def gen():
        for k in range(int(0.9 * X.FPS)):
            t = k / X.FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            sc = 1.5 - 0.5 * X.ease(t / 0.18); f = X.hf(int(150 * sc))
            d.text((W // 2, 380), "THE WAIT", font=f, fill=X.WHITE + (255,), anchor="mm")
            d.text((W // 2, 540), "IS OVER", font=f, fill=X.CYAN + (255,), anchor="mm")
            X.brackets(d, (120, 250, W - 120, 660), X.CYAN, L=40, w=6)
            im = Image.alpha_composite(im, X.glow(ov, 10))
            if t < 0.06:
                im = Image.alpha_composite(im, Image.new("RGBA", im.size, (255, 255, 255, 150)))
            yield im
    X.write(OUT / "wait_is_over.mp4", gen())


def lockon_red():
    X.lockon(fresh("IMG_2783"), 0.4, 3.6, OUT / "lockon_red.mp4")


def tease_jd():
    """Sunday tease: the REAL Salesforce posting (screenshot of the public careers page, cropped to the job card),
    with the title, city and requisition ringed, then one verbatim line from the same posting."""
    X.H, X.SAFE_BOTTOM, P.H = PH, PH - 100, PH
    card = Image.open(HERE.parents[2] / "outputs" / "hiring-posttraining-reel" / "jd_card_top.png").convert("RGB")
    cw = 1000; card = card.resize((cw, int(card.height * cw / card.width))); sc = cw / 1691
    def box(x0, y0, x1, y1):  # card pixel coords (1691-wide crop) -> panel coords
        return (40 + x0 * sc, 40 + y0 * sc, 40 + x1 * sc, 40 + y1 * sc)
    rings = [(box(60, 55, 1160, 135), 0.5), (box(80, 425, 470, 535), 1.0), (box(575, 430, 885, 492), 1.4)]
    def gen():
        for k in range(int(3.6 * X.FPS)):
            t = k / X.FPS; im = blank(); z = 1.0 + 0.02 * t
            c = card.crop((0, 0, cw, min(card.height, 600)))
            im.paste(c, (40, 40)); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            X.brackets(d, (34, 34, 46 + cw, 646), X.CYAN, L=30, w=5)
            for (bx, t0) in rings:
                p = X.ease((t - t0) / 0.35)
                if p > 0:
                    x0, y0, x1, y1 = bx; d.rectangle([x0, y0, x0 + (x1 - x0) * p, y1], outline=X.RED + (255,), width=6)
            if t > 1.8:
                a = int(255 * X.ease((t - 1.8) / 0.3))
                d.rectangle([40, 670, W - 40, 850], fill=(4, 22, 34, min(a, 235)), outline=X.CYAN + (a,), width=2)
                d.text((W // 2, 712), "FROM THE SAME POSTING:", font=X.hf(30, False), fill=X.CYAN + (a,), anchor="mm")
                d.text((W // 2, 762), "\u201cTHIS IS A MODEL-TRAINING ROLE, NOT A WRAPPER", font=X.hf(42), fill=X.WHITE + (a,), anchor="mm")
                d.text((W // 2, 814), "AROUND A HOSTED LLM\u201d", font=X.hf(46), fill=X.WHITE + (a,), anchor="mm")
            yield Image.alpha_composite(im.convert("RGBA"), X.glow(ov, 5))
    X.write(OUT / "tease_jd.mp4", gen())


def verdict_chips():
    """Beat 17: the raw swing with the two AI verdicts landing side by side (judge.json + label.json, IMG_2661)."""
    c = fresh("IMG_2661"); kp, video = P.keypoints(c)
    def gen():
        for k, img in enumerate(P.frames(video, int(9.6 * X.FPS), int(2.6 * X.FPS))):
            t = k / X.FPS; img, _ = X.prep(X.grade(img), kp[int(9.6 * X.FPS) + k]); ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            if t > 0.3:
                X.panel(d, (60, 60), ["JUDGE: STOP"], col=X.RED, size=60, sub="numbers + frames")
            if t > 1.1:
                X.panel(d, (560, 60), ["COACH: BAD"], col=X.RED, size=60, sub="video only")
            if t > 1.8:
                d.text((W // 2, 780), "TWO AIs. ONE OPINION.", font=X.hf(64), fill=X.WHITE + (255,), anchor="mm")
            yield Image.alpha_composite(img, X.glow(ov, 6))
    X.write(OUT / "verdict_chips.mp4", gen())



SCR = Path("/private/tmp/claude-501/-Users-sagartekwani/9336bd28-6bb6-450a-be06-4a6959088d43/scratchpad")


def judge_hold():
    """JUDGE example on the red day: lat pulldown, best rep 1 as the ghost over rep 4; HOLD (judge.json IMG_2783)."""
    c = fresh("IMG_2783"); j = judge("IMG_2783")
    X.ghost(c, j["worst_rep"], j["best_rep"], OUT / "judge_hold.mp4", "HOLD", j["reason"], hold_s=1.4, slow=1, loops=1)


def dual_wave_v2():
    """Two lifts, two waves: hack squat (legs, knee) + lat pulldown (back, elbow). No lunge here."""
    dual_wave(left=("IMG_2649", 1.5, "LEGS · KNEE", "knee"), right=("IMG_2783", 0.5, "BACK · ELBOW", "elbow"), dur=6.0)


def arch3(stage):
    """3-part schematic: 0 = overview (SEE · JUDGE · CHECK appear), 1 = SEE lit, 2 = JUDGE lit, 3 = CHECK lit (+ gate)."""
    X.H, X.SAFE_BOTTOM, P.H = PH, PH - 100, PH
    parts = [("SEE", ["17 JOINTS · 30 FPS", "REPS = WAVES", "CAN'T SEE? NO VERDICT"], 200),
             ("JUDGE", ["EVERY REP vs MY BEST", "CONTINUE · HOLD · STOP", "CLAUDE FABLE 5.2"], 540),
             ("CHECK", ["A COACH: VIDEO ONLY", "BOTH AGREE → STOP", "ELSE: CHECK FOOTAGE"], 880)]
    def gen():
        for k in range(int(2.6 * X.FPS)):
            t = k / X.FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            for gx in range(0, W, 60):
                d.line([(gx, 0), (gx, PH)], fill=X.CYAN_D + (22,), width=1)
            d.text((W // 2, 90), "I SPLIT IT INTO THREE PARTS", font=X.hf(54), fill=X.WHITE + (int(255 * X.ease(t / 0.3)),), anchor="mm")
            for i, (name, subs, cx) in enumerate(parts):
                appear = X.ease((t - 0.2 - i * 0.25) / 0.35) if stage == 0 else 1.0
                lit = stage == i + 1
                a = int(255 * appear) if (stage == 0 or lit) else 90
                col = X.RED if (lit and name == "CHECK") else (X.GREEN if lit and name == "JUDGE" else X.CYAN)
                y0, y1 = 200, 660
                d.rectangle([cx - 150, y0, cx + 150, y1], fill=(4, 22, 34, min(a, 230)), outline=col + (a,), width=5 if lit else 3)
                X.brackets(d, (cx - 150, y0, cx + 150, y1), col, L=22, w=5, a=a)
                d.text((cx, y0 + 70), f"{i + 1}", font=X.hf(60), fill=col + (a,), anchor="mm")
                d.text((cx, y0 + 150), name, font=X.hf(84), fill=X.WHITE + (a,), anchor="mm")
                if lit or stage == 0:
                    for q, sub in enumerate(subs):
                        sa = int(a * X.ease((t - 0.5 - q * 0.3) / 0.3)) if lit else int(a * 0.8)
                        d.text((cx, y0 + 250 + q * 60), sub, font=X.hf(30, False), fill=X.CYAN + (sa,), anchor="mm")
                if lit:
                    X.ring(d, (cx + 130, y0 + 20), 22, t, col, w=4)
                if i < 2:
                    pa = X.ease((t - 0.4 - i * 0.25) / 0.3) if stage == 0 else 1
                    d.line([(cx + 150, 430), (cx + 150 + 40 * pa, 430)], fill=X.CYAN + (200,), width=5)
                    q = (t * 0.9 + i * 0.3) % 1
                    d.ellipse([cx + 150 + 40 * q - 6, 424, cx + 150 + 40 * q + 6, 436], fill=X.WHITE + (255,))
            if stage == 3 and t > 1.2:
                aa = int(255 * X.ease((t - 1.2) / 0.3))
                d.rectangle([180, 700, W - 180, 800], fill=(4, 22, 34, min(aa, 230)), outline=X.RED + (aa,), width=3)
                d.text((W // 2, 750), "TO CALL STOP, BOTH MUST AGREE", font=X.hf(48), fill=X.WHITE + (aa,), anchor="mm")
            yield Image.alpha_composite(im, X.glow(ov, 6))
    X.write(OUT / f"arch3_{['overview', 'see', 'judge', 'check'][stage]}.mp4", gen())


def research_warning():
    """Beat 3: the research pass, one finding (arXiv 2608.24384) and the WARNING chip that pins to the corner."""
    X.H, X.SAFE_BOTTOM, P.H = PH, PH - 100, PH
    papers = [("MARKERLESS POSE ESTIMATION FOR", "RESISTANCE TRAINING TECHNIQUE", "arXiv 2608.24384"),
              ("SMARTPHONE CAMERA POSITIONING &", "AI POSE ESTIMATION ACCURACY", "PMC12978916"),
              ("VIEWPOINT-INVARIANT EXERCISE", "REPETITION COUNTING", "arXiv 2107.13760")]
    def gen():
        for k in range(int(4.2 * X.FPS)):
            t = k / X.FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            d.text((W // 2, 110), "CLAUDE DUG THROUGH THE RESEARCH", font=X.hf(48), fill=X.CYAN + (255,), anchor="mm")
            for i, (l1, l2, ref) in enumerate(papers):
                a = int(255 * X.ease((t - i * 0.35) / 0.3)); y = 160 + i * 160
                hot = i == 0 and t > 1.5
                col = X.AMBER if hot else X.CYAN
                d.rectangle([90, y, W - 90, y + 135], fill=(4, 22, 34, min(a, 220)), outline=col + (a,), width=4 if hot else 2)
                d.text((120, y + 22), l1, font=X.hf(40), fill=X.WHITE + (a,)); d.text((120, y + 66), l2, font=X.hf(40), fill=X.WHITE + (a,))
                d.text((W - 120, y + 112), ref, font=X.hf(26, False), fill=col + (a,), anchor="rm")
            if t > 1.5:
                p = X.ease((t - 1.5) / 0.4)
                d.text((W // 2, 690), "FINDING: JOINT ANGLES ARE MOST SENSITIVE TO CAMERA ORIENTATION", font=X.hf(32, False), fill=X.AMBER + (int(255 * p),), anchor="mm")
            if t > 2.3:
                p = X.ease((t - 2.3) / 0.5)
                x0 = 140 + (40 - 140) * X.ease((t - 3.4) / 0.5) if t > 3.4 else 140
                y0 = 740 + (12 - 740) * X.ease((t - 3.4) / 0.5) if t > 3.4 else 740
                sc = 1 - 0.45 * X.ease((t - 3.4) / 0.5) if t > 3.4 else 1
                w, h = int(800 * sc), int(90 * sc)
                d.rectangle([x0, y0, x0 + w, y0 + h], fill=(40, 22, 0, int(230 * p)), outline=X.AMBER + (int(255 * p),), width=4)
                d.text((x0 + w // 2, y0 + h // 2), "WARNING: THE CAMERA ANGLE CAN FOOL IT", font=X.hf(int(46 * sc)), fill=X.AMBER + (int(255 * p),), anchor="mm")
            yield Image.alpha_composite(im, X.glow(ov, 5))
    X.write(OUT / "research_warning.mp4", gen())


def build_montage():
    """Beat 2: months of weekends. Real assets only: the Gym Jarvis HUD (demo data), the Ep 2 meal agent, the judge's
    code, the skeleton lock-on; dated tags from FACTS."""
    import cv2
    X.H, X.SAFE_BOTTOM, P.H = PH, PH - 100, PH
    hud = Image.open(SCR / "hud_app.png").convert("RGB")
    cap = cv2.VideoCapture(str(Path.home() / "Movies/ContentOS/food-tracker/deliver/food_tracker_v3_FINAL.mp4")); cap.set(cv2.CAP_PROP_POS_MSEC, 9000)
    ok, fr = cap.read(); cap.release()
    ep2 = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).crop((0, 0, 1440, 1280)) if ok else hud
    code = (HERE.parent / "judge" / "judge.py").read_text().splitlines()[30:58]
    cap = cv2.VideoCapture(str(OUT / "lockon_red.mp4")); cap.set(cv2.CAP_PROP_POS_FRAMES, 95); ok, fr = cap.read(); cap.release()
    lock = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)) if ok else hud
    shots = [("SEPT 2026 · THE PLAN", None), ("12 NOV · GYM JARVIS", hud), ("16 NOV · MEAL AGENT", ep2), ("19 NOV · THE JUDGE", "code"), ("20 NOV · WORKOUT ANALYSER", lock)]
    seg = 0.8
    def gen():
        for k in range(int(seg * len(shots) * X.FPS)):
            t = k / X.FPS; i = min(len(shots) - 1, int(t / seg)); lt = t - i * seg; tag, src = shots[i]
            im = blank()
            if src is None:
                d0 = ImageDraw.Draw(im)
                for r in range(9):
                    d0.text((90, 120 + r * 70), ["WEEKEND 1: WHAT SHOULD A GYM AI SEE?", "WEEKEND 2: MEALS FIRST", "WEEKEND 3: GRAMS, NOT CALORIES",
                             "WEEKEND 4: A HUD", "WEEKEND 5: POSE, 17 JOINTS", "WEEKEND 6: REPS AS WAVES", "WEEKEND 7: A JUDGE",
                             "WEEKEND 8: IT WAS WRONG", "WEEKEND 9: A SECOND AI"][r], font=X.hf(44, False),
                             fill=(X.CYAN if r <= int(lt / seg * 9) else X.CYAN_D) + (255,))
            elif src == "code":
                d0 = ImageDraw.Draw(im)
                for r, line in enumerate(code[:13]):
                    d0.text((60, 90 + r * 54), line[:58], font=X.hf(34, False), fill=(X.GREEN if "def " in line else X.CYAN) + (255,))
            else:
                z = 1.0 + 0.06 * lt / seg; s2 = src.copy(); sw, sh = s2.size
                cw, ch = int(sw / z), int(sw / z * PH / W)
                ch = min(ch, sh); cw = int(ch * W / PH)
                s2 = s2.crop(((sw - cw) // 2, 0, (sw - cw) // 2 + cw, ch)).resize((W, PH)); im.paste(s2, (0, 0))
            d = ImageDraw.Draw(im)
            X.panel(d, (40, PH - 220), [tag], size=50, sub="months of weekends")
            if lt < 0.08:
                im = Image.alpha_composite(im.convert("RGBA"), Image.new("RGBA", im.size, (255, 255, 255, 90)))
            yield im.convert("RGBA")
    X.write(OUT / "build_montage.mp4", gen())


JOBS = {"judge_hold": judge_hold, "dual_wave_v2": dual_wave_v2, "research_warning": research_warning, "build_montage": build_montage, **{f"arch3_{n}": (lambda i=i: arch3(i)) for i, n in enumerate(["overview", "see", "judge", "check"])}, "verdict_chips": verdict_chips, "tease_jd": tease_jd, "dual_wave": dual_wave, "wait_is_over": wait_is_over, "lockon_red": lockon_red, "raw_swing": lambda: raw_label("IMG_2661", 9.6, 2.4, "REVERSE CRUNCH: WATCH THE SWING", "raw_swing.mp4"),
        "sample_result": sample_result, "labelled_lunge": labelled_lunge, "countdown_blast": countdown_blast, "ghost_stop": ghost_stop, "lockon": lockon, "wave": wave, "false_alarm": false_alarm, "cant_see": cant_see,
        "sway_red": sway_red, "wall": wall, **{f"arch_{s}": (lambda s=s: arch(s)) for s in range(1, 6)}}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name in (sys.argv[1:] or JOBS):
        JOBS[name]()
