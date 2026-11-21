"""Stamp a STEP n / 5 progress bar (bottom-left, above the caption-safe strip) onto rendered Ep 3 clips, and an
'IT GOT ONE WRONG' tag onto the wall of sets. Originals are kept in visuals/_orig/ so this is repeatable."""
import shutil, sys
from pathlib import Path
import cv2
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import hud_fx as X, pose_fx as P
V = HERE.parents[2] / "outputs" / "workout-analyser-reel" / "visuals"; O = V / "_orig"; O.mkdir(exist_ok=True)
STEPS = {"lockon_red.mp4": (1, "POSE"), "dual_wave.mp4": (2, "REP MATHS"), "arch_2.mp4": (3, "SAFETY CHECK"), "cant_see.mp4": (3, "SAFETY CHECK"),
         "arch_3.mp4": (4, "JUDGE"), "arch_4.mp4": (5, "COACH")}

def process(name, draw):
    src = O / name
    if not src.exists():
        shutil.copy(V / name, src)
    cap = cv2.VideoCapture(str(src)); P.H = 960; wr = P.Writer(V / name); k = 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        im = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        draw(ImageDraw.Draw(ov), k / 30); wr.add(Image.alpha_composite(im, ov)); k += 1
    cap.release(); wr.close(); print(name, k)

def step_bar(n, label):
    def f(d, t):
        x0, y0 = 40, 868
        d.rectangle([x0 - 8, y0 - 62, x0 + 5 * 74 + 250, y0 + 4], fill=(3, 12, 20, 215))
        d.text((x0, y0 - 56), f"STEP {n} / 5 · {label}", font=X.hf(34), fill=X.WHITE + (255,))
        for i in range(5):
            c = X.CYAN if i < n else X.CYAN_D
            d.rectangle([x0 + i * 74, y0 - 14, x0 + i * 74 + 64, y0 - 4], fill=c + (255,))
    return f

def wall_tag(d, t):
    if t > 2.9:
        a = int(255 * X.ease((t - 2.9) / 0.3))
        d.rectangle([40, 772, 620, 846], fill=(3, 12, 20, min(a, 230)), outline=X.AMBER + (a,), width=3)
        d.text((60, 786), "AND 1 IT GOT WRONG · WAIT FOR IT", font=X.hf(40), fill=X.AMBER + (a,))

for name, (n, label) in STEPS.items():
    process(name, step_bar(n, label))
process("wall_of_sets.mp4", wall_tag)
