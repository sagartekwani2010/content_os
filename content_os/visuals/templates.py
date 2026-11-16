"""Reusable animated diagram templates.

A beat in the spec names one template plus its params; the template returns elements whose ids are
the targets the beat's word-anchored cues animate. Numbers enter only as ``"@fact"`` references or
``{fact}`` placeholders inside text (see facts.py). Everything is laid out inside the safe zone of the
1080x960 top panel: x 60-1020, y 250-745 (Instagram header above, captions below); footers sit in the
strip at y 926-960.

``CATALOGUE`` documents every template (params, target ids, motion) and is what ``draft-spec`` sends
to the model.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
import skia

from . import doodles as D
from . import rough as R
from .elements import Custom, Doodle, Element, Label, Number, Picture, arrow, box, clamp, ease_out
from .facts import REPO, fill, value

W, H = 1080, 960
X0, X1, Y0, Y1 = 60, 1020, 250, 745
FOOTER_Y = 950
from .palette import NAMED as COLORS  # noqa: E402


def col(name: str | None, default: str = R.INK) -> str:
    if not name:
        return default
    return COLORS.get(name, name if str(name).startswith("#") else default)


def txt(s) -> str:
    return fill(str(s)) if s is not None else ""


def num(spec: dict, id: str, x: float, y: float, size: float, color: str, align="left", **kw) -> Number:
    """A Number element from a spec dict: value ("@fact"), prefix, suffix, decimals, from."""
    v = value(spec["value"])
    dec = int(spec.get("decimals", 0 if float(v).is_integer() else 1))
    fmt = "{:,.%df}" % dec
    return Number(id, float(v), x, y, size, color, frm=float(value(spec.get("from", 0))), fmt=fmt,
                  prefix=txt(spec.get("prefix", "")), suffix=txt(spec.get("suffix", "")),
                  suffix_size=spec.get("suffix_size"), align=align, **kw)


# ------------------------------------------------------------------ motion elements

class Edge(Element):
    """Connector that draws itself, then keeps sending a small dot ("packet") along its path."""

    def __init__(self, id, p0, p1, color=R.INK, label=None, bend=0.0, live=False, **kw):
        super().__init__(id, **kw)
        self.doodle = arrow(id + ":a", p0, p1, color, 6, bend=bend, label=label, label_size=30)
        self.path = self.doodle.strokes[0].passes[0]
        self.color, self.live = color, live
        self.t_done = None

    def bounds(self):
        return self.doodle.bounds()

    def paint(self, c, p, alpha, t):
        self.doodle.paint(c, p, alpha, t)
        if p >= 1 and self.live and not self.dim:
            if self.t_done is None:
                self.t_done = t
            q = ((t - self.t_done) / 1.3) % 1.0
            pts = self.path
            k = min(len(pts) - 1, int(q * (len(pts) - 1)))
            c.drawCircle(float(pts[k][0]), float(pts[k][1]), 9, R.fill_paint(self.color, alpha * 0.9))


class Bar(Element):
    """Bar that grows from the baseline, with an error bar that springs into place."""

    def __init__(self, id, x, w, base, top, ci_px, color, **kw):
        super().__init__(id, **kw)
        self.x, self.w, self.base, self.top, self.ci_px, self.color = x, w, base, top, ci_px, color
        self.outline = R.Stroke([(x, base), (x, top), (x + w, top), (x + w, base)], color, 6, id + ":o")
        self.hatch = R.Hachure([(x, base), (x, top), (x + w, top), (x + w, base)], color, id + ":h", gap=14, tint=0.18)

    def bounds(self):
        lo, hi = self.ci_px if self.ci_px else (self.top, self.top)
        return self.x, min(hi, self.top), self.w, self.base - min(hi, self.top)

    def paint(self, c, p, alpha, t):
        g = clamp(p * 1.25)
        h = (self.base - self.top) * ease_out(g)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(self.x - 10, self.base - h - 6, self.x + self.w + 10, self.base + 6))
        self.hatch.draw(c, 1.0, alpha)
        self.outline.draw(c, 1.0, alpha)
        c.restore()
        if self.ci_px and p > 0.6:
            q = clamp((p - 0.6) / 0.4)  # whiskers draw out from the bar top
            lo, hi = self.ci_px
            cx = self.x + self.w / 2
            pa = R.stroke_paint(R.INK, 4.5, alpha * q)
            mid = self.top
            c.drawLine(cx, mid + (lo - mid) * q, cx, mid + (hi - mid) * q, pa)
            if q >= 1:
                c.drawLine(cx - 26, lo, cx + 26, lo, pa)
                c.drawLine(cx - 26, hi, cx + 26, hi, pa)


class Mover(Element):
    """An icon doodle that keeps moving once it has appeared: ``path(t) -> (dx, dy, deg)``."""

    def __init__(self, id, doodle: Doodle, path, **kw):
        super().__init__(id, **kw)
        self.doodle, self.path = doodle, path
        self.t0 = None

    def bounds(self):
        return self.doodle.bounds()

    def paint(self, c, p, alpha, t):
        if self.t0 is None and p > 0:
            self.t0 = t
        dx, dy, deg = self.path(max(0.0, t - (self.t0 or t)))
        cx, cy = self.center()
        c.save()
        c.translate(dx, dy)
        if deg:
            c.rotate(deg, cx, cy)
        self.doodle.paint(c, p, alpha, t)
        c.restore()


def scan_path(rx: float, ry: float, period: float = 2.4):
    return lambda t: (rx * math.sin(2 * math.pi * t / period), ry * math.sin(4 * math.pi * t / period), 0)


def wobble_path(deg: float = 4, period: float = 1.6):
    return lambda t: (0, 0, deg * math.exp(-t / 2.5) * math.sin(2 * math.pi * t / period))


# ------------------------------------------------------------------ shared pieces

def common(P: dict, ctx: dict) -> list[Element]:
    out = []
    if P.get("title"):
        out.append(Label("title", txt(P["title"]), X0, 268, P.get("title_size", 46), col(P.get("title_color"))))
    if P.get("footer"):
        out.append(Label("footer", txt(P["footer"]), W / 2, FOOTER_Y, 24, R.GREY, align="center", weight="regular"))
    return out


def image_for(name, ctx) -> skia.Image | None:
    if not name:
        return None
    if name in ctx.get("images", {}):
        return ctx["images"][name]
    return D.load_image(Path(name).expanduser() if Path(name).expanduser().is_absolute() else REPO / name)


def annotations(rect, items: list[dict]) -> list[Element]:
    """Drawn annotations that move onto a photo; x, y, w, h are fractions of the photo rect."""
    px, py, pw, ph = rect
    out = []
    for a in items or []:
        kind, c = a.get("kind", "circle"), col(a.get("color"), R.RED)
        x, y = px + a.get("x", 0.5) * pw, py + a.get("y", 0.5) * ph
        w, h = a.get("w", 0.25) * pw, a.get("h", 0.2) * ph
        aid = a["id"]
        if kind == "circle":
            out.append(Doodle(aid, strokes=[(R.ellipse_pts(x, y, w / 2, h / 2, start=-2.4, sweep=6.9), c, 7)],
                              labels=[{"text": txt(a["text"]), "x": x, "y": y - h / 2 - 14, "size": a.get("size", 40),
                                       "color": c, "align": "center", "halo": "#FFFFFF"}] if a.get("text") else []))
        elif kind == "outline":  # hidden thing: white + colour wobbly blob with a label inside
            pts = [(x + w / 2 * math.cos(s) + 0.05 * w * math.sin(3 * s), y + h / 2 * math.sin(s)) for s in
                   np.linspace(0, 2 * math.pi, 40)]
            out.append(Doodle(aid, strokes=[(pts, "#FFFFFF", 10, True), (pts, c, 5, True)],
                              labels=[{"text": txt(a.get("text", "")), "x": x, "y": y + 14, "size": a.get("size", 38),
                                       "color": "#FFFFFF", "align": "center"}]))
        elif kind == "arrow":  # flies in from outside the photo to the point
            sx = px + pw + 40 if a.get("from", "right") == "right" else px - 40
            out.append(Edge(aid, (sx, y - 70), (x, y), c, bend=30, live=False))
        elif kind == "label":
            out.append(Label(aid, txt(a["text"]), x, y, a.get("size", 40), c, align="center"))
        elif kind == "strokes":  # e.g. carrots drawn over the photo
            rng = np.random.default_rng(len(aid))
            st = []
            for _ in range(int(a.get("pieces", 9))):
                sx, sy = x - w / 2 + rng.uniform(0, w), y - h / 2 + rng.uniform(0, h)
                st.append(([(sx, sy), (sx + rng.uniform(0.3, 0.6) * w / 3, sy + rng.uniform(-0.2, 0.2) * h)], c, 9))
            out.append(Doodle(aid, strokes=st))
        elif kind == "card":  # a reference card placed on the plate for scale
            out.append(Doodle(aid, strokes=[(R.rect_pts(x - w / 2, y - h / 2, w, h), c, 6, True),
                                            ([(x - w * 0.4, y - h * 0.2), (x + w * 0.4, y - h * 0.2)], c, 8)],
                              fills=[(R.rect_pts(x - w / 2 + 2, y - h / 2 + 2, w - 4, h - 4)[:4], c, {"tint": 0.25, "gap": 10})]))
        elif kind == "scan":  # magnifier moving over the photo
            mag = D.magnifier(aid + ":m", x, y, a.get("scale", 0.9), c)
            out.append(Mover(aid, mag, scan_path(pw * 0.25, ph * 0.12)))
        else:
            raise ValueError(f"annotation {aid}: unknown kind {kind!r}")
    for el in out:
        el.burst = False
    return out


def side_rows(rows: list[dict], x: float, y_top: float, y_bot: float) -> list[Element]:
    """Right-column stack: text, number, change (from -> to with arrow), range (lo — mid — hi)."""
    out = []
    n = len(rows)
    if not n:
        return out
    step = (y_bot - y_top) / n
    for i, r in enumerate(rows):
        y = y_top + step * (i + 0.72)
        kind, c, size = r.get("kind", "text"), col(r.get("color")), r.get("size")
        if kind == "text":
            out.append(Label(r["id"], txt(r["text"]), x, y, size or 46, c, weight=r.get("weight", "bold")))
        elif kind == "number":
            out.append(num(r, r["id"], x, y, size or 96, c))
        elif kind == "change":
            a = num({"value": r["from"], "suffix": ""}, r["id"] + "_from", x, y, size or 88, R.INK)
            fw = R.text_width(R_fmt(r["from"]), size or 88)
            out.append(a)
            out.append(Edge(r["id"] + "_arrow", (x + fw + 18, y - (size or 88) * 0.3), (x + fw + 100, y - (size or 88) * 0.3),
                            c, live=False))
            out.append(num({"value": r["to"], "from": r["from"], "suffix": r.get("suffix", "")}, r["id"], x + fw + 115, y,
                           size or 88, c))
        elif kind == "range":
            lo, hi, mid = (float(value(r[k])) for k in ("lo", "hi", "mid"))
            span = 380
            xm = x + (mid - lo) / (hi - lo) * span

            def draw(cv, p, alpha, t, lo=lo, hi=hi, xm=xm, y=y, c=c):
                q = ease_out(p)
                cv.drawLine(x, y, x + span * q, y, R.stroke_paint(c, 8, alpha))
                for xx in (x, x + span * q):
                    cv.drawLine(xx, y - 18, xx, y + 18, R.stroke_paint(c, 6, alpha))
                R.draw_text(cv, f"{lo:,.0f}", x, y + 56, 40, R.INK, align="center", alpha=alpha * q)
                R.draw_text(cv, f"{hi:,.0f}", x + span, y + 56, 40, R.INK, align="center", alpha=alpha * q)
                if q > 0.8:
                    cv.drawCircle(xm, y, 13, R.fill_paint(R.INK, alpha))

            out.append(Custom(r["id"], (x, y - 20, span, 80), draw))
        else:
            raise ValueError(f"row {r.get('id')}: unknown kind {kind!r}")
    return out


def R_fmt(ref) -> str:
    v = float(value(ref))
    return f"{v:,.0f}" if v.is_integer() else f"{v:,.1f}"


# ------------------------------------------------------------------ templates

def t_versus(P, ctx):
    """Hook: optional phone + photo on the left; two labelled rows on the right with a verdict sign."""
    els = []
    img = image_for(P.get("photo"), ctx)
    if P.get("photo") is not None:
        if P.get("phone", True):
            els.append(Doodle("phone", strokes=[(R.rect_pts(70, 250, 440, 490), R.INK, 7, True),
                                                (R.ellipse_pts(290, 718, 10, 10), R.INK, 4, True)]))
        els.append(D.lunch("photo", (95, 285, 390, 410), img))
    L, Rt = P["left"], P["right"]
    els += [Label("left", txt(L["text"]), 560, 360, 56, col(L.get("color"), R.GREEN)),
            Label("left_sub", txt(L.get("sub", "")), 562, 410, 36, R.GREY, weight="regular"),
            Label("right", txt(Rt["text"]), 560, 640, 56, col(Rt.get("color"), R.ORANGE)),
            Label("right_sub", txt(Rt.get("sub", "")), 562, 690, 36, R.GREY, weight="regular")]
    v = P.get("verdict", "=")
    strokes = [([(580, 490), (700, 486)], R.RED, 14), ([(580, 540), (700, 536)], R.RED, 14)]
    if v == "≠":
        strokes.append(([(670, 450), (610, 580)], R.RED, 10))
    els += [Doodle("verdict", strokes=strokes),
            Label("verdict_text", txt(P.get("verdict_text", "")), 735, 535, 60, R.RED)]
    return els


def t_paper(P, ctx):
    """A paper card (title, venue) with either key points (right column) or a row of 2-3 steps with icons."""
    steps = P.get("steps")
    els = []
    if steps:
        card = bool(P.get("venue"))
        if card:
            els.append(D.paper_card("paper", X0, 230, 600, 160, txt(P["title"]), txt(P["venue"])))
        sc = float(P.get("icon_scale", 1.0 if card else 1.35))
        yi, yl = (545, 700) if card else (470, 680)
        n = len(steps)
        xs = [190 + i * (690 / max(1, n - 1)) for i in range(n)] if n > 1 else [540]
        for i, s in enumerate(steps):
            x = xs[i]
            icon = icon_doodle(s.get("icon", "plate"), s["id"], x, yi, col(s.get("color"), R.BLUE), sc)
            els.append(icon)
            els.append(Label(s["id"] + "_l", txt(s["text"]), x, yl, 46 if card else 60, col(s.get("color"), R.BLUE),
                             align="center"))
            if i:
                els.append(Edge(f"a{i}", (xs[i - 1] + 110 * sc, yi), (x - 110 * sc, yi), R.INK))
        if P.get("count"):
            els.append(Label("count", txt(P["count"]), 760, 330, 56))
    else:
        els.append(D.paper_card("paper", X0, 250, 470, 470, txt(P["title"]), txt(P["venue"])))
        if P.get("icon"):
            els.append(icon_doodle(P["icon"], "icon", 295, 560, R.BLUE, scale=1.15))
        y = 380
        for pt in P.get("points", []):
            if "value" in pt:
                els.append(num(pt, pt["id"], 580, y, pt.get("size", 96), col(pt.get("color"), R.BLUE)))
            else:
                els.append(Label(pt["id"], txt(pt["text"]), 580, y, pt.get("size", 52), col(pt.get("color")),
                                 weight=pt.get("weight", "bold")))
            y += pt.get("gap", 110)
    return els


def icon_doodle(kind, id, x, y, c, scale=1.0) -> Element:
    if kind == "magnifier":  # over a plate
        plate = Doodle(id + ":plate", strokes=[(R.ellipse_pts(x, y + 10, 80 * scale, 80 * scale), R.GREY, 4, True)])
        return Group(id, [plate, D.magnifier(id + ":m", x, y, 0.8 * scale, c)])
    if kind == "ruler":
        return D.ruler(id, x, y, scale, c)
    if kind == "book":
        return D.book(id, x, y, scale, c)
    if kind == "scale":
        return D.scale_doodle(id, x, y, scale)
    if kind == "plate":
        return D.plate_doodle(id, x, y, 90 * scale)
    if kind == "table":
        return Doodle(id, strokes=[(R.rect_pts(x - 90, y - 70, 180, 140), c, 6, True),
                                   ([(x - 90, y - 30), (x + 90, y - 30)], c, 5), ([(x - 90, y + 10), (x + 90, y + 10)], R.GREY, 3),
                                   ([(x - 90, y + 45), (x + 90, y + 45)], R.GREY, 3), ([(x - 20, y - 30), (x - 20, y + 70)], R.GREY, 3)])
    if kind == "card":
        return Doodle(id, strokes=[(R.rect_pts(x - 80, y - 50, 160, 100), c, 6, True), ([(x - 65, y - 20), (x + 65, y - 20)], c, 8)])
    if kind == "ball":
        return D.crystal_ball(id, x, y, scale)
    raise ValueError(f"unknown icon {kind!r}")


class Group(Element):
    def __init__(self, id, parts, **kw):
        super().__init__(id, **kw)
        self.parts = parts

    def bounds(self):
        b = [p.bounds() for p in self.parts]
        x0 = min(v[0] for v in b); y0 = min(v[1] for v in b)
        x1 = max(v[0] + v[2] for v in b); y1 = max(v[1] + v[3] for v in b)
        return x0, y0, x1 - x0, y1 - y0

    def paint(self, c, p, alpha, t):
        for part in self.parts:
            part.paint(c, p, alpha, t)


def t_flow(P, ctx):
    """Boxes on a 3-column grid ("at": [col, row]) joined by edges that draw on and then carry moving dots.
    Node kinds: box, photo, diamond, bubble. ``dim: true`` = shown faded from the first frame (earlier step)."""
    nodes = P["nodes"]
    rows = int(P.get("rows", 1 + max(n.get("at", [i % 3, i // 3])[1] for i, n in enumerate(nodes))))
    top = 290 if P.get("title") else 262
    rh = (Y1 - top) / rows
    ncol = int(P.get("cols", 3))
    cw = (X1 - X0) / ncol
    geo = {}
    els = []
    for i, n in enumerate(nodes):
        cx_i, ry = n.get("at", [i % ncol, i // ncol])
        w, h = n.get("w", 270), min(n.get("h", 118), rh - 36)
        cx, cy = X0 + cw * (cx_i + 0.5), top + rh * (ry + 0.5)
        x, y = cx - w / 2, cy - h / 2
        geo[n["id"]] = (x, y, w, h)
        c = col(n.get("color"), R.INK)
        kind = n.get("kind", "box")
        dim = bool(n.get("dim"))
        if kind == "box":
            els.append(box(n["id"], x, y, w, h, [txt(n["text"])], c, n.get("size", 40), fill=c if n.get("fill", True) else None,
                           sub=txt(n["sub"]) if n.get("sub") else None, dim=dim))
        elif kind == "photo":
            els.append(Doodle(n["id"], strokes=[(R.rect_pts(cx - 70, cy - 52, 140, 104), c, 6, True),
                                                (R.ellipse_pts(cx, cy, 26, 26), c, 4, True)],
                              labels=[{"text": txt(n.get("text", "photo")), "x": cx, "y": cy + 92, "size": 30,
                                       "color": R.GREY, "align": "center", "weight": "regular"}], dim=dim))
            geo[n["id"]] = (cx - 70, cy - 52, 140, 104)
        elif kind == "diamond":
            dia = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy), (cx, cy - h / 2)]
            els.append(Doodle(n["id"], strokes=[(dia, c, 7, True)], fills=[(dia[:4], c, {"tint": 0.15, "gap": 12})],
                              labels=[{"text": txt(n["text"]), "x": cx, "y": cy + 14, "size": n.get("size", 40),
                                       "color": R.INK, "align": "center"}], dim=dim))
        elif kind == "bubble":
            els.append(D.bubble(n["id"], x, y, w, h, [txt(n["text"])], c, tail=n.get("tail", "left"), size=n.get("size", 42),
                                dim=dim))
        else:
            raise ValueError(f"node {n['id']}: unknown kind {kind!r}")
    for e in P.get("edges", []):
        a, b = geo[e["from"]], geo[e["to"]]
        p0, p1 = _border_points(a, b)
        dim = any(n.get("dim") for n in nodes if n["id"] in (e["from"], e["to"])) and e.get("dim", True)
        els.append(Edge(e.get("id", f"e_{e['from']}_{e['to']}"), p0, p1, col(e.get("color")), label=txt(e.get("label")) or None,
                        bend=e.get("bend", 0), dim=dim))
    for nt in P.get("notes", []):
        x, y, w, h = geo[nt["near"]]
        side = nt.get("side", "below")
        size = nt.get("size", 50)
        if side == "below":
            px, py, al = x + w / 2, y + h + size + 6, "center"
        elif side == "above":
            px, py, al = x + w / 2, y - 18, "center"
        elif side == "right":
            px, py, al = x + w + 24, y + h / 2 + size * 0.3, "left"
        else:
            px, py, al = x - 24, y + h / 2 + size * 0.3, "right"
        els.append(Label(nt["id"], txt(nt["text"]), px, py, size, col(nt.get("color")), align=al))
    if P.get("frame"):
        els.append(Doodle("frame", strokes=D.dashed_rect(40, top - 22, 1000, Y1 - top + 30, key="frame"),
                          labels=[{"text": txt(P["frame"]), "x": 60, "y": top - 34, "size": 34, "color": R.GREY}]))
    return els


def _border_points(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ca = np.array([ax + aw / 2, ay + ah / 2])
    cb = np.array([bx + bw / 2, by + bh / 2])
    d = cb - ca

    def exit_pt(c, w, h, v):
        tx = (w / 2 + 12) / abs(v[0]) if v[0] else math.inf
        ty = (h / 2 + 12) / abs(v[1]) if v[1] else math.inf
        return c + v * min(tx, ty)

    return tuple(exit_pt(ca, aw, ah, d)), tuple(exit_pt(cb, bw, bh, -d))


@lru_cache(maxsize=1)
def _usda_table():
    spec = importlib.util.spec_from_file_location("ft_estimate", REPO / "demos/food-tracker/estimate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Table(REPO / "demos/food-tracker/data/fdc_compact.csv")


def usda_rows(query: str, k: int = 8) -> list[str]:
    return [r["description"] for r in _usda_table().search(query, k=k)]


def t_table_search(P, ctx):
    """A food item searches the USDA table: the real top candidate rows (BM25 over fdc_compact.csv, as
    estimate.py does) appear one by one; the matcher circles its pick, or rejects them all."""
    query = txt(P["query"])
    cands = usda_rows(P.get("search", query), int(P.get("k", 8)))
    pick = P.get("pick")
    if pick is not None and pick not in cands:
        raise ValueError(f"table_search: pick {pick!r} is not among the top candidates {cands}")
    tx, ty, tw, th = 380, 296, 640, 372
    rh = th / 6
    state = {"search": None}

    def short(s, n=34):
        return s if len(s) <= n else s[: n - 1] + "…"

    def table(c, p, alpha, t):
        R.Stroke(R.rect_pts(tx, ty, tw, th), R.GREEN, 6, "tbl:o", closed=True).draw(c, p, alpha)
        for i in range(1, 6):
            c.drawLine(tx + 6, ty + i * rh, tx + tw - 6, ty + i * rh, R.stroke_paint(R.LIGHT, 2, alpha * p))
        sc = state["search"]
        if sc is not None and t >= sc.t:
            shown = clamp((t - sc.t) / sc.dur) * 6  # candidate rows appear one after another
            for i, s in enumerate(cands[:6]):
                a = clamp(shown - i)
                if a > 0:
                    R.draw_text(c, short(s), tx + 20, ty + i * rh + rh * 0.65, 30, R.INK, weight="regular", alpha=alpha * a)

    tb = Custom("table", (tx, ty, tw, th), table)
    tb._search_state = state
    els = [Label("query_l", txt(P.get("query_label", "item")), X0 + 6, 292, 34, R.GREY, weight="regular"),
           D.bubble("query", X0, 306, 290, 116, [query], R.BLUE, tail="right", size=46),
           num({"value": P["count"]}, "count", X0, 580, 76, R.GREEN) if P.get("count") else None,
           Label("count_l", txt(P.get("count_label", "USDA foods")), X0 + 4, 628, 38, R.GREY, weight="regular"),
           tb]
    if pick is not None:
        i = cands.index(pick)
        y = ty + i * rh
        els.append(Doodle("pick", strokes=[(R.ellipse_pts(tx + tw / 2, y + rh / 2, tw / 2 - 8, rh / 2 + 4, start=-2.4,
                                                          sweep=6.9), R.RED, 6)]))
        els.append(Doodle("pick_ok", strokes=D.check_strokes(tx + tw - 60, y + rh * 0.55, 40)))
    if P.get("reject", True):
        els.append(Doodle("reject", strokes=D.xmark_strokes(tx + 24, ty + th + 44, 40),
                      labels=[{"text": txt(P.get("reject_text", "or reject them all")), "x": tx + 84, "y": ty + th + 58,
                               "size": 40, "color": R.RED}]))
    if P.get("matcher"):
        els.append(Label("matcher", txt(P["matcher"]), X0, 712, 46, R.PURPLE))
    return [e for e in els if e is not None]


def t_bars(P, ctx):
    """Bars with 95% CI whiskers that grow and wiggle into place; optional overlap band, drop arrow and
    a callout column on the right."""
    bars = P["bars"]
    base = 690
    def top_of(b):
        ci = value(b["ci"]) if b.get("ci") else None
        return float(ci[1]) if ci else float(value(b["value"]))
    vmax = max(top_of(b) for b in bars)
    axis_h = P.get("axis_h", 380)
    scale = (axis_h - 40) / vmax
    x_axis = (110, 110 + 170 * len(bars) + 90)
    els = [Doodle("axis", strokes=[([(x_axis[0], base), (x_axis[1], base)], R.INK, 6),
                                   ([(x_axis[0], base), (x_axis[0], base - axis_h)], R.INK, 5)])]
    if P.get("y_label"):
        els.append(Label("y_label", txt(P["y_label"]), X0, 262, 32, R.GREY, weight="regular"))
    pos = {}
    for i, b in enumerate(bars):
        x = 160 + i * 230
        v = float(value(b["value"]))
        ci = value(b["ci"]) if b.get("ci") else None
        top = base - v * scale
        ci_px = (base - ci[0] * scale, base - ci[1] * scale) if ci else None
        c = col(b.get("color"), R.BLUE)
        els.append(Bar(b["id"], x, 150, base, top, ci_px, c))
        ytop = (ci_px[1] if ci_px else top) - 16
        els.append(num({"value": b.get("shown", b["value"])}, b["id"] + "_v", x + 75, ytop, 64, c, align="center"))
        els.append(Label(b["id"] + "_l", txt(b["label"]), x + 75, base + 44, 36, R.INK, align="center"))
        pos[b["id"]] = (x, top, ci_px)
    if P.get("band"):
        a, b = (pos[k] for k in P["band"]["between"])
        lo = max(a[2][1], b[2][1]) if a[2] and b[2] else min(a[1], b[1])
        hi = min(a[2][0], b[2][0]) if a[2] and b[2] else max(a[1], b[1])
        els.insert(0, Doodle(P["band"]["id"], fills=[([(x_axis[0] + 20, lo), (x_axis[1], lo), (x_axis[1], hi), (x_axis[0] + 20, hi)],
                                                     R.YELLOW, {"tint": 0.35, "gap": 18, "width": 2.5})]))
    if P.get("drop"):
        a, b = pos[P["drop"]["from"]], pos[P["drop"]["to"]]
        els.append(Edge(P["drop"]["id"], (a[0] + 80, a[1] - 70), (b[0] + 40, b[1] - 75), R.RED, bend=-60, live=False))
    if P.get("header"):
        hd = P["header"]
        if hd.get("icon"):
            els.append(icon_doodle(hd["icon"], hd["id"] + "_icon", 100, 285, R.PURPLE, 0.9))
        els.append(Label(hd["id"], txt(hd["text"]), 160 if hd.get("icon") else X0, 300, 56, col(hd.get("color"), R.PURPLE)))
        if hd.get("sub"):
            els.append(Label(hd["id"] + "_sub", txt(hd["sub"]), 500, 300, 32, R.GREY, weight="regular"))
    cx = (x_axis[1] + X1) / 2 + 10
    for r in P.get("callout", []):
        els.append(Label(r["id"], txt(r["text"]), cx, r.get("y", 470), r.get("size", 60), col(r.get("color")), align="center",
                         weight=r.get("weight", "bold")))
    return els


def t_ticker(P, ctx):
    """One big number that ticks up (right), with a small moving illustration on the left
    (a grid of n plates popping in, a wobbling scale)."""
    els = []
    L = P.get("left") or {}
    if L.get("kind") == "plates":
        n = int(value(L["n"]))
        cols = 10
        strokes = []
        for i in range(n):
            r, cc = divmod(i, cols)
            strokes.append((R.ellipse_pts(95 + cc * 44, 330 + r * 50, 17, 17, n=24), R.INK, 3.5, True))
        els.append(Doodle("plates", strokes=strokes))
        els.append(num({"value": L["n"], "suffix": L.get("suffix", "")}, "n", 70, 640, 96, R.BLUE))
        if L.get("caption"):
            els.append(Label("caption", txt(L["caption"]), 74, 700, 40, R.GREY, weight="regular"))
        els.append(D.scale_doodle("scale", 470, 655, 0.6))
    N = P["number"]
    els += [Label("label", txt(P.get("label", "")), 580, 370, 48),
            num(N, "num", 590, 540, N.get("size", 170), col(N.get("color"), R.RED)),
            Label("sub", txt(P.get("sub", "")), 600, 610, 44)]
    if P.get("ci"):
        els.append(Label("ci", txt(P["ci"]), 600, 670, 32, R.GREY, weight="regular"))
    return els


def t_photo(P, ctx):
    """Evidence photo (left) with annotations drawn onto it, and a right column of rows."""
    rect = tuple(P.get("rect", (X0, 270, 430, 420)))
    img = image_for(P["image"], ctx)
    els = [Picture("photo", img, rect) if img is not None else D.plate_doodle("photo", rect[0] + rect[2] / 2,
                                                                                rect[1] + rect[3] / 2, 180)]
    els += annotations(rect, P.get("annotations", []))
    if P.get("credit"):
        lines = txt(P["credit"]).split("\n")
        els.append(Doodle("credit", labels=[{"text": ln, "x": rect[0], "y": rect[1] + rect[3] + 30 + 24 * i, "size": 21,
                                             "color": R.GREY, "weight": "regular"} for i, ln in enumerate(lines)]))
    els += side_rows(P.get("rows", []), rect[0] + rect[2] + 50, 260, Y1)
    return els


def t_line_chart(P, ctx):
    """Labelled line chart that draws left to right with a moving head dot; points flagged by the
    monitor are red. Series "simulated_log" = the simulated usage log (tagged as simulated)."""
    series = D.meal_series(ctx.get("simulated_log")) if P.get("series", "simulated_log") == "simulated_log" else []
    x0, x1, y0, y1 = 110, P.get("width_to", 640), 320, 660
    hi = max(k for k, _ in series) * 1.08
    pts = [(x0 + 24 + (x1 - x0 - 48) * i / max(1, len(series) - 1), y1 - k / hi * (y1 - y0), a) for i, (k, a) in enumerate(series)]
    line = R.Stroke([(x, y) for x, y, _ in pts], R.BLUE, 5, "lc:line", amp=1.0)

    def draw(c, p, alpha, t):
        line.draw(c, p, alpha * 0.8)
        n = int(p * len(pts))
        for x, y, a in pts[:n]:
            c.drawCircle(x, y, 9, R.fill_paint(R.RED if a else R.BLUE, alpha))
        if 0 < p < 1:
            x, y, _ = pts[min(len(pts) - 1, n)]
            c.drawCircle(x, y, 15, R.stroke_paint(R.INK, 4, alpha))

    els = [Doodle("axes", strokes=[([(x0, y1), (x1, y1)], R.INK, 5), ([(x0, y1), (x0, y0 - 20)], R.INK, 5)]),
           Custom("line", (x0, y0, x1 - x0, y1 - y0), draw)]
    if P.get("legend"):
        els.append(Label("legend", txt(P["legend"]), x0 + 10, y1 + 44, 30, R.RED, weight="regular"))
    els.append(Label("tag", txt(P.get("tag", "simulated data")), x1, y0 - 4, 36, R.RED, align="right"))
    els += side_rows(P.get("rows", []), x1 + 40, 280, Y1)
    return els


def t_checklist(P, ctx):
    """Short items that write on and get a check or a cross (or an icon); optional photo on the left
    with annotations."""
    els = []
    xl = 560 if P.get("photo") else 120
    if P.get("photo"):
        rect = (X0, 296, 440, 420)
        img = image_for(P["photo"], ctx)
        els.append(Picture("photo", img, rect) if img is not None else D.plate_doodle("photo", 280, 480, 180))
        els += annotations(rect, P.get("annotations", []))
    items = P["items"]
    step = (Y1 - 300) / len(items)
    for i, it in enumerate(items):
        y = 330 + step * (i + 0.6)
        size = it.get("size", 84 if len(items) <= 2 else 56)
        c = col(it.get("color"), R.GREEN if it.get("mark") == "check" else (R.RED if it.get("mark") == "cross" else R.INK))
        lab = Label(it["id"], txt(it["text"]), xl, y, size, c)
        els.append(lab)
        end = xl + R.text_width(lab.text, size) + 24
        if it.get("mark") == "check":
            els.append(Doodle(it["id"] + "_mark", strokes=D.check_strokes(end, y - size * 0.35, size * 0.75)))
        elif it.get("mark") == "cross":
            els.append(Doodle(it["id"] + "_mark", strokes=D.xmark_strokes(end, y - size * 0.35, size * 0.6)))
        if it.get("icon"):
            els.append(icon_doodle(it["icon"], it["id"] + "_icon", xl - 0, y - size * 0.3, c, 0.6))
    return els


def t_gauge(P, ctx):
    """Confidence gauge whose needle swings to the value, plus an optional dot grid
    ("k of n caught": n dots, k of them circled one by one)."""
    cx, cy, r = 250, 640, 150
    v = float(value(P["value"]))
    state = {"cue": None}

    def gauge(c, p, alpha, t):
        R.Stroke(R.ellipse_pts(cx, cy, r, r, start=math.pi, sweep=math.pi, n=40), R.INK, 7, "g:arc").draw(c, p, alpha)
        for i in range(6):
            a = math.pi + math.pi * i / 5
            c.drawLine(cx + (r - 18) * math.cos(a), cy + (r - 18) * math.sin(a), cx + r * math.cos(a), cy + r * math.sin(a),
                       R.stroke_paint(R.INK, 4, alpha * p))
        R.draw_text(c, "0", cx - r - 8, cy + 36, 30, R.GREY, align="center", alpha=alpha * p, weight="regular")
        R.draw_text(c, "1", cx + r + 8, cy + 36, 30, R.GREY, align="center", alpha=alpha * p, weight="regular")
        q = 0.0
        cue = state["cue"]
        if cue is not None and t >= cue.t:
            q = ease_out((t - cue.t) / cue.dur)
        a = math.pi + math.pi * v * q
        c.drawLine(cx, cy, cx + (r - 30) * math.cos(a), cy + (r - 30) * math.sin(a), R.stroke_paint(R.RED, 9, alpha))
        c.drawCircle(cx, cy, 10, R.fill_paint(R.INK, alpha))

    g = Custom("gauge", (cx - r, cy - r, 2 * r, r), gauge)
    g._gauge_state = state
    els = [g, Label("conf_l", txt(P.get("label", "confidence")), 100, 450, 40, R.GREY, weight="regular"),
           num({"value": P["value"], "decimals": P.get("decimals", 1)}, "num", 330, 462, 72, R.RED)]
    if P.get("headline"):
        els += [icon_bulb(), Label("headline", txt(P["headline"]), 180, 352, 72, R.ORANGE)]
    dots = P.get("dots")
    if dots:
        n, k = int(value(dots["n"])), int(value(dots["k"]))
        strokes, flags = [], []
        for i in range(n):
            rr, cc = divmod(i, 5)
            x, y = 610 + cc * 84, 380 + rr * 84
            strokes.append((R.ellipse_pts(x, y, 22, 22, n=24), R.INK, 5, True))
            if i < k:
                flags.append((R.ellipse_pts(x, y, 34, 34, start=-2.2, sweep=6.7, n=30), R.RED, 5))
        els += [Label("dots_l", txt(dots.get("label", "")), 600, 320, 42), Doodle("dots", strokes=strokes),
                Doodle("flags", strokes=flags),
                num({"value": dots["k"], "suffix": txt(dots.get("suffix", "")), "suffix_size": 44}, "caught", 600, 660, 88,
                    R.RED)]
        if dots.get("sub"):
            els.append(Label("dots_sub", txt(dots["sub"]), 604, 712, 34, R.GREY, weight="regular"))
    return els


def icon_bulb():
    return Doodle("bulb", strokes=[(R.ellipse_pts(110, 330, 40, 44), R.ORANGE, 6, True), ([(92, 376), (128, 376)], R.ORANGE, 6),
                                   ([(96, 392), (124, 392)], R.ORANGE, 6), ([(110, 262), (110, 248)], R.ORANGE, 5),
                                   ([(58, 290), (48, 282)], R.ORANGE, 5), ([(162, 290), (172, 282)], R.ORANGE, 5)])


def t_table(P, ctx):
    """A hand-drawn table; rows appear one by one (cue each row id "r0", "r1"... or the whole "table").
    Cells may hold {fact} placeholders, e.g. the lunch items' grams from the estimate log."""
    cols = P["columns"]
    widths = P.get("widths") or [1] * len(cols)
    rows = P["rows"]
    x0, x1 = X0, X1
    y0 = 300 if P.get("title") else 262
    rh = min(92, (Y1 - y0) / (len(rows) + 1))
    tw = x1 - x0
    xs = [x0]
    for w_ in widths:
        xs.append(xs[-1] + tw * w_ / sum(widths))
    size = P.get("size", 44)
    th = rh * (len(rows) + 1)
    grid = [(R.rect_pts(x0, y0, tw, th), R.INK, 6, True), ([(x0, y0 + rh), (x1, y0 + rh)], R.INK, 5)]
    grid += [([(xx, y0), (xx, y0 + th)], R.LIGHT, 3) for xx in xs[1:-1]]
    grid += [([(x0 + 6, y0 + rh * (i + 1)), (x1 - 6, y0 + rh * (i + 1))], R.LIGHT, 3) for i in range(1, len(rows))]
    head = [{"text": txt(cn), "x": xs[j] + 18, "y": y0 + rh * 0.68, "size": size * 0.85, "color": R.GREY, "weight": "regular"}
            for j, cn in enumerate(cols)]
    els = [Doodle("table", strokes=grid, labels=head)]
    ccol = [col(c) for c in P.get("col_colors", [None] * len(cols))]
    for i, r in enumerate(rows):
        y = y0 + rh * (i + 1) + rh * 0.68
        labels = [{"text": txt(cell), "x": xs[j] + 18, "y": y, "size": size if j == 0 else size * P.get("cell_scale", 0.9),
                   "color": ccol[j], "weight": "bold"} for j, cell in enumerate(r)]
        els.append(Doodle(f"r{i}", labels=labels))
    return els


