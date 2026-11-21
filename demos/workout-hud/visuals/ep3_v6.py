"""Script v6 visuals (creator's 15 notes, 20 Nov 2026). Reuses the HUD helpers; adds simple line diagrams.

Usage: demos/workout-hud/.venv/bin/python demos/workout-hud/visuals/ep3_v6.py [name ...]
"""
import json, sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "judge"))
import ep3_render as E  # noqa: E402
import hud_fx as X  # noqa: E402
import pose_fx as P  # noqa: E402

OUT = E.OUT; W, PH, FPS = 1080, 960, 30
DL = Path.home() / "Downloads"
KALAM = P.FONTS / "Kalam-Bold.ttf"


def kf(n):
    return ImageFont.truetype(str(KALAM), n)


def panelmode():
    X.H, X.SAFE_BOTTOM, P.H = PH, PH - 100, PH; X.CROP.update(on=False, y0=0)


def write(name, gen):
    panelmode(); X.write(OUT / name, gen())


def blank():
    return Image.new("RGBA", (W, PH), (3, 12, 20, 255))


def read_frames(path, start_s=0.0, dur_s=None):
    cap = cv2.VideoCapture(str(path)); fps = cap.get(cv2.CAP_PROP_FPS) or 30
    cap.set(cv2.CAP_PROP_POS_MSEC, start_s * 1000); out = []
    while True:
        ok, fr = cap.read()
        if not ok or (dur_s and len(out) >= dur_s * fps):
            break
        out.append(Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA"))
    cap.release(); return out


def banner(d, text, col=X.CYAN):
    """Part heading on top of the visual (creator note 7)."""
    d.rectangle([0, 0, W, 92], fill=(3, 12, 20, 235)); d.line([(0, 92), (W, 92)], fill=col + (255,), width=4)
    d.text((W // 2, 46), text, font=X.hf(58), fill=col + (255,), anchor="mm")


def with_banner(src, name, text, col=X.CYAN):
    frames = read_frames(OUT / src)
    def gen():
        for im in frames:
            ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); banner(ImageDraw.Draw(ov), text, col)
            yield Image.alpha_composite(im, ov)
    write(name, gen)


def rough_box(d, box, col, w=5, seed=0, p=1.0):
    x0, y0, x1, y1 = box; pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    total = 4; done = p * total
    for i in range(4):
        seg = min(1.0, max(0.0, done - i))
        if seg > 0:
            P.rough_line(d, pts[i], pts[i + 1], col, w, seed + i, seg)


def arrow(d, a, b, col, w=5, p=1.0, seed=0):
    if p <= 0:
        return
    e = (a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p); P.rough_line(d, a, e, col, w, seed, 1.0)
    if p >= 1:
        v = np.subtract(b, a); v = v / (np.linalg.norm(v) + 1e-6); n = np.array([-v[1], v[0]])
        tip = np.array(b, float)
        for s in (1, -1):
            P.rough_line(d, tuple(tip), tuple(tip - 22 * v + s * 12 * n), col, w, seed + s, 1.0)


# ------------------------------------------------------------------ beat 2
def build_montage():
    """Months of effort on weekends: Ep 1 SYSTEM ONLINE (5 parts) with SET SCAN circled -> the judge's code -> first run."""
    ep1 = Image.open(OUT / "ep1_system_online.png").convert("RGBA").crop((0, 860, 1080, 1820))  # SYSTEM ONLINE + the 5-part list
    code = (HERE.parent / "judge" / "judge.py").read_text().splitlines()[30:44]
    lock = read_frames(OUT / "lockon_red.mp4", 2.6, 1.2)
    def gen():
        n1, n2, n3 = int(2.2 * FPS), int(1.0 * FPS), len(lock)
        for k in range(n1):
            t = k / FPS; im = ep1.copy(); d = ImageDraw.Draw(im, "RGBA")
            d.rectangle([400, 790, 680, 900], fill=(9, 12, 20, 255))  # mask Ep 1's burned-in caption word
            if t > 0.6:  # circle SET SCAN (second row of the list)
                p = X.ease((t - 0.6) / 0.6)
                d.arc([150, 495, 960, 600], 200, 200 + 360 * p, fill=X.RED + (255,), width=8)
            if t > 1.2:
                a = int(255 * X.ease((t - 1.2) / 0.3))
                d.rectangle([150, 130, 930, 210], fill=(30, 0, 0, min(a, 220)), outline=X.RED + (a,), width=3)
                d.text((W // 2, 170), "TODAY: SET SCAN = WORKOUT ANALYSER", font=X.hf(48), fill=X.WHITE + (a,), anchor="mm")
            X.panel(d, (40, 20), ["12 NOV · GYM JARVIS: 5 PARTS"], size=36, sub="months of effort, on weekends")
            yield im
        for k in range(n2):
            im = blank(); d = ImageDraw.Draw(im)
            for r, line in enumerate(code):
                d.text((60, 110 + r * 52), line[:60], font=X.hf(34, False), fill=(X.GREEN if "def " in line else X.CYAN) + (255,))
            X.panel(d, (40, 20), ["19 NOV · THE JUDGE"], size=40)
            yield im
        for im in lock:
            d = ImageDraw.Draw(im); X.panel(d, (40, 650), ["20 NOV · FIRST RUN"], size=40); yield im
    write("build_montage.mp4", gen)


# ------------------------------------------------------------------ beats 3-4
def research_warning(n_sources, n_papers, n_tools):
    lines = ["COUNTING REPS: EASY", "JUDGING THEM: HARD", "THE CAMERA ANGLE CAN FOOL THE AGENT"]
    def gen():
        for k in range(int(5.2 * FPS)):
            t = k / FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            if n_sources:
                cnt = int(n_sources * X.ease(t / 1.6))
                d.text((W // 2, 120), f"{cnt}", font=X.hf(190), fill=X.WHITE + (255,), anchor="mm")
                d.text((W // 2, 245), f"PAPERS + TOOLS  ·  {n_papers} PAPERS · {n_tools} TOOLS · 16 REVIEWS", font=X.hf(40, False), fill=X.CYAN + (255,), anchor="mm")
            else:  # provisional until the research sweep reports the true count
                d.text((W // 2, 150), "PAPERS + TOOLS", font=X.hf(120), fill=X.WHITE + (255,), anchor="mm")
            for i in range(14):  # source cards stacking behind the count
                a = int(120 * X.ease((t - i * 0.08) / 0.2))
                y = 300 + (i % 7) * 10; x = 120 + i * 60
                d.rectangle([x, y, x + 160, y + 26], outline=X.CYAN_D + (a,), width=2)
            for i, ln in enumerate(lines):
                tt = 1.8 + i * 0.6
                if t > tt:
                    a = int(255 * X.ease((t - tt) / 0.3)); col = X.AMBER if i == 2 else (X.GREEN if i == 0 else X.RED)
                    d.text((W // 2, 430 + i * 105), ln, font=X.hf(72 if i < 2 else 58), fill=col + (a,), anchor="mm")
            if t > 4.0:
                p = X.ease((t - 4.0) / 0.5); x0 = 140 + (40 - 140) * p; y0 = 760 + (12 - 760) * p; sc = 1 - 0.45 * p
                w, h = int(800 * sc), int(84 * sc)
                d.rectangle([x0, y0, x0 + w, y0 + h], fill=(40, 22, 0, 230), outline=X.AMBER + (255,), width=4)
                d.text((x0 + w // 2, y0 + h // 2), "WARNING: THE CAMERA ANGLE CAN FOOL IT", font=X.hf(int(44 * sc)), fill=X.AMBER + (255,), anchor="mm")
            yield Image.alpha_composite(im, X.glow(ov, 5))
    write("research_warning.mp4", gen)


# ------------------------------------------------------------------ beat 5
def wait_countdown():
    """WAIT FOR IT slam (0.8 s) then the plain 3-2-1 + blast (no wall)."""
    cd = read_frames(OUT / "countdown_blast.mp4")
    def gen():
        for k in range(int(0.8 * FPS)):
            t = k / FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            f = X.hf(int(170 * (1.4 - 0.4 * X.ease(t / 0.18))))
            d.text((W // 2, 420), "WAIT FOR IT", font=f, fill=X.WHITE + (255,), anchor="mm")
            X.brackets(d, (110, 300, W - 110, 540), X.CYAN, L=40, w=6)
            im = Image.alpha_composite(im, X.glow(ov, 10))
            if t < 0.06:
                im = Image.alpha_composite(im, Image.new("RGBA", im.size, (255, 255, 255, 140)))
            yield im
        for im in cd:
            yield im
    write("wait_countdown.mp4", gen)


# ------------------------------------------------------------------ beat 6
def sets_montage():
    """23 sets on trial: quick cuts across body parts (raw, graded), body-part tag + running count."""
    shots = [("IMG_2780", 6, "CHEST · CABLE FLY"), ("IMG_2783", 4, "BACK · LAT PULLDOWN"), ("IMG_2785", 4, "BACK · SEATED ROW"),
             ("IMG_2649", 10, "LEGS · HACK SQUAT"), ("IMG_2653", 6, "LEGS · LEG PRESS"), ("IMG_2661", 3, "CORE · REVERSE CRUNCH"),
             ("IMG_2662", 10, "CORE · RUSSIAN TWIST")]
    seg = 0.45
    def gen():
        for i, (clip, t0, tag) in enumerate(shots):
            c = DL / f"{clip}.MOV"; kp, video = P.keypoints(c)
            fr = list(P.frames(video, int(t0 * FPS), int(seg * FPS)))
            vis = kp[:, :, 2] >= P.CONF_MIN; cy = float(np.median(kp[:, :, 1][vis])) if vis.any() else 960
            y0 = int(min(max(cy - 480, 0), 1920 - 960))
            for k, im in enumerate(fr):
                im = X.grade(im).crop((0, y0, W, y0 + PH)); d = ImageDraw.Draw(im)
                X.panel(d, (40, 30), [tag], size=46, sub="on trial")
                n = round(23 * (i * len(fr) + k + 1) / (len(shots) * len(fr)))
                X.panel(d, (W - 330, 30), [f"{n} / 23 SETS"], size=46)
                yield im
    write("sets_montage.mp4", gen)


# ------------------------------------------------------------------ beat 7
def system_card():
    """Simple hand-drawn line diagram: THE SYSTEM -> 1 SEE -> 2 JUDGE -> 3 CHECK."""
    boxes = [("1", "SEE", "17 joints · waves", 60), ("2", "JUDGE", "rep vs my best", 410), ("3", "CHECK", "2nd AI · video", 760)]
    def gen():
        for k in range(int(2.6 * FPS)):
            t = k / FPS; im = blank(); d = ImageDraw.Draw(im)
            d.text((W // 2, 120), "THE SYSTEM", font=kf(96), fill=X.WHITE + (255,), anchor="mm")
            P.rough_line(d, (330, 185), (330 + 420 * X.ease(t / 0.4), 185), X.CYAN, 5, 1, 1.0)
            for i, (num, name, sub, x) in enumerate(boxes):
                p = X.ease((t - 0.4 - i * 0.35) / 0.4)
                if p <= 0:
                    continue
                rough_box(d, (x, 330, x + 260, 640), X.CYAN if i < 2 else X.RED, 5, 10 + i, p)
                if p > 0.6:
                    a = int(255 * X.ease((p - 0.6) / 0.4))
                    d.text((x + 130, 400), num, font=kf(64), fill=X.AMBER + (a,), anchor="mm")
                    d.text((x + 130, 490), name, font=kf(78), fill=X.WHITE + (a,), anchor="mm")
                    d.text((x + 130, 585), sub, font=kf(28), fill=X.CYAN + (a,), anchor="mm")
                if i < 2:
                    arrow(d, (x + 268, 485), (x + 342, 485), X.CYAN, 5, X.ease((t - 0.7 - i * 0.35) / 0.3), 30 + i)
            yield im
    write("system_card.mp4", gen)


# ------------------------------------------------------------------ beat 9
def hidden_card():
    def gen():
        for k in range(int(1.3 * FPS)):
            t = k / FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            banner(d, "PART 1 · SEE")
            d.text((W // 2, 330), "WHAT IF A JOINT", font=X.hf(100), fill=X.WHITE + (255,), anchor="mm")
            d.text((W // 2, 450), "IS HIDDEN?", font=X.hf(100), fill=X.WHITE + (255,), anchor="mm")
            if t > 0.6:
                a = int(255 * X.ease((t - 0.6) / 0.25))
                d.text((W // 2, 620), "NO VERDICT. 4 OF 23 SETS.", font=X.hf(66), fill=X.RED + (a,), anchor="mm")
            yield Image.alpha_composite(im, X.glow(ov, 6))
    write("hidden_card.mp4", gen)


# ------------------------------------------------------------------ beat 12
def check_gate():
    """Line diagram of the rule: STOP only when both say STOP; disagreement -> CHECK FOOTAGE."""
    def row(d, y, judge, coach, result, colr, ex, p, seed):
        rough_box(d, (60, y, 330, y + 120), X.CYAN, 4, seed, p); rough_box(d, (390, y, 660, y + 120), X.CYAN, 4, seed + 5, p)
        if p > 0.7:
            d.text((195, y + 38), "JUDGE", font=kf(34), fill=X.CYAN + (255,), anchor="mm"); d.text((195, y + 82), judge, font=kf(42), fill=X.RED + (255,), anchor="mm")
            d.text((525, y + 38), "COACH", font=kf(34), fill=X.CYAN + (255,), anchor="mm"); d.text((525, y + 82), coach, font=kf(42), fill=(X.RED if coach == "STOP" else X.GREEN) + (255,), anchor="mm")
            d.text((360, y + 60), "+", font=kf(60), fill=X.WHITE + (255,), anchor="mm")
            arrow(d, (670, y + 60), (740, y + 60), X.WHITE, 4, 1.0, seed + 9)
            rough_box(d, (750, y + 5, 1050, y + 115), colr, 6, seed + 11, 1.0)
            d.text((900, y + 60), result, font=kf(40 if len(result) > 6 else 46), fill=colr + (255,), anchor="mm")
            d.text((60, y + 140), ex, font=kf(30), fill=X.GREY + (255,))
    def gen():
        for k in range(int(3.2 * FPS)):
            t = k / FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            banner(d, "PART 3 · CHECK · A SECOND PAIR OF EYES", X.RED)
            d.text((W // 2, 150), "A SECOND JUDGE: VIDEO ONLY", font=kf(52), fill=X.WHITE + (255,), anchor="mm")
            row(d, 230, "STOP", "STOP", "STOP", X.RED, "both say STOP (my reverse crunch)", X.ease((t - 0.3) / 0.6), 40)
            row(d, 470, "STOP", "OK", "CHECK FOOTAGE", X.AMBER, "they disagree (my lunge)", X.ease((t - 1.3) / 0.6), 60)
            if t > 2.3:
                a = int(255 * X.ease((t - 2.3) / 0.3))
                d.text((W // 2, 800), "STOP ONLY WHEN BOTH SAY STOP", font=X.hf(60), fill=X.WHITE + (a,), anchor="mm")
            yield Image.alpha_composite(im, ov)
    write("check_gate.mp4", gen)


# ------------------------------------------------------------------ beat 13
def chest_continue():
    """Chest fly (IMG_2780): raw graded footage + CONTINUE (judge.json)."""
    j = json.loads((P.DATA / "IMG_2780" / "judge.json").read_text())["verdict"]
    E.fresh("IMG_2780"); kp, video = P.keypoints(DL / "IMG_2780.MOV")
    fr = list(P.frames(video, int(4 * FPS), int(1.6 * FPS)))
    def gen():
        last = None
        for k, im in enumerate(fr):
            im, _ = X.prep(X.grade(im), kp[int(4 * FPS) + k]); d = ImageDraw.Draw(im)
            X.panel(d, (40, 30), ["CHEST · CABLE FLY"], size=48, sub="judge + coach")
            last = im; yield im
        for k in range(int(0.9 * FPS)):
            yield X.stamp(last, "CONTINUE", j["reason"], k / (0.2 * FPS))
    E.fresh("IMG_2780"); X.write(OUT / "chest_continue.mp4", gen())


# ------------------------------------------------------------------ beat 15
def news_jobs():
    """Top: the real People Matters headline (cropped). Bottom: the real posting, title ringed."""
    news = Image.open(HERE.parents[2] / "outputs" / "hiring-posttraining-reel" / "news_headline.png").convert("RGB")
    job = Image.open(HERE.parents[2] / "outputs" / "hiring-posttraining-reel" / "jd_card_top.png").convert("RGB")
    nw = 1000; news = news.resize((nw, int(news.height * nw / news.width)))
    job = job.resize((nw, int(job.height * nw / job.width))).crop((0, 0, nw, 300))
    sc = nw / 1691
    def gen():
        for k in range(int(3.6 * FPS)):
            t = k / FPS; im = blank(); im.paste(news, (40, 20)); y2 = 20 + news.height + 60
            ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            d.text((40, 20 + news.height + 10), "REPORTEDLY · NOT CONFIRMED BY SALESFORCE", font=X.hf(32, False), fill=X.AMBER + (255,))
            if t > 1.0:
                im.paste(job, (40, y2)); d.text((40, y2 + 305), "MEANWHILE, ON SALESFORCE CAREERS (BANGALORE · POSTED LAST WEEK)", font=X.hf(30, False), fill=X.CYAN + (255,))
                p = X.ease((t - 1.5) / 0.4)
                if p > 0:
                    x0, y0, x1, y1 = 40 + 60 * sc, y2 + 55 * sc, 40 + 1160 * sc, y2 + 135 * sc
                    d.rectangle([x0, y0, x0 + (x1 - x0) * p, y1], outline=X.RED + (255,), width=6)
            yield Image.alpha_composite(im, X.glow(ov, 4))
    write("news_jobs.mp4", gen)


def ending_screen():
    def gen():
        for k in range(int(2.6 * FPS)):
            t = k / FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            d.text((W // 2, 260), "HOW DO YOU", font=X.hf(120), fill=X.WHITE + (255,), anchor="mm")
            d.text((W // 2, 390), "GET READY?", font=X.hf(120), fill=X.CYAN + (255,), anchor="mm")
            if t > 0.7:
                a = int(255 * X.ease((t - 0.7) / 0.3))
                d.text((W // 2, 560), "FOLLOW TO FIND OUT", font=X.hf(64), fill=X.AMBER + (a,), anchor="mm")
            if t > 1.3:
                a = int(255 * X.ease((t - 1.3) / 0.3))
                d.text((W // 2, 680), "HIRING  ·  EVALS  ·  POST-TRAINING", font=X.hf(44, False), fill=X.CYAN + (a,), anchor="mm")
                pulse = 1 + 0.06 * np.sin(t * 10)
                bw, bh = 260 * pulse, 60 * pulse
                d.rectangle([540 - bw, 780 - bh, 540 + bw, 780 + bh], fill=(4, 40, 60, a), outline=X.CYAN + (a,), width=6)
                d.text((540, 780), "FOLLOW", font=X.hf(int(96 * pulse)), fill=X.WHITE + (a,), anchor="mm")
            yield Image.alpha_composite(im, X.glow(ov, 8))
    write("ending_screen.mp4", gen)


def part_banners():
    with_banner("lockon_red.mp4", "lockon_red.mp4", "PART 1 · SEE")
    with_banner("dual_wave.mp4", "dual_wave.mp4", "PART 1 · SEE")
    with_banner("cant_see.mp4", "cant_see.mp4", "PART 1 · SEE")
    with_banner("judge_hold.mp4", "judge_hold.mp4", "PART 2 · JUDGE", X.GREEN)


JOBS = {"research_final": lambda: research_warning(225, 119, 90), "research_provisional": lambda: research_warning(None, 0, 0), "build_montage": build_montage, "wait_countdown": wait_countdown, "sets_montage": sets_montage, "system_card": system_card,
        "hidden_card": hidden_card, "check_gate": check_gate, "chest_continue": chest_continue, "news_jobs": news_jobs,
        "ending_screen": ending_screen, "part_banners": part_banners}



# ------------------------------------------------------------------ v6.1 (creator notes, 20 Nov 19:40)
def gj_zoom():
    """Beat 2: Gym Jarvis as a line diagram (5 parts around the hub), then zoom into SET SCAN -> WORKOUT ANALYSER."""
    import math
    parts = ["MEAL SCAN", "SET SCAN", "BODY MAP", "DECISIONS", "PLAN"]
    cx, cy, R = W // 2, 470, 300
    pos = [(cx + R * math.cos(math.radians(-90 + i * 72)), cy + R * math.sin(math.radians(-90 + i * 72))) for i in range(5)]
    def frame(t):
        im = blank(); d = ImageDraw.Draw(im)
        d.text((W // 2, 60), "GYM JARVIS · 5 PARTS", font=kf(54), fill=X.WHITE + (255,), anchor="mm")
        rough_box(d, (cx - 130, cy - 55, cx + 130, cy + 55), X.CYAN, 5, 1, X.ease(t / 0.4))
        if t > 0.2:
            d.text((cx, cy), "GYM JARVIS", font=kf(44), fill=X.CYAN + (255,), anchor="mm")
        for i, (x, y) in enumerate(pos):
            p = X.ease((t - 0.3 - i * 0.12) / 0.3)
            if p <= 0:
                continue
            hot = i == 1 and t > 1.3
            col = X.RED if hot else X.CYAN
            ex, ey = cx + (x - cx) * 0.42, cy + (y - cy) * 0.42
            P.rough_line(d, (ex, ey), (cx + (x - cx) * (0.42 + 0.4 * p), cy + (y - cy) * (0.42 + 0.4 * p)), X.CYAN_D, 4, 20 + i, 1.0)
            rough_box(d, (x - 120, y - 45, x + 120, y + 45), col, 6 if hot else 4, 30 + i, p)
            if p > 0.6:
                d.text((x, y), parts[i], font=kf(36), fill=(X.WHITE if not hot else X.RED) + (255,), anchor="mm")
        if t > 1.3:
            a = int(255 * X.ease((t - 1.3) / 0.3)); x, y = pos[1]
            d.text((x, y + 75), "TODAY", font=X.hf(36), fill=X.RED + (a,), anchor="mm")
        return im
    def gen():
        n = int(3.4 * FPS)
        for k in range(n):
            t = k / FPS; im = frame(min(t, 1.9))
            if t > 1.9:  # zoom into SET SCAN, then it becomes WORKOUT ANALYSER
                z = 1 + 3.5 * X.ease((t - 1.9) / 0.9); x, y = pos[1]
                w2, h2 = W / z, PH / z; x0 = min(max(x - w2 / 2, 0), W - w2); y0 = min(max(y - h2 / 2, 0), PH - h2)
                im = im.crop((int(x0), int(y0), int(x0 + w2), int(y0 + h2))).resize((W, PH))
                if t > 2.7:
                    a = int(255 * X.ease((t - 2.7) / 0.3)); ov = Image.new("RGBA", im.size, (3, 12, 20, int(a * 0.85))); d = ImageDraw.Draw(ov)
                    d.text((W // 2, PH // 2), "WORKOUT ANALYSER", font=X.hf(120), fill=X.WHITE + (a,), anchor="mm")
                    im = Image.alpha_composite(im, ov)
            yield im
    write("gj_zoom.mp4", gen)


def research_short():
    """Beats 3-4, no counter: OVER 200 PAPERS + TOOLS, then the three findings, WARNING chip pins (3.6 s)."""
    lines = [("COUNTING REPS: EASY", X.GREEN), ("JUDGING THEM: HARD", X.RED), ("THE CAMERA ANGLE CAN FOOL THE AGENT", X.AMBER)]
    def gen():
        for k in range(int(3.6 * FPS)):
            t = k / FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            d.text((W // 2, 160), "OVER 200", font=X.hf(150), fill=X.WHITE + (int(255 * X.ease(t / 0.25)),), anchor="mm")
            d.text((W // 2, 270), "PAPERS + TOOLS", font=X.hf(64), fill=X.CYAN + (int(255 * X.ease(t / 0.25)),), anchor="mm")
            for i, (ln, col) in enumerate(lines):
                tt = 0.7 + i * 0.55
                if t > tt:
                    a = int(255 * X.ease((t - tt) / 0.25))
                    d.text((W // 2, 420 + i * 110), ln, font=X.hf(72 if i < 2 else 56), fill=col + (a,), anchor="mm")
            if t > 2.8:
                p = X.ease((t - 2.8) / 0.5); x0 = 140 + (40 - 140) * p; y0 = 760 + (12 - 760) * p; sc = 1 - 0.45 * p
                w, h = int(800 * sc), int(84 * sc)
                d.rectangle([x0, y0, x0 + w, y0 + h], fill=(40, 22, 0, 230), outline=X.AMBER + (255,), width=4)
                d.text((x0 + w // 2, y0 + h // 2), "WARNING: THE CAMERA ANGLE CAN FOOL IT", font=X.hf(int(44 * sc)), fill=X.AMBER + (255,), anchor="mm")
            yield Image.alpha_composite(im, X.glow(ov, 5))
    write("research_short.mp4", gen)


def hidden_diagram():
    """Beat 9: line diagram - a stick figure with its knee hidden -> no wave -> NO VERDICT (1.8 s)."""
    J = {"head": (260, 230), "sh": (260, 300), "hip": (260, 470), "knee": (330, 590), "ank": (300, 720), "hand": (360, 400)}
    def gen():
        for k in range(int(2.0 * FPS)):
            t = k / FPS; im = blank(); d = ImageDraw.Draw(im)
            banner(ImageDraw.Draw(im), "PART 1 · SEE")
            d.ellipse([230, 170, 290, 230], outline=X.CYAN + (255,), width=5)
            for a, b in (("sh", "hip"), ("sh", "hand"), ("hip", "knee"), ("knee", "ank")):
                hid = "knee" in (a, b)
                P.rough_line(d, J[a], J[b], (X.GREY if hid else X.CYAN), 5, hash(a + b) % 50, 1.0)
            x, y = J["knee"]; blink = (k // 5) % 2 == 0
            d.ellipse([x - 34, y - 34, x + 34, y + 34], outline=(X.RED if blink else X.GREY) + (255,), width=5)
            d.text((x, y), "?", font=kf(52), fill=X.RED + (255,), anchor="mm")
            d.text((x + 50, y - 20), "knee hidden", font=kf(34), fill=X.RED + (255,))
            p = X.ease((t - 0.5) / 0.4); arrow(d, (480, 470), (480 + 160 * p, 470), X.WHITE, 5, 1.0 if p >= 1 else p, 7)
            if t > 0.6:
                d.text((570, 420), "no wave", font=kf(36), fill=X.GREY + (255,), anchor="mm")
            if t > 0.9:
                a = int(255 * X.ease((t - 0.9) / 0.3))
                rough_box(d, (680, 380, 1040, 560), X.RED, 6, 9, 1.0)
                d.text((860, 445), "NO", font=X.hf(70), fill=X.RED + (a,), anchor="mm"); d.text((860, 515), "VERDICT", font=X.hf(70), fill=X.RED + (a,), anchor="mm")
            if t > 1.3:
                d.text((W // 2, 820), "4 OF 23 SETS", font=X.hf(56), fill=X.WHITE + (255,), anchor="mm")
            yield im.convert("RGBA")
    write("hidden_diagram.mp4", gen)


def false_alarm_label():
    """Big FALSE ALARM line over the lunge clip from the strike-through onward."""
    src = OUT / "_orig" / "false_alarm.mp4"
    if not src.exists():
        import shutil; shutil.copy(OUT / "false_alarm.mp4", src)
    frames = read_frames(src)
    def gen():
        for k, im in enumerate(frames):
            t = k / FPS
            if t > 3.0:
                ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); a = int(255 * X.ease((t - 3.0) / 0.2))
                d.rectangle([0, 600, W, 760], fill=(30, 0, 0, min(a, 220)))
                d.text((W // 2, 650), "FALSE ALARM", font=X.hf(90), fill=X.RED + (a,), anchor="mm")
                d.text((W // 2, 725), "I HAD ONLY TURNED TO THE CAMERA", font=X.hf(46), fill=X.WHITE + (a,), anchor="mm")
                im = Image.alpha_composite(im, ov)
            yield im
    write("false_alarm.mp4", gen)


def news_long():
    """Salesforce news on screen for the whole sentence (about 6.5 s), then the ending screen is its own beat."""
    global news_jobs
    import types
    src = news_jobs.__code__
    news = Image.open(HERE.parents[2] / "outputs" / "hiring-posttraining-reel" / "news_headline.png").convert("RGB")
    job = Image.open(HERE.parents[2] / "outputs" / "hiring-posttraining-reel" / "jd_card_top.png").convert("RGB")
    nw = 1000; news = news.resize((nw, int(news.height * nw / news.width)))
    job = job.resize((nw, int(job.height * nw / job.width))).crop((0, 0, nw, 300)); sc = nw / 1691
    def gen():
        for k in range(int(6.5 * FPS)):
            t = k / FPS; im = blank(); im.paste(news, (40, 20)); y2 = 20 + news.height + 60
            ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            d.text((40, 20 + news.height + 10), "REPORTEDLY · NOT CONFIRMED BY SALESFORCE", font=X.hf(36, False), fill=X.AMBER + (255,))
            if t > 2.6:
                im.paste(job, (40, y2)); d.text((40, y2 + 305), "MEANWHILE, ON SALESFORCE CAREERS (BANGALORE · POSTED LAST WEEK)", font=X.hf(32, False), fill=X.CYAN + (255,))
                p = X.ease((t - 3.1) / 0.4)
                if p > 0:
                    x0, y0, x1, y1 = 40 + 60 * sc, y2 + 55 * sc, 40 + 1160 * sc, y2 + 135 * sc
                    d.rectangle([x0, y0, x0 + (x1 - x0) * p, y1], outline=X.RED + (255,), width=6)
            yield Image.alpha_composite(im, X.glow(ov, 4))
    write("news_jobs.mp4", gen)


JOBS.update({"gj_zoom": gj_zoom, "research_short": research_short, "hidden_diagram": hidden_diagram,
             "false_alarm_label": false_alarm_label, "news_long": news_long})


# ------------------------------------------------------------------ v6.2 (creator notes, 20 Nov ~19:55)
def research_visual():
    """Beat 4 visualised: COUNTING REPS = EASY (a wave + ticking counter) | JUDGING = HARD (best vs this rep, '?'),
    then SAME REP, TWO CAMERA ANGLES, TWO ANSWERS (line diagram), WARNING chip pins."""
    import math
    def gen():
        for k in range(int(5.0 * FPS)):
            t = k / FPS; im = blank(); d = ImageDraw.Draw(im)
            if t < 3.0:
                d.text((W // 2, 50), "OVER 200 PAPERS + TOOLS", font=X.hf(56), fill=X.WHITE + (255,), anchor="mm")
            if t < 3.0:
                # left: counting (easy)
                rough_box(d, (40, 110, 520, 700), X.GREEN, 4, 3, 1.0)
                d.text((280, 160), "COUNTING REPS", font=kf(46), fill=X.WHITE + (255,), anchor="mm")
                pts = [(70 + i * 4, 380 - 90 * math.sin(i * 0.11)) for i in range(int(min(1, t / 1.6) * 105))]
                for a, b in zip(pts, pts[1:]):
                    d.line([a, b], fill=X.GREEN + (255,), width=5)
                reps = min(3, int(t / 1.6 * 105 * 0.11 / (2 * math.pi) + 0.25))
                d.text((280, 560), f"{reps}", font=X.hf(140), fill=X.GREEN + (255,), anchor="mm")
                d.text((280, 655), "EASY", font=X.hf(60), fill=X.GREEN + (255,), anchor="mm")
                # right: judging (hard)
                rough_box(d, (560, 110, 1040, 700), X.RED, 4, 4, 1.0)
                d.text((800, 160), "JUDGING THEM", font=kf(46), fill=X.WHITE + (255,), anchor="mm")
                for j, (col, amp) in enumerate(((X.GREEN, 95), (X.RED, 55))):
                    pts = [(590 + i * 4, 380 - amp * math.sin(i * 0.06)) for i in range(105)]
                    for a, b in zip(pts, pts[1:]):
                        d.line([a, b], fill=col + (255,), width=5)
                d.text((640, 250), "best rep", font=kf(30), fill=X.GREEN + (255,)); d.text((640, 300), "this rep", font=kf(30), fill=X.RED + (255,))
                if t > 0.8:
                    d.text((800, 540), "?", font=kf(140), fill=X.RED + (255,), anchor="mm")
                    d.text((800, 655), "HARD", font=X.hf(60), fill=X.RED + (255,), anchor="mm")
            else:
                # camera angle: the same rep from two cameras gives two answers
                tt = t - 3.0
                d.text((W // 2, 140), "SAME REP · TWO CAMERA ANGLES", font=kf(54), fill=X.AMBER + (255,), anchor="mm")
                cx, cy = W // 2, 470
                d.ellipse([cx - 22, cy - 160, cx + 22, cy - 116], outline=X.CYAN + (255,), width=5)
                P.rough_line(d, (cx, cy - 116), (cx, cy), X.CYAN, 5, 1, 1.0); P.rough_line(d, (cx, cy), (cx + 60, cy + 90), X.CYAN, 5, 2, 1.0)
                P.rough_line(d, (cx + 60, cy + 90), (cx + 30, cy + 190), X.CYAN, 5, 3, 1.0)
                for (x, lab, col) in ((150, "SIDE", X.GREEN), (930, "FRONT", X.RED)):
                    rough_box(d, (x - 70, cy - 40, x + 70, cy + 40), col, 4, 5, 1.0)
                    d.ellipse([x - 22, cy - 22, x + 22, cy + 22], outline=col + (255,), width=4)
                    d.text((x, cy + 75), lab, font=kf(36), fill=col + (255,), anchor="mm")
                    P.rough_line(d, (x + (70 if x < cx else -70), cy), (cx + (-40 if x < cx else 90), cy + 60), col, 3, 6, min(1, tt / 0.4))
                if tt > 0.5:
                    d.text((150, cy + 140), "deep rep", font=kf(36), fill=X.GREEN + (255,), anchor="mm")
                    d.text((930, cy + 140), "looks short", font=kf(36), fill=X.RED + (255,), anchor="mm")
                if tt > 1.0:
                    p = X.ease((tt - 1.0) / 0.5); x0 = 140 + (40 - 140) * p; y0 = 780 + (12 - 780) * p; sc = 1 - 0.45 * p
                    w, h = int(800 * sc), int(84 * sc)
                    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(40, 22, 0, 230), outline=X.AMBER + (255,), width=4)
                    d.text((x0 + w // 2, y0 + h // 2), "WARNING: THE CAMERA ANGLE CAN FOOL IT", font=X.hf(int(44 * sc)), fill=X.AMBER + (255,), anchor="mm")
            yield im.convert("RGBA")
    write("research_visual.mp4", gen)


def cant_see_big():
    """Leg extension with the refusal BIG and centred (creator note: bigger font, centre of frame)."""
    E.fresh("IMG_2655"); kp, video = P.keypoints(DL / "IMG_2655.MOV"); kp = P.smooth_kp(kp)
    msg = json.loads((P.DATA / "IMG_2655" / "judge.json").read_text())["verdict"]["detail"]
    l1, l2 = [x.strip() + "." for x in msg.split(".")[:2]]
    def gen():
        for k, img in enumerate(P.frames(video, 0, int(2.8 * FPS))):
            img, f = X.prep(X.grade(img), kp[k]); ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            X.skeleton(d, f, w=5); banner(d, "PART 1 · SEE")
            d.rectangle([40, 330, W - 40, 600], fill=(30, 0, 0, 215), outline=X.RED + (255,), width=5)
            d.text((W // 2, 410), l1, font=X.hf(84), fill=X.RED + (255,), anchor="mm")
            d.text((W // 2, 520), l2, font=X.hf(66), fill=X.WHITE + (255,), anchor="mm")
            yield Image.alpha_composite(img, X.glow(ov, 5))
    E.fresh("IMG_2655"); X.write(OUT / "cant_see.mp4", gen())


def full_vertical(src, name):
    """1080x1920 full-screen variant of a 1080x960 graphic clip (dark padding matches the HUD background)."""
    import subprocess
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(OUT / src), "-vf", "pad=1080:1920:0:480:color=0x03121c",
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(OUT / name)], check=True); print(OUT / name)


def full_hook():
    import shutil
    shutil.copy(P.DATA / "IMG_2661" / "hud" / "ghost_full.mp4", OUT / "FULL_hook_ghost.mp4"); print(OUT / "FULL_hook_ghost.mp4")


JOBS.update({"research_visual": research_visual, "cant_see_big": cant_see_big, "full_hook": full_hook,
             "full_countdown": lambda: full_vertical("countdown_blast.mp4", "FULL_countdown.mp4"),
             "full_wall": lambda: full_vertical("wall_of_sets.mp4", "FULL_wall_of_sets.mp4")})


def research_blocks():
    """Beat 4 as block diagrams (no skeleton): REPS -> COUNT -> EASY; REPS -> JUDGE -> HARD; CAMERA ANGLE -> FOOLS THE AGENT."""
    rows = [("REPS", "COUNT THEM", "EASY", X.GREEN, 0.3), ("REPS", "JUDGE THEM", "HARD", X.RED, 1.2),
            ("CAMERA ANGLE", "WRONG VIEW", "FOOLS THE AGENT", X.AMBER, 2.1)]
    def gen():
        for k in range(int(4.4 * FPS)):
            t = k / FPS; im = blank(); d = ImageDraw.Draw(im)
            d.text((W // 2, 70), "OVER 200 PAPERS + TOOLS SAID:", font=X.hf(58), fill=X.WHITE + (255,), anchor="mm")
            for i, (a, b, c, col, t0) in enumerate(rows):
                p = X.ease((t - t0) / 0.5)
                if p <= 0:
                    continue
                y = 170 + i * 220
                rough_box(d, (40, y, 300, y + 140), X.CYAN, 5, 10 + i, min(1, p * 1.5))
                d.text((170, y + 70), a, font=kf(44 if len(a) < 6 else 36), fill=X.WHITE + (255,), anchor="mm")
                arrow(d, (310, y + 70), (390, y + 70), X.WHITE, 5, min(1, max(0, p * 2 - 0.5)), 20 + i)
                if p > 0.4:
                    rough_box(d, (400, y, 680, y + 140), X.CYAN, 5, 30 + i, 1.0)
                    d.text((540, y + 70), b, font=kf(40), fill=X.WHITE + (255,), anchor="mm")
                    arrow(d, (690, y + 70), (760, y + 70), X.WHITE, 5, 1.0 if p > 0.7 else 0, 40 + i)
                if p > 0.7:
                    rough_box(d, (770, y, 1050, y + 140), col, 7, 50 + i, 1.0)
                    d.text((910, y + 70), c, font=X.hf(60 if len(c) < 6 else 40), fill=col + (255,), anchor="mm")
            yield im.convert("RGBA")
    write("research_blocks.mp4", gen)


def ending_follow():
    """Ending screen: HOW CAN YOU BE THAT ONE? FOLLOW ALONG TO KNOW (big pulsing FOLLOW)."""
    def gen():
        for k in range(int(2.8 * FPS)):
            t = k / FPS; im = blank(); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            d.text((W // 2, 230), "HOW CAN YOU", font=X.hf(120), fill=X.WHITE + (255,), anchor="mm")
            d.text((W // 2, 360), "BE THAT ONE?", font=X.hf(120), fill=X.CYAN + (255,), anchor="mm")
            if t > 0.7:
                a = int(255 * X.ease((t - 0.7) / 0.3))
                d.text((W // 2, 520), "FOLLOW ALONG TO KNOW", font=X.hf(70), fill=X.AMBER + (a,), anchor="mm")
            if t > 1.2:
                a = int(255 * X.ease((t - 1.2) / 0.3)); pulse = 1 + 0.06 * np.sin(t * 10); bw, bh = 260 * pulse, 60 * pulse
                d.rectangle([540 - bw, 700 - bh, 540 + bw, 700 + bh], fill=(4, 40, 60, a), outline=X.CYAN + (a,), width=6)
                d.text((540, 700), "FOLLOW", font=X.hf(int(96 * pulse)), fill=X.WHITE + (a,), anchor="mm")
            yield Image.alpha_composite(im, X.glow(ov, 8))
    write("ending_screen.mp4", gen)


JOBS.update({"research_blocks": research_blocks, "ending_follow": ending_follow})


if __name__ == "__main__":
    for n in (sys.argv[1:] or JOBS):
        JOBS[n]()
