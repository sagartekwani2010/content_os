"""Scene elements and the per-frame animation state.

An element becomes visible through its first *appearance* cue (draw, write, pop, fade, countup);
``highlight``, ``cross`` and ``shake`` decorate it afterwards. Elements no cue targets are either
shown from the first frame (``intro=None``) or drawn on at ``intro`` seconds.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import skia

from . import rough as R
from .palette import DIM_ALPHA, NAMED

APPEAR = ("draw", "write", "pop", "fade", "countup")


def clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return max(a, min(b, x))


def ease_out(p: float) -> float:
    return 1 - (1 - clamp(p)) ** 3


def back_out(p: float, s: float = 1.7) -> float:
    p = clamp(p) - 1
    return p * p * ((s + 1) * p + s) + 1


@dataclass
class Cue:
    action: str
    t: float
    dur: float
    emphasis: bool = False
    params: dict = field(default_factory=dict)

    def progress(self, t: float) -> float:
        return clamp((t - self.t) / self.dur) if t >= self.t else -1.0


class Element:
    appear = "draw"
    burst = False  # emphasis "pow" lines: off (creator: no decorative effects); kept as an opt-in

    def __init__(self, id: str, *, intro: float | None = None, dim: bool = False, z: int = 0):
        self.id, self.intro, self.dim, self.z = id, intro, dim, z
        self.cues: list[Cue] = []

    # geometry
    def bounds(self) -> tuple[float, float, float, float]:
        raise NotImplementedError

    def center(self) -> tuple[float, float]:
        x, y, w, h = self.bounds()
        return x + w / 2, y + h / 2

    def paint(self, c: skia.Canvas, p: float, alpha: float, t: float) -> None:
        raise NotImplementedError

    # animation
    def appear_cue(self) -> Cue | None:
        cs = [c for c in self.cues if c.action in APPEAR]
        return min(cs, key=lambda c: c.t) if cs else None

    def render(self, c: skia.Canvas, t: float) -> None:
        ac = self.appear_cue()
        if ac is None:
            if self.intro is None:
                p, kind, emph = 1.0, "draw", False
            else:
                p, kind, emph = ease_out((t - self.intro) / 0.5) if t >= self.intro else -1, "draw", False
        else:
            p, kind, emph = ac.progress(t), ac.action, ac.emphasis
        if p < 0:
            return
        alpha = DIM_ALPHA if self.dim else 1.0
        cx, cy = self.center()
        c.save()
        # shake: decaying wiggle
        for sc in self.cues:
            if sc.action == "shake":
                q = sc.progress(t)
                if 0 <= q < 1:
                    amp = (5.0 if sc.emphasis else 3.0) * (1 - q)
                    c.rotate(amp * math.sin(q * 6 * math.pi), cx, cy)
        # highlighter band behind the element
        for hc in self.cues:
            if hc.action == "highlight" and hc.params.get("style", "circle") == "marker":
                q = hc.progress(t)
                if q >= 0:
                    self._marker(c, ease_out(q))
        if kind == "pop":
            s = back_out(p, 1.6 if emph else 1.0)  # gentle settle, no bounce
            c.translate(cx, cy)
            c.scale(max(0.01, s), max(0.01, s))
            c.translate(-cx, -cy)
            self.paint(c, 1.0, alpha * clamp(p * 3), t)
        elif kind == "fade":
            self.paint(c, 1.0, alpha * ease_out(p), t)
        elif kind == "countup":
            self.paint(c, ease_out(p), alpha, t)
        else:  # draw / write
            self.paint(c, ease_out(p) if kind == "draw" else clamp(p), alpha, t)
        c.restore()
        for dc in self.cues:
            q = dc.progress(t)
            if q < 0:
                continue
            if dc.action == "highlight" and dc.params.get("style", "circle") != "marker":
                self._circle(c, ease_out(q), dc)
            elif dc.action == "cross":
                self._cross(c, ease_out(q))
            if dc.emphasis and self.burst:
                self._burst(c, q, dc)

    # decorations
    def _deco(self, name: str, make):
        cache = self.__dict__.setdefault("_deco_cache", {})
        if name not in cache:
            cache[name] = make()
        return cache[name]

    def _circle(self, c, q, cue: Cue) -> None:
        x, y, w, h = self.bounds()
        col = NAMED.get(cue.params.get("color", "red"), cue.params.get("color", R.RED))
        if cue.params.get("style") == "underline":
            st = self._deco("ul", lambda: [R.Stroke([(x - 6, y + h + 10), (x + w + 6, y + h + 4)], col, 7, f"{self.id}:ul")])
        else:
            pad = cue.params.get("pad", 18)
            st = self._deco("circ", lambda: [R.Stroke(R.ellipse_pts(x + w / 2, y + h / 2, w / 2 + pad, h / 2 + pad,
                                                                     start=-2.4, sweep=6.9), col, 6, f"{self.id}:circ")])
        R.draw_strokes(c, st, q)

    def _marker(self, c, q) -> None:
        x, y, w, h = self.bounds()
        st = self._deco("mk", lambda: [R.Stroke([(x - 8, y + h * 0.55), (x + w + 8, y + h * 0.5)], R.YELLOW, h * 0.75,
                                                f"{self.id}:mk", amp=3, double=False, alpha=0.75)])
        R.draw_strokes(c, st, q)

    def _cross(self, c, q) -> None:
        x, y, w, h = self.bounds()
        st = self._deco("x", lambda: [R.Stroke([(x - 10, y - 6), (x + w + 10, y + h + 6)], R.RED, 9, f"{self.id}:x1"),
                                      R.Stroke([(x + w + 10, y - 6), (x - 10, y + h + 6)], R.RED, 9, f"{self.id}:x2")])
        R.draw_strokes(c, st, q)

    def _burst(self, c, q, cue: Cue) -> None:
        """Short radial 'pow' lines for emphasis words: shoot out, then fade."""
        if q >= 1.0 or q < 0.1:
            return
        x, y, w, h = self.bounds()
        cx, cy = x + w / 2, y + h / 2
        rx, ry = w / 2 + 26, h / 2 + 26
        col = cue.params.get("burst_color", R.ORANGE)
        a = 1.0 if q < 0.7 else max(0.0, (1 - q) / 0.3)
        n = 7
        for i in range(n):
            ang = -math.pi / 2 + 2 * math.pi * i / n + 0.2
            ux, uy = math.cos(ang), math.sin(ang)
            r0 = 1.0 + 0.08 * ease_out(q)
            ln = 26 * ease_out(min(1, q * 1.4))
            p0 = (cx + ux * rx * r0, cy + uy * ry * r0)
            p1 = (p0[0] + ux * ln, p0[1] + uy * ln)
            c.drawLine(*p0, *p1, R.stroke_paint(col, 6, a))


class Doodle(Element):
    """Rough strokes + hachure fills + labels, drawn on in that order."""

    def __init__(self, id: str, strokes=(), fills=(), labels=(), **kw):
        super().__init__(id, **kw)
        self.strokes = [s if isinstance(s, R.Stroke) else R.Stroke(s[0], s[1] if len(s) > 1 else R.INK,
                                                                     s[2] if len(s) > 2 else 6, f"{id}:{i}",
                                                                     closed=s[3] if len(s) > 3 else False)
                        for i, s in enumerate(strokes)]
        self.fills = [R.Hachure(f[0], f[1], f"{id}:f{i}", **(f[2] if len(f) > 2 else {})) for i, f in enumerate(fills)]
        self.labels = list(labels)  # dicts: text, x, y, size, color, align, weight

    def bounds(self):
        pts = [p for s in self.strokes for p in s.passes[0]] + [p for f in self.fills for p in f.poly]
        if not pts and self.labels:
            lb = self.labels[0]
            w = R.text_width(lb["text"], lb.get("size", 40))
            x = lb["x"] - (w / 2 if lb.get("align") == "center" else 0)
            return x, lb["y"] - lb.get("size", 40) * 0.8, w, lb.get("size", 40)
        a = np.asarray(pts)
        x0, y0 = a.min(axis=0)
        x1, y1 = a.max(axis=0)
        return float(x0), float(y0), float(x1 - x0), float(y1 - y0)

    def paint(self, c, p, alpha, t):
        has_lab = bool(self.labels)
        ps = clamp(p / 0.7) if has_lab else p
        for f in self.fills:
            f.draw(c, clamp((ps - 0.3) / 0.7), alpha)
        R.draw_strokes(c, self.strokes, ps, alpha)
        if has_lab:
            pl = clamp((p - 0.45) / 0.55) if self.strokes or self.fills else p
            for lb in self.labels:
                R.draw_text(c, lb["text"], lb["x"], lb["y"], lb.get("size", 40), lb.get("color", R.INK),
                            weight=lb.get("weight", "bold"), align=lb.get("align", "left"), reveal=pl, alpha=alpha,
                            halo=lb.get("halo"))


class Label(Element):
    appear = "write"

    def __init__(self, id, text, x, y, size=44, col=R.INK, align="left", weight="bold", **kw):
        super().__init__(id, **kw)
        self.text, self.x, self.y, self.size, self.col, self.align, self.weight = text, x, y, size, col, align, weight

    def bounds(self):
        w = R.text_width(self.text, self.size, self.weight)
        x = self.x - (w / 2 if self.align == "center" else (w if self.align == "right" else 0))
        return x, self.y - self.size * 0.78, w, self.size * 0.95

    def paint(self, c, p, alpha, t):
        R.draw_text(c, self.text, self.x, self.y, self.size, self.col, weight=self.weight, align=self.align,
                    reveal=p, alpha=alpha)


class Number(Element):
    """Counts from ``frm`` to ``value``; the final text is exactly ``fmt.format(value)``."""
    appear = "countup"

    def __init__(self, id, value, x, y, size=120, col=R.INK, frm=0.0, fmt="{:.0f}", prefix="", suffix="",
                 suffix_size=None, align="left", **kw):
        super().__init__(id, **kw)
        self.value, self.frm, self.fmt = value, frm, fmt
        self.x, self.y, self.size, self.col, self.align = x, y, size, col, align
        self.prefix, self.suffix = prefix, suffix
        self.suffix_size = suffix_size or max(size * 0.42, 34)

    def text_at(self, p: float) -> str:
        v = self.value if p >= 1 else self.frm + (self.value - self.frm) * p
        return self.prefix + self.fmt.format(v)

    def bounds(self):
        main = self.prefix + self.fmt.format(self.value)
        w = R.text_width(main, self.size) + (R.text_width(" " + self.suffix, self.suffix_size) if self.suffix else 0)
        x = self.x - (w / 2 if self.align == "center" else (w if self.align == "right" else 0))
        return x, self.y - self.size * 0.75, w, self.size * 0.8

    def paint(self, c, p, alpha, t):
        x, _, w, _ = self.bounds()
        s = self.text_at(p)
        R.draw_text(c, s, x, self.y, self.size, self.col, alpha=alpha)
        if self.suffix:
            final_w = R.text_width(self.prefix + self.fmt.format(self.value), self.size)
            R.draw_text(c, " " + self.suffix, x + final_w, self.y, self.suffix_size, self.col, alpha=alpha)


class Picture(Element):
    appear = "fade"
    burst = False

    def __init__(self, id, image: skia.Image, rect, *, frame_col=R.INK, cover=True, radius=18, tilt=0.0,
                 polaroid=False, **kw):
        super().__init__(id, **kw)
        self.image, self.rect, self.cover, self.radius = image, rect, cover, radius
        self.tilt, self.polaroid = tilt, polaroid
        x, y, w, h = rect
        self.frame = R.Stroke(R.rect_pts(x - 6, y - 6, w + 12, h + 12), frame_col, 5, f"{id}:frame", closed=True)

    def bounds(self):
        return self.rect

    def paint(self, c, p, alpha, t):
        x, y, w, h = self.rect
        c.save()
        if self.tilt:
            c.rotate(self.tilt, x + w / 2, y + h / 2)
        if self.polaroid:  # white print border with a soft shadow
            c.drawRect(skia.Rect.MakeXYWH(x - 14 + 7, y - 14 + 9, w + 28, h + 70), R.fill_paint(R.INK, 0.18 * alpha * clamp(p)))
            c.drawRect(skia.Rect.MakeXYWH(x - 14, y - 14, w + 28, h + 70), R.fill_paint("#FFFFFF", alpha * clamp(p)))
        self._paint(c, p, alpha, t)
        c.restore()

    def _paint(self, c, p, alpha, t):
        x, y, w, h = self.rect
        iw, ih = self.image.width(), self.image.height()
        s = max(w / iw, h / ih) if self.cover else min(w / iw, h / ih)
        sw, sh = w / s, h / s
        src = skia.Rect.MakeXYWH((iw - sw) / 2, (ih - sh) / 2, sw, sh)
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), self.radius, self.radius), True)
        paint = skia.Paint(AntiAlias=True, Alphaf=alpha * clamp(p))
        c.drawImageRect(self.image, src, skia.Rect.MakeXYWH(x, y, w, h), skia.SamplingOptions(skia.FilterMode.kLinear),
                        paint)
        c.restore()
        self.frame.draw(c, p, alpha)


class Custom(Element):
    """Element painted by a function ``fn(canvas, p, alpha, t)``; bounds given explicitly."""

    def __init__(self, id, rect, fn, appear="draw", **kw):
        super().__init__(id, **kw)
        self.rect, self.fn, self.appear = rect, fn, appear

    def bounds(self):
        return self.rect

    def paint(self, c, p, alpha, t):
        self.fn(c, p, alpha, t)


# ------------------------------------------------------------------ helpers that build doodles

def box(id, x, y, w, h, lines, col=R.INK, size=40, fill=None, sub=None, sub_col=R.INK, top=False, **kw) -> Doodle:
    """Rough box with centred label lines (and an optional smaller subtitle); ``top`` puts them at the top."""
    labels = []
    n = len(lines) + (1 if sub else 0)
    lh = size * 1.08
    y0 = (y + size * 1.15) if top else (y + h / 2 - (n * lh) / 2 + size * 0.8)
    for i, ln in enumerate(lines):
        labels.append({"text": ln, "x": x + w / 2, "y": y0 + i * lh, "size": size, "color": col, "align": "center"})
    if sub:
        labels.append({"text": sub, "x": x + w / 2, "y": y0 + len(lines) * lh - size * 0.05, "size": size * 0.72,
                       "color": sub_col, "align": "center", "weight": "regular"})
    fills = [(R.rect_pts(x + 4, y + 4, w - 8, h - 8)[:4], fill, {"tint": 0.12, "gap": 18, "width": 2.0})] if fill else []
    return Doodle(id, strokes=[(R.rect_pts(x, y, w, h), col, 6, True)], fills=fills, labels=labels, **kw)


def arrow(id, p0, p1, col=R.INK, width=6, bend=0.0, label=None, label_size=32, **kw) -> Doodle:
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0)
    ln = math.hypot(nx, ny) or 1
    cx, cy = mx + nx / ln * bend, my + ny / ln * bend
    pts = [((1 - s) ** 2 * x0 + 2 * (1 - s) * s * cx + s * s * x1, (1 - s) ** 2 * y0 + 2 * (1 - s) * s * cy + s * s * y1)
           for s in np.linspace(0, 1, 24)]
    main = R.Stroke(pts, col, width, f"{id}:shaft")
    heads = [R.Stroke(hp, col, width, f"{id}:h{i}", double=False) for i, hp in enumerate(R.arrow_head(main.passes[0]))]
    labels = []
    if label:
        labels.append({"text": label, "x": cx, "y": cy - 14, "size": label_size, "color": col, "align": "center",
                       "weight": "regular"})
    return Doodle(id, strokes=[main, *heads], labels=labels, **kw)
