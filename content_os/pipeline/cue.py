"""Cue-sheet timing helpers shared by cutpoints, render, review and the SFX cue list.

Covers per-beat playback speed, the cold open (a beat repeated as the first segment under its own
beat id), sound effects anchored to beat starts / words / visual cues, and music drops. Everything
here is pure (no ffmpeg) so it is unit-tested directly.
"""

from __future__ import annotations

import re
from pathlib import Path

from .reel import StageError, read_json


def by_beat(cue: dict | None) -> dict[int, dict]:
    return {int(b["beat"]): b for b in (cue or {}).get("beats", [])}


def source_beat(seg: dict) -> int:
    """The script beat a segment speaks (a cold-open segment carries its own id in ``beat``)."""
    return int(seg.get("source_beat", seg["beat"]))


def entry_for(cue: dict | None, beat: int, src_beat: int | None = None) -> dict:
    """Cue-sheet entry of a beat; a cold-open beat without an entry inherits its source beat's."""
    beats = by_beat(cue)
    if beat in beats:
        return beats[beat]
    if src_beat is not None and src_beat in beats:
        return beats[src_beat]
    return {}


def cold_open(cue: dict | None) -> dict | None:
    co = (cue or {}).get("cold_open")
    if not co:
        return None
    return {"beat": int(co["beat"]), "id": int(co.get("id", 0)), "speed": float(co.get("speed", 1.0))}


def speed_for(cue: dict | None, beat: int, scfg: dict | None = None) -> float:
    """Per-beat ``speed`` override, else the cue sheet's top-level ``speed``, else 1.0."""
    scfg = scfg or {"min": 0.5, "max": 2.0}
    e = by_beat(cue).get(int(beat), {})
    sp = float(e.get("speed", (cue or {}).get("speed", 1.0)))
    if not scfg["min"] <= sp <= scfg["max"]:
        raise StageError(f"beat {beat}: speed {sp} outside {scfg['min']}..{scfg['max']}")
    return sp


def out_frames(src_frames: int, speed: float) -> int:
    return src_frames if speed == 1.0 else max(1, int(round(src_frames / speed)))


# ------------------------------------------------------------------ beat windows / words

def beat_windows(cuts: dict) -> dict[int, tuple[float, float]]:
    win: dict[int, list[float]] = {}
    for s in cuts["segments"]:
        a, b = s["out_start"], s["out_start"] + s["duration"]
        if s["beat"] in win:
            win[s["beat"]][1] = b
        else:
            win[s["beat"]] = [a, b]
    return {k: (v[0], v[1]) for k, v in win.items()}


def _norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(t).lower())


def beat_words(cuts: dict, beat: int) -> list[dict]:
    return [w for s in cuts["segments"] if s["beat"] == beat for w in s["words"]]


def find_word(cuts: dict, beat: int, word: str, occurrence: int = 1) -> dict | None:
    """Output-time word of a beat ("94" matches "94."; a multi-word phrase matches its first word)."""
    words = beat_words(cuts, beat)
    toks = [_norm(t) for t in str(word).split()]
    seen = 0
    for i in range(len(words) - len(toks) + 1):
        if all(_norm(words[i + k]["text"]) == toks[k] for k in range(len(toks))):
            seen += 1
            if seen == occurrence:
                return {**words[i], "end": words[i + len(toks) - 1]["end"],
                        "text": " ".join(w["text"] for w in words[i:i + len(toks)])}
    return None


# ------------------------------------------------------------------ sound effects

def visual_manifest(cue: dict | None, root: Path | None, cuts: dict) -> dict[int, list[dict]]:
    """Resolved visual cues per beat (beat-relative t/dur) from the clips' visuals.json, only when the
    clips were rendered for these exact cuts."""
    d = (cue or {}).get("visual_clips")
    if not d or root is None:
        return {}
    p = Path(d).expanduser()
    p = (p if p.is_absolute() else root / d) / "visuals.json"
    if not p.exists():
        return {}
    m = read_json(p)
    if m.get("cuts_sha256") != cuts.get("sha256"):
        return {}
    return {int(b["beat"]): b.get("cues", []) for b in m.get("beats", [])}


def _sfx_type(s: dict) -> str:
    return s.get("type") or Path(s["path"]).stem.split("_")[0]


