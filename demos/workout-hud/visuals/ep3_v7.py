"""Ep 3 final-cut fixes (20-21 Nov night): visuals timed to the creator's recorded words (cuts.json).

Fixes from the final-cut judge + creator: clean hook (no tiny HUD labels), research rows pop on EASY / HARD / FOOL,
1.25 s countdown, camera-angle callback on the false alarm, CHECK gate timed to the voice and relabelled CHECK, the
lunge shown passing after the fix, the hook paid off (THE ONE SET on the 23-set wall), a big send-to-a-friend CTA.
Writes per-beat assets into ~/Movies/ContentOS/workout-analyser-main/assets/v7_*.mp4.
"""
import json, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "judge"))
import ep3_render as E  # noqa: E402
import ep3_v6 as V  # noqa: E402
import hud_fx as X  # noqa: E402
import pose_fx as P  # noqa: E402
import judge as J  # noqa: E402

W, PH, FPS = 1080, 960, 30
A = Path.home() / "Movies/ContentOS/workout-analyser-main/assets"
VIS = E.OUT
WT = json.loads(Path("/private/tmp/claude-501/-Users-sagartekwani/9336bd28-6bb6-450a-be06-4a6959088d43/scratchpad/word_times.json").read_text())
DL = Path.home() / "Downloads"


def wt(beat, word, i=0):
    return WT[str(beat)]["words"][word][i]


def dur(beat):
    return WT[str(beat)]["dur"]


def writer(name):
    V.panelmode(); return P.Writer(A / name)


def frames(path, start=0.0, d=None):
    return V.read_frames(path, start, d)


def hold(seq, n):
    """Pad/trim a frame list to n frames (hold the last frame)."""
    seq = list(seq)[:n]
    return seq + [seq[-1]] * (n - len(seq)) if seq else [V.blank()] * n


# ------------------------------------------------------------------ beat 1: clean hook, STOP on "never"
def hook():
    kp, video = P.keypoints(DL / "IMG_2661.MOV"); kpn = P.smooth_kp(kp); a = J.analyse(kpn)
    reps = {r["rep"]: r for r in a["reps"]}; j = json.loads((P.DATA / "IMG_2661" / "judge.json").read_text())["verdict"]
    r, br = reps[j["worst_rep"]], reps[j["best_rep"]]; h0, _, h1 = r["_f"]; b0, _, b1 = br["_f"]; n = h1 - h0
    side = a["side"]; names = (5, 11, 13); A_, B_, C_ = [J.RIGHT[x] if side == "right" else x for x in names]
    wr = writer("v7_beat01.mp4")  # open the writer first: panelmode() resets the crop
    E.fresh("IMG_2661"); seg = kpn[h0:h1 + 1]; ys = seg[:, :, 1][seg[:, :, 2] >= P.CONF_MIN]
    X.CROP["y0"] = int(min(max(float(np.percentile(ys, 2)) - 120, 0), 1920 - 960))
    src = list(P.frames(video, h0, n)); stamp_at = 2.45; total = int((dur(1) + 0.2) * FPS)
    last = None
    for k in range(total):
        t = k / FPS
        if t < stamp_at:
            i = int(t * FPS / 2) % len(src)  # half-speed loop of the worst rep
            img, f = X.prep(X.grade(src[i]), kpn[h0 + i]); bi = b0 + int(round(i / max(1, n) * (b1 - b0)))
            o = f[B_, :2]; s = np.linalg.norm(f[A_, :2] - o) + 1e-6; ob = kpn[bi][B_, :2]
            sb = np.linalg.norm(kpn[bi][A_, :2] - ob) + 1e-6; g = (kpn[bi][:, :2] - ob) / sb * s + o
            gf = np.concatenate([g, np.ones((17, 1))], 1); gf[:, 1] -= 0; ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            gf[:, 1] = gf[:, 1] - (X.CROP["y0"] if False else 0)
            chain = [J.RIGHT[x] if side == "right" else x for x in (5, 11, 13, 15)]
            for a_, b_ in zip(chain, chain[1:]):
                d.line([P.px(gf, a_), P.px(gf, b_)], fill=X.GREEN + (200,), width=16)
            X.skeleton(d, f, w=6)
            d.polygon([P.px(f, B_), P.px(f, C_), (gf[C_, 0], gf[C_, 1])], fill=X.RED + (150,))
            last = Image.alpha_composite(img, X.glow(ov)); wr.add(last)
        else:
            wr.add(X.stamp(last, "STOP", "HALF REPS", (t - stamp_at) / 0.2))
    wr.close(); print("v7_beat01")


