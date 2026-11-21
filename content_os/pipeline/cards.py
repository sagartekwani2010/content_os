"""Full-frame section transition cards (cue sheet ``section_cards``), in the Gym Jarvis look.

A card covers the whole 1080x1920 frame (speaker panel included) for ~0.7 s from just before its
beat's first frame: dark navy with a faint grid, thin cyan corner brackets and a glow rule, a small
grey-blue kicker, a huge bold condensed uppercase title (white, last line in the accent colour; a
one-line title puts the accent on the kicker and the underline instead), an underline and an optional accent sub line. Motion: content punches in 1.12 -> 1.0 over 5
frames (ease-out), holds, then fades out over 4 frames while drifting up. The voice is untouched;
the card only sits over the picture.

``{"section_cards": [{"beat": 3, "title": "THE RESEARCH", "sub": "...", "dur": 0.7, "accent": "cyan",
                      "kicker": "optional", "lead": 0.05}]}``
Without ``kicker``, a leading "THE" or the text before ":" becomes the kicker.
Font: Barlow Condensed (SIL OFL 1.1) in ``~/.cache/content_os/fonts`` (``python -m content_os.pipeline setup``).
"""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

from .config import CACHE_DIR
from .cue import beat_windows
from .reel import StageError

FONT_DIR = CACHE_DIR / "fonts"
FONT_BOLD = "BarlowCondensed-ExtraBold.ttf"
FONT_SEMI = "BarlowCondensed-SemiBold.ttf"

BG = (9, 13, 22)
GRID = (20, 28, 42)
WHITE = (244, 246, 248)
KICKER = (141, 160, 184)
ACCENTS = {"cyan": (63, 193, 217), "yellow": (247, 181, 59), "white": WHITE}

PUNCH_FRAMES = 5
PUNCH_FROM = 1.12
OUT_FRAMES = 4


def font_file(name: str) -> Path:
    p = FONT_DIR / name
    if not p.exists():
        raise StageError(f"{p} missing: run `python -m content_os.pipeline setup` (Barlow Condensed, SIL OFL 1.1)")
    return p


@lru_cache(maxsize=None)
def _font(name: str, size: int):
    from PIL import ImageFont

    return ImageFont.truetype(str(font_file(name)), size)


def _rgb(c) -> tuple[int, int, int]:
    if isinstance(c, (list, tuple)):
        return tuple(int(v) for v in c[:3])
    if c in ACCENTS:
        return ACCENTS[c]
    c = str(c).lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def split_title(spec: dict) -> tuple[str, list[str]]:
    """(kicker, title lines). Explicit ``kicker`` wins; else "NEXT UP: X" -> ("NEXT UP", X) and
    "THE X" -> ("THE", X). Two-or-more-word titles go on two lines (the last word on its own)."""
    title = str(spec["title"]).upper().strip()
    kicker = str(spec.get("kicker", "")).upper().strip()
    if not kicker:
        if ":" in title:
            kicker, title = (s.strip() for s in title.split(":", 1))
        elif title.startswith("THE ") and len(title.split()) > 1:
            kicker, title = "THE", title[4:].strip()
    if "\n" in title:
        lines = [x.strip() for x in title.split("\n") if x.strip()]
    else:
        words = title.split()
        lines = [" ".join(words[:-1]), words[-1]] if len(words) > 1 else words
    return kicker, lines


def plan(cuts: dict, cue: dict | None) -> list[dict]:
    """Frame-exact card windows on the output timeline."""
    fps = cuts["fps"]
    total = int(round(cuts["duration"] * fps))
    windows = beat_windows(cuts)
    out = []
    for c in (cue or {}).get("section_cards", []) or []:
        beat = int(c["beat"])
        if beat not in windows:
            raise StageError(f"section card for beat {beat}: no such beat in cuts.json")
        start = max(0, int(round((windows[beat][0] - float(c.get("lead", 0.05))) * fps)))
        frames = max(PUNCH_FRAMES + OUT_FRAMES + 1, int(round(float(c.get("dur", 0.7)) * fps)))
        frames = min(frames, total - start)
        out.append({**c, "beat": beat, "start_frame": start, "frames": frames, "start": round(start / fps, 4)})
    out.sort(key=lambda x: x["start_frame"])
    for a, b in zip(out, out[1:]):
        if a["start_frame"] + a["frames"] > b["start_frame"]:
            raise StageError(f"section cards for beats {a['beat']} and {b['beat']} overlap")
    return out


