"""Stage 4, score: measurable features per take, then the deterministic default pick per beat.

Pick rule: among *eligible* takes (complete, no restart/repeat, fillers <= max, face present when
faces are measurable, >= 1 s), the default is the LAST one recorded. A close call is flagged when
another eligible take's composite score is within ``close_call_gap`` of the pick, or beats it by
more than the gap; 10 s audition clips are exported for every take in a close call.
A beat with no eligible take is marked ``needs_rerecord``.
"""

from __future__ import annotations

import numpy as np

from . import audio, media
from .face import get_detector, summarise
from .reel import Reel, StageError, load_beats, read_json, schema, write_json


def eligibility(t: dict, cfg: dict, faces_measurable: bool) -> list[str]:
    s = cfg["score"]
    reasons = []
    if not t["complete"]:
        reasons.append("incomplete sentence")
    if t["restart"]:
        reasons.append("restart / repeated words inside the take")
    if t["fillers"] > s["max_fillers"]:
        reasons.append(f"{t['fillers']} fillers")
    if t["duration"] < cfg["qa"]["min_clip_s"]:
        reasons.append("shorter than min clip")
    if faces_measurable and t["face"].get("measured") and t["face"].get("present_ratio", 0) < s["min_face_present"]:
        reasons.append("face missing in too many frames")
    if any(f.startswith("beat_mismatch") for f in t["flags"]):
        reasons.append("words match a different beat")
    return reasons


def composite(t: dict, cfg: dict, ref_cx: float | None) -> float:
    w = cfg["score"]["weights"]
    fluency = max(0.0, 1 - 0.25 * t["fillers"] - 0.1 * len(t["internal_pauses"]))
    face = t["face"]
    frontal = face.get("frontal_ratio", 1.0) if face.get("measured") else 1.0
    align = 1.0
    if ref_cx is not None and face.get("cx") is not None:
        align = max(0.0, 1 - abs(face["cx"] - ref_cx) / 0.1)
    loud = 1.0 if t.get("loudness_rel_beat_db") is None else max(0.0, 1 - abs(t["loudness_rel_beat_db"]) / 6)
    pace = max(0.0, 1 - abs(t["wpm"] - cfg["score"]["target_wpm"]) / 60)
    parts = {"completeness": t["completeness"], "fluency": fluency, "frontal": frontal, "alignment": align,
             "loudness": loud, "pace": pace}
    t["score_parts"] = {k: round(v, 3) for k, v in parts.items()}
    return round(sum(w[k] * parts[k] for k in w), 4)


