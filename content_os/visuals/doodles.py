"""Reusable hand-drawn doodles (point lists -> rough strokes) and image loading."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import skia

from . import rough as R
from .elements import Doodle, Element, Picture

# ------------------------------------------------------------------ assets

def load_image(path: str | Path | None) -> skia.Image | None:
    if not path:
        return None
    p = Path(path).expanduser()
    if not p.exists():
        return None
    from PIL import Image, ImageOps

    im = ImageOps.exif_transpose(Image.open(p)).convert("RGBA")
    im.thumbnail((1600, 1600))
    return skia.Image.fromarray(np.ascontiguousarray(np.asarray(im)), colorType=skia.ColorType.kRGBA_8888_ColorType)


# ------------------------------------------------------------------ doodle library (point lists)

def check_strokes(x, y, s, col=R.GREEN, key="chk"):
    return [R.Stroke([(x, y), (x + s * 0.35, y + s * 0.4), (x + s, y - s * 0.55)], col, 10, key)]


def xmark_strokes(x, y, s, col=R.RED, key="xm"):
    return [R.Stroke([(x, y - s / 2), (x + s, y + s / 2)], col, 10, key + "a"),
            R.Stroke([(x + s, y - s / 2), (x, y + s / 2)], col, 10, key + "b")]


def plate_doodle(id, cx, cy, r, **kw) -> Doodle:
    """Placeholder plate (rice, dal, sabzi blobs) used until the creator's lunch photo exists."""
    def blob(x, y, rr, n=14, seed=0):
        rng = np.random.default_rng(seed)
        return [(x + rr * (1 + 0.12 * rng.uniform(-1, 1)) * math.cos(2 * math.pi * i / n),
                 y + rr * (1 + 0.12 * rng.uniform(-1, 1)) * math.sin(2 * math.pi * i / n)) for i in range(n)]
    rice = blob(cx - r * 0.3, cy - r * 0.15, r * 0.36, seed=1)
    dal = blob(cx + r * 0.32, cy - r * 0.25, r * 0.27, seed=2)
    sabzi = blob(cx + r * 0.1, cy + r * 0.38, r * 0.27, seed=3)
    return Doodle(id, strokes=[(R.ellipse_pts(cx, cy, r, r), R.INK, 6, True),
                               (R.ellipse_pts(cx, cy, r * 0.8, r * 0.8), R.GREY, 3, True),
                               (rice + rice[:1], R.GREY, 4, True), (dal + dal[:1], R.ORANGE, 4, True),
                               (sabzi + sabzi[:1], R.GREEN, 4, True)],
                  fills=[(dal, R.YELLOW, {"tint": 0.35, "gap": 9}), (sabzi, R.GREEN, {"tint": 0.2, "gap": 9})],
                  labels=[{"text": "your lunch photo", "x": cx, "y": cy + r + 40, "size": 26, "color": R.GREY,
                           "align": "center", "weight": "regular"}], **kw)


def lunch(id, rect, img, **kw) -> Element:
    x, y, w, h = rect
    if img is not None:
        return Picture(id, img, rect, **kw)
    return plate_doodle(id, x + w / 2, y + h / 2 - 20, min(w, h) / 2 - 30, **kw)


def paper_card(id, x, y, w, h, title, venue, **kw) -> Doodle:
    fold = 46
    outline = [(x, y), (x + w - fold, y), (x + w, y + fold), (x + w, y + h), (x, y + h), (x, y + 2)]
    return Doodle(id, strokes=[(outline, R.INK, 6, True),
                               ([(x + w - fold, y), (x + w - fold, y + fold), (x + w, y + fold)], R.INK, 4)],
                  labels=[{"text": title, "x": x + 34, "y": y + 84, "size": 64, "color": R.BLUE},
                          {"text": venue, "x": x + 36, "y": y + 132, "size": 34, "color": R.GREY, "weight": "regular"}],
                  **kw)


def scale_doodle(id, cx, cy, s=1.0, **kw) -> Doodle:
    """Kitchen scale with a plate on it."""
    w, h = 220 * s, 90 * s
    body = R.rect_pts(cx - w / 2, cy, w, h)
    dial = R.ellipse_pts(cx, cy + h * 0.55, 26 * s, 26 * s)
    needle = [(cx, cy + h * 0.55), (cx + 14 * s, cy + h * 0.55 - 16 * s)]
    platform = [(cx - w * 0.45, cy - 6 * s), (cx + w * 0.45, cy - 6 * s)]
    plate = [(cx - 90 * s, cy - 18 * s), (cx - 60 * s, cy - 40 * s), (cx + 60 * s, cy - 40 * s), (cx + 90 * s, cy - 18 * s)]
    return Doodle(id, strokes=[(body, R.INK, 6, True), (platform, R.INK, 6), (plate, R.BLUE, 6), (dial, R.INK, 4, True),
                               (needle, R.RED, 4)], **kw)


def magnifier(id, cx, cy, s=1.0, col=R.BLUE, **kw) -> Doodle:
    return Doodle(id, strokes=[(R.ellipse_pts(cx - 15 * s, cy - 15 * s, 55 * s, 55 * s), col, 8, True),
                               ([(cx + 25 * s, cy + 25 * s), (cx + 75 * s, cy + 75 * s)], col, 14)], **kw)


