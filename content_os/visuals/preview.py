"""Sync preview before the shoot: macOS ``say`` reads each beat line, the pipeline's whisper stage
transcribes the joined track, the beats are rendered against those word timestamps and stacked over
a grey placeholder speaker panel (with the pipeline's captions burned in) as a 1080x1920 MP4.

The synthetic track is cut like the real reel: each beat = its speech plus a short lead and tail,
butted together, every beat padded to the 30 fps frame grid so picture and sound stay aligned.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from content_os.pipeline import media
from content_os.pipeline.captions import chunk_words, write_ass
from content_os.pipeline.config import load_config
from content_os.pipeline.layouts import build_layout
from content_os.pipeline.transcribe import transcribe_file

from .build import render_all, spoken_line
from .render import FPS

SR = 48000
LEAD, TAIL = 0.25, 0.45


def synth_voice(sheet: dict, work: Path, voice: str = "Samantha", rate: int = 175,
                only: list[int] | None = None) -> tuple[Path, list[dict]]:
    params = sheet.get("params", {})
    pieces, beats, t = [], [], 0.0
    for b in sheet["beats"]:
        if only and int(b["beat"]) not in only:
            continue
        line = spoken_line(b, params)
        aiff = work / f"say_{b['beat']:02d}.aiff"
        subprocess.run(["say", "-v", voice, "-r", str(rate), "-o", str(aiff), line], check=True)
        x, _ = media.read_wav(aiff, SR)
        nz = np.nonzero(np.abs(x) > 1e-3)[0]
        x = x[nz[0]: nz[-1] + 1] if len(nz) else x
        frames = int(np.ceil((LEAD + len(x) / SR + TAIL) * FPS))
        n = int(round(frames / FPS * SR))
        seg = np.zeros(n, np.float32)
        a = int(LEAD * SR)
        seg[a: a + len(x)] = x[: n - a]
        beats.append({"beat": int(b["beat"]), "start": round(t, 4), "duration": round(frames / FPS, 4), "line": line})
        pieces.append(seg)
        t += frames / FPS
    track = np.concatenate(pieces)
    track += np.random.default_rng(7).normal(0, 10 ** (-65 / 20), len(track)).astype(np.float32)
    raw = work / "voice.f32"
    raw.write_bytes(track.astype(np.float32).tobytes())
    wav48 = work / "voice48.wav"
    media.ffmpeg("-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(raw), "-c:a", "pcm_s24le", str(wav48))
    return wav48, beats


def assign_words(words: list[dict], beats: list[dict]) -> dict[int, dict]:
    out = {}
    for b in beats:
        a, e = b["start"], b["start"] + b["duration"]
        ws = [{"text": w["text"], "start": round(w["start"] - a, 3), "end": round(w["end"] - a, 3)}
              for w in words if a <= (w["start"] + w["end"]) / 2 < e]
        out[b["beat"]] = {"words": ws, "duration": b["duration"]}
    return out


def build_preview(sheet: dict, reel_dir: Path, out_dir: Path, *, voice: str = "Samantha", rate: int = 175,
                  beats_only: list[int] | None = None, name: str = "food_tracker_preview", log=print) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="visuals_preview_"))
    try:
        wav48, beats = synth_voice(sheet, work, voice, rate, beats_only)
        wav16 = work / "voice16.wav"
        media.ffmpeg("-v", "error", "-i", str(wav48), "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav16))
        cfg = load_config(work, {})
        tr = transcribe_file(wav16, work / "asr", cfg, "whisper_cpp")
        timings = assign_words(tr["words"], beats)
        (out_dir / "synthetic_transcript.json").write_text(json.dumps(
            {"note": "macOS say voice, transcribed with content_os.pipeline.transcribe (whisper.cpp)",
             "voice": voice, "rate": rate, "beats": beats, "words": tr["words"]}, indent=1) + "\n")
        clips = out_dir / "beats"
        manifest = render_all(sheet, reel_dir, clips, timings, beats=beats_only, log=log)
        # visual track
        lst = clips / "concat.txt"
        lst.write_text("".join(f"file 'beat_{b['beat']:02d}.mp4'\n" for b in beats))
        visual = work / "visual.mp4"
        media.ffmpeg("-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(visual))
        total = sum(b["duration"] for b in beats)
        # captions exactly as the pipeline would place them
        layout = build_layout(cfg, {"layout": "split_vertical"})
        segs = [{"index": i, "words": [{"text": w["text"], "start": w["start"] + b["start"], "end": w["end"] + b["start"]}
                                       for w in timings[b["beat"]]["words"]]} for i, b in enumerate(beats)]
        chunks = chunk_words(segs, cfg["captions"])
        write_ass(work / "captions.ass", chunks, layout, cfg["captions"])
        fonts = work / "fonts"
        fonts.mkdir()
        if Path(cfg["captions"]["font_file"]).exists():
            shutil.copy(cfg["captions"]["font_file"], fonts)
        out = out_dir / f"{name}.mp4"
        fg = (f"color=c=0x6B6B6B:s=1080x960:r={FPS}:d={total:.3f},"
              f"drawtext=fontfile=fonts/{Path(cfg['captions']['font_file']).name}:text='speaker (recorded tomorrow)':"
              f"fontsize=44:fontcolor=0xDDDDDD:x=(w-text_w)/2:y=h*0.55[spk];"
              f"[0:v]setsar=1[vis];[vis][spk]vstack=inputs=2,subtitles=filename=captions.ass:fontsdir=fonts,"
              f"drawtext=fontfile=fonts/{Path(cfg['captions']['font_file']).name}:text='PREVIEW - synthetic voice':"
              f"fontsize=30:fontcolor=0xC0392B:x=60:y=1000,format=yuv420p,{media.SETPARAMS_709}[v]")
        proc = subprocess.run([media.tool("ffmpeg"), "-hide_banner", "-nostdin", "-y", "-v", "error",
                               "-i", str(visual), "-i", str(wav48), "-filter_complex", fg, "-map", "[v]", "-map", "1:a",
                               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                               "-profile:v", "high", *media.BT709_ARGS, "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
                               "-ar", "48000", "-t", f"{total:.4f}", "-movflags", "+faststart", str(out)],
                              cwd=work, capture_output=True, text=True)
        if proc.returncode != 0:
            raise media.MediaError(proc.stderr[-2000:])
        manifest["preview"] = str(out)
        manifest["preview_duration"] = round(total, 3)
        (clips / "visuals.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
        return manifest
    finally:
        shutil.rmtree(work, ignore_errors=True)