def export_audition(reel: Reel, src: dict, take: dict, seconds: float, label: str) -> str:
    out = reel.p("auditions", f"beat{take['beat']:02d}_{take['id']}{label}.mp4")
    start = max(0.0, take["start"] - 0.1)
    dur = min(seconds, take["end"] - start + 0.15)
    args = ["-v", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}"]
    if src.get("proxy"):
        args += ["-i", str(reel.resolve(src["proxy"])), "-ss", f"{start:.3f}", "-t", f"{dur:.3f}",
                 "-i", str(reel.resolve(src["wav48"])), "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                 "-preset", "veryfast", "-crf", "26", *media.BT709_ARGS]
    else:
        args += ["-i", str(reel.resolve(src["wav48"]))]
    args += ["-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)]
    media.ffmpeg(*args)
    return reel.rel(out)


def run(reel: Reel, cfg: dict, auditions: bool = True) -> dict:
    takes_doc = reel.need(reel.takes_file, "segment")
    sources = {s["id"]: s for s in reel.need(reel.sources_file, "ingest")["sources"]}
    beats = load_beats(reel)
    takes = takes_doc["takes"]
    det = get_detector(cfg)
    scfg = cfg["score"]
    wav_cache: dict[str, tuple[np.ndarray, int]] = {}
    for t in takes:
        src = sources[t["source"]]
        n_words = len(t["words"])
        t["wpm"] = round(n_words / max(t["duration"], 0.1) * 60, 1)
        ld = media.loudness(reel.resolve(src["wav48"]), t["start"], max(0.5, t["duration"]))
        t["loudness_lufs"] = ld["integrated_lufs"]
        t["true_peak_db"] = ld["true_peak_db"]
        if src["id"] not in wav_cache:
            wav_cache[src["id"]] = media.read_wav(reel.resolve(src["wav16"]), 16000)
        x, sr = wav_cache[src["id"]]
        t["variation"] = audio.variation_features(x[int(t["start"] * sr): int(t["end"] * sr)], sr)
        if det is not None and src.get("proxy"):
            pw, ph = src["proxy_size"]
            frames = media.sample_frames(reel.resolve(src["proxy"]), t["start"], t["end"], scfg["face_sample_fps"], pw, ph)
            t["face"] = summarise([(ts, det.detect(fr)) for ts, fr in frames], scfg["frontal_yaw_max"])
        else:
            t["face"] = {"measured": False, "reason": "no detector/model" if det is None else "audio-only source"}
    # loudness relative to the beat median
    for b in beats:
        vals = [media.finite(t["loudness_lufs"]) for t in takes if t["beat"] == b["id"]]
        med = float(np.median(vals)) if vals else None
        for t in takes:
            if t["beat"] == b["id"] and med is not None:
                t["loudness_rel_beat_db"] = round(media.finite(t["loudness_lufs"]) - med, 2)
    faces_measurable = any(t["face"].get("present_ratio", 0) > 0 for t in takes)
    cxs = [t["face"]["cx"] for t in takes if t["face"].get("cx") is not None]
    ref_cx = float(np.median(cxs)) if cxs else None
    for t in takes:
        t["ineligible_reasons"] = eligibility(t, cfg, faces_measurable)
        t["eligible"] = not t["ineligible_reasons"]
        t["score"] = composite(t, cfg, ref_cx)
    scores = {"schema": schema("scores"), "face_detector": det.name if det else None,
              "faces_measurable": faces_measurable, "reference_face_cx": ref_cx, "takes": takes}
    write_json(reel.scores_file, scores)
    selects = build_selects(reel, cfg, beats, takes, sources, auditions)
    return {"scores": scores, "selects": selects}


def build_selects(reel: Reel, cfg: dict, beats: list[dict], takes: list[dict], sources: dict, auditions: bool) -> dict:
    gap = cfg["score"]["close_call_gap"]
    out = []
    for b in beats:
        bt = [t for t in takes if t["beat"] == b["id"]]
        elig = [t for t in bt if t["eligible"]]
        entry = {"beat": b["id"], "text": b["text"],
                 "candidates": [{"take": t["id"], "eligible": t["eligible"], "score": t["score"],
                                 "reasons": t["ineligible_reasons"], "text": t["text"]} for t in bt]}
        if not elig:
            entry.update({"take": None, "status": "needs_rerecord",
                          "reason": "no complete fluent take" if bt else "no takes found"})
            out.append(entry)
            continue
        pick = elig[-1]
        rivals = [t for t in elig if t is not pick and t["score"] >= pick["score"] - gap]
        better = [t for t in elig if t is not pick and t["score"] > pick["score"] + gap]
        entry.update({"take": pick["id"], "status": "ok", "picked_by": "rule:last_complete_fluent",
                      "reason": "last complete fluent take", "close_call": bool(rivals or better),
                      "better_alternatives": [t["id"] for t in better],
                      "close_rivals": [t["id"] for t in rivals if t not in better]})
        if entry["close_call"] and auditions:
            clips = []
            for t in [pick] + rivals:
                label = "_PICK" if t is pick else ""
                clips.append(export_audition(reel, sources[t["source"]], t, cfg["score"]["audition_seconds"], label))
            entry["audition_clips"] = clips
        out.append(entry)
    data = {"schema": schema("selects"), "beats": out,
            "needs_rerecord": [e["beat"] for e in out if e["status"] == "needs_rerecord"]}
    write_json(reel.selects_file, data)
    return data


def override(reel: Reel, beat: int, take_id: str, by: str = "creator") -> dict:
    """Creator (or judge) override: only eligible takes may be chosen."""
    sel = reel.need(reel.selects_file, "score")
    scores = read_json(reel.scores_file)
    take = next((t for t in scores["takes"] if t["id"] == take_id), None)
    if take is None or take["beat"] != beat:
        raise StageError(f"{take_id} is not a take of beat {beat}")
    if not take["eligible"]:
        raise StageError(f"{take_id} failed hard checks: {', '.join(take['ineligible_reasons'])}")
    for e in sel["beats"]:
        if e["beat"] == beat:
            e.update({"take": take_id, "status": "ok", "picked_by": by, "reason": f"override by {by}"})
    sel["needs_rerecord"] = [e["beat"] for e in sel["beats"] if e["status"] == "needs_rerecord"]
    write_json(reel.selects_file, sel)
    return sel
