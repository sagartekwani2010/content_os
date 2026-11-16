"""Phrase-level burned captions (2-4 words per chunk) from the selected words, as an ASS file."""

from __future__ import annotations

import re

from .layouts import Layout

_PUNCT_END = re.compile(r"[.,?!;:]$")


def chunk_words(segments: list[dict], ccfg: dict) -> list[dict]:
    chunks: list[dict] = []
    for seg in segments:
        words = seg["words"]
        cur: list[dict] = []
        for i, w in enumerate(words):
            cur.append(w)
            text = " ".join(x["text"] for x in cur)
            nxt = words[i + 1] if i + 1 < len(words) else None
            gap = (nxt["start"] - w["end"]) if nxt else 0
            nxt_len = len(text) + 1 + len(nxt["text"]) if nxt else 0
            brk = (nxt is None or len(cur) >= ccfg["max_words"] or nxt_len > ccfg["max_chars"]
                   or gap > 0.4 or (_PUNCT_END.search(w["text"]) and len(cur) >= ccfg["min_words"]))
            if brk:
                chunks.append({"segment": seg["index"], "words": cur})
                cur = []
        # no lone trailing word: merge it back if that stays within max_words, else borrow one word
        if len(chunks) >= 2 and len(chunks[-1]["words"]) == 1 and chunks[-2]["segment"] == seg["index"]:
            prev = chunks[-2]["words"]
            if len(prev) + 1 <= ccfg["max_words"]:
                prev += chunks.pop()["words"]
            elif len(prev) - 1 >= ccfg["min_words"]:
                chunks[-1]["words"].insert(0, prev.pop())
    out = []
    for i, c in enumerate(chunks):
        start = c["words"][0]["start"]
        end = c["words"][-1]["end"] + 0.15
        if i + 1 < len(chunks) and chunks[i + 1]["words"][0]["start"] - c["words"][-1]["end"] < 0.3:
            end = chunks[i + 1]["words"][0]["start"]
        if i + 1 < len(chunks):
            end = min(end, chunks[i + 1]["words"][0]["start"])
        text = " ".join(w["text"] for w in c["words"])
        if ccfg.get("uppercase"):
            text = text.upper()
        out.append({"start": round(start, 3), "end": round(max(end, start + 0.2), 3), "text": text,
                    "segment": c["segment"]})
    return out


def _ass_colour(hex_rgb: str, alpha: int = 0) -> str:
    h = hex_rgb.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def _ts(t: float) -> str:
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", " ")


def write_ass(path, chunks: list[dict], layout: Layout, ccfg: dict) -> None:
    box = layout.caption_box
    margin_l = box.x
    margin_r = layout.width - box.right
    margin_v = layout.height - box.bottom
    style = ",".join(str(v) for v in [
        "Default", ccfg["font_name"], ccfg["font_size"], _ass_colour(ccfg["primary"]), _ass_colour(ccfg["primary"]),
        _ass_colour(ccfg["outline"]), _ass_colour(ccfg["outline"], 0x80), -1 if ccfg["bold"] else 0, 0, 0, 0,
        100, 100, 0, 0, 1, ccfg["outline_px"], ccfg["shadow_px"], 2, margin_l, margin_r, margin_v, 1])
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {layout.width}", f"PlayResY: {layout.height}",
        "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding",
        f"Style: {style}", "",
        "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for c in chunks:
        lines.append(f"Dialogue: 0,{_ts(c['start'])},{_ts(c['end'])},Default,,0,0,0,,{_escape(c['text'])}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