def ruler(id, cx, cy, s=1.0, col=R.ORANGE, **kw) -> Doodle:
    w, h = 190 * s, 56 * s
    x0, y0 = cx - w / 2, cy - h / 2
    ticks = [([(x0 + i * w / 8, y0), (x0 + i * w / 8, y0 + (h * 0.5 if i % 2 else h * 0.3))], col, 4) for i in range(1, 8)]
    return Doodle(id, strokes=[(R.rect_pts(x0, y0, w, h), col, 7, True), *ticks], **kw)


def book(id, cx, cy, s=1.0, col=R.GREEN, **kw) -> Doodle:
    w, h = 80 * s, 110 * s
    left = [(cx, cy - h / 2 + 10), (cx - w, cy - h / 2), (cx - w, cy + h / 2), (cx, cy + h / 2 + 10)]
    right = [(cx, cy - h / 2 + 10), (cx + w, cy - h / 2), (cx + w, cy + h / 2), (cx, cy + h / 2 + 10)]
    lines = [([(cx - w * 0.8, cy - h * 0.25 + i * 22 * s), (cx - w * 0.15, cy - h * 0.2 + i * 22 * s)], R.GREY, 3)
             for i in range(3)]
    return Doodle(id, strokes=[(left, col, 7), (right, col, 7), ([(cx, cy - h / 2 + 10), (cx, cy + h / 2 + 10)], col, 5),
                               *lines], **kw)


def bubble(id, x, y, w, h, lines, col=R.BLUE, tail="left", size=40, **kw) -> Doodle:
    r = 28
    pts = []
    for (ax, ay, a0) in ((x + w - r, y + r, -math.pi / 2), (x + w - r, y + h - r, 0), (x + r, y + h - r, math.pi / 2),
                         (x + r, y + r, math.pi)):
        pts += [(ax + r * math.cos(a0 + math.pi / 2 * i / 6), ay + r * math.sin(a0 + math.pi / 2 * i / 6)) for i in range(7)]
    pts.append(pts[0])
    if tail == "left":
        t = [(x + 50, y + h - 2), (x + 10, y + h + 40), (x + 90, y + h - 2)]
    else:
        t = [(x + w - 90, y + h - 2), (x + w - 10, y + h + 40), (x + w - 50, y + h - 2)]
    lh = size * 1.1
    y0 = y + h / 2 - len(lines) * lh / 2 + size * 0.8
    labels = [{"text": ln, "x": x + w / 2, "y": y0 + i * lh, "size": size, "color": R.INK, "align": "center"}
              for i, ln in enumerate(lines)]
    return Doodle(id, strokes=[(pts, col, 6, True), (t, col, 6)], fills=[(pts, col, {"tint": 0.08, "gap": 22, "width": 2})],
                  labels=labels, **kw)


def dashed_rect(x, y, w, h, col=R.GREY, key="dash", dash=26, gap=16):
    out = []
    edges = [((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)), ((x + w, y + h), (x, y + h)), ((x, y + h), (x, y))]
    k = 0
    for (a, b) in edges:
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        n = int(ln // (dash + gap))
        for i in range(n + 1):
            s0, s1 = i * (dash + gap) / ln, min(1, (i * (dash + gap) + dash) / ln)
            if s0 >= 1:
                break
            out.append(R.Stroke([(a[0] + (b[0] - a[0]) * s0, a[1] + (b[1] - a[1]) * s0),
                                 (a[0] + (b[0] - a[0]) * s1, a[1] + (b[1] - a[1]) * s1)], col, 4, f"{key}{k}",
                                double=False))
            k += 1
    return out


def crystal_ball(id, cx, cy, s=1.0, **kw):
    return Doodle(id, strokes=[(R.ellipse_pts(cx, cy, 38 * s, 38 * s), R.PURPLE, 6, True),
                               ([(cx - 34 * s, cy + 44 * s), (cx + 34 * s, cy + 44 * s)], R.PURPLE, 7),
                               (R.ellipse_pts(cx - 12 * s, cy - 12 * s, 9 * s, 6 * s, n=20), R.PURPLE, 3, True)],
                  fills=[(R.ellipse_pts(cx, cy, 36 * s, 36 * s, n=30)[:-1], R.PURPLE, {"tint": 0.15, "gap": 10})], **kw)




def meal_series(path: Path | None) -> list[tuple[float, bool]]:
    """(kcal, asked the user) per simulated meal, in time order, from the simulated usage log (outside
    the repo; every record is ``simulated: true``). A fixed illustrative fallback otherwise."""
    if path and Path(path).expanduser().exists():
        rows = []
        for line in Path(path).expanduser().read_text().splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("kind") == "estimate" and r.get("simulated"):
                rows.append((r["ts"], float(r["totals"]["kcal"]), bool(r.get("alerts"))))
        if len(rows) >= 8:
            return [(k, a) for _, k, a in sorted(rows)]
    return [(410, False), (520, True), (300, False), (640, False), (480, True), (560, False), (390, False), (610, True),
            (450, False), (530, False), (700, True), (420, False)]
