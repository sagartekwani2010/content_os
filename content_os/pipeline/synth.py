"""Synthetic test reel: macOS ``say`` voice, a drawn face over a plain background, spoken
"beat N" cues and 2-3 attempts per beat, with level differences and a head shift between takes.

Used by the tests and for a dry run of the whole pipeline without personal footage:
``python -m content_os.pipeline synth <dir> [--hdr] [--files 2]``.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import numpy as np

from . import media
from .reel import write_json

SR = 48000

DEFAULT_BEATS = [
    "Most agents are workflows wearing a costume.",
    "Here is the test I use before I build one.",
    "If the steps never change, write a script instead.",
]


def say_wav(text: str, voice: str, rate: int, workdir: Path, name: str) -> np.ndarray:
    aiff = workdir / f"{name}.aiff"
    subprocess.run(["say", "-v", voice, "-r", str(rate), "-o", str(aiff), text], check=True)
    x, _ = media.read_wav(aiff, SR)
    nz = np.nonzero(np.abs(x) > 1e-4)[0]
    return x[nz[0]: nz[-1] + 1] if len(nz) else x


def draw_face_png(path: Path, size: int = 360) -> None:
    import cv2

    img = np.zeros((int(size * 1.6), int(size * 1.4), 4), np.uint8)
    s = size // 3
    cx, cy = img.shape[1] // 2, int(size * 0.55)

    def fill(fn, *args, color):
        fn(img, *args, (*color, 255), -1)

    fill(cv2.ellipse, (cx, cy + int(1.6 * s)), (int(s * 1.6), int(s * 0.8)), 0, 180, 360, color=(90, 60, 40))
    fill(cv2.ellipse, (cx, cy), (int(s * 0.8), s), 0, 0, 360, color=(140, 170, 215))
    fill(cv2.ellipse, (cx, cy - int(s * 0.95)), (int(s * 0.85), int(s * 0.45)), 0, 180, 360, color=(30, 30, 40))
    for dx in (-0.33, 0.33):
        ex, ey = cx + int(dx * s), cy - int(0.18 * s)
        fill(cv2.ellipse, (ex, ey), (int(s * 0.16), int(s * 0.08)), 0, 0, 360, color=(255, 255, 255))
        fill(cv2.circle, (ex, ey), int(s * 0.06), color=(40, 30, 20))
        cv2.line(img, (ex - int(s * .17), ey - int(s * .17)), (ex + int(s * .17), ey - int(s * .2)), (30, 30, 40, 255), 4)
    cv2.line(img, (cx, cy - int(.05 * s)), (cx - int(.06 * s), cy + int(.2 * s)), (100, 120, 170, 255), 3)
    fill(cv2.ellipse, (cx, cy + int(.45 * s)), (int(s * .25), int(s * .08)), 0, 0, 360, color=(60, 60, 150))
    cv2.imwrite(str(path), img)


def make_reel(root: Path, beats: list[str] | None = None, *, hdr: bool = False, files: int = 1,
              size: tuple[int, int] = (1280, 720), voice: str = "Samantha", rate: int = 175,
              cue_style: list[str] | None = None) -> dict:
    """Write beats.json, cue_sheet.json, raw/*.mov and assets/ under ``root``. Returns ground truth."""
    beats = beats or DEFAULT_BEATS
    root = Path(root)
    tmp = root / ".synth_tmp"
    for d in (root / "raw", root / "assets", tmp):
        d.mkdir(parents=True, exist_ok=True)
    cue_style = cue_style or [f"Beat {i}." for i in range(1, len(beats) + 1)]
    # script of the shoot: (kind, text, gain_db, face_dx)
    events: list[tuple[str, str, float, int, int]] = []
    for i, line in enumerate(beats, start=1):
        events.append(("cue", cue_style[i - 1], 0.0, 0, i))
        words = line.split()
        if i == 2:  # a false start, then two full attempts, the last one 6 dB quieter
            events.append(("take", " ".join(words[:3]), 0.0, 0, i))
            events.append(("take", line, 0.0, 0, i))
            events.append(("take", line, -6.0, 0, i))
        elif i == 3:  # two attempts; the head moves right ~3% of frame width on the last one
            events.append(("take", line, 0.0, 0, i))
            events.append(("take", line, 0.0, int(size[0] * 0.03), i))
        else:
            events.append(("take", line, 0.0, 0, i))
            events.append(("take", line, 0.0, 0, i))
    pieces, truth = [], []
    t = 0.8
    lead = np.zeros(int(SR * t), np.float32)
    pieces.append(lead)
    for k, (kind, text, gain, dx, beat) in enumerate(events):
        x = say_wav(text, voice, rate, tmp, f"e{k:02d}") * (10 ** (gain / 20))
        truth.append({"kind": kind, "beat": beat, "text": text, "start": round(t, 3),
                      "end": round(t + len(x) / SR, 3), "gain_db": gain, "face_dx": dx})
        pieces.append(x.astype(np.float32))
        t += len(x) / SR
        gap = 0.9 if kind == "cue" else 1.1
        pieces.append(np.zeros(int(SR * gap), np.float32))
        t += gap
    rng = np.random.default_rng(7)
    voice_track = np.concatenate(pieces)
    voice_track = voice_track + rng.normal(0, 10 ** (-62 / 20), len(voice_track)).astype(np.float32)  # room tone
    total = len(voice_track) / SR
    face = tmp / "face.png"
    draw_face_png(face, size=size[1] // 2)
    # file boundaries: split before a cue so each file starts with "beat N"
    cues = [e for e in truth if e["kind"] == "cue"]
    bounds = [0.0]
    if files > 1:
        for c in cues[1:]:
            if len(bounds) < files:
                bounds.append(round(c["start"] - 0.4, 3))
    bounds.append(total)
    outs = []
    for fi in range(len(bounds) - 1):
        a, b = bounds[fi], bounds[fi + 1]
        seg = voice_track[int(a * SR): int(b * SR)]
        wav = tmp / f"voice_{fi}.f32"
        wav.write_bytes(seg.astype(np.float32).tobytes())
        moves = [(e["start"] - a - 0.3, e["end"] - a + 0.6, e["face_dx"]) for e in truth if e["face_dx"] and a <= e["start"] < b]
        xexpr = "(W-w)/2"
        for s0, s1, dx in moves:
            xexpr = f"if(between(t\\,{s0:.2f}\\,{s1:.2f})\\,(W-w)/2+{dx}\\,{xexpr})"
        fg = (f"color=c=0x5A6470:s={size[0]}x{size[1]}:r=30:d={b - a:.3f}[bg];"
              f"[0:v]format=rgba[f];[bg][f]overlay=x='{xexpr}':y=(H-h)/2+{size[1] // 10}:shortest=0,format=yuv420p[v]")
        out = root / "raw" / f"IMG_{9000 + fi}.MOV"
        venc = (["-c:v", "libx265", "-pix_fmt", "yuv420p10le", "-tag:v", "hvc1", "-x265-params",
                 "log-level=error:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc",
                 "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc"]
                if hdr else ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", *media.BT709_ARGS])
        media.ffmpeg("-v", "error", "-loop", "1", "-i", str(face),
                     "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(wav),
                     "-filter_complex", fg, "-map", "[v]", "-map", "1:a", *venc, "-c:a", "aac", "-b:a", "192k", "-t", f"{b - a:.3f}", str(out))
        outs.append(out.name)
    # assets for the cue sheet
    media.ffmpeg("-v", "error", "-f", "lavfi", "-i", "testsrc2=s=1280x720:r=30:d=6", "-c:v", "libx264", "-preset",
                 "veryfast", "-pix_fmt", "yuv420p", str(root / "assets" / "broll.mp4"))
    media.ffmpeg("-v", "error", "-f", "lavfi", "-i", "smptehdbars=s=1200x900", "-frames:v", "1",
                 str(root / "assets" / "screenshot.png"))
    media.ffmpeg("-v", "error", "-f", "lavfi", "-i",
                 "aevalsrc='0.2*sin(2*PI*220*t)+0.15*sin(2*PI*277.18*t)+0.12*sin(2*PI*329.63*t)':s=48000:d=12",
                 "-c:a", "pcm_s16le", str(root / "assets" / "music.wav"))
    media.ffmpeg("-v", "error", "-f", "lavfi", "-i", "anoisesrc=d=0.35:c=pink:a=0.5", "-af", "afade=t=out:st=0.05:d=0.3",
                 str(root / "assets" / "whoosh.wav"))
    write_json(root / "beats.json", {"reel_id": "synthetic-test", "beats": [{"id": i, "text": t} for i, t in enumerate(beats, 1)]})
    cue_beats = []
    for i in range(1, len(beats) + 1):
        if i == 1:
            cue_beats.append({"beat": i, "visual": {"type": "card", "text": "AGENT OR WORKFLOW?"}})
        elif i == 2:
            cue_beats.append({"beat": i, "visual": {"type": "image", "path": "assets/screenshot.png", "fit": "contain"},
                              "start_offset": 0.3, "sfx": [{"path": "assets/whoosh.wav", "at": 0.3, "gain_db": -14}]})
        else:
            cue_beats.append({"beat": i, "visual": {"type": "video", "path": "assets/broll.mp4", "start": 1.0, "fit": "cover"}})
    write_json(root / "cue_sheet.json", {"layout": "split_vertical",
                                         "layout_params": {"speaker_ratio": 0.5, "speaker_position": "bottom"},
                                         "beats": cue_beats,
                                         "music": {"path": "assets/music.wav", "gain_db": -20}})
    shutil.rmtree(tmp)
    return {"files": outs, "events": truth, "bounds": bounds}