# ------------------------------------------------------------------ beat 3: research, rows on the words
def research():
    rows = [("REPS", "COUNT THEM", "EASY", X.GREEN, wt(3, "easy") - 0.25), ("REPS", "JUDGE THEM", "HARD", X.RED, wt(3, "hard") - 0.25),
            ("CAMERA ANGLE", "WRONG VIEW", "FOOLS THE AGENT", X.AMBER, wt(3, "fool") - 0.5)]
    wr = writer("v7_beat03.mp4")
    for k in range(int((dur(3) + 0.2) * FPS)):
        t = k / FPS; im = V.blank(); d = ImageDraw.Draw(im)
        if t < rows[0][4]:  # the research: papers stacking up
            n = min(200, int(200 * X.ease(t / 3.0)))
            d.text((W // 2, 300), f"{n}+", font=X.hf(220), fill=X.WHITE + (255,), anchor="mm")
            d.text((W // 2, 450), "RESEARCH PAPERS + TOOLS", font=X.hf(64), fill=X.CYAN + (255,), anchor="mm")
            for i in range(min(18, int(t * 6))):
                x = 140 + (i % 9) * 92; y = 560 + (i // 9) * 120
                V.rough_box(d, (x, y, x + 74, y + 96), X.CYAN_D, 3, 70 + i, 1.0)
                for q in range(4):
                    d.line([(x + 10, y + 18 + q * 18), (x + 62, y + 18 + q * 18)], fill=X.CYAN_D + (255,), width=3)
        else:
            d.text((W // 2, 70), "200+ PAPERS + TOOLS SAID:", font=X.hf(58), fill=X.WHITE + (255,), anchor="mm")
            for i, (a, b, c, col, t0) in enumerate(rows):
                p = X.ease((t - t0) / 0.45)
                if p <= 0:
                    continue
                y = 170 + i * 220
                V.rough_box(d, (40, y, 300, y + 140), X.CYAN, 5, 10 + i, min(1, p * 1.5))
                d.text((170, y + 70), a, font=V.kf(44 if len(a) < 6 else 36), fill=X.WHITE + (255,), anchor="mm")
                V.arrow(d, (310, y + 70), (390, y + 70), X.WHITE, 5, min(1, max(0, p * 2 - 0.5)), 20 + i)
                if p > 0.4:
                    V.rough_box(d, (400, y, 680, y + 140), X.CYAN, 5, 30 + i, 1.0)
                    d.text((540, y + 70), b, font=V.kf(40), fill=X.WHITE + (255,), anchor="mm")
                    V.arrow(d, (690, y + 70), (760, y + 70), X.WHITE, 5, 1.0 if p > 0.7 else 0, 40 + i)
                if p > 0.7:
                    V.rough_box(d, (770, y, 1050, y + 140), col, 7, 50 + i, 1.0)
                    d.text((910, y + 70), c, font=X.hf(60 if len(c) < 6 else 40), fill=col + (255,), anchor="mm")
        wr.add(im.convert("RGBA"))
    wr.close(); print("v7_beat03")


# ------------------------------------------------------------------ countdown 1.25 s (full vertical)
def countdown():
    E.countdown_blast(step=0.25, blast=0.5)
    V.full_vertical("countdown_blast.mp4", "FULL_countdown_short.mp4")


# ------------------------------------------------------------------ beat 9: false alarm + camera callback
def false_alarm():
    src = frames(VIS / "false_alarm.mp4"); n = int((dur(9) + 0.2) * FPS); seq = hold(src, n); cam = wt(9, "camera") - 0.3
    wr = writer("v7_beat09.mp4")
    for k, im in enumerate(seq):
        t = k / FPS
        if t > cam:
            ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); a = int(255 * X.ease((t - cam) / 0.25))
            d.rectangle([0, 0, W, 96], fill=(40, 22, 0, min(a, 235)))
            d.text((W // 2, 48), "THE CAMERA ANGLE FOOLED IT · THE RESEARCH WARNED", font=X.hf(46), fill=X.AMBER + (a,), anchor="mm")
            im = Image.alpha_composite(im, ov)
        wr.add(im)
    wr.close(); print("v7_beat09")


# ------------------------------------------------------------------ beat 10: CHECK, gate on the voice, lunge passes
def check():
    head = frames(VIS / "arch3_check.mp4"); n_total = int((dur(10) + 0.2) * FPS)
    r1, r2, slam = wt(10, "only", 0) - 0.2, wt(10, "nothing") - 0.2, wt(10, "both") - 0.2
    gate_from = min(r1, 4.6); fixed_from = slam + 0.35
    lunge = frames(VIS / "_orig" / "false_alarm.mp4", 2.4, 1.0) or frames(VIS / "false_alarm.mp4", 2.4, 1.0)

    def row(d, y, judge, chk, result, colr, ex, p, seed):
        V.rough_box(d, (60, y, 330, y + 120), X.CYAN, 4, seed, p); V.rough_box(d, (390, y, 660, y + 120), X.CYAN, 4, seed + 5, p)
        if p > 0.7:
            d.text((195, y + 38), "JUDGE", font=V.kf(34), fill=X.CYAN + (255,), anchor="mm"); d.text((195, y + 82), judge, font=V.kf(42), fill=X.RED + (255,), anchor="mm")
            d.text((525, y + 38), "CHECK", font=V.kf(34), fill=X.CYAN + (255,), anchor="mm")
            d.text((525, y + 82), chk, font=V.kf(42), fill=(X.RED if chk == "STOP" else X.GREEN) + (255,), anchor="mm")
            d.text((360, y + 60), "+", font=V.kf(60), fill=X.WHITE + (255,), anchor="mm"); V.arrow(d, (670, y + 60), (740, y + 60), X.WHITE, 4, 1.0, seed + 9)
            V.rough_box(d, (750, y + 5, 1050, y + 115), colr, 6, seed + 11, 1.0)
            d.text((900, y + 60), result, font=V.kf(40 if len(result) > 6 else 46), fill=colr + (255,), anchor="mm")
            d.text((60, y + 140), ex, font=V.kf(32), fill=X.GREY + (255,))

    wr = writer("v7_beat10.mp4")
    for k in range(n_total):
        t = k / FPS
        if t < gate_from:
            wr.add(head[min(k, len(head) - 1)])
        elif t < fixed_from:
            im = V.blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            V.banner(d, "PART 3 · CHECK", X.RED)
            d.text((W // 2, 150), "CHECK: WATCHES THE VIDEO ONLY", font=V.kf(52), fill=X.WHITE + (255,), anchor="mm")
            row(d, 230, "STOP", "STOP", "STOP", X.RED, "both say STOP (my reverse crunch)", X.ease((t - r1) / 0.5), 40)
            row(d, 470, "STOP", "OK", "CHECK FOOTAGE", X.AMBER, "they disagree (my lunge)", X.ease((t - r2) / 0.5), 60)
            if t > slam:
                a = int(255 * X.ease((t - slam) / 0.2)); sc = 1.3 - 0.3 * X.ease((t - slam) / 0.2)
                d.text((W // 2, 790), "STOP ONLY WHEN BOTH SAY STOP", font=X.hf(int(64 * sc)), fill=X.WHITE + (a,), anchor="mm")
            wr.add(Image.alpha_composite(im, ov))
        else:  # the fix working on the same lunge
            i = min(int((t - fixed_from) * FPS), len(lunge) - 1); im = X.grade(lunge[i]) if lunge else V.blank()
            ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); a = int(255 * X.ease((t - fixed_from) / 0.2))
            d.rectangle([40, 300, W - 40, 620], fill=(0, 30, 16, min(a, 225)), outline=X.GREEN + (a,), width=6)
            d.text((W // 2, 370), "MY LUNGE, RE-CHECKED", font=X.hf(52), fill=X.WHITE + (a,), anchor="mm")
            d.text((W // 2, 460), "JUDGE: STOP · CHECK: OK", font=X.hf(60), fill=X.AMBER + (a,), anchor="mm")
            d.text((W // 2, 560), "NO STOP. FALSE ALARM FIXED", font=X.hf(60), fill=X.GREEN + (a,), anchor="mm")
            wr.add(Image.alpha_composite(im.convert("RGBA"), X.glow(ov, 6)))
    wr.close(); print("v7_beat10")


# ------------------------------------------------------------------ beat 11: CONTINUE on "continue", STOP on "stop"
def verdicts():
    chest = frames(VIS / "chest_continue.mp4"); ghost = frames(VIS / "ghost_stop.mp4")
    c_at, s_at = wt(11, "continue"), wt(11, "stop")
    chest_stamp_idx = int(1.6 * FPS)  # chest_continue stamps at 1.6 s
    ghost_stamp_idx = len(ghost) - int(2.0 * FPS)  # ghost_stop: stamp for the last 2.0 s
    n = int((dur(11) + 0.2) * FPS); wr = writer("v7_beat11.mp4")
    for k in range(n):
        t = k / FPS
        if t < s_at - 0.9:
            i = chest_stamp_idx + int((t - c_at) * FPS)
            wr.add(chest[max(0, min(i, len(chest) - 1))])
        else:
            i = ghost_stamp_idx + int((t - s_at) * FPS)
            wr.add(ghost[max(0, min(i, len(ghost) - 1))])
    wr.close(); print("v7_beat11")


# ------------------------------------------------------------------ beat 12: hook payoff + big CTA
def payoff_cta():
    wall = frames(VIS / "wall_of_sets.mp4"); last = wall[-1].convert("RGBA")
    # the STOP tile: row 3, col 1 of the 6x4 grid (index 12) in wall_of_sets
    cols, tw, th = 6, W // 6, (PH - 220) // 4; i = 12; x, y = (i % cols) * tw + 4, 150 + (i // cols) * th + 4
    swing = frames(VIS / "raw_swing.mp4"); n_pay = int(1.2 * FPS); wr = writer("v7_beat12.mp4")
    for k in range(n_pay):
        p = X.ease(k / (0.7 * FPS)); z = 1 + 2.2 * p
        cx, cy = x + tw / 2, y + th / 2; w2, h2 = W / z, PH / z
        x0 = min(max(cx - w2 / 2, 0), W - w2); y0 = min(max(cy - h2 / 2, 0), PH - h2)
        im = last.crop((int(x0), int(y0), int(x0 + w2), int(y0 + h2))).resize((W, PH)); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        if k > 0.5 * FPS:
            a = int(255 * X.ease((k / FPS - 0.5) / 0.25))
            d.rectangle([60, 680, W - 60, 860], fill=(30, 0, 0, min(a, 225)), outline=X.RED + (a,), width=5)
            d.text((W // 2, 740), "THE ONE SET · OF 23", font=X.hf(64), fill=X.WHITE + (a,), anchor="mm")
            d.text((W // 2, 815), "HALF REPS", font=X.hf(56), fill=X.RED + (a,), anchor="mm")
        wr.add(Image.alpha_composite(im, ov))
    for k in range(int(4.0 * FPS)):
        im = swing[min(k, len(swing) - 1)].copy(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        a = int(255 * X.ease(k / (0.25 * FPS)))
        d.rectangle([0, 640, W, 860], fill=(3, 12, 20, min(a, 225)))
        d.text((W // 2, 705), "SEND THIS TO YOUR", font=X.hf(66), fill=X.WHITE + (a,), anchor="mm")
        d.text((W // 2, 790), "HALF-REP FRIEND", font=X.hf(84), fill=X.AMBER + (a,), anchor="mm")
        wr.add(Image.alpha_composite(im, ov))
    wr.close(); print("v7_beat12")


JOBS = {"hook": hook, "research": research, "countdown": countdown, "false_alarm": false_alarm, "check": check,
        "verdicts": verdicts, "payoff_cta": payoff_cta}

if __name__ == "__main__":
    for n in (sys.argv[1:] or JOBS):
        JOBS[n]()