def _background(W: int, H: int):
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    step = 72
    for x in range(step // 2, W, step):
        d.line([(x, 0), (x, H)], fill=GRID, width=1)
    for y in range(step // 2, H, step):
        d.line([(0, y), (W, y)], fill=GRID, width=1)
    return img


def _content(spec: dict, W: int, H: int):
    """Transparent layer with everything that punches in (text, brackets, rules)."""
    from PIL import Image, ImageDraw, ImageFilter

    accent = _rgb(spec.get("accent", "cyan"))
    kicker, lines = split_title(spec)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # glow rules: one high on the left, one low on the right (as in the reference)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.rectangle([0, 262, int(W * 0.62), 270], fill=(*ACCENTS["cyan"], 150))
    g.rectangle([int(W * 0.38), H - 470, W, H - 464], fill=(*ACCENTS["cyan"], 120))
    layer = Image.alpha_composite(layer, glow.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(layer)
    d.rectangle([0, 265, int(W * 0.62), 267], fill=(*ACCENTS["cyan"], 220))
    d.rectangle([int(W * 0.38), H - 468, W, H - 466], fill=(*ACCENTS["cyan"], 200))
    # corner brackets
    arm, t, m = 92, 5, 96
    top, bot = 380, H - 560
    cy = ACCENTS["cyan"]
    d.rectangle([m, top, m + arm, top + t], fill=cy)
    d.rectangle([m, top, m + t, top + arm], fill=cy)
    d.rectangle([W - m - arm, bot - t, W - m, bot], fill=cy)
    d.rectangle([W - m - t, bot - arm, W - m, bot], fill=cy)

    # text block, centred between the brackets
    max_w = W - 2 * (m + 40)
    size = 300
    while size > 120 and max(_font(FONT_BOLD, size).getlength(x) for x in lines) > max_w:
        size -= 6
    big = _font(FONT_BOLD, size)
    kf = _font(FONT_SEMI, 84)
    sf = _font(FONT_SEMI, 76)
    line_h = int(size * 0.98)
    blocks = []  # (text, font, colour, height, gap_after)
    single = len(lines) == 1  # one-line title: the kicker and the rule carry the accent
    if kicker:
        blocks.append((kicker, kf, accent if single else KICKER, 84, 26))
    for i, ln in enumerate(lines):
        colour = accent if (len(lines) > 1 and i == len(lines) - 1) else WHITE
        blocks.append((ln, big, colour, line_h, 0))
    rule_gap, rule_h = 30, 9
    sub = str(spec.get("sub", "")).upper().strip()
    total_h = sum(b[3] + b[4] for b in blocks) + rule_gap + rule_h + (40 + 76 if sub else 0)
    y = (top + bot) / 2 - total_h / 2
    widest = 0.0
    for text, f, colour, h, gap in blocks:
        w = f.getlength(text)
        widest = max(widest, w) if f is big else widest
        d.text((W / 2, y + h / 2), text, font=f, fill=(*colour, 255), anchor="mm")
        y += h + gap
    y += rule_gap
    # two-line title: the rule takes the other accent (Gym Jarvis: JARVIS cyan / rule yellow)
    rule_col = accent if single else (ACCENTS["cyan"] if accent == ACCENTS["yellow"] else ACCENTS["yellow"])
    rw = widest * 0.92
    d.rectangle([W / 2 - rw / 2, y, W / 2 + rw / 2, y + rule_h], fill=(*rule_col, 255))
    y += rule_h
    if sub:
        y += 40
        d.text((W / 2, y + 38), sub, font=sf, fill=(*accent, 255), anchor="mm")
    return layer


def ease_scale(i: int) -> float:
    """Punch-in scale for frame i: 1.12 at frame 0, 1.0 from frame 5 (quadratic ease-out)."""
    if i >= PUNCH_FRAMES:
        return 1.0
    return 1.0 + (PUNCH_FROM - 1.0) * (1 - i / PUNCH_FRAMES) ** 2


def frame_alpha(i: int, n: int) -> float:
    """Card opacity: 1 until the last OUT_FRAMES frames, then 0.8, 0.6, 0.4, 0.2."""
    k = i - (n - OUT_FRAMES)
    return 1.0 if k < 0 else 1.0 - (k + 1) / (OUT_FRAMES + 1)


def render_frames(spec: dict, n: int, W: int, H: int, out_dir: Path, prefix: str = "card") -> list[Path]:
    """n RGBA PNG frames ``<prefix>_000.png`` ... for one card."""
    from PIL import Image

    out_dir.mkdir(parents=True, exist_ok=True)
    bg = _background(W, H).convert("RGBA")
    content = _content(spec, W, H)
    paths = []
    for i in range(n):
        s = ease_scale(i)
        k = i - (n - OUT_FRAMES)
        drift = -10 * (k + 1) if k >= 0 else 0
        if s != 1.0:
            cw, ch = int(round(W * s)), int(round(H * s))
            big = content.resize((cw, ch), Image.LANCZOS)
            x0, y0 = (cw - W) // 2, (ch - H) // 2 - drift
            layer = big.crop((x0, y0, x0 + W, y0 + H))
        elif drift:
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            layer.paste(content, (0, drift))
        else:
            layer = content
        frame = Image.alpha_composite(bg, layer)
        a = frame_alpha(i, n)
        if a < 1.0:
            frame.putalpha(int(round(255 * a)))
        p = out_dir / f"{prefix}_{i:03d}.png"
        frame.save(p, compress_level=1)
        paths.append(p)
    return paths


def build(cuts: dict, cue: dict | None, W: int, H: int, rdir: Path, first_input: int, last: str
          ) -> tuple[list[str], list[str], str, list[dict]]:
    """Render every card's frames into ``rdir/cards`` and return (ffmpeg input args relative to rdir,
    filtergraph lines overlaying them on ``last``, the new last label, the plan)."""
    fps = cuts["fps"]
    items = plan(cuts, cue)
    args: list[str] = []
    fg: list[str] = []
    for n, c in enumerate(items):
        prefix = f"b{c['beat']:02d}"
        render_frames(c, c["frames"], W, H, rdir / "cards", prefix)
        k = first_input + n
        args += ["-framerate", str(fps), "-start_number", "0", "-i", f"cards/{prefix}_%03d.png"]
        fg.append(f"[{k}:v]format=rgba,setpts=PTS-STARTPTS+{c['start_frame']}/({fps}*TB)[card{n}]")
        fg.append(f"{last}[card{n}]overlay=eof_action=pass:repeatlast=0:format=auto[co{n}]")
        last = f"[co{n}]"
    return args, fg, last, items
