"""Ep 3 v8 fixes (two-judge review, 21 Nov ~01:50): no product-name pile-up at 5-10 s, shorter research counter,
the fix shown working for 2 s, a clean ONE-SET payoff card with the 23-set tally, CTA on its own beat.
"""
import json, sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ep3_v7 as S7  # noqa: E402  (loads word_times.json; helpers)
import ep3_v6 as V  # noqa: E402
import hud_fx as X  # noqa: E402
import pose_fx as P  # noqa: E402

W, PH, FPS = 1080, 960, 30
VIS = S7.VIS; A = S7.A; wt = S7.wt; dur = S7.dur
TALLY = json.loads((P.DATA / "verdicts.json").read_text())["summary"]["final_counts"]


def beat2():
    """Months of effort: 3 fast real-footage shots with skeletons + a strip; WORKOUT ANALYSER lands on 'see'."""
    shots = [(VIS / "lockon_red.mp4", 2.4), (VIS / "dual_wave.mp4", 2.0), (VIS / "judge_hold.mp4", 1.0)]
    title_at = wt(2, "see") - 0.5; n = int((dur(2) + 0.2) * FPS); seg = title_at / len(shots)
    srcs = [S7.frames(p, s0, seg + 0.1) for p, s0 in shots]; wr = S7.writer("v8_beat02.mp4")
    for k in range(n):
        t = k / FPS
        if t < title_at:
            i = min(int(t / seg), len(srcs) - 1); fr = srcs[i]; im = fr[min(int((t - i * seg) * FPS), len(fr) - 1)].copy()
            ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            d.rectangle([0, 0, W, 100], fill=(3, 12, 20, 235)); d.line([(0, 100), (W, 100)], fill=X.CYAN + (255,), width=4)
            d.text((W // 2, 50), "MONTHS OF EFFORT · ON WEEKENDS", font=X.hf(56), fill=X.WHITE + (255,), anchor="mm")
            im = Image.alpha_composite(im, ov)
            if t - i * seg < 0.06:
                im = Image.alpha_composite(im, Image.new("RGBA", im.size, (255, 255, 255, 90)))
        else:
            im = V.blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            sc = 1.25 - 0.25 * X.ease((t - title_at) / 0.2)
            d.text((W // 2, 440), "WORKOUT", font=X.hf(int(170 * sc)), fill=X.WHITE + (255,), anchor="mm")
            d.text((W // 2, 600), "ANALYSER", font=X.hf(int(170 * sc)), fill=X.CYAN + (255,), anchor="mm")
            X.brackets(d, (110, 300, W - 110, 720), X.CYAN, L=46, w=6); im = Image.alpha_composite(im, X.glow(ov, 10))
        wr.add(im)
    wr.close(); print("v8_beat02")


def beat3():
    """Counter ramps fast (lands ~1.2 s, held to 3 s), then the rows build early; verdict blocks land on the words."""
    v_easy, v_hard, v_fool = wt(3, "easy") - 0.25, wt(3, "hard") - 0.25, wt(3, "fool") - 0.5
    rows = [("REPS", "COUNT THEM", "EASY", X.GREEN, 3.0, v_easy), ("REPS", "JUDGE THEM", "HARD", X.RED, 3.4, v_hard),
            ("CAMERA ANGLE", "WRONG VIEW", "FOOLS THE AGENT", X.AMBER, v_fool - 0.6, v_fool)]
    wr = S7.writer("v8_beat03.mp4")
    for k in range(int((dur(3) + 0.2) * FPS)):
        t = k / FPS; im = V.blank(); d = ImageDraw.Draw(im)
        if t < 3.0:
            n = min(200, int(200 * X.ease(t / 1.2)))
            d.text((W // 2, 360), f"{n}+", font=X.hf(int(240 * (1.15 - 0.15 * X.ease((t - 1.2) / 0.2) if t > 1.2 else 1.15))), fill=X.WHITE + (255,), anchor="mm")
            d.text((W // 2, 520), "RESEARCH PAPERS + TOOLS", font=X.hf(70), fill=X.CYAN + (255,), anchor="mm")
        else:
            d.text((W // 2, 70), "200+ PAPERS + TOOLS SAID:", font=X.hf(58), fill=X.WHITE + (255,), anchor="mm")
            for i, (a, b, c, col, t_in, t_v) in enumerate(rows):
                p = X.ease((t - t_in) / 0.4)
                if p <= 0:
                    continue
                y = 170 + i * 220
                V.rough_box(d, (40, y, 300, y + 140), X.CYAN, 5, 10 + i, min(1, p * 1.5))
                d.text((170, y + 70), a, font=V.kf(44 if len(a) < 6 else 36), fill=X.WHITE + (255,), anchor="mm")
                if p > 0.5:
                    V.arrow(d, (310, y + 70), (390, y + 70), X.WHITE, 5, 1.0, 20 + i)
                    V.rough_box(d, (400, y, 680, y + 140), X.CYAN, 5, 30 + i, 1.0)
                    d.text((540, y + 70), b, font=V.kf(40), fill=X.WHITE + (255,), anchor="mm")
                if t > t_v:
                    q = X.ease((t - t_v) / 0.25)
                    V.arrow(d, (690, y + 70), (760, y + 70), X.WHITE, 5, 1.0, 40 + i)
                    V.rough_box(d, (770, y, 1050, y + 140), col, 7, 50 + i, 1.0)
                    d.text((910, y + 70), c, font=X.hf(int((60 if len(c) < 6 else 40) * (1.3 - 0.3 * q))), fill=col + (255,), anchor="mm")
        wr.add(im.convert("RGBA"))
    wr.close(); print("v8_beat03")


def beat10():
    """CHECK gate on the voice; the lunge re-check shown for ~2 s."""
    S7.wt_orig = S7.wt
    import types
    src = S7.check.__code__
    # reuse v7's check() but start the 'fixed' card right after "both ... stop"
    old = S7.check
    def patched():
        both = wt(10, "both")
        S7.WT["10"]["words"]["both"] = [both]  # keep
        old_fixed = 1.4
        return old_fixed
    # simplest: re-render via v7 with the fixed card earlier
    p = Path(S7.__file__); s = p.read_text()
    if "fixed_from = slam + 1.4" in s:
        p.write_text(s.replace("fixed_from = slam + 1.4", "fixed_from = slam + 0.35"))
    import importlib; importlib.reload(S7); S7.check()
    import shutil; shutil.move(str(A / "v7_beat10.mp4"), str(A / "v8_beat10.mp4")); print("v8_beat10")


def beat11():
    """CONTINUE on 'continue', STOP on 'stop', then from 'because' a clean payoff card: THE ONE SET OF 23 + tally."""
    chest = S7.frames(VIS / "chest_continue.mp4"); ghost = S7.frames(A / "v7_beat01.mp4")
    c_at, s_at, pay_at = wt(11, "continue"), wt(11, "stop"), wt(11, "because") - 0.1
    chest_stamp_idx = int(1.6 * FPS); hook_last = ghost[-1].convert("RGBA")
    wr = S7.writer("v8_beat11.mp4")
    for k in range(int((dur(11) + 0.2) * FPS)):
        t = k / FPS
        if t < s_at - 0.15:
            i = chest_stamp_idx + int((t - c_at) * FPS); wr.add(chest[max(0, min(i, len(chest) - 1))])
        elif t < pay_at:
            wr.add(hook_last)
        else:
            im = Image.alpha_composite(hook_last, Image.new("RGBA", hook_last.size, (3, 12, 20, 200)))
            ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); a = int(255 * X.ease((t - pay_at) / 0.25))
            d.text((W // 2, 170), "THE ONE SET", font=X.hf(150), fill=X.RED + (a,), anchor="mm")
            d.text((W // 2, 300), "OUT OF 23", font=X.hf(96), fill=X.WHITE + (a,), anchor="mm")
            d.text((W // 2, 410), "REVERSE CRUNCH · HALF REPS", font=X.hf(60), fill=X.AMBER + (a,), anchor="mm")
            if t > pay_at + 1.2:
                b = int(255 * X.ease((t - pay_at - 1.2) / 0.3)); y = 540
                items = [(f"{TALLY['CONTINUE']}", "CONTINUE", X.GREEN), (f"{TALLY['HOLD']}", "HOLD", X.AMBER), (f"{TALLY['STOP']}", "STOP", X.RED),
                         (f"{TALLY[chr(67) + 'AN' + chr(39) + 'T SEE']}", "CAN'T SEE", X.GREY), (f"{TALLY['CHECK FOOTAGE']}", "FALSE ALARM CAUGHT", X.CYAN)]
                xs = [110, 300, 470, 640, 860]
                for (num, lab, col), x in zip(items, xs):
                    d.text((x, y), num, font=X.hf(110), fill=col + (b,), anchor="mm")
                    d.text((x, y + 85), lab, font=X.hf(30 if len(lab) > 9 else 36), fill=col + (b,), anchor="mm")
            wr.add(Image.alpha_composite(im, X.glow(ov, 6)))
    wr.close(); print("v8_beat11")


def beat12():
    """CTA only: the swing with a big SEND THIS TO YOUR HALF-REP FRIEND."""
    swing = S7.frames(VIS / "raw_swing.mp4"); wr = S7.writer("v8_beat12.mp4")
    for k in range(int((dur(12) + 0.3) * FPS)):
        im = swing[min(k, len(swing) - 1)].copy(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        a = int(255 * X.ease(k / (0.2 * FPS)))
        d.rectangle([0, 600, W, 860], fill=(3, 12, 20, min(a, 230)))
        d.text((W // 2, 680), "SEND THIS TO YOUR", font=X.hf(72), fill=X.WHITE + (a,), anchor="mm")
        d.text((W // 2, 785), "HALF-REP FRIEND", font=X.hf(96), fill=X.AMBER + (a,), anchor="mm")
        wr.add(Image.alpha_composite(im, ov))
    wr.close(); print("v8_beat12")


JOBS = {"beat2": beat2, "beat3": beat3, "beat10": beat10, "beat11": beat11, "beat12": beat12}
if __name__ == "__main__":
    for n in (sys.argv[1:] or JOBS):
        JOBS[n]()


def beat8():
    """JUDGE: ghost of my best pulldown rep over rep 4 first, then the proof big (62 vs 86 on 'best'), HOLD last and small."""
    import ep3_render as E, judge as J
    j = json.loads((P.DATA / "IMG_2783" / "judge.json").read_text())["verdict"]
    E.fresh("IMG_2783"); tmp = A / "_tmp_ghost8.mp4"
    X.ghost(S7.DL / "IMG_2783.MOV", j["worst_rep"], j["best_rep"], tmp, None, None, slow=2, loops=3)
    g = S7.frames(tmp); best_at = 4.5; hold_at = 6.0; n = int((7.4 + 0.2) * FPS); wr = S7.writer("v8_beat08.mp4")
    for k in range(n):
        t = k / FPS; im = g[min(k, len(g) - 1)].copy() if t < best_at else g[min(int(best_at * FPS), len(g) - 1)].copy()
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        d.rectangle([0, 0, W, 92], fill=(3, 12, 20, 235)); d.line([(0, 92), (W, 92)], fill=X.GREEN + (255,), width=4)
        d.text((W // 2, 46), "PART 2 · JUDGE · GREEN = MY BEST REP", font=X.hf(50), fill=X.GREEN + (255,), anchor="mm")
        if t > best_at:
            a = int(255 * X.ease((t - best_at) / 0.25)); sc = 1.25 - 0.25 * X.ease((t - best_at) / 0.25)
            d.rectangle([40, 300, W - 40, 560], fill=(3, 12, 20, min(a, 225)), outline=X.AMBER + (a,), width=5)
            d.text((W // 2, 375), "REP 4: 62°", font=X.hf(int(96 * sc)), fill=X.WHITE + (a,), anchor="mm")
            d.text((W // 2, 485), "VS MY BEST: 86°", font=X.hf(int(96 * sc)), fill=X.GREEN + (a,), anchor="mm")
        if t > hold_at:
            b = int(255 * X.ease((t - hold_at) / 0.2))
            d.rectangle([200, 620, W - 200, 760], fill=(40, 22, 0, min(b, 230)), outline=X.AMBER + (b,), width=5)
            d.text((W // 2, 668), "HOLD", font=X.hf(70), fill=X.AMBER + (b,), anchor="mm")
            d.text((W // 2, 730), "FIX IT NEXT SET", font=X.hf(40), fill=X.WHITE + (b,), anchor="mm")
        wr.add(Image.alpha_composite(im, X.glow(ov, 5)))
    wr.close(); tmp.unlink(missing_ok=True); print("v8_beat08")


JOBS["beat8"] = beat8