def resolve_sfx(cue: dict | None, cuts: dict, root: Path | None = None) -> list[dict]:
    """Every SFX of the cue sheet at an output time.

    Per entry (beat-relative): ``at`` seconds from the beat start (may be negative: lands before
    the beat); or ``word`` (+ ``occurrence``, ``offset``) = that word's onset; or ``visual_cue``
    {target, action, edge: start|end} (+ ``offset``) from the visual clips' manifest, falling back
    to ``word``/``at`` when the clips are missing or stale. Level: ``level_db`` relative to the voice
    target (by the effect's max momentary loudness) or legacy ``gain_db`` (plain gain on the file). ``word_offset``
    (default ``offset``) applies to the word anchor only, so a visual-cue entry can carry its own
    spoken-word fallback.
    """
    windows = beat_windows(cuts)
    vis = visual_manifest(cue, root, cuts)
    out = []
    for b in (cue or {}).get("beats", []):
        beat = int(b["beat"])
        if beat not in windows:
            continue
        b0 = windows[beat][0]
        for s in b.get("sfx", []) or []:
            off = float(s.get("offset", 0.0))
            rel, anchor = None, None
            vc = s.get("visual_cue")
            if vc:
                hit = next((c for c in vis.get(beat, []) if c.get("target") == vc["target"]
                            and ("action" not in vc or c.get("action") == vc["action"])), None)
                if hit is not None:
                    edge = vc.get("edge", "start")
                    rel = float(hit["t"]) + (float(hit.get("dur", 0)) if edge == "end" else 0.0) + off
                    anchor = f"visual {vc.get('action', 'cue')} {vc['target']} ({edge})"
            if rel is None and s.get("word") is not None:
                w = find_word(cuts, beat, s["word"], int(s.get("occurrence", 1)))
                if w is None:
                    raise StageError(f"beat {beat}: sfx word {s['word']!r} not found in the cut")
                rel = w["start"] - b0 + float(s.get("word_offset", off))  # word_offset: fallback-only offset
                anchor = f"word \"{w['text']}\""
            if rel is None:
                rel = float(s.get("at", 0.0))
                anchor = f"beat {beat} start {rel:+.2f} s" if rel else f"beat {beat} start"
            item = {"beat": beat, "path": s["path"], "type": _sfx_type(s), "at": round(b0 + rel, 4),
                    "anchor": anchor, "label": s.get("label", "")}
            if "level_db" in s:
                item["level_db"] = float(s["level_db"])
            else:
                item["gain_db"] = float(s.get("gain_db", -12))
            out.append(item)
    return sorted(out, key=lambda x: x["at"])


def words_overlapping(cuts: dict, a: float, b: float) -> list[str]:
    return [w["text"] for s in cuts["segments"] for w in s["words"] if w["start"] < b and w["end"] > a]


# ------------------------------------------------------------------ music drops

def resolve_music_drops(cue: dict | None, cuts: dict) -> list[dict]:
    """``music_drops`` entries as output-time envelopes.

    ``{"from_beat": 15, "to_beat": 16, "level_db": -60, "fade_out": 0.25, "fade_in": 0.6}``: fade starts
    at from_beat's start, held down to to_beat's end, fades back in after it.
    ``{"before_beat": 1, "duration": 0.3, ...}``: down (fully) for the ``duration`` before that beat
    starts, back up from its start. ``{"start": s, "end": e}``: explicit output seconds (held span).
    """
    windows = beat_windows(cuts)
    out = []
    for d in (cue or {}).get("music_drops", []) or []:
        fo, fi = float(d.get("fade_out", 0.25)), float(d.get("fade_in", 0.6))
        if "from_beat" in d:
            a = windows[int(d["from_beat"])][0]
            e = windows[int(d.get("to_beat", d["from_beat"]))][1]
            r = {"fade_out_start": a, "hold_start": a + fo, "hold_end": e, "fade_in_end": e + fi}
        elif "before_beat" in d:
            b = windows[int(d["before_beat"])][0]
            hs = b - float(d.get("duration", 0.3))
            r = {"fade_out_start": hs - fo, "hold_start": hs, "hold_end": b, "fade_in_end": b + fi}
        else:
            hs, e = float(d["start"]), float(d["end"])
            r = {"fade_out_start": hs - fo, "hold_start": hs, "hold_end": e, "fade_in_end": e + fi}
        r = {k: round(max(0.0, v), 4) for k, v in r.items()}
        r["level_db"] = float(d.get("level_db", -60))
        out.append(r)
    return out


def drop_gain(drops: list[dict], t: float) -> float:
    """Linear music gain at time t (reference implementation of :func:`drop_expr`)."""
    g = 1.0
    for d in drops:
        lvl = 10 ** (d["level_db"] / 20)
        fo = max(d["hold_start"] - d["fade_out_start"], 1e-3)
        fi = max(d["fade_in_end"] - d["hold_end"], 1e-3)
        depth = min(min(max((t - d["fade_out_start"]) / fo, 0.0), 1.0), min(max((d["fade_in_end"] - t) / fi, 0.0), 1.0))
        g *= 1 - (1 - lvl) * depth
    return g


def drop_expr(drops: list[dict]) -> str:
    """ffmpeg ``volume`` expression (eval=frame) equal to :func:`drop_gain`."""
    parts = []
    for d in drops:
        lvl = 10 ** (d["level_db"] / 20)
        fo = max(d["hold_start"] - d["fade_out_start"], 1e-3)
        fi = max(d["fade_in_end"] - d["hold_end"], 1e-3)
        parts.append(f"(1-{1 - lvl:.6f}*min(clip((t-{d['fade_out_start']:.4f})/{fo:.4f},0,1),"
                     f"clip(({d['fade_in_end']:.4f}-t)/{fi:.4f},0,1)))")
    return "*".join(parts) or "1"
