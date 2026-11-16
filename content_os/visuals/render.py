"""Render one beat: build its scene, attach resolved cues, draw every frame with skia, pipe RGBA to
ffmpeg (libx264, yuv420p, BT.709 tagged, 1080x960, 30 fps). Deterministic and offline."""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import skia

from content_os.pipeline import media

from . import rough as R
from . import scenes
from .cues import resolve_beat
from .elements import Cue, Element

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


class BeatRenderer:
    def __init__(self, beat: dict, ctx: dict, words: list[dict] | None, duration: float):
        self.beat = beat
        self.duration = duration
        self.resolved, self.report = resolve_beat(beat["line"], beat.get("cues", []), words or [], duration)
        self.elements = scenes.build(beat, ctx)
        missing = attach(self.elements, self.resolved)
        if missing:
            raise ValueError(f"beat {beat['beat']}: cue targets not in scene: {sorted(set(missing))}")
        self.bg = R.paper_background(W, H)
        self.surface = skia.Surface(W, H)

    def frame(self, t: float) -> np.ndarray:
        c = self.surface.getCanvas()
        c.drawImage(self.bg, 0, 0)
        for el in sorted(self.elements, key=lambda e: e.z):
            el.render(c, t)
        img = self.surface.makeImageSnapshot()
        return img.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

    def key_time(self) -> float:
        """The moment that best shows the beat: just after the last emphasis cue settles (else the last cue)."""
        if not self.resolved:
            return self.duration * 0.8
        emph = [r for r in self.resolved if r.emphasis]
        last = max(self.resolved, key=lambda r: r.t + r.dur)
        r = max(emph, key=lambda r: r.t) if emph else last
        return min(self.duration - 1 / FPS, max(last.t + last.dur, r.t + r.dur) + 0.25)


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
