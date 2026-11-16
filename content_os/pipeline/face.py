"""Face detection with OpenCV's YuNet (cv2.FaceDetectorYN, ONNX model in ~/.cache/content_os/models).

OpenCV 5 no longer ships Haar cascades in the main module, so YuNet is the only bundled detector.
If OpenCV or the model is missing, ``get_detector`` returns None and every stage degrades to
"face: not measured" instead of failing.

Head-pose proxy ("eye-on-lens"): YuNet gives eye, nose and mouth-corner landmarks. Yaw is the nose's
horizontal offset from the eye midpoint divided by the eye distance; near 0 means facing the lens.
This is a head-orientation proxy, not gaze tracking.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Face:
    cx: float      # centre, fraction of frame width
    cy: float      # centre, fraction of frame height
    w: float       # face width, fraction of frame width
    h: float
    score: float
    yaw: float     # nose offset / eye distance (0 = frontal)

    def as_dict(self) -> dict:
        return {k: round(float(v), 4) for k, v in self.__dict__.items()}


class YuNet:
    name = "opencv-yunet-2023mar"

    def __init__(self, model_path: str, score_threshold: float = 0.6):
        import cv2

        self.cv2 = cv2
        try:  # silence "Targets are not supported by the new graph engine" warnings
            cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
        except AttributeError:
            pass
        self.model_path = model_path
        self.thr = score_threshold
        self._det = None
        self._size = None

    def detect(self, frame: np.ndarray, max_width: int = 640) -> Face | None:
        # YuNet misses faces that fill much of a large frame; detect on a <=640 px copy
        # (results are fractions of the frame, so the scale does not matter downstream)
        if frame.shape[1] > max_width:
            scale = max_width / frame.shape[1]
            frame = self.cv2.resize(frame, (max_width, int(round(frame.shape[0] * scale))),
                                    interpolation=self.cv2.INTER_AREA)
        h, w = frame.shape[:2]
        if self._det is None or self._size != (w, h):
            self._det = self.cv2.FaceDetectorYN.create(self.model_path, "", (w, h), self.thr)
            self._size = (w, h)
        _, faces = self._det.detect(frame)
        if faces is None or len(faces) == 0:
            return None
        f = max(faces, key=lambda r: r[2] * r[3])  # largest face = the speaker
        x, y, fw, fh = map(float, f[:4])
        rex, rey, lex, ley, nx, ny = map(float, f[4:10])
        eye_mid = (rex + lex) / 2
        eye_dist = max(1.0, abs(lex - rex))
        return Face(cx=(x + fw / 2) / w, cy=(y + fh / 2) / h, w=fw / w, h=fh / h, score=float(f[14]),
                    yaw=(nx - eye_mid) / eye_dist)


def get_detector(cfg: dict):
    fcfg = cfg["face"]
    if fcfg.get("detector") in (None, "none", "off"):
        return None
    try:
        import cv2  # noqa: F401  (availability check)
    except ImportError:
        return None
    path = Path(fcfg["model"]).expanduser()
    if not path.exists():
        return None
    return YuNet(str(path), fcfg["score_threshold"])


def summarise(samples: list[tuple[float, Face | None]], frontal_max: float) -> dict:
    n = len(samples)
    faces = [f for _, f in samples if f is not None]
    if n == 0:
        return {"measured": False}
    if not faces:
        return {"measured": True, "samples": n, "present_ratio": 0.0}
    cx = np.array([f.cx for f in faces])
    cy = np.array([f.cy for f in faces])
    return {
        "measured": True, "samples": n, "present_ratio": round(len(faces) / n, 3),
        "cx": round(float(np.median(cx)), 4), "cy": round(float(np.median(cy)), 4),
        "w": round(float(np.median([f.w for f in faces])), 4),
        "drift_x": round(float(cx.max() - cx.min()), 4),
        "frontal_ratio": round(sum(abs(f.yaw) <= frontal_max for f in faces) / n, 3),
        "median_abs_yaw": round(float(np.median([abs(f.yaw) for f in faces])), 3),
    }
