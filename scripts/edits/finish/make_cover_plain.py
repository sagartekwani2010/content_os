"""Plain cover: title, one hook, the creator's face. 1080x1920; key content inside the 3:4 profile-grid
crop (y 240-1680). Usage: python make_cover_plain.py <face_frame.png> <out.png>"""
import math, random, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1920
PAPER = (250, 247, 240)
INK = (25, 25, 25)
RED = (226, 40, 40)
BLUE = (20, 90, 230)
ORANGE = (255, 140, 0)
FONTS = Path.home() / ".cache/content_os/fonts"
kalam = lambda s: ImageFont.truetype(str(FONTS / "Kalam-Bold.ttf"), s)
digits = lambda s: ImageFont.truetype(str(FONTS / "PatrickHand-Regular.ttf"), s)


def rough_line(d, p0, p1, color, width, seed=3):
    rnd = random.Random(seed)
    for k in range(2):
        pts = [(p0[0] + (p1[0] - p0[0]) * i / 20 + rnd.uniform(-2.5, 2.5),
                p0[1] + (p1[1] - p0[1]) * i / 20 + rnd.uniform(-2.5, 2.5)) for i in range(21)]
        d.line(pts, fill=color, width=width - 2 * k, joint="curve")


def rough_ellipse(d, box, color, width, seed=5):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    pts = []
    for i in range(130):
        t = 2 * math.pi * 1.06 * i / 129 - 0.5
        w = 1 + 0.02 * math.sin(3 * t + rnd.random())
        pts.append((cx + rx * w * math.cos(t), cy + ry * w * math.sin(t)))
    d.line(pts, fill=color, width=width, joint="curve")


def centered(d, y, text, font, fill):
    w = d.textlength(text, font=font)
    d.text(((W - w) / 2, y), text, font=font, fill=fill)
    return w


def main(face_path, out_path):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    centered(d, 250, "Gym Jarvis · Ep 2", kalam(56), BLUE)
    centered(d, 330, "MEAL", kalam(190), INK)
    w = centered(d, 520, "ANALYSER", kalam(190), BLUE)
    rough_line(d, ((W - w) / 2, 735), ((W + w) / 2, 731), ORANGE, 14, seed=4)
    # hook: 499 kcal -> 94
    d.text((110, 770), "499 kcal", font=digits(150), fill=INK)
    rough_line(d, (590, 875), (720, 875), INK, 11, seed=6)
    rough_line(d, (690, 848), (724, 875), INK, 11, seed=7)
    rough_line(d, (690, 902), (724, 875), INK, 11, seed=8)
    d.text((770, 745), "94", font=digits(200), fill=RED)
    rough_ellipse(d, (745, 775, 1000, 985), RED, 10)
    # face: large, bottom, full width
    face = ImageOps.fit(Image.open(face_path).convert("RGB"), (W, 880), Image.LANCZOS, centering=(0.5, 0.35))
    im.paste(face, (0, 1040))
    rough_line(d, (0, 1040), (W, 1040), INK, 10, seed=9)
    im.save(out_path)
    print(out_path)


if __name__ == "__main__":
    main(*sys.argv[1:3])
