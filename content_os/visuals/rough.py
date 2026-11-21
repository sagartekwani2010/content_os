"""Rough, marker-style drawing on a skia canvas.

Geometry is wobbled once per element with a seeded RNG (seed = crc32 of the element id), so
every frame and every run draws the same strokes: deterministic and flicker-free. Strokes can be
drawn partially (``frac``) for draw-on animation.
"""

from __future__ import annotations

import math
import os
import zlib
from functools import lru_cache
from pathlib import Path

import numpy as np
import skia

FONT_DIR = Path(os.environ.get("CONTENT_OS_CACHE", Path.home() / ".cache" / "content_os")) / "fonts"
FONTS = {
    "bold": ("Kalam-Bold.ttf", "https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Bold.ttf",
             "2f6576601db015d4f6c08678120277fc8510b98c06e932ce7a6a9cbff4cbdded"),
    "regular": ("Kalam-Regular.ttf", "https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Regular.ttf",
                "57cecb63d4608019371954274ae1d8c397764debd5b19d4a33c1efa4dc923c0b"),
    # digits: Kalam's 5 reads as S and its 4 as a script 4 at phone size; Patrick Hand's are unambiguous
    "digits": ("PatrickHand-Regular.ttf", "https://github.com/google/fonts/raw/main/ofl/patrickhand/PatrickHand-Regular.ttf",
               "0f173b3e6cb6d1af25babf7f0057c5ac4ee11f9992b0469bb817e967ef4ad0fc"),
}
SYMBOL_FONTS = ["/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/Library/Fonts/Arial Unicode.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
FONT_LICENSES = {"OFL-Kalam.txt": "https://github.com/google/fonts/raw/main/ofl/kalam/OFL.txt",
                 "OFL-PatrickHand.txt": "https://github.com/google/fonts/raw/main/ofl/patrickhand/OFL.txt"}

# marker palette on off-white paper: tune in palette.py
from .palette import (BLUE, GREEN, GREY, HATCH_LINE_ALPHA, HATCH_TINT_MAX, HATCH_TINT_SCALE, INK, LIGHT,  # noqa: E402
                      ORANGE, PAPER, PURPLE, RED, STROKE_SCALE, YELLOW)


_THEME: dict[str, str] = {}


def set_theme(theme: str | dict | None) -> None:
    """Spec-level colour theme: "paper" (default, the approved whiteboard look), "dark", "cold", or a
    {"#OLD": "#NEW"} map. Every colour passes through ``color()``, so remapping here re-themes every template."""
    from .palette import THEMES
    m = THEMES[theme or "paper"] if isinstance(theme, str) or theme is None else theme
    _THEME.clear()
    _THEME.update({k.lstrip("#").upper(): v.lstrip("#").upper() for k, v in m.items()})


def color(c: str, alpha: float = 1.0) -> int:
    c = c.lstrip("#").upper()
    c = _THEME.get(c, c)
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return skia.Color(r, g, b, int(round(255 * max(0.0, min(1.0, alpha)))))


def seed_of(key: str) -> int:
    return zlib.crc32(key.encode()) & 0xFFFFFFFF


# ------------------------------------------------------------------ fonts

def font_path(weight: str = "bold") -> Path:
    name = FONTS[weight][0]
    p = FONT_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"{p} missing: run `python -m content_os.visuals setup` (downloads Kalam, SIL OFL 1.1)")
    return p


@lru_cache(maxsize=None)
def typeface(weight: str = "bold") -> skia.Typeface:
    if weight.startswith("sym"):  # a symbol neither hand font has (→): a fixed system font with wide coverage
        for f in SYMBOL_FONTS:
            if Path(f).exists():
                tf = skia.Typeface.MakeFromFile(f)
                if tf is not None:
                    return tf
        return typeface("bold")
    tf = skia.Typeface.MakeFromFile(str(font_path(weight)))
    if tf is None:
        raise RuntimeError(f"could not load {font_path(weight)}")
    return tf


