"""Render one beat: build its scene, attach resolved cues, draw every frame with skia, pipe RGBA to
ffmpeg (libx264, yuv420p, BT.709 tagged, 1080x960, 30 fps). Deterministic and offline."""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

import numpy as np
import skia

from content_os.pipeline import media

from . import rough as R
from . import scenes
from .cues import DEFAULT_OFFSET, resolve_beat
from .elements import Cue, Element, clamp, ease_out
from .templates import col

W, H, FPS = scenes.W, scenes.H, 30


def attach(elements: list[Element], resolved) -> list[str]:
    """Attach resolved cues to their elements; returns unknown target names."""
    by_id = {e.id: e for e in elements}
    missing = []
    for r in resolved:
        el = by_id.get(r.target)
        if el is None:
            missing.append(r.target)
            continue
        el.cues.append(Cue(r.action, r.t, r.dur, r.emphasis, r.params or {}))
    for el in elements:
        countups = sorted((c for c in el.cues if c.action == "countup"), key=lambda c: c.t)
        if hasattr(el, "_chip_state") and countups:
            el._chip_state["switch"] = countups[0]
        if hasattr(el, "_gauge_state") and countups:
            el._gauge_state["cue"] = countups[0]
        if hasattr(el, "_search_state") and countups:
            el._search_state["search"] = countups[0]
    return missing


class Scene:
    """One scene of a beat: its elements, resolved cues and the time it takes over the panel."""

    def __init__(self, spec: dict, line: str, ctx: dict, words, duration: float, start: float, index: int):
        self.spec, self.start, self.index = spec, start, index
        self.resolved, self.report = resolve_beat(line, spec.get("cues", []), words or [], duration)
        for r in self.resolved:
            r.scene = index
        self.elements = scenes.build(spec, ctx)
        missing = attach(self.elements, self.resolved)
        if missing:
            raise ValueError(f"scene {index}: cue targets not in scene: {sorted(set(missing))}")
        self.transition = SceneTransition((spec.get("transition") or {}) if index else {"kind": "none"})

    def paint(self, c: skia.Canvas, bg: skia.Image, t: float) -> None:
        c.drawImage(bg, 0, 0)
        for el in sorted(self.elements, key=lambda e: e.z):
            el.render(c, t)


class BeatRenderer:
    """A beat = one or more scenes. Scene 0 is the beat's own template/params/cues; ``"scenes": [{"on_word",
    "offset", "transition": {"kind": "slide|zoom|wipe|cut"}, "template", "params", "cues"}]`` add scenes that
    take over the panel on a word (policy: big concept first, then the detailed diagram)."""

    def __init__(self, beat: dict, ctx: dict, words: list[dict] | None, duration: float):
        self.beat = beat
        self.duration = duration
        self.scenes = [Scene(beat, beat["line"], ctx, words, duration, 0.0, 0)]
        for k, sp in enumerate(beat.get("scenes", []), start=1):
            sw, _ = resolve_beat(beat["line"], [{"on_word": sp["on_word"], "offset": sp.get("offset", DEFAULT_OFFSET),
                                                 "anchor": sp.get("anchor", "start"), "action": "fade", "target": "_",
                                                 **({"occurrence": sp["occurrence"]} if "occurrence" in sp else {})}],
                                 words or [], duration)
            start = min(sw[0].t, duration - 0.5)
            self.scenes.append(Scene(sp, beat["line"], ctx, words, duration, start, k))
        self.resolved = [r for sc in self.scenes for r in sc.resolved]
        rep = self.scenes[0].report
        self.report = {**rep, "fallbacks": [f for sc in self.scenes for f in sc.report["fallbacks"]],
                       "fit_shifts": [f for sc in self.scenes for f in sc.report["fit_shifts"]],
                       "methods": {m: sum(sc.report["methods"][m] for sc in self.scenes) for m in rep["methods"]},
                       "scene_starts": [round(sc.start, 3) for sc in self.scenes]}
        self.elements = [e for sc in self.scenes for e in sc.elements]
        self.bg = R.paper_background(W, H)
        self.surface = skia.Surface(W, H)
        self.prev = skia.Surface(W, H) if len(self.scenes) > 1 else None
        self.enter = Entrance(beat.get("params", {}).get("enter"))
        self.out = skia.Surface(W, H)

    def scene_at(self, t: float) -> int:
        i = 0
        for k, sc in enumerate(self.scenes):
            if t >= sc.start:
                i = k
        return i

    def frame(self, t: float) -> np.ndarray:
        i = self.scene_at(t)
        sc = self.scenes[i]
        sc.paint(self.surface.getCanvas(), self.bg, t)
        img = self.surface.makeImageSnapshot()
        tr = sc.transition
        if i and tr.kind != "cut" and t < sc.start + tr.dur:
            self.scenes[i - 1].paint(self.prev.getCanvas(), self.bg, t)
            old = self.prev.makeImageSnapshot()
            tr.paint(self.out.getCanvas(), old, img, (t - sc.start) / tr.dur)
            img = self.out.makeImageSnapshot()
        if self.enter.kind != "none" and t < self.enter.dur:
            self.enter.paint(self.out.getCanvas(), img, t)
            img = self.out.makeImageSnapshot()
        return img.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

    def key_time(self) -> float:
        """The moment that best shows the beat: just after the last emphasis cue settles (else the last cue)."""
        if not self.resolved:
            return self.duration * 0.8
        emph = [r for r in self.resolved if r.emphasis]
        last = max(self.resolved, key=lambda r: r.t + r.dur)
        r = max(emph, key=lambda r: r.t) if emph else last
        return min(self.duration - 1 / FPS, max(last.t + last.dur, r.t + r.dur) + 0.25)


