"""Thin, deterministic wrappers around ffmpeg / ffprobe."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

import numpy as np

_EXTRA_PATHS = [str(Path.home() / ".local" / "bin")]


class MediaError(RuntimeError):
    pass


def tool(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    for d in _EXTRA_PATHS:
        p = Path(d) / name
        if p.exists():
            return str(p)
    raise MediaError(f"{name} not found on PATH or in ~/.local/bin")


def have_tool(name: str) -> bool:
    try:
        tool(name)
        return True
    except MediaError:
        return False


def run(cmd: list[str], *, capture: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    exe = cmd[0]
    if exe in ("ffmpeg", "ffprobe", "whisper-cli"):
        cmd = [tool(exe)] + cmd[1:]
    proc = subprocess.run(cmd, capture_output=capture, text=True)
    if check and proc.returncode != 0:
        tail = (proc.stderr or "")[-3000:]
        raise MediaError(f"command failed ({proc.returncode}): {' '.join(cmd[:12])} ...\n{tail}")
    return proc


def ffmpeg(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return run(["ffmpeg", "-hide_banner", "-nostdin", "-y", *args], check=check)


HDR_TRANSFERS = {"arib-std-b67", "smpte2084"}


def probe(path: Path | str) -> dict:
    out = run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)]).stdout
    data = json.loads(out)
    fmt = data.get("format", {})
    info: dict = {"duration": float(fmt.get("duration", 0.0) or 0.0), "format": fmt.get("format_name"),
                  "creation_time": (fmt.get("tags") or {}).get("creation_time"), "video": None, "audio": None}
    for s in data.get("streams", []):
        if s.get("codec_type") == "video" and info["video"] is None and s.get("disposition", {}).get("attached_pic", 0) == 0:
            rot = 0
            for sd in s.get("side_data_list", []) or []:
                if "rotation" in sd:
                    rot = int(sd["rotation"])
            if "rotate" in (s.get("tags") or {}):
                rot = int(s["tags"]["rotate"])
            w, h = int(s["width"]), int(s["height"])
            dw, dh = (h, w) if abs(rot) % 180 == 90 else (w, h)
            fr = s.get("avg_frame_rate") or s.get("r_frame_rate") or "0/1"
            try:
                fps = float(Fraction(fr)) if fr != "0/0" else 0.0
            except (ZeroDivisionError, ValueError):
                fps = 0.0
            trc = s.get("color_transfer")
            info["video"] = {
                "codec": s.get("codec_name"), "width": w, "height": h, "display_width": dw,
                "display_height": dh, "rotation": rot, "fps": round(fps, 4), "pix_fmt": s.get("pix_fmt"),
                "color_transfer": trc, "color_primaries": s.get("color_primaries"),
                "color_space": s.get("color_space"), "color_range": s.get("color_range"),
                "hdr": trc in HDR_TRANSFERS, "duration": float(s.get("duration", 0) or 0),
            }
        elif s.get("codec_type") == "audio" and info["audio"] is None:
            info["audio"] = {"codec": s.get("codec_name"), "sample_rate": int(s.get("sample_rate", 0)),
                             "channels": int(s.get("channels", 0))}
    return info


def sdr_filter(video_info: dict | None, method: str = "swscale") -> str:
    """Filter chain prefix that brings any source to 8-bit-safe BT.709 SDR.

    HLG / PQ sources are converted with swscale's transfer + primaries conversion (ffmpeg >= 8).
    SDR sources only get their matrix normalised to BT.709.
    """
    if video_info and video_info.get("hdr") and method == "swscale":
        return ("scale=out_transfer=bt709:out_primaries=bt709:out_color_matrix=bt709:out_range=tv,"
                "format=yuv420p")
    if video_info and (video_info.get("color_space") or "bt709") not in ("bt709", "unknown", None):
        return "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"
    return "format=yuv420p"


# Filtered frames carry "unspecified" colour props that override encoder flags; tag them explicitly.
SETPARAMS_709 = "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv"

BT709_ARGS = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv"]


def read_wav(path: Path | str, sr: int | None = None) -> tuple[np.ndarray, int]:
    """Decode any audio to mono float32 via ffmpeg (avoids extra Python deps)."""
    args = ["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-i", str(path), "-ac", "1"]
    if sr:
        args += ["-ar", str(sr)]
    args += ["-f", "f32le", "-"]
    proc = subprocess.run([tool("ffmpeg")] + args[1:], capture_output=True)
    if proc.returncode != 0:
        raise MediaError(proc.stderr.decode(errors="replace")[-2000:])
    data = np.frombuffer(proc.stdout, dtype=np.float32)
    if sr is None:
        sr = probe(path)["audio"]["sample_rate"]
    return data, sr


_EBU_I = re.compile(r"^\s+I:\s+(-?[\d.]+|-inf)\s+LUFS", re.M)
_EBU_LRA = re.compile(r"^\s+LRA:\s+(-?[\d.]+)\s+LU", re.M)
_EBU_PEAK = re.compile(r"True peak:\s*\n\s+Peak:\s+(-?[\d.]+|-inf)\s+dBFS", re.M)


def loudness(path: Path | str, start: float | None = None, duration: float | None = None,
             stream: str | None = None) -> dict:
    """Integrated loudness (LUFS), LRA and true peak (dBTP) via ffmpeg ebur128."""
    args = []
    if start is not None:
        args += ["-ss", f"{start:.4f}"]
    if duration is not None:
        args += ["-t", f"{duration:.4f}"]
    args += ["-i", str(path), "-vn"]
    if stream:
        args += ["-map", stream]
    args += ["-af", "ebur128=peak=true", "-f", "null", "-"]
    err = ffmpeg(*args).stderr
    summary = err[err.rfind("Summary:"):]
    i = _EBU_I.search(summary)
    lra = _EBU_LRA.search(summary)
    pk = _EBU_PEAK.search(summary)

    def f(m):
        if not m:
            return None
        return float("-inf") if m.group(1) == "-inf" else float(m.group(1))

    return {"integrated_lufs": f(i), "lra": f(lra), "true_peak_db": f(pk)}


def finite(x: float | None, default: float = -70.0) -> float:
    if x is None or x != x or x in (float("inf"), float("-inf")):
        return default
    return x


def extract_frames(video: Path | str, times: list[float], width: int | None = None) -> list[np.ndarray | None]:
    """Grab single BGR frames at the given times (one ffmpeg call per frame, accurate seek)."""
    import cv2  # local import: optional dependency

    frames = []
    for t in times:
        vf = f"scale={width}:-2" if width else "null"
        proc = subprocess.run([tool("ffmpeg"), "-hide_banner", "-nostdin", "-v", "error", "-ss", f"{max(0, t):.4f}",
                               "-i", str(video), "-frames:v", "1", "-vf", vf, "-f", "image2pipe",
                               "-vcodec", "png", "-"], capture_output=True)
        if proc.returncode != 0 or not proc.stdout:
            frames.append(None)
            continue
        arr = np.frombuffer(proc.stdout, dtype=np.uint8)
        frames.append(cv2.imdecode(arr, cv2.IMREAD_COLOR))
    return frames


def sample_frames(video: Path | str, start: float, end: float, fps: float, width: int, height: int):
    """Decode frames between start and end at ``fps`` as BGR arrays, with their source times."""
    dur = max(0.05, end - start)
    proc = subprocess.run([tool("ffmpeg"), "-hide_banner", "-nostdin", "-v", "error", "-ss", f"{start:.4f}",
                           "-t", f"{dur:.4f}", "-i", str(video), "-vf", f"fps={fps},scale={width}:{height}",
                           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True)
    if proc.returncode != 0:
        raise MediaError(proc.stderr.decode(errors="replace")[-2000:])
    frame_bytes = width * height * 3
    n = len(proc.stdout) // frame_bytes
    out = []
    for i in range(n):
        arr = np.frombuffer(proc.stdout, dtype=np.uint8, count=frame_bytes, offset=i * frame_bytes)
        out.append((start + i / fps, arr.reshape(height, width, 3)))
    return out


def env_threads() -> int:
    return int(os.environ.get("CONTENT_OS_THREADS", "0")) or (os.cpu_count() or 4)
