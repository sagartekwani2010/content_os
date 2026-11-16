"""Build a beat's scene from the spec: template elements + the corner chip (plate thread), and
validate a spec (templates exist, cue targets exist, every drawn number is sourced)."""

from __future__ import annotations

import skia

from . import rough as R
from . import templates as T
from .cues import resolve_beat
from .elements import Custom, Element
from .facts import FACTS, number_problems

W, H = T.W, T.H
NUMERIC_KEYS = {"value", "ci", "from", "to", "lo", "hi", "mid", "n", "k", "count", "shown"}
__all__ = ["FACTS", "build", "chip", "validate_spec"]


def chip(P: dict) -> Element:
    """Small corner chip with the creator's lunch calories (the plate thread across the reel)."""
    f = FACTS.get("lunch_kcal")
    text = f"{f.display} kcal" if f else "? kcal"
    x1, y0, h = 1020, 200, 56

    def fn(c, p, alpha, t):
        w = R.text_width(text, 38) + 96
        x0 = x1 - w
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, w, h), h / 2, h / 2)
        c.drawRRect(rr, R.fill_paint("#FFFFFF", 0.92 * alpha))
        c.drawRRect(rr, R.stroke_paint(R.INK, 4, alpha))
        c.drawCircle(x0 + 36, y0 + h / 2, 17, R.stroke_paint(R.INK, 3.5, alpha))
        c.drawCircle(x0 + 36, y0 + h / 2, 9, R.fill_paint(R.ORANGE, 0.8 * alpha))
        R.draw_text(c, text, x0 + 64, y0 + h / 2 + 13, 38, R.INK, alpha=alpha)

    return Custom("chip", (x1 - 250, y0, 250, h), fn, appear="pop")


def build(beat: dict, ctx: dict) -> list[Element]:
    P = beat.get("params", {})
    els = T.build(beat["template"], P, ctx)
    if P.get("chip", "show") != "none":
        els.append(chip(P))
    return els


def _walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")
    else:
        yield path, obj


def number_errors(beat: dict) -> list[str]:
    """Numbers must be "@fact" refs (numeric keys) or {fact} placeholders / spoken digits (text)."""
    errs = []
    line = beat.get("line", "")
    for path, v in _walk(beat.get("params", {})):
        key = path.split(".")[-1].split("[")[0]
        if key in NUMERIC_KEYS:
            if isinstance(v, str) and v.startswith("@"):
                if v[1:] not in FACTS:
                    errs.append(f"{path}: unknown fact {v}")
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                errs.append(f"{path}: number {v} must be a fact reference like \"@table_mae\"")
        elif isinstance(v, str):
            for n in number_problems(v, line):
                errs.append(f"{path}: {n!r} in {v!r} is neither a {{fact}} nor spoken in the line")
    return errs


def validate_spec(sheet: dict, ctx: dict) -> list[str]:
    """Everything a render would trip over, as messages (empty = OK)."""
    errs = []
    for b in sheet.get("beats", []):
        tag = f"beat {b.get('beat')}"
        if not b.get("line"):
            errs.append(f"{tag}: no line for this beat in the teleprompter")
            continue
        if b.get("template") not in T.TEMPLATES:
            errs.append(f"{tag}: unknown template {b.get('template')!r}")
            continue
        errs += [f"{tag}: {e}" for e in number_errors(b)]
        try:
            els = build(b, ctx)
            resolved, _ = resolve_beat(b["line"], b.get("cues", []), [], 6.0)
        except (ValueError, KeyError, TypeError) as e:
            errs.append(f"{tag}: {e}")
            continue
        ids = {e.id for e in els}
        for r in resolved:
            if r.target not in ids:
                errs.append(f"{tag}: cue target {r.target!r} not in template {b['template']} (has {sorted(ids)})")
    return errs