class SceneTransition:
    """Quick in-beat switch between two scenes (6-8 frames): ``slide`` (old out left, new in from the right,
    motion blur), ``zoom`` (old pushes in and fades, new settles from 92%), ``wipe`` (marker band sweeps), ``cut``."""

    def __init__(self, spec: dict):
        self.kind = spec.get("kind", "slide")
        if self.kind not in {"none", "cut", "slide", "zoom", "wipe"}:
            raise ValueError(f"unknown scene transition {self.kind!r}")
        if self.kind == "none":
            self.kind = "cut"
        self.dur = int(spec.get("frames", 8)) / FPS
        self.color = col(spec.get("color"), R.YELLOW)

    def paint(self, c: skia.Canvas, old: skia.Image, new: skia.Image, p: float) -> None:
        e = ease_out(p)
        c.clear(R.color(R.PAPER))
        if self.kind == "slide":
            Entrance._img(c, old, x=-W * e, sx=40 * math.sin(math.pi * e))
            Entrance._img(c, new, x=W * (1 - e), sx=40 * math.sin(math.pi * e))
            c.drawLine(W * (1 - e), 0, W * (1 - e), H, R.stroke_paint(R.INK, 6))
        elif self.kind == "zoom":
            c.saveLayerAlpha(None, int(255 * (1 - e)))
            Entrance._img(c, old, scale=1 + 0.35 * e, sx=14 * e, sy=14 * e)
            c.restore()
            c.saveLayerAlpha(None, int(255 * e))
            Entrance._img(c, new, scale=0.92 + 0.08 * e)
            c.restore()
        else:  # wipe
            edge = -140 + (W + 280) * e
            Entrance._img(c, old)
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(0, 0, max(0.0, edge - 40), H))
            Entrance._img(c, new)
            c.restore()
            band = [(edge - 70, -20), (edge + 30, -20), (edge + 70, H + 20), (edge - 30, H + 20)]
            pth = R.path_of(np.asarray(band), closed=True)
            c.drawPath(pth, R.fill_paint(self.color))
            c.drawPath(pth, R.stroke_paint(R.INK, 6))