@lru_cache(maxsize=None)
def font(size: float, weight: str = "bold") -> skia.Font:
    f = skia.Font(typeface(weight), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    if weight == "digits":
        f.setEmbolden(True)
    return f


def pick(s: str, weight: str) -> str:
    """Any text containing a digit is set in the digits font (bold faces only). ``letters`` (mixed runs: Kalam
    letters, Patrick Hand digits) is handled by ``runs``."""
    return "digits" if weight == "bold" and any(ch.isdigit() for ch in s) else weight


def runs(s: str, weight: str) -> list[tuple[str, str]]:
    """(text, font weight) runs: ``letters`` sets letters in bold Kalam and digit runs in the digits font, so a
    title line that names Nutrition5k keeps its Kalam face while its 5 still reads as a 5. Characters the chosen
    face lacks (₹ in Patrick Hand, → anywhere) fall back to Kalam, then to a system font."""
    if weight != "letters":
        base = [(s, pick(s, weight))]
    else:
        import re as _re
        base = [(m.group(0), "digits" if m.group(0)[0].isdigit() else "bold") for m in _re.finditer(r"\d+|\D+", s)]
    return _fallback_runs(base)


@lru_cache(maxsize=4096)
def _has_glyph(weight: str, ch: str) -> bool:
    return ch.isspace() or typeface(weight).unicharToGlyph(ord(ch)) != 0


def _fallback_runs(base: list[tuple[str, str]]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for text, w in base:
        for ch in text:
            wt = w
            if not _has_glyph(w, ch):
                wt = "bold" if _has_glyph("bold", ch) else "sym"
            if out and out[-1][1] == wt:
                out[-1] = (out[-1][0] + ch, wt)
            else:
                out.append((ch, wt))
    return out


def text_width(s: str, size: float, weight: str = "bold") -> float:
    return sum(font(size, w).measureText(t) for t, w in runs(s, weight))


def draw_text(canvas: skia.Canvas, s: str, x: float, y: float, size: float, col: str = INK, *,
              weight: str = "bold", align: str = "left", reveal: float = 1.0, alpha: float = 1.0,
              halo: str | None = None) -> tuple[float, float]:
    """Draw ``s`` with its baseline at y. ``reveal`` < 1 clips left-to-right (write-on). Returns (x0, width)."""
    if reveal <= 0 or alpha <= 0:
        return x, 0.0
    parts = runs(s, weight)
    w = text_width(s, size, weight)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    paint = skia.Paint(AntiAlias=True, Color=color(col, alpha))
    canvas.save()
    if reveal < 1:
        canvas.clipRect(skia.Rect.MakeXYWH(x0 - 4, y - size * 1.4, (w + 8) * reveal, size * 2.0))
    xx = x0
    for t, wt in parts:
        f = font(size, wt)
        if halo:  # light outline so text stays legible on a photo
            canvas.drawString(t, xx, y, f, stroke_paint(halo, max(6.0, size * 0.18), alpha * 0.9))
        canvas.drawString(t, xx, y, f, paint)
        xx += f.measureText(t)
    canvas.restore()
    return x0, w


# ------------------------------------------------------------------ geometry

def resample(pts: list[tuple[float, float]], step: float = 6.0) -> np.ndarray:
    p = np.asarray(pts, dtype=float)
    if len(p) < 2:
        return p
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    total = cum[-1]
    if total == 0:
        return p[:1]
    n = max(2, int(total / step) + 1)
    s = np.linspace(0, total, n)
    return np.stack([np.interp(s, cum, p[:, 0]), np.interp(s, cum, p[:, 1])], axis=1)


def wobble(pts: list[tuple[float, float]], seed: int, amp: float = 2.2, overshoot: float = 0.0) -> np.ndarray:
    """Resample and displace perpendicular to the stroke with smooth low-frequency noise."""
    p = resample(pts)
    if len(p) < 2:
        return p
    rng = np.random.default_rng(seed)
    if overshoot:
        d0 = p[1] - p[0]
        d1 = p[-1] - p[-2]
        n0, n1 = np.linalg.norm(d0) or 1, np.linalg.norm(d1) or 1
        p = np.vstack([p[0] - d0 / n0 * overshoot * rng.uniform(0.2, 1), p, p[-1] + d1 / n1 * overshoot * rng.uniform(0.2, 1)])
    t = np.linspace(0, 1, len(p))
    length = float(np.sum(np.linalg.norm(np.diff(p, axis=0), axis=1)))
    cycles = max(1.0, length / 260.0)
    off = np.zeros(len(p))
    for k, a in ((1, 1.0), (2.3, 0.5), (4.1, 0.25)):
        off += a * np.sin(2 * math.pi * (k * cycles * t + rng.uniform(0, 1)))
    off *= amp / 1.75
    tang = np.gradient(p, axis=0)
    norm = np.linalg.norm(tang, axis=1, keepdims=True)
    norm[norm == 0] = 1
    nrm = np.stack([-tang[:, 1], tang[:, 0]], axis=1) / norm
    return p + nrm * off[:, None]


def polyline_length(p: np.ndarray) -> float:
    return float(np.sum(np.linalg.norm(np.diff(p, axis=0), axis=1))) if len(p) > 1 else 0.0


def partial(p: np.ndarray, frac: float) -> np.ndarray:
    if frac >= 1 or len(p) < 2:
        return p
    if frac <= 0:
        return p[:0]
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    target = cum[-1] * frac
    k = int(np.searchsorted(cum, target))
    k = max(1, min(k, len(p) - 1))
    a = (target - cum[k - 1]) / (seg[k - 1] or 1)
    end = p[k - 1] + (p[k] - p[k - 1]) * a
    return np.vstack([p[:k], end])


def path_of(p: np.ndarray, closed: bool = False) -> skia.Path:
    path = skia.Path()
    if len(p) == 0:
        return path
    path.moveTo(*p[0])
    for x, y in p[1:]:
        path.lineTo(x, y)
    if closed:
        path.close()
    return path


def stroke_paint(col: str, width: float, alpha: float = 1.0) -> skia.Paint:
    return skia.Paint(AntiAlias=True, Color=color(col, alpha), Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                      StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)


def fill_paint(col: str, alpha: float = 1.0) -> skia.Paint:
    return skia.Paint(AntiAlias=True, Color=color(col, alpha), Style=skia.Paint.kFill_Style)


# ------------------------------------------------------------------ shapes as point lists

def rect_pts(x: float, y: float, w: float, h: float) -> list[tuple[float, float]]:
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y + 2)]


