"""Pluggable output layouts. A layout says where each panel sits on the 9:16 canvas, where captions
may go, and how to compose the panel streams with ffmpeg.

Register a new layout (e.g. a full 9:16 talking head) by adding a factory to ``LAYOUTS``:
``factory(width, height, safe, captions_cfg, **params) -> Layout``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def bottom(self) -> int:
        return self.y + self.h

    @property
    def right(self) -> int:
        return self.x + self.w

    def intersects(self, o: "Rect") -> bool:
        return not (self.right <= o.x or o.right <= self.x or self.bottom <= o.y or o.bottom <= self.y)

    def as_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h}


@dataclass
class Layout:
    name: str
    width: int
    height: int
    panels: dict[str, Rect]
    caption_box: Rect
    compose: Callable[[dict[str, str]], str]
    params: dict = field(default_factory=dict)

    def describe(self) -> dict:
        return {"name": self.name, "width": self.width, "height": self.height, "params": self.params,
                "panels": {k: v.as_dict() for k, v in self.panels.items()}, "caption_box": self.caption_box.as_dict()}


def _even(v: float) -> int:
    return int(round(v / 2.0)) * 2


def split_vertical(width: int, height: int, safe: dict, captions: dict, speaker_ratio: float = 0.5,
                   speaker_position: str = "bottom", caption_position: str = "top_safe") -> Layout:
    if not 0.2 <= speaker_ratio <= 0.8:
        raise ValueError("speaker_ratio must be between 0.2 and 0.8")
    sh = _even(height * speaker_ratio)
    vh = height - sh
    if speaker_position == "bottom":
        visual, speaker = Rect(0, 0, width, vh), Rect(0, vh, width, sh)
        seam = vh
    elif speaker_position == "top":
        speaker, visual = Rect(0, 0, width, sh), Rect(0, sh, width, vh)
        seam = sh
    else:
        raise ValueError("speaker_position must be top or bottom")
    box_h = int(captions["font_size"] * 2.6)
    x0, x1 = safe["left"], width - safe["right"]
    if caption_position == "seam":
        y = seam - box_h // 2
    elif caption_position == "top_safe":
        # inside the visual panel, against the seam (speaker bottom) or above the bottom safe area
        if speaker_position == "bottom":
            y = seam - captions["margin_above_seam"] - box_h
        else:
            y = min(height - safe["bottom"], visual.bottom) - captions["margin_above_seam"] - box_h
    else:
        raise ValueError("caption_position must be top_safe or seam")
    y = min(y, height - safe["bottom"] - box_h)
    box = Rect(x0, max(safe["top"], y), x1 - x0, box_h)

    def compose(inputs: dict[str, str]) -> str:
        v, s = inputs["visual"], inputs["speaker"]
        order = f"{v}{s}" if speaker_position == "bottom" else f"{s}{v}"
        return f"{order}vstack=inputs=2[base]"

    return Layout("split_vertical", width, height, {"visual": visual, "speaker": speaker}, box, compose,
                  {"speaker_ratio": speaker_ratio, "speaker_position": speaker_position,
                   "caption_position": caption_position})


LAYOUTS: dict[str, Callable[..., Layout]] = {"split_vertical": split_vertical}


def build_layout(cfg: dict, cue_sheet: dict | None = None) -> Layout:
    lcfg = dict(cfg["layout"])
    params = dict(lcfg.get("params", {}))
    if cue_sheet:
        lcfg["name"] = cue_sheet.get("layout", lcfg["name"])
        params.update(cue_sheet.get("layout_params", {}))
    factory = LAYOUTS.get(lcfg["name"])
    if factory is None:
        raise ValueError(f"unknown layout {lcfg['name']}; known: {sorted(LAYOUTS)}")
    return factory(cfg["output"]["width"], cfg["output"]["height"], cfg["safe_area"], cfg["captions"], **params)


def speaker_crop(src_w: int, src_h: int, panel: Rect, face_cx: float | None, face_cy: float | None,
                 zoom: float = 1.0, eye_line: float = 0.4) -> Rect:
    """Crop rect (source pixels) that fills the speaker panel, centred on the face horizontally."""
    aspect = panel.w / panel.h
    ch = src_h / max(zoom, 1.0)
    cw = ch * aspect
    if cw > src_w:  # panel wider than source: limit by width
        cw = src_w
        ch = cw / aspect
    cx = (face_cx if face_cx is not None else 0.5) * src_w
    x = min(max(cx - cw / 2, 0), src_w - cw)
    if ch < src_h and face_cy is not None:
        # eyes sit ~0.12 face heights above the face-box centre; approximate with the centre
        y = face_cy * src_h - eye_line * ch
    else:
        y = (src_h - ch) / 2
    y = min(max(y, 0), src_h - ch)
    w, h = _even(cw), _even(ch)
    return Rect(min(_even(x), src_w - w), min(_even(y), src_h - h), w, h)