class Entrance:
    """Edits-style entrance transition over a beat's first frames (``params.enter`` in the spec).

    ``{"kind": "slide|whip|zoom|punch|wipe|chapter|none", "color": "blue", "label": "the build",
    "frames": 8, "from": "right|left|bottom|top", "scale": 1.12, "blur": 10, "label_color": "ink"}``. The scene keeps animating underneath; only its first ``frames`` frames are moved,
    blurred or covered, so word-anchored cues keep their times. Every kind ends on the plain scene,
    and nothing is drawn after it, so the clip's last frame is the settled diagram (exit-friendly).

    - slide: the panel slides in from the right over a section-coloured backdrop, motion-blurred.
    - whip: a fast whip-pan from the left, heavy horizontal blur.
    - zoom: zoom-punch, the panel lands from 135% with a blur that clears.
    - punch: a small 108% punch-in (continuity cut between two beats that share a layout).
    - wipe: a section-coloured marker band sweeps left to right and reveals the panel.
    - chapter: a section-coloured card with a big hand-lettered chapter label, which then slides up
      and off (vertical blur) to reveal the panel: the section-change beats.
    """

    DEFAULT_FRAMES = {"slide": 8, "whip": 7, "zoom": 8, "punch": 6, "wipe": 9, "chapter": 12}

    def __init__(self, spec: dict | None):
        spec = spec or {}
        self.kind = spec.get("kind", "none")
        if self.kind not in {"none", *self.DEFAULT_FRAMES}:
            raise ValueError(f"unknown entrance {self.kind!r}")
        self.frames = int(spec.get("frames", self.DEFAULT_FRAMES.get(self.kind, 0)))
        self.dur = self.frames / FPS
        self.color = col(spec.get("color"), R.INK)
        self.side = spec.get("from", "left" if self.kind == "whip" else "right")
        self.scale = float(spec.get("scale", {"zoom": 1.35, "punch": 1.08}.get(self.kind, 1.0)))
        self.blur = float(spec.get("blur", {"zoom": 22, "punch": 6}.get(self.kind, 0)))
        self.label_color = col(spec.get("label_color"), "#FFFFFF")
        self.label = spec.get("label", "")
        if self.label:
            from .templates import txt
            self.label = txt(self.label)

    @staticmethod
    def _img(c, img, x=0.0, y=0.0, scale=1.0, sx=0.0, sy=0.0):
        paint = skia.Paint(AntiAlias=True)
        if sx > 0.3 or sy > 0.3:
            paint.setImageFilter(skia.ImageFilters.Blur(sx, sy, skia.TileMode.kClamp))
        c.save()
        if scale != 1.0:
            c.translate(W / 2, H / 2)
            c.scale(scale, scale)
            c.translate(-W / 2, -H / 2)
        c.drawImage(img, x, y, paint=paint)
        c.restore()

    def paint(self, c: skia.Canvas, img: skia.Image, t: float) -> None:
        p = clamp(t / self.dur) if self.dur else 1.0
        e = ease_out(p)
        c.clear(R.color(self.color))
        k = self.kind
        if k in ("slide", "whip"):
            amt = (1 - e) if k == "slide" else (1 - e) ** 1.4
            dist = 0.85 if k == "slide" else 1.0
            blur = (36 * (1 - e) ** 1.5) if k == "slide" else 70 * (1 - e) ** 1.2
            sgn = {"right": 1, "left": -1, "bottom": 1, "top": -1}[self.side]
            if self.side in ("right", "left"):
                off = sgn * W * dist * amt
                self._img(c, img, x=off, sx=blur)
                if 0 < amt:
                    xe = off if sgn > 0 else W + off
                    c.drawLine(xe, 0, xe, H, R.stroke_paint(R.INK, 6))
            else:
                off = sgn * H * dist * amt
                self._img(c, img, y=off, sy=blur)
                if 0 < amt:
                    ye = off if sgn > 0 else H + off
                    c.drawLine(0, ye, W, ye, R.stroke_paint(R.INK, 6))
        elif k in ("zoom", "punch"):
            s0, sig = self.scale, self.blur
            self._img(c, img, scale=1 + (s0 - 1) * (1 - e) ** 2, sx=sig * (1 - e), sy=sig * (1 - e))
        elif k == "wipe":
            edge = -140 + (W + 280) * ease_out(p * 1.05)
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(0, 0, max(0.0, edge - 40), H))
            self._img(c, img)
            c.restore()
            band = [(edge - 70, -20), (edge + 30, -20), (edge + 70, H + 20), (edge - 30, H + 20)]
            pth = R.path_of(np.asarray(band), closed=True)
            c.drawPath(pth, R.fill_paint(self.color))
            c.drawPath(pth, R.stroke_paint(R.INK, 6))
        elif k == "chapter":
            hold = 0.42  # fraction of the entrance the card holds before sliding off
            q = clamp((p - hold) / (1 - hold))
            qe = q ** 2 * (3 - 2 * q)
            self._img(c, img, scale=1 + 0.06 * (1 - qe))
            y = -H * qe
            c.save()
            c.translate(0, y)
            paint = skia.Paint(AntiAlias=True)
            blur = 40 * math.sin(math.pi * qe)
            if blur > 0.3:
                paint.setImageFilter(skia.ImageFilters.Blur(0.1, blur, skia.TileMode.kClamp))
            c.saveLayer(None, paint)
            c.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), R.fill_paint(self.color))
            if self.label:
                s = 1.0 + 0.12 * (1 - ease_out(clamp(p / hold)))
                c.save()
                c.translate(W / 2, 520)
                c.scale(s, s)
                R.draw_text(c, self.label, 0, 0, 118, self.label_color, align="center")
                c.restore()
                c.drawLine(W / 2 - 220, 570, W / 2 + 220, 562, R.stroke_paint(self.label_color, 9, 0.9))
            c.restore()
            c.restore()


def encode(renderer: BeatRenderer, out: Path, fps: int = FPS, crf: int = 16) -> dict:
    n = max(1, int(round(renderer.duration * fps)))
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [media.tool("ffmpeg"), "-hide_banner", "-nostdin", "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-vf", f"scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,{media.SETPARAMS_709}",
           "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-tune", "animation", "-profile:v", "high",
           *media.BT709_ARGS, "-r", str(fps), "-frames:v", str(n), "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i in range(n):
            proc.stdin.write(renderer.frame(i / fps).tobytes())
        proc.stdin.close()
    except BrokenPipeError:
        pass
    err = proc.stderr.read().decode()
    if proc.wait() != 0:
        raise media.MediaError(err[-2000:])
    return {"path": str(out), "frames": n, "duration": round(n / fps, 4)}


def still(renderer: BeatRenderer, t: float, out: Path) -> Path:
    from PIL import Image

    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(renderer.frame(t)).convert("RGB").save(out)
    return out