def t_papers(P, ctx):
    """Two or three research-paper cards side by side (title, venue, one doodle each)."""
    cards = P["cards"]
    n = len(cards)
    gap = 30
    w = ((X1 - X0) - gap * (n - 1)) / n
    y0 = 300 if P.get("title") else 262
    h = Y1 - y0 - 10
    els = []
    for i, cd in enumerate(cards):
        x = X0 + i * (w + gap)
        els.append(D.paper_card(cd["id"], x, y0, w, h, txt(cd["title"]), txt(cd["venue"])))
        if cd.get("icon"):
            els.append(icon_doodle(cd["icon"], cd["id"] + "_icon", x + w / 2, y0 + h * 0.62, col(cd.get("color"), R.BLUE),
                                   cd.get("icon_scale", 1.2)))
        if cd.get("note"):
            els.append(Label(cd["id"] + "_note", txt(cd["note"]), x + w / 2, y0 + h - 30, 36, col(cd.get("color"), R.BLUE),
                             align="center"))
    return els


def t_photo_grid(P, ctx):
    """2-3 photos in a row with captions (the creator's meals), optional big caption below."""
    names = P["photos"]
    n = len(names)
    gap = 24
    w = ((X1 - X0) - gap * (n - 1)) / n
    y0 = 300 if P.get("title") else 270
    h = min(w * 1.05, 330)
    els = []
    for i, ph in enumerate(names):
        x = X0 + i * (w + gap)
        img = image_for(ph["image"], ctx)
        rect = (x, y0, w, h)
        els.append(Picture(ph["id"], img, rect) if img is not None else
                   D.plate_doodle(ph["id"], x + w / 2, y0 + h / 2, min(w, h) / 2 - 20))
        if ph.get("caption"):
            els.append(Label(ph["id"] + "_c", txt(ph["caption"]), x + w / 2, y0 + h + 50, 40, R.GREY, align="center",
                             weight="regular"))
    if P.get("caption"):
        els.append(Label("caption", txt(P["caption"]), W / 2, Y1 - 20, P.get("caption_size", 60),
                         col(P.get("caption_color"), R.GREEN), align="center"))
    return els


