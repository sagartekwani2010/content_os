"""Stage 5, cutpoints: exact in/out per selected take, speaker crop, per-take gain -> cuts.json.

in  = first-word onset - lead (40 ms), out = last-word offset + tail (80 ms); each is moved to the
quietest 10 ms frame within +-20 ms, never into the take's own speech and never into neighbouring
speech, then put on the video frame grid (in floored, out ceiled) so audio and picture cut on the
same instant. Every join gets a 30 ms audio crossfade at render (audio is extended 15 ms each side).
"""

from __future__ import annotations

import math

import numpy as np

from . import audio, media
from .layouts import build_layout, speaker_crop
from .reel import Reel, StageError, canonical_hash, read_json, schema, write_json


def _bounds(regions: list[list[float]], start: float, end: float) -> tuple[float, float]:
    prev_end = 0.0
    next_start = math.inf
    for r0, r1 in regions:
        if r1 <= start + 1e-3 and r1 > prev_end:
            prev_end = r1
        if r0 >= end - 1e-3 and r0 < next_start:
            next_start = r0
    return prev_end, next_start


def refine(take: dict, env: np.ndarray, frame_s: float, regions: list[list[float]], duration: float,
           fps: float, ccfg: dict) -> dict:
    start, end = take["start"], take["end"]
    prev_end, next_start = _bounds(regions, start, end)
    lo = prev_end + 0.01
    hi = min(next_start - 0.01, duration)
    t_in = audio.snap_low_energy(env, frame_s, start - ccfg["lead_s"], ccfg["snap_window_s"], not_after=start, not_before=lo)
    t_out = audio.snap_low_energy(env, frame_s, end + ccfg["tail_s"], ccfg["snap_window_s"], not_before=end, not_after=hi)
    t_in, t_out = max(t_in, lo, 0.0), min(t_out, hi)
    f_in = math.floor(t_in * fps + 1e-6)
    if f_in / fps < lo:
        f_in = math.ceil(lo * fps)
    f_out = math.ceil(t_out * fps - 1e-6)
    if f_out / fps > hi:
        f_out = math.floor(hi * fps)
    notes = []
    if start - f_in / fps < ccfg["lead_s"] * 0.5:
        notes.append("short lead-in: neighbouring speech is close")
    if f_out / fps - end < ccfg["tail_s"] * 0.5:
        notes.append("short tail: neighbouring speech is close")
    return {"in": round(f_in / fps, 4), "out": round(f_out / fps, 4), "frames": f_out - f_in,
            "lead_s": round(start - f_in / fps, 3), "tail_s": round(f_out / fps - end, 3), "notes": notes}


def run(reel: Reel, cfg: dict) -> dict:
    selects = reel.need(reel.selects_file, "score")
    scores = reel.need(reel.scores_file, "score")
    transcript = reel.need(reel.transcript_file, "transcribe")
    sources = {s["id"]: s for s in reel.need(reel.sources_file, "ingest")["sources"]}
    takes = {t["id"]: t for t in scores["takes"]}
    if selects["needs_rerecord"]:
        raise StageError(f"beats without a usable take: {selects['needs_rerecord']} (re-record, or override with "
                         "`select`)")
    cue = read_json(reel.cue_sheet_file) if reel.cue_sheet_file.exists() else None
    layout = build_layout(cfg, cue)
    panel = layout.panels["speaker"]
    fps = cfg["fps"]
    ccfg = cfg["cutpoints"]
    chosen = [takes[e["take"]] for e in selects["beats"] if e["take"]]
    faces = [t["face"] for t in chosen if t["face"].get("cx") is not None]
    ref_cx = float(np.median([f["cx"] for f in faces])) if faces else None
    ref_cy = float(np.median([f["cy"] for f in faces])) if faces else None
    envs: dict[str, np.ndarray] = {}
    segments = []
    frame_total = 0
    for idx, t in enumerate(chosen):
        src = sources[t["source"]]
        if t["source"] not in envs:
            x, sr = media.read_wav(reel.resolve(src["wav16"]), 16000)
            envs[t["source"]] = audio.envelope_db(x, sr, 10)
        regions = transcript["sources"][t["source"]]["speech_regions"]
        r = refine(t, envs[t["source"]], 0.01, regions, src["duration"], fps, ccfg)
        ld = media.loudness(reel.resolve(src["wav48"]), r["in"], r["out"] - r["in"])
        v = src.get("video") or {}
        sw, sh = v.get("display_width", 1920), v.get("display_height", 1080)
        f = t["face"]
        realigned = False
        cx, cy = ref_cx, ref_cy
        if f.get("cx") is not None and ref_cx is not None and abs(f["cx"] - ref_cx) > cfg["speaker"]["realign_threshold"]:
            cx, cy, realigned = f["cx"], f["cy"], True
        crop = speaker_crop(sw, sh, panel, cx, cy, cfg["speaker"]["zoom"], cfg["speaker"]["eye_line"])
        out_start = frame_total / fps
        segments.append({
            "index": idx, "beat": t["beat"], "take": t["id"], "source": t["source"], "in": r["in"], "out": r["out"],
            "frames": r["frames"], "duration": round(r["frames"] / fps, 4), "out_start": round(out_start, 4),
            "lead_s": r["lead_s"], "tail_s": r["tail_s"], "notes": r["notes"],
            "lufs": ld["integrated_lufs"], "face": {k: f.get(k) for k in ("cx", "cy", "w", "present_ratio")},
            "crop": crop.as_dict(), "crop_realigned": realigned, "src_size": [sw, sh],
            "text": t["text"],
            "words": [{"text": w["text"], "start": round(out_start + w["start"] - r["in"], 3),
                       "end": round(out_start + w["end"] - r["in"], 3)} for w in t["words"]],
        })
        frame_total += r["frames"]
    lufs = [media.finite(s["lufs"]) for s in segments]
    ref = float(np.median(lufs)) if lufs else -23.0
    clamp = cfg["master"]["take_gain_clamp_db"]
    for s in segments:
        s["gain_db"] = round(min(clamp, max(-clamp, ref - media.finite(s["lufs"]))), 2)
    joins = [{"index": i, "time": segments[i + 1]["out_start"], "left": i, "right": i + 1,
              "crossfade_ms": ccfg["crossfade_ms"]} for i in range(len(segments) - 1)]
    body = {"fps": fps, "layout": layout.describe(), "reference_face": {"cx": ref_cx, "cy": ref_cy},
            "reference_lufs": round(ref, 2), "segments": segments, "joins": joins,
            "duration": round(frame_total / fps, 4)}
    data = {"schema": schema("cuts"), **body, "sha256": canonical_hash(body)}
    write_json(reel.cuts_file, data)
    return data
