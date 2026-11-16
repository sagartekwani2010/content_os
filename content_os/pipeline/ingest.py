"""Stage 1, ingest: probe sources, extract 16 kHz mono (ASR) + 48 kHz mono (mix) wavs and an SDR proxy."""

from __future__ import annotations

from pathlib import Path

from . import media
from .reel import Reel, StageError, schema, write_json


def find_sources(reel: Reel, cfg: dict, explicit: list[str] | None) -> list[Path]:
    if explicit:
        paths = [reel.resolve(p) for p in explicit]
    else:
        seen: dict[str, Path] = {}
        for pattern in cfg["ingest"]["source_glob"]:
            for p in reel.root.glob(pattern):
                seen[str(p.resolve()).lower()] = p.resolve()
        paths = sorted(seen.values(), key=lambda p: p.name)
    missing = [p for p in paths if not p.exists()]
    if missing:
        raise StageError(f"source not found: {missing[0]}")
    if not paths:
        raise StageError("no sources: put footage in <reel_dir>/raw/ or pass --source")
    return paths


def run(reel: Reel, cfg: dict, sources: list[str] | None = None) -> dict:
    paths = find_sources(reel, cfg, sources)
    out = []
    for idx, path in enumerate(paths, start=1):
        sid = f"s{idx}"
        info = media.probe(path)
        if info["audio"] is None:
            raise StageError(f"{path.name} has no audio stream")
        wav16 = reel.p("audio", f"{sid}_16k.wav")
        wav48 = reel.p("audio", f"{sid}_48k.wav")
        # first audio stream, downmixed to mono; 48 kHz kept at 24-bit for the mix
        media.ffmpeg("-v", "error", "-i", str(path), "-map", "0:a:0", "-ac", "1", "-ar", "16000",
                     "-c:a", "pcm_s16le", str(wav16))
        media.ffmpeg("-v", "error", "-i", str(path), "-map", "0:a:0", "-ac", "1", "-ar", "48000",
                     "-c:a", "pcm_s24le", str(wav48))
        entry = {"id": sid, "path": reel.rel(path), "file": path.name, "duration": round(info["duration"], 3),
                 "creation_time": info["creation_time"], "video": info["video"], "audio": info["audio"],
                 "wav16": reel.rel(wav16), "wav48": reel.rel(wav48), "proxy": None}
        if info["video"]:
            proxy = reel.p("proxy", f"{sid}.mp4")
            vf = media.sdr_filter(info["video"], cfg["ingest"]["hdr_method"])
            pw = cfg["ingest"]["proxy_width"]
            # proxy: SDR, short GOP for fast accurate seeks; used for face detection and review frames
            media.ffmpeg("-v", "error", "-i", str(path), "-map", "0:v:0", "-an",
                         "-vf", f"{vf},scale={pw}:-2:flags=bicubic,{media.SETPARAMS_709}", "-c:v", "libx264", "-preset", "veryfast",
                         "-crf", "23", "-g", "15", *media.BT709_ARGS, str(proxy))
            pinfo = media.probe(proxy)["video"]
            entry["proxy"] = reel.rel(proxy)
            entry["proxy_size"] = [pinfo["width"], pinfo["height"]]
            if info["video"]["hdr"]:
                entry["notes"] = [f"HDR ({info['video']['color_transfer']}) converted to BT.709 SDR with "
                                  f"{cfg['ingest']['hdr_method']}; check skin tones on the cut review page"]
        out.append(entry)
    data = {"schema": schema("sources"), "sources": out}
    write_json(reel.sources_file, data)
    return data