TEMPLATES = {"versus": t_versus, "paper": t_paper, "flow": t_flow, "table_search": t_table_search, "bars": t_bars,
             "ticker": t_ticker, "photo": t_photo, "line_chart": t_line_chart, "checklist": t_checklist, "gauge": t_gauge,
             "table": t_table, "papers": t_papers, "photo_grid": t_photo_grid}

CATALOGUE = {
    "versus": {"use": "hook / comparison of two approaches with a verdict sign",
               "params": {"photo": "lunch|null", "phone": True, "left": {"text": "by the book", "sub": "", "color": "green"},
                          "right": {"text": "lazy version", "sub": "one prompt", "color": "orange"}, "verdict": "=|≠",
                          "verdict_text": "matched!"},
               "targets": ["phone", "photo", "left", "left_sub", "verdict", "verdict_text", "right", "right_sub"]},
    "paper": {"use": "a research paper: card + key points, or card + 2-3 steps with moving icons",
              "params": {"title": "Nutrition5k", "venue": "Google · CVPR {n5k_year}", "icon": "scale|plate|none",
                         "points": [{"id": "p1", "value": "@n5k_dishes_spoken", "suffix": "dishes"},
                                    {"id": "p2", "text": "naming it: easy", "color": "green"}],
                         "steps": [{"id": "find", "text": "find it", "icon": "magnifier|ruler|book|scale|plate|table|card",
                                    "color": "blue"}], "count": "3 jobs"},
              "targets": ["paper", "icon", "<point ids>", "<step ids>", "<step id>_l", "a1", "a2", "count"]},
    "flow": {"use": "pipeline / architecture that draws itself box by box, arrows drawing between them",
             "params": {"title": "", "frame": "Claude skill", "rows": 3, "nodes": [
                 {"id": "photo", "kind": "photo|box|diamond|bubble", "text": "photo", "sub": "Fable {fable}", "at": [0, 0],
                  "color": "blue", "dim": False}],
                 "edges": [{"from": "photo", "to": "vision", "label": "yes", "color": "green", "bend": 0}],
                 "notes": [{"id": "kcal", "text": "kcal", "near": "vision", "side": "below|above|left|right", "color": "red"}]},
             "targets": ["<node ids>", "e_<from>_<to>", "<note ids>", "frame"]},
    "table_search": {"use": "searching the USDA table: real top candidate rows appear one by one, matcher picks or rejects",
                     "params": {"query": "dal", "search": "lentil soup", "pick": "<exact description from the top 8>",
                                "count": "@usda_foods", "count_label": "USDA foods", "matcher": "matcher agent"},
                     "targets": ["query", "query_l", "table (use action 'countup' to start the search)", "count", "count_l",
                                 "pick", "pick_ok", "reject", "matcher"]},
    "bars": {"use": "compare 2-3 measured values; bars grow, 95% CI whiskers draw on",
             "params": {"y_label": "kcal missed per plate", "bars": [{"id": "agents", "label": "two agents", "value": "@table_mae",
                                                                      "ci": "@table_ci", "shown": "@table_mae_spoken", "color": "blue"}],
                        "band": {"id": "band", "between": ["agents", "lazy"]}, "drop": {"id": "drop", "from": "a", "to": "b"},
                        "header": {"id": "oracle", "text": "oracle test", "icon": "ball", "sub": "only the weight fixed"},
                        "callout": [{"id": "tie", "text": "TIE", "size": 130, "color": "red", "y": 470}]},
             "targets": ["axis", "y_label", "<bar id>", "<bar id>_v", "<bar id>_l", "band", "drop", "<header id>",
                         "<header id>_icon", "<header id>_sub", "<callout ids>"]},
    "ticker": {"use": "one big number ticking up, with a small illustration (n plates drawn in, a scale)",
               "params": {"left": {"kind": "plates", "n": "@n_dishes", "suffix": "dishes", "caption": "weighed in a lab"},
                          "label": "it missed by", "number": {"value": "@table_mae_spoken", "prefix": "≈", "suffix": "kcal"},
                          "sub": "per plate", "ci": "95% CI {table_ci}"},
               "targets": ["plates", "n", "caption", "scale", "label", "num", "sub", "ci"]},
    "photo": {"use": "evidence photo (hidden-chicken dish or the creator's lunch) with annotations drawn onto it",
              "params": {"image": "dish|lunch", "credit": "Photo: ...", "annotations": [
                  {"id": "a1", "kind": "circle|outline|arrow|label|strokes|card|scan", "x": 0.5, "y": 0.5, "w": 0.3, "h": 0.2,
                   "text": "", "color": "red", "pieces": 9}],
                  "rows": [{"id": "r1", "kind": "text|number|change|range", "text": "", "value": "@fact", "from": "@fact",
                            "to": "@fact", "lo": "@fact", "hi": "@fact", "mid": "@fact", "suffix": "kcal", "color": "red"}]},
              "targets": ["photo", "credit", "<annotation ids>", "<row ids>", "<change id>_from", "<change id>_arrow"]},
    "line_chart": {"use": "monitoring history drawn left to right (simulated usage log; always tagged)",
                   "params": {"series": "simulated_log", "legend": "red = it asked me", "tag": "simulated data", "rows": []},
                   "targets": ["axes", "line", "legend", "tag", "<row ids>"]},
    "checklist": {"use": "takeaway or next steps: items with a check, a cross or an icon; optional photo",
                  "params": {"photo": "lunch|null", "annotations": [], "items": [
                      {"id": "what", "text": "what", "mark": "check|cross", "icon": "card|table|..."}]},
                  "targets": ["photo", "<item ids>", "<item id>_mark", "<item id>_icon", "<annotation ids>"]},
    "gauge": {"use": "a confidence value with a swinging needle, optionally 'k of n caught' dots",
              "params": {"value": "@chicken_conf", "label": "confidence", "headline": "it knew",
                         "dots": {"n": "@worst", "k": "@caught", "label": "15 worst misses", "suffix": "of {worst} caught",
                                  "sub": "flagged {flagged} of {n_dishes} plates"}},
              "targets": ["gauge (draw; countup swings the needle)", "conf_l", "num", "bulb", "headline", "dots_l", "dots",
                          "flags", "caught", "dots_sub"]},
}
CATALOGUE.update({
    "table": {"use": "a small table whose rows appear one by one (item / grams, item -> USDA row -> kcal)",
              "params": {"columns": ["item", "grams"], "widths": [2, 1], "col_colors": ["ink", "blue"],
                         "rows": [["rice", "{lunch_i0_g} g"]], "size": 44},
              "targets": ["table", "r0", "r1", "..."]},
    "papers": {"use": "research papers side by side (title, venue, doodle)",
               "params": {"cards": [{"id": "n5k", "title": "Nutrition5k", "venue": "Google · CVPR {n5k_year}", "icon": "scale",
                                     "note": "", "color": "blue"}]},
               "targets": ["<card ids>", "<card id>_icon", "<card id>_note"]},
    "photo_grid": {"use": "2-3 of the creator's meal photos in a row with captions",
                   "params": {"photos": [{"id": "p1", "image": "breakfast|lunch|dinner", "caption": "breakfast"}],
                              "caption": "short line under the grid"},
                   "targets": ["<photo ids>", "<photo id>_c", "caption"]},
})
CATALOGUE["flow"]["params"]["cols"] = 3
COMMON = {"title": "short heading (top-left)", "footer": "small source line at the bottom",
          "chip": "show|none: lunch kcal chip in the top-right corner (default show)"}


OWN_TITLE = {"paper"}  # templates that draw "title" themselves


def build(name: str, P: dict, ctx: dict) -> list[Element]:
    if name not in TEMPLATES:
        raise ValueError(f"unknown template {name!r}; one of {sorted(TEMPLATES)}")
    shared = {k: v for k, v in P.items() if not (k == "title" and name in OWN_TITLE and P.get("venue"))}
    return TEMPLATES[name](P, ctx) + common(shared, ctx)


def catalogue_text() -> str:
    lines = []
    for k, v in CATALOGUE.items():
        lines.append(f"## {k}: {v['use']}\nparams example: {json.dumps(v['params'], ensure_ascii=False)}\n"
                     f"cue targets: {', '.join(v['targets'])}")
    lines.append(f"## every template also takes: {json.dumps(COMMON)}")
    return "\n\n".join(lines)
