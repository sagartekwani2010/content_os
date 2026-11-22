"""Carousel slide items: wrapped text, sticky notes, quote cards, recipe cards, photos and line-art icons.

Every item is a ``content_os.visuals.elements.Element`` so it animates with the same cues as the reel visuals
(draw / write / fade). Items with no ``at`` are visible from frame 0. Each built item also reports the text it
draws (size and box) so QA can check sizes, margins and the Instagram UI zone.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import skia

from content_os.visuals import rough as R
from content_os.visuals.doodles import check_strokes, load_image, xmark_strokes
from content_os.visuals.elements import Custom, Cue, Doodle, Element, Picture, arrow, clamp
from content_os.visuals.palette import NAMED

NOTE = NAMED["note"]


def col(c: str | None, default: str = R.INK) -> str:
    if not c:
        return default
    return NAMED.get(c, c)


@dataclass
class TextBox:
    item: str
    text: str
    size: float
    box: tuple[float, float, float, float]  # x, y, w, h
    exempt: bool = False  # decorative (page counter): not held to the 40 px rule


# ------------------------------------------------------------------ text

def marker(x0: float, x1: float, baseline: float, size: float, key: str) -> R.Stroke:
    """Yellow highlighter band behind text from x0 to x1. The stroke has round caps half its width wide, so the
    end points are pulled in by that much (minus a little overhang) to keep the band on the highlighted words."""
    width = size * 0.62
    cap = width * R.STROKE_SCALE / 2 - 6
    return R.Stroke([(x0 + cap, baseline - size * 0.28), (max(x0 + cap + 1, x1 - cap), baseline - size * 0.31)],
                    R.YELLOW, width, key, amp=1.5, double=False, alpha=0.8, closed=True)


def wrap(text: str, size: float, width: float, weight: str = "bold") -> list[str]:
    """Greedy word wrap; explicit newlines are kept."""
    out: list[str] = []
    for para in text.split("\n"):
        line = ""
        for w in para.split():
            trial = f"{line} {w}".strip()
            if line and R.text_width(trial, size, weight) > width:
                out.append(line)
                line = w
            else:
                line = trial
        out.append(line)
    return out


def text_block(id: str, text: str, x: float, y: float, w: float, size: float = 44, color: str = R.INK,
               weight: str = "regular", align: str = "left", lh: float = 1.22, highlight: list[str] | None = None,
               boxes: list | None = None, exempt: bool = False, **kw) -> tuple[Element, float]:
    """Wrapped text with its first baseline at ``y``. Returns the element and the y of the block's bottom.
    ``highlight`` words get the yellow marker band behind them."""
    lines = wrap(text, size, w, weight)
    step = size * lh
    xs = []
    for i, ln in enumerate(lines):
        lw = R.text_width(ln, size, weight)
        x0 = x + (w - lw) / 2 if align == "center" else x
        xs.append(x0)
        if boxes is not None:
            boxes.append(TextBox(id, ln, size, (x0, y + i * step - size * 0.8, lw, size * 1.05), exempt))
    marks = []
    for hw in highlight or []:
        for i, ln in enumerate(lines):
            k = ln.find(hw)
            if k >= 0:
                x0 = xs[i] + R.text_width(ln[:k], size, weight)
                ww = R.text_width(hw, size, weight)
                yy = y + i * step
                marks.append(marker(x0, x0 + ww, yy, size, f"{id}:hl{i}{k}"))

    def fn(c, p, alpha, t):
        R.draw_strokes(c, marks, clamp(p * 1.5), alpha)
        n = len(lines)
        for i, ln in enumerate(lines):
            q = clamp(p * n - i)
            R.draw_text(c, ln, xs[i], y + i * step, size, color, weight=weight, reveal=q, alpha=alpha)

    bottom = y + (len(lines) - 1) * step + size * 0.3
    return Custom(id, (x, y - size, w, bottom - y + size), fn, appear="write", **kw), bottom


# ------------------------------------------------------------------ cards and notes

def _rot(c, deg, x, y, w, h):
    if deg:
        c.rotate(deg, x + w / 2, y + h / 2)


def sticky(id, x, y, w, lines: list[str], size=42, title=None, color=NOTE, tilt=-1.5, boxes=None, pad=26,
           **kw) -> tuple[Element, float]:
    """Sticky note with a title and wrapped lines; height fits the text. Returns (element, bottom y)."""
    body = [ln for line in lines for ln in wrap(line, size, w - 2 * pad, "regular")]
    tsz = size * 1.08
    h = pad * 2 + (tsz * 1.2 if title else 0) + len(body) * size * 1.2
    yy = y + pad + (tsz if title else size)
    texts = []
    if title:
        texts.append((title, x + pad, yy, tsz, "bold"))
        yy += tsz * 1.2
    for ln in body:
        texts.append((ln, x + pad, yy, size, "regular"))
        yy += size * 1.2
    if boxes is not None:
        for tx, tx_x, tx_y, s, wt in texts:
            boxes.append(TextBox(id, tx, s, (tx_x, tx_y - s * 0.8, R.text_width(tx, s, wt), s), False))
    edge = R.Stroke(R.rect_pts(x, y, w, h), "#B89B00", 3, f"{id}:edge", closed=True, double=False)

    def fn(c, p, alpha, t):
        a = alpha * clamp(p * 3)
        c.save()
        _rot(c, tilt, x, y, w, h)
        c.drawRect(skia.Rect.MakeXYWH(x + 6, y + 8, w, h), R.fill_paint(R.INK, 0.12 * a))
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), R.fill_paint(color, a))
        edge.draw(c, 1.0, a * 0.6)
        n = len(texts)
        for i, (tx, tx_x, tx_y, s, wt) in enumerate(texts):
            R.draw_text(c, tx, tx_x, tx_y, s, NAMED["noteink"], weight=wt, reveal=clamp((p - 0.2) * 1.25 * n - i),
                        alpha=alpha)
        c.restore()

    return Custom(id, (x, y, w, h), fn, appear="draw", **kw), y + h


def quote_card(id, x, y, w, lines: list[str], tag: str | None = None, size=40, boxes=None, hl: list[str] = (),
               border=R.INK, tilt=0.0, pad=28, title: str | None = None, title_col: str | None = None,
               **kw) -> tuple[Element, float]:
    """White paper card holding verbatim output lines (quoted), with a small grey source tag under it.
    ``title`` (e.g. "BEFORE" / "AFTER") is written in bold in ``title_col`` above the lines, inside the card."""
    wrapped: list[tuple[str, bool]] = []
    for ln in lines:
        for k, piece in enumerate(wrap(ln, size, w - 2 * pad, "digits")):
            wrapped.append((piece, k == 0))
    step = size * 1.22
    tsz = 44
    th = tsz * 1.25 if title else 0
    h = pad * 2 + th + len(wrapped) * step - size * 0.22
    texts = []
    yy = y + pad + th + size * 0.82
    for i, (ln, first) in enumerate(wrapped):
        texts.append((ln, x + pad, yy + i * step))
    if boxes is not None:
        for tx, tx_x, tx_y in texts:
            boxes.append(TextBox(id, tx, size, (tx_x, tx_y - size * 0.8, R.text_width(tx, size, "digits"), size)))
    tag_y = y + h + 46
    if title and boxes is not None:
        boxes.append(TextBox(id, title, tsz, (x + pad, y + pad, R.text_width(title, tsz, "bold"), tsz)))
    if tag and boxes is not None:
        boxes.append(TextBox(id, tag, 40, (x + 6, tag_y - 32, R.text_width(tag, 40, "regular"), 40)))
    frame = R.Stroke(R.rect_pts(x, y, w, h), border, 5, f"{id}:frame", closed=True)
    marks = []
    for word in hl:
        for tx, tx_x, tx_y in texts:
            k = tx.find(word)
            if k >= 0:
                x0 = tx_x + R.text_width(tx[:k], size, "digits")
                ww = R.text_width(word, size, "digits")
                marks.append(marker(x0, x0 + ww, tx_y, size, f"{id}:m{k}{tx_y:.0f}"))
                break

    def fn(c, p, alpha, t):
        c.save()
        _rot(c, tilt, x, y, w, h)
        c.drawRect(skia.Rect.MakeXYWH(x + 7, y + 9, w, h), R.fill_paint(R.INK, 0.10 * alpha * clamp(p * 3)))
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), R.fill_paint("#FFFFFF", alpha * clamp(p * 3)))
        frame.draw(c, clamp(p * 2), alpha)
        R.draw_strokes(c, marks, clamp((p - 0.6) / 0.4), alpha)
        if title:
            R.draw_text(c, title, x + pad, y + pad + tsz * 0.85, tsz, title_col or border, weight="bold",
                        alpha=alpha * clamp(p * 3))
        n = len(texts)
        for i, (tx, tx_x, tx_y) in enumerate(texts):
            R.draw_text(c, tx, tx_x, tx_y, size, R.INK, weight="digits", reveal=clamp((p - 0.15) * 1.3 * n - i),
                        alpha=alpha)
        if tag:
            R.draw_text(c, tag, x + 6, tag_y, 40, R.GREY, weight="regular", alpha=alpha * clamp((p - 0.7) / 0.3))
        c.restore()

    return Custom(id, (x, y, w, h), fn, appear="draw", **kw), (tag_y + 12 if tag else y + h)


def recipe_card(id, x, y, w, rows: list[dict], size=44, boxes=None, static_frame=False, **kw) -> tuple[Element, float]:
    """Ruled index card: per row a highlighted label, its meaning, and an optional grey example line."""
    pad = 34
    lines = []  # (text, x, y, size, weight, color, highlight)
    yy = y + 56 + size
    for r in rows:
        lab = r["label"] + ":"
        lw = R.text_width(lab, size, "bold")
        lines.append((lab, x + pad, yy, size, "bold", R.INK, True))
        mean = wrap(r.get("text", ""), size, w - 2 * pad - lw - 16, "regular")
        for k, m in enumerate(mean):
            lines.append((m, x + pad + lw + 16, yy + k * size * 1.15, size, "regular", R.INK, False))
        yy += max(1, len(mean)) * size * 1.15
        if r.get("eg"):
            for eg in wrap(r["eg"], 40, w - 2 * pad - 30, "regular"):
                lines.append((eg, x + pad + 30, yy, 40, "regular", r.get("eg_color", R.GREY), False))
                yy += 40 * 1.15
        yy += size * 0.55
    h = yy - y - size * 0.2
    if boxes is not None:
        for tx, tx_x, tx_y, s, wt, *_ in lines:
            boxes.append(TextBox(id, tx, s, (tx_x, tx_y - s * 0.8, R.text_width(tx, s, wt), s)))
    frame = R.Stroke(R.rect_pts(x, y, w, h), R.INK, 6, f"{id}:frame", closed=True)
    rules = [R.Stroke([(x + 20, ty + 16), (x + w - 20, ty + 16)], "#9EC5F0", 2, f"{id}:r{i}", double=False, amp=1)
             for i, (_, _, ty, s, wt, _, hl) in enumerate(lines) if hl]
    hole = R.Stroke(R.ellipse_pts(x + w / 2, y + 26, 13, 13, start=0, sweep=6.4), R.INK, 4, f"{id}:hole")
    marks = [marker(tx_x, tx_x + R.text_width(tx, s, wt), ty, s, f"{id}:hl{i}")
             for i, (tx, tx_x, ty, s, wt, _, hl) in enumerate(lines) if hl]

    def fn(c, p, alpha, t):
        pf = 1.0 if static_frame else clamp(p * 3)
        c.drawRect(skia.Rect.MakeXYWH(x + 8, y + 10, w, h), R.fill_paint(R.INK, 0.10 * alpha * pf))
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), R.fill_paint("#FFFFFF", alpha * pf))
        frame.draw(c, 1.0 if static_frame else clamp(p * 2), alpha)
        hole.draw(c, 1.0 if static_frame else clamp(p * 2), alpha)
        R.draw_strokes(c, rules, 1.0 if static_frame else clamp(p * 2), alpha * 0.8)
        R.draw_strokes(c, marks, clamp((p - 0.3) / 0.5), alpha)
        n = len(lines)
        for i, (tx, tx_x, ty, s, wt, cl, _) in enumerate(lines):
            R.draw_text(c, tx, tx_x, ty, s, cl, weight=wt, reveal=clamp((p - 0.1) * 1.2 * n - i), alpha=alpha)

    el = Custom(id, (x, y, w, h), fn, appear="draw", **kw)
    if static_frame:  # the empty card is on screen from frame 0; only the rows write on
        el.render_before = True
    return el, y + h


def photo(id, path, rect, tilt=-3.0, caption=None, boxes=None, **kw) -> tuple[Element, float]:
    """Polaroid on paper with two strips of tape. ``caption`` is handwritten on the white strip."""
    img = load_image(path)
    if img is None:
        raise FileNotFoundError(f"photo missing: {path}")
    x, y, w, h = rect
    pic = Picture(id + "_pic", img, rect, polaroid=True, tilt=tilt, radius=4)
    tape = [(x + w * 0.12, y - 30, 150, 46, -14), (x + w * 0.88 - 150, y - 30, 150, 46, 12)]
    if caption and boxes is not None:
        boxes.append(TextBox(id, caption, 44, (x, y + h + 10, R.text_width(caption, 44, "bold"), 44)))

    def fn(c, p, alpha, t):
        pic.paint(c, 1.0, alpha * clamp(p * 2), t)
        c.save()
        c.rotate(tilt, x + w / 2, y + h / 2)
        if caption:
            R.draw_text(c, caption, x + w / 2, y + h + 44, 44, R.INK, align="center", alpha=alpha * clamp(p * 2))
        for tx, ty, tw, th, rot in tape:
            c.save()
            c.rotate(rot, tx + tw / 2, ty + th / 2)
            c.drawRect(skia.Rect.MakeXYWH(tx, ty, tw, th), R.fill_paint("#F2E6B8", 0.85 * alpha * clamp(p * 2)))
            c.restore()
        c.restore()

    return Custom(id, rect, fn, appear="fade", **kw), y + h + 60


# ------------------------------------------------------------------ icons (line art, centred at cx, cy, scale s)

def _circ(cx, cy, r, ry=None, start=-2.0, sweep=6.6):
    return R.ellipse_pts(cx, cy, r, ry or r, start=start, sweep=sweep)


def _rect(x, y, w, h):
    return R.rect_pts(x, y, w, h)


def icon_strokes(name: str, cx: float, cy: float, s: float, color: str, key: str):
    """Point lists for a small library of kitchen/AI doodles. Returns (strokes, fills)."""
    S = lambda v: v * s  # noqa: E731
    st, fills = [], []

    def add(pts, c=color, wd=6, closed=False):
        st.append(R.Stroke(pts, c, wd, f"{key}:{len(st)}", closed=closed))

    if name == "chicken":
        meat = _circ(cx - S(20), cy - S(18), S(62), S(48), start=0.6, sweep=5.2)
        add(meat, R.ORANGE)
        add([(cx + S(20), cy + S(12)), (cx + S(70), cy + S(52))], R.INK)
        add(_circ(cx + S(78), cy + S(48), S(14)), R.INK)
        add(_circ(cx + S(66), cy + S(64), S(14)), R.INK)
        fills.append((_circ(cx - S(20), cy - S(18), S(58), S(44), start=0, sweep=6.28), R.ORANGE, {"tint": 0.3}))
    elif name == "oven":
        add(_rect(cx - S(90), cy - S(80), S(180), S(160)), color, closed=True)
        add(_rect(cx - S(66), cy - S(30), S(132), S(90)), color, 5, closed=True)
        add([(cx - S(50), cy - S(52)), (cx + S(50), cy - S(52))], color, 5)
        for dx in (-60, -30, 30, 60):
            add(_circ(cx + S(dx), cy - S(64), S(7)), color, 4)
    elif name == "bowl":
        add(_circ(cx, cy - S(10), S(110), S(26), start=0, sweep=6.4), R.INK)
        add(_circ(cx, cy - S(10), S(110), S(90), start=0.05, sweep=3.04), R.INK)
        for i, dx in enumerate((-50, -10, 34)):
            add(_rect(cx + S(dx), cy - S(30 + 6 * (i % 2)), S(26), S(22)), R.ORANGE, 4, closed=True)
        add(_circ(cx + S(70), cy - S(24), S(14), S(8)), R.GREEN, 4)
        for dx in (-40, 0, 40):
            add([(cx + S(dx), cy - S(56)), (cx + S(dx - 12), cy - S(80)), (cx + S(dx + 6), cy - S(104)),
                 (cx + S(dx - 6), cy - S(126))], R.GREY, 4)
        fills.append((_circ(cx, cy - S(10), S(104), S(22), start=0, sweep=6.28), R.YELLOW, {"tint": 0.4}))
    elif name == "robot":
        add(_rect(cx - S(60), cy - S(120), S(120), S(90)), R.BLUE, closed=True)
        add([(cx, cy - S(120)), (cx, cy - S(150))], R.BLUE, 5)
        add(_circ(cx, cy - S(158), S(9)), R.BLUE, 5)
        add(_circ(cx - S(25), cy - S(80), S(11)), R.INK, 5)
        add(_circ(cx + S(25), cy - S(80), S(11)), R.INK, 5)
        add([(cx - S(22), cy - S(50)), (cx + S(22), cy - S(50))], R.INK, 5)
        add(_rect(cx - S(50), cy - S(20), S(100), S(110)), R.BLUE, closed=True)
        add([(cx - S(50), cy + S(10)), (cx - S(100), cy + S(40))], R.BLUE, 5)
        add([(cx + S(50), cy + S(10)), (cx + S(100), cy + S(40))], R.BLUE, 5)
        add([(cx - S(25), cy + S(90)), (cx - S(25), cy + S(130))], R.BLUE, 5)
        add([(cx + S(25), cy + S(90)), (cx + S(25), cy + S(130))], R.BLUE, 5)
    elif name == "plate":
        add(_circ(cx, cy, S(70), S(20), start=0, sweep=6.4), R.INK, 5)
        add(_circ(cx, cy, S(48), S(12), start=0, sweep=6.4), R.GREY, 3)
    elif name == "people":
        for dx in (-70, 70):
            add(_circ(cx + S(dx), cy - S(80), S(26)), color, 5)
            add([(cx + S(dx), cy - S(54)), (cx + S(dx), cy + S(20))], color, 5)
            add([(cx + S(dx - 34), cy - S(20)), (cx + S(dx + 34), cy - S(20))], color, 5)
            add([(cx + S(dx), cy + S(20)), (cx + S(dx - 24), cy + S(70))], color, 5)
            add([(cx + S(dx), cy + S(20)), (cx + S(dx + 24), cy + S(70))], color, 5)
        add([(cx - S(40), cy + S(6)), (cx + S(40), cy + S(6))], R.INK, 6)
        add([(cx, cy + S(6)), (cx, cy + S(60))], R.INK, 5)
    elif name == "shelf":
        add([(cx - S(130), cy + S(70)), (cx + S(130), cy + S(70))], R.INK, 6)
        add(_rect(cx - S(115), cy + S(10), S(70), S(56)), R.INK, 5, closed=True)  # paneer block
        fills.append((_rect(cx - S(111), cy + S(14), S(62), S(48))[:4], "#FFFFFF", {"tint": 0.5}))
        add(_rect(cx - S(25), cy - S(40), S(56), S(106)), R.ORANGE, 5, closed=True)  # dal jar
        add([(cx - S(25), cy - S(18)), (cx + S(31), cy - S(18))], R.ORANGE, 4)
        fills.append((_rect(cx - S(21), cy + S(4), S(48), S(58))[:4], R.YELLOW, {"tint": 0.45}))
        add(_circ(cx + S(90), cy + S(36), S(38), S(26), start=0, sweep=6.4), R.GREEN, 5)  # spinach leaf
        add([(cx + S(56), cy + S(40)), (cx + S(124), cy + S(30))], R.GREEN, 3)
    elif name == "spoon":
        add(_circ(cx - S(40), cy + S(40), S(36), S(24), start=0, sweep=6.4), R.INK, 5)
        add([(cx - S(10), cy + S(22)), (cx + S(90), cy - S(70))], R.INK, 7)
    elif name == "pot":
        add(_rect(cx - S(90), cy - S(40), S(180), S(110)), R.INK, closed=True)
        add([(cx - S(110), cy - S(40)), (cx + S(110), cy - S(40))], R.INK, 6)
        add([(cx - S(90), cy - S(10)), (cx - S(120), cy - S(10))], R.INK, 6)
        add([(cx + S(90), cy - S(10)), (cx + S(120), cy - S(10))], R.INK, 6)
        fills.append((_rect(cx - S(86), cy - S(36), S(172), S(102))[:4], R.ORANGE, {"tint": 0.25}))
    elif name == "kadhai":
        add(_circ(cx, cy - S(20), S(80), S(60), start=0.05, sweep=3.04), R.INK)
        add([(cx - S(80), cy - S(20)), (cx + S(80), cy - S(20))], R.INK)
        add(_circ(cx - S(96), cy - S(26), S(16), S(10)), R.INK, 4)
        add(_circ(cx + S(96), cy - S(26), S(16), S(10)), R.INK, 4)
        for dx in (-30, 0, 30):
            add(_circ(cx + S(dx), cy - S(44), S(6)), R.ORANGE, 4)
    elif name == "cream":
        add([(cx - S(40), cy + S(60)), (cx - S(40), cy - S(30)), (cx, cy - S(70)), (cx + S(40), cy - S(30)),
             (cx + S(40), cy + S(60)), (cx - S(40), cy + S(60))], R.INK, 5, closed=True)
        add([(cx - S(40), cy - S(30)), (cx + S(40), cy - S(30))], R.INK, 4)
    elif name == "clock":
        add(_circ(cx, cy, S(60)), R.INK, 5)
        add([(cx, cy), (cx, cy - S(42))], R.INK, 5)
        add([(cx, cy), (cx + S(30), cy + S(12))], R.INK, 5)
    elif name == "comment":
        add(_rect(cx - S(170), cy - S(70), S(340), S(120)), R.INK, closed=True)
        add([(cx - S(110), cy + S(50)), (cx - S(140), cy + S(100)), (cx - S(60), cy + S(50))], R.INK)
    elif name == "envelope":
        add(_rect(cx - S(110), cy - S(70), S(220), S(140)), R.INK, closed=True)
        add([(cx - S(110), cy - S(70)), (cx, cy + S(10)), (cx + S(110), cy - S(70))], R.INK, 5)
    elif name == "door":
        add(_rect(cx - S(100), cy - S(190), S(200), S(380)), R.INK, closed=True)
        add(_rect(cx - S(120), cy - S(210), S(240), S(400)), R.GREY, 4, closed=True)
        add(_circ(cx + S(70), cy + S(10), S(9)), R.INK, 5)
    elif name == "diary":
        add(_rect(cx - S(160), cy - S(110), S(320), S(220)), R.INK, closed=True)
        for i in range(4):
            add([(cx - S(130), cy - S(50) + S(44) * i), (cx + S(130), cy - S(50) + S(44) * i)], "#9EC5F0", 2)
        fills.append((_circ(cx + S(110), cy + S(70), S(30), S(22), start=0, sweep=6.28), R.YELLOW, {"tint": 0.5}))
    elif name == "chat":
        add(_rect(cx - S(90), cy - S(60), S(180), S(110)), R.BLUE, closed=True)
        add([(cx + S(30), cy + S(50)), (cx + S(60), cy + S(90)), (cx + S(70), cy + S(50))], R.BLUE)
    elif name == "check":
        st += check_strokes(cx - S(30), cy, S(60), R.GREEN, key)
    elif name == "cross":
        st += xmark_strokes(cx - S(30), cy, S(60), R.RED, key)
    elif name == "list":
        for i in range(3):
            yy = cy - S(70) + S(70) * i
            add(_circ(cx - S(120), yy, S(18)), R.BLUE, 4)
            add([(cx - S(80), yy), (cx + S(40), yy)], R.INK, 5)
    else:
        raise ValueError(f"unknown icon {name!r}")
    return st, fills


def icon(id, name, cx, cy, s=1.0, color=None, **kw) -> Doodle:
    st, fills = icon_strokes(name, cx, cy, s, col(color), id)
    return Doodle(id, strokes=st, fills=fills, **kw)


def ring(id, rect, color="red", pad=16, **kw) -> Doodle:
    x, y, w, h = rect
    return Doodle(id, strokes=[R.Stroke(R.ellipse_pts(x + w / 2, y + h / 2, w / 2 + pad, h / 2 + pad, start=-2.4,
                                                       sweep=6.9), col(color, R.RED), 6, f"{id}:ring")], **kw)


def line_arrow(id, p0, p1, color=None, bend=0.0, **kw) -> Doodle:
    return arrow(id, tuple(p0), tuple(p1), col(color), 6, bend, **kw)


def animate(el: Element, at: float | None, dur: float | None, action: str | None = None) -> Element:
    """Give an element its appearance cue (``at`` None = visible from frame 0)."""
    if at is not None:
        el.cues.append(Cue(action or el.appear, float(at), float(dur or 0.8)))
    return el