def ellipse_pts(cx: float, cy: float, rx: float, ry: float, start: float = -2.0, sweep: float = 6.6, n: int = 80):
    return [(cx + rx * math.cos(start + sweep * i / n), cy + ry * math.sin(start + sweep * i / n)) for i in range(n + 1)]


def arrow_head(p: np.ndarray, size: float = 22) -> list[list[tuple[float, float]]]:
    if len(p) < 2:
        return []
    tip = p[-1]
    back = p[max(0, len(p) - 4)]
    d = tip - back
    n = np.linalg.norm(d) or 1
    d = d / n
    left = tip - size * (d * math.cos(0.45) + np.array([-d[1], d[0]]) * math.sin(0.45))
    right = tip - size * (d * math.cos(0.45) - np.array([-d[1], d[0]]) * math.sin(0.45))
    return [[tuple(left), tuple(tip)], [tuple(right), tuple(tip)]]


class Stroke:
    """One wobbly stroke, pre-computed (two passes like a marker going over twice)."""

    def __init__(self, pts, col: str = INK, width: float = 6.0, key: str = "", amp: float = 2.2,
                 double: bool = True, closed: bool = False, alpha: float = 1.0):
        s = seed_of(key)
        width = width * STROKE_SCALE
        self.col, self.width, self.alpha = col, width, alpha
        ov = width * 0.8 if not closed else 0.0
        self.passes = [wobble(pts, s, amp, ov)]
        if double:
            self.passes.append(wobble(pts, s + 1, amp * 0.8, ov * 0.5))
        self.length = polyline_length(self.passes[0])

    def draw(self, canvas: skia.Canvas, frac: float = 1.0, alpha: float = 1.0) -> None:
        if frac <= 0:
            return
        for i, p in enumerate(self.passes):
            q = partial(p, frac)
            if len(q) < 2:
                continue
            w = self.width if i == 0 else self.width * 0.45
            a = self.alpha * alpha * (1.0 if i == 0 else 0.55)
            canvas.drawPath(path_of(q), stroke_paint(self.col, w, a))


class Hachure:
    """rough.js-style diagonal hatch fill clipped to a polygon."""

    def __init__(self, poly, col: str, key: str, gap: float = 13.0, angle: float = -0.72, width: float = 3.0,
                 tint: float = 0.18):
        self.poly = np.asarray(poly, float)
        self.col, self.width, self.tint = col, width, min(HATCH_TINT_MAX, tint * HATCH_TINT_SCALE)
        xs, ys = self.poly[:, 0], self.poly[:, 1]
        cx, cy = xs.mean(), ys.mean()
        r = math.hypot(xs.max() - xs.min(), ys.max() - ys.min())
        d = np.array([math.cos(angle), math.sin(angle)])
        nrm = np.array([-d[1], d[0]])
        self.lines = []
        k = 0
        for off in np.arange(-r / 2, r / 2, gap):
            c = np.array([cx, cy]) + nrm * off
            self.lines.append(Stroke([tuple(c - d * r / 2), tuple(c + d * r / 2)], col, width, f"{key}:h{k}",
                                     amp=1.2, double=False))
            k += 1

    def draw(self, canvas: skia.Canvas, frac: float = 1.0, alpha: float = 1.0) -> None:
        if frac <= 0:
            return
        clip = path_of(self.poly, closed=True)
        canvas.save()
        canvas.clipPath(clip, doAntiAlias=True)
        canvas.drawPath(clip, fill_paint(self.col, self.tint * alpha * min(1.0, frac * 2)))
        n = len(self.lines)
        shown = frac * n
        for i, s in enumerate(self.lines):
            if i < shown:
                s.draw(canvas, min(1.0, shown - i), alpha * HATCH_LINE_ALPHA)
        canvas.restore()


def draw_strokes(canvas: skia.Canvas, strokes: list, frac: float, alpha: float = 1.0) -> None:
    """Draw a list of strokes on in order; ``frac`` of their total length is shown."""
    if frac <= 0:
        return
    lengths = [max(1.0, getattr(s, "length", 400.0)) for s in strokes]
    total = sum(lengths)
    budget = total * frac
    for s, ln in zip(strokes, lengths):
        if budget <= 0:
            break
        s.draw(canvas, min(1.0, budget / ln), alpha)
        budget -= ln


def paper_background(w: int, h: int, seed: int = 3) -> skia.Image:
    """Off-white paper with a faint dot grid (pre-rendered once)."""
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    c.clear(color(PAPER))
    rng = np.random.default_rng(seed)
    p = fill_paint("#E4DED1", 0.9)
    for y in range(30, h, 40):
        for x in range(30, w, 40):
            c.drawCircle(x + rng.uniform(-0.6, 0.6), y + rng.uniform(-0.6, 0.6), 1.6, p)
    return surf.makeImageSnapshot()
