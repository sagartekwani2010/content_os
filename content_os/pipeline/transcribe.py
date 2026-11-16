"""Stage 2, transcribe: word-level transcript per source.

Engines (``transcribe.engine``):
- ``whisper_cpp`` (default, local): whisper-cli with ``-ojf`` (full JSON, per-token data) and
  ``-dtw <preset> -nfa`` (DTW token timestamps; DTW needs flash attention off). Audio is cut into
  chunks at silences by our own energy VAD and all chunks go through one whisper-cli call, so the
  model loads once and no chunk is longer than ``chunk_max_s``. whisper.cpp's own ``--vad`` is
  available behind ``whisper_vad: true`` but in 1.9.3 its token offsets come back in VAD-compressed
  time, so it is off by default.
- ``openai`` (opt-in, uploads the voice): ``whisper-1`` with ``response_format=verbose_json`` and
  ``timestamp_granularities=["word"]``. The key is read from ``OPENAI_API_KEY`` only.

Word boundaries are then snapped to energy-detected speech regions so every pause edge is exact
at 10 ms; inside continuous speech the ASR/DTW timing is kept.
"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

import numpy as np

from . import audio, media
from .reel import Reel, StageError, read_json, schema, write_json

SR = 16000


# ---------------------------------------------------------------- chunking

def make_chunks(regions: list[list[float]], duration: float, max_len: float, pad: float = 0.25,
                split_gap: float = 0.5) -> list[list[float]]:
    """Group speech regions into ASR chunks. A pause >= split_gap always starts a new chunk: whisper
    tends to drop a sentence that repeats inside one 30 s window, which is exactly what retakes are."""
    if not regions:
        return []
    groups: list[list[list[float]]] = [[regions[0]]]
    for r in regions[1:]:
        if r[0] - groups[-1][-1][1] >= split_gap or r[1] - groups[-1][0][0] + 2 * pad > max_len:
            groups.append([r])
        else:
            groups[-1].append(r)
    chunks = []
    for gi, g in enumerate(groups):
        start = g[0][0] - pad
        end = g[-1][1] + pad
        if gi > 0:
            start = max(start, (groups[gi - 1][-1][1] + g[0][0]) / 2)
        if gi + 1 < len(groups):
            end = min(end, (g[-1][1] + groups[gi + 1][0][0]) / 2)
        chunks.append([round(max(0.0, start), 3), round(min(duration, end), 3)])
    return chunks


# ---------------------------------------------------------------- whisper.cpp

def dtw_preset(model_path: str, setting: str) -> str | None:
    if setting not in ("auto", None, ""):
        return None if setting == "off" else setting
    m = re.search(r"ggml-(tiny|base|small|medium|large-v[123](?:-turbo)?|large)(\.en)?", Path(model_path).name)
    if not m:
        return None
    name = m.group(1) + (m.group(2) or "")
    return name.replace("large-v3-turbo", "large.v3.turbo").replace("large-v", "large.v")


def whisper_words(js: dict) -> list[dict]:
    """Merge whisper.cpp tokens (-ojf) into words. Times are in seconds relative to the input file."""
    words: list[dict] = []
    for seg in js.get("transcription", []):
        for tok in seg.get("tokens", []):
            text = tok.get("text", "")
            if not text or text.startswith("[_") or text.startswith("<|"):
                continue
            t_dtw = tok.get("t_dtw", -1)
            anchor = t_dtw / 100.0 if t_dtw is not None and t_dtw >= 0 else tok["offsets"]["from"] / 1000.0
            starts_word = text.startswith(" ") or not words
            stripped = text.strip()
            if not stripped:
                continue
            is_punct = not re.search(r"\w", stripped)
            if starts_word and not is_punct:
                words.append({"text": stripped, "anchor": anchor, "t1": tok["offsets"]["to"] / 1000.0,
                              "p": [tok.get("p", 1.0)]})
            elif words:
                words[-1]["text"] += stripped
                if not is_punct:
                    words[-1]["p"].append(tok.get("p", 1.0))
                    words[-1]["t1"] = tok["offsets"]["to"] / 1000.0
    for w in words:
        w["conf"] = round(float(np.mean(w.pop("p"))), 3)
    return words


def run_whisper_cpp(chunk_files: list[Path], tcfg: dict) -> list[dict]:
    model = Path(tcfg["model"]).expanduser()
    if not model.exists():
        raise StageError(f"whisper model missing: {model} (run `python -m content_os.pipeline setup`)")
    base = [tcfg["whisper_cli"], "-m", str(model), "-l", tcfg["language"], "-ojf", "-np",
            "-t", str(tcfg["threads"]), "-mc", "64"]
    preset = dtw_preset(str(model), tcfg["dtw_preset"])
    if preset:
        base += ["-dtw", preset, "-nfa"]
    if tcfg.get("whisper_vad"):
        base += ["--vad", "-vm", str(Path(tcfg["vad_model"]).expanduser())]
    attempts = [base + ["-ng"]] if tcfg["gpu"] in (False, "off", "cpu") else [base, base + ["-ng"]]
    for p in chunk_files:
        Path(str(p) + ".json").unlink(missing_ok=True)
    last_err = ""
    for cmd in attempts:
        proc = media.run(cmd + [str(p) for p in chunk_files], check=False)
        outs = [Path(str(p) + ".json") for p in chunk_files]
        if proc.returncode == 0 and all(o.exists() for o in outs):
            return [read_json(o) for o in outs]
        last_err = (proc.stderr or "")[-1500:]
    raise StageError(f"whisper-cli failed:\n{last_err}")


# ---------------------------------------------------------------- openai

def run_openai(chunk_files: list[Path], tcfg: dict) -> list[list[dict]]:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise StageError("engine openai needs OPENAI_API_KEY in the environment (never in a file)")
    from openai import OpenAI

    client = OpenAI(api_key=key)
    results = []
    for p in chunk_files:
        if p.stat().st_size > 24 * 1024 * 1024:
            raise StageError(f"{p.name} exceeds the 25 MB upload limit; lower openai_chunk_max_s")
        with open(p, "rb") as fh:
            resp = client.audio.transcriptions.create(
                file=fh, model=tcfg["openai_model"], response_format="verbose_json",
                timestamp_granularities=["word"], language=tcfg["language"])
        results.append(openai_words(resp))
    return results


def openai_words(resp) -> list[dict]:
    raw = getattr(resp, "words", None)
    if raw is None and isinstance(resp, dict):
        raw = resp.get("words")
    out = []
    for w in raw or []:
        get = (lambda k: w.get(k)) if isinstance(w, dict) else (lambda k: getattr(w, k))
        out.append({"text": get("word").strip(), "anchor": float(get("start")), "t1": float(get("end")), "conf": None})
    return out


# ---------------------------------------------------------------- snapping

def snap_words(words: list[dict], regions: list[list[float]], lead: float) -> list[dict]:
    """Give each word start/end; pause edges come from the energy VAD regions."""
    if not words:
        return []
    assigned: list[int | None] = []
    prev = 0
    for w in words:
        a = w["anchor"]
        best, best_d = None, 0.6
        for ri in range(prev, len(regions)):
            r0, r1 = regions[ri]
            if r0 - 0.6 > a:
                break
            d = 0.0 if r0 <= a <= r1 else min(abs(a - r0), abs(a - r1))
            if d < best_d:
                best, best_d = ri, d
        if best is not None:
            prev = best
        assigned.append(best)
    out = []
    for i, w in enumerate(words):
        ri = assigned[i]
        start = w["anchor"] - lead
        if ri is not None:
            r0, r1 = regions[ri]
            first = i == 0 or assigned[i - 1] != ri
            start = r0 if first else min(max(start, r0), r1 - 0.02)
        out.append({"text": w["text"], "start": start, "region": ri, "conf": w.get("conf"),
                    "anchor": round(w["anchor"], 3)})
    for i, w in enumerate(out):
        if i > 0 and w["start"] < out[i - 1]["start"] + 0.02:
            w["start"] = out[i - 1]["start"] + 0.02
        ri = w["region"]
        nxt = out[i + 1] if i + 1 < len(out) else None
        if ri is not None and (nxt is None or nxt["region"] != ri):
            end = regions[ri][1]
        elif nxt is not None:
            end = nxt["start"]
        else:
            end = w["start"] + 0.3
        w["end"] = max(end, w["start"] + 0.02)
    for w in out:
        w["start"], w["end"] = round(w["start"], 3), round(w["end"], 3)
    return out


# ---------------------------------------------------------------- stage

def transcribe_file(wav16: Path, workdir: Path, cfg: dict, engine: str) -> dict:
    tcfg = cfg["transcribe"]
    x, sr = media.read_wav(wav16, SR)
    duration = len(x) / sr
    regions = audio.speech_regions(x, sr, cfg["vad"])
    max_len = tcfg["chunk_max_s"] if engine == "whisper_cpp" else tcfg["openai_chunk_max_s"]
    chunks = make_chunks(regions, duration, max_len, split_gap=tcfg["chunk_split_gap_s"])
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)
    files = []
    for k, (c0, c1) in enumerate(chunks):
        f = workdir / f"chunk_{k:03d}.wav"
        media.ffmpeg("-v", "error", "-ss", f"{c0:.3f}", "-t", f"{c1 - c0:.3f}", "-i", str(wav16),
                     "-c:a", "pcm_s16le", str(f))
        files.append(f)
    words: list[dict] = []
    lead = 0.0
    if files:
        if engine == "whisper_cpp":
            per_chunk = [whisper_words(js) for js in run_whisper_cpp(files, tcfg)]
            lead = tcfg["dtw_lead_s"] if dtw_preset(tcfg["model"], tcfg["dtw_preset"]) else 0.0
        elif engine == "openai":
            per_chunk = run_openai(files, tcfg)
            lead = 0.0
        else:
            raise StageError(f"unknown engine {engine}")
        for (c0, _), ws in zip(chunks, per_chunk):
            for w in ws:
                w["anchor"] += c0
                words.append(w)
    return {"duration": round(duration, 3), "speech_regions": regions, "chunks": chunks,
            "words": snap_words(words, regions, lead)}


def run(reel: Reel, cfg: dict, engine: str | None = None) -> dict:
    sources = reel.need(reel.sources_file, "ingest")["sources"]
    engine = engine or cfg["transcribe"]["engine"]
    out = {"schema": schema("transcript"), "engine": engine,
           "model": Path(cfg["transcribe"]["model"]).name if engine == "whisper_cpp" else cfg["transcribe"]["openai_model"],
           "sources": {}}
    lines = []
    for s in sources:
        res = transcribe_file(reel.resolve(s["wav16"]), reel.work / "asr" / s["id"], cfg, engine)
        out["sources"][s["id"]] = res
        for ri, (r0, r1) in enumerate(res["speech_regions"]):
            txt = " ".join(w["text"] for w in res["words"] if w["region"] == ri)
            if txt:
                lines.append(f"[{s['id']} {r0:8.2f}-{r1:8.2f}] {txt}")
    write_json(reel.transcript_file, out)
    reel.p("transcript.txt").write_text("\n".join(lines) + "\n")
    return out
