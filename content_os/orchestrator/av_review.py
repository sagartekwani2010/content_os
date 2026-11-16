"""Audio/video delivery review through OpenAI, because Claude cannot hear.

The final MP4's audio (mono 16 kHz WAV, capped at ``max_audio_seconds``) goes to an audio-input chat
model (``av_review.audio_model``; Chat Completions ``input_audio`` content part, base64 WAV) for energy,
clarity, pacing and music balance. Sampled frames (when ffmpeg is available) go to
``av_review.vision_model`` for a framing/legibility check. Both models come from
config/orchestrator.yaml.

The key is read from the macOS Keychain (``security find-generic-password -s content_os_openai -a $USER
-w``) or OPENAI_API_KEY, held in memory only, never logged or written. No key -> status
"skipped: no key". The review is advisory: the creator's final-listen gate is never auto-approved.
"""

from __future__ import annotations

import base64
import getpass
import json
import os
import re
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Any, Callable

from . import settings
from .state import now, sha256_file

AUDIO_PROMPT = """You are reviewing the audio of a short vertical video (Instagram Reel) narrated by its creator.
Listen to the whole clip and judge DELIVERY and MIX only (not the topic). Return ONLY a JSON object:
{"energy": {"score": 1-5, "notes": str}, "clarity": {"score": 1-5, "notes": str},
 "pacing": {"score": 1-5, "words_per_minute_estimate": int, "notes": str},
 "music_balance": {"score": 1-5, "music_present": bool, "notes": str},
 "issues": [{"at_s": number or null, "issue": str, "severity": "low|medium|high"}],
 "transcript_excerpt": str, "overall": str}
Scores: 5 = ready to post. Be specific with timestamps. If you cannot hear something, say so."""

FRAMES_PROMPT = """These are frames sampled evenly from a short vertical reel (times in seconds given in order).
Check: speaker framing and eye line, caption legibility and placement (clear of the bottom 250 px and
right 120 px Instagram UI), visual clutter, black or broken frames. Return ONLY a JSON object:
{"framing": str, "captions": str, "issues": [{"at_s": number, "issue": str, "severity": "low|medium|high"}],
 "overall": str}"""


def _cfg() -> dict[str, Any]:
    return settings.load()["av_review"]


def get_key() -> str | None:
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    try:
        out = subprocess.run(["security", "find-generic-password", "-s", _cfg()["keychain_service"],
                              "-a", getpass.getuser(), "-w"], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    k = out.stdout.strip()
    return k or None


def _default_client(key: str) -> Any:
    from openai import OpenAI

    return OpenAI(api_key=key, timeout=_cfg()["timeout_seconds"], max_retries=1)


CLIENT_FACTORY: Callable[[str], Any] = _default_client


def _ffmpeg() -> str | None:
    path = os.pathsep.join([*settings.tool_path(), os.environ.get("PATH", "")])
    return shutil.which("ffmpeg", path=path)


def extract_audio(src: Path, dest: Path) -> dict[str, Any]:
    cfg = _cfg()
    sr, cap = int(cfg["audio_sample_rate"]), float(cfg["max_audio_seconds"])
    ff = _ffmpeg()
    if ff:
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(src), "-t", str(cap), "-vn", "-ac", "1",
                        "-ar", str(sr), "-c:a", "pcm_s16le", str(dest)], check=True, timeout=300)
        tool = "ffmpeg"
    else:
        # macOS built-in fallback (no ffmpeg): decodes AAC/MP4/M4A/AIFF/WAV.
        subprocess.run(["afconvert", "-f", "WAVE", "-d", f"LEI16@{sr}", "-c", "1", str(src), str(dest)],
                       check=True, timeout=300, capture_output=True)
        tool = "afconvert"
    with wave.open(str(dest), "rb") as w:
        frames, rate = w.getnframes(), w.getframerate()
        duration = frames / rate
        if duration > cap:
            data = w.readframes(int(cap * rate))
            params = w.getparams()
        else:
            data = None
    if data is not None:
        with wave.open(str(dest), "wb") as w:
            w.setparams(params)
            w.writeframes(data)
    return {"tool": tool, "source_duration_s": round(duration, 2), "sent_seconds": round(min(duration, cap), 2)}


def extract_frames(src: Path, dest_dir: Path, duration: float) -> list[tuple[float, Path]]:
    ff = _ffmpeg()
    n = int(_cfg()["frames"])
    if not ff or n <= 0 or duration <= 0:
        return []
    out = []
    for i in range(n):
        t = duration * (i + 0.5) / n
        p = dest_dir / f"frame_{i:02d}.jpg"
        subprocess.run([ff, "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(src), "-frames:v", "1",
                        "-vf", "scale=432:-2", "-q:v", "5", str(p)], check=False, timeout=60)
        if p.exists():
            out.append((round(t, 2), p))
    return out


def _parse_json(text: str) -> dict[str, Any]:
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return {"unparsed": text}
    try:
        return json.loads(m.group(0))
    except ValueError:
        return {"unparsed": text}


def review(src: Path, out_dir: Path, *, key: str | None = None) -> dict[str, Any]:
    cfg = _cfg()
    out_dir.mkdir(parents=True, exist_ok=True)
    base = {"at": now(), "source": settings.tilde(src), "audio_model": cfg["audio_model"],
            "vision_model": cfg["vision_model"], "advisory": True,
            "note": "Advisory only; the creator's final-listen gate stays with the creator."}
    if not src.exists():
        return _save(out_dir, {**base, "status": "skipped: no final file"})
    key = key or get_key()
    if not key:
        return _save(out_dir, {**base, "status": "skipped: no key"})
    base["source_sha256"] = sha256_file(src)[:16]
    client = CLIENT_FACTORY(key)
    with tempfile.TemporaryDirectory(prefix="content_os_av_") as tmp:
        tmpd = Path(tmp)
        wav = tmpd / "audio.wav"
        try:
            meta = extract_audio(src, wav)
        except (subprocess.CalledProcessError, OSError, wave.Error) as exc:
            return _save(out_dir, {**base, "status": f"error: audio extraction failed: {exc}"})
        b64 = base64.b64encode(wav.read_bytes()).decode()
        result: dict[str, Any] = {**base, "audio": meta}
        try:
            resp = client.chat.completions.create(
                model=cfg["audio_model"], modalities=["text"],
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": AUDIO_PROMPT},
                    {"type": "input_audio", "input_audio": {"data": b64, "format": "wav"}}]}])
            text = resp.choices[0].message.content or ""
            result["audio_review"] = _parse_json(text)
            result["audio_usage"] = _usage(resp)
        except Exception as exc:  # noqa: BLE001 - surfaced in the report, never fatal for the gate
            result["audio_error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
        frames = extract_frames(src, tmpd, meta["source_duration_s"])
        if frames:
            content: list[dict[str, Any]] = [{"type": "text", "text": FRAMES_PROMPT + "\nTimes: " +
                                              ", ".join(str(t) for t, _ in frames)}]
            for _, p in frames:
                content.append({"type": "image_url", "image_url": {
                    "url": "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode(), "detail": "low"}})
            try:
                resp = client.chat.completions.create(model=cfg["vision_model"],
                                                      messages=[{"role": "user", "content": content}])
                result["frames_review"] = _parse_json(resp.choices[0].message.content or "")
                result["frames_usage"] = _usage(resp)
            except Exception as exc:  # noqa: BLE001
                result["frames_error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
        else:
            result["frames_review"] = None
            result["frames_note"] = "frames not sampled (ffmpeg not found or frames: 0)"
    ok = "audio_review" in result
    result["status"] = "done" if ok else f"error: {result.get('audio_error', 'no audio review')}"
    result["provenance"] = {"provider": "openai", "audio_model": cfg["audio_model"],
                            "vision_model": cfg["vision_model"] if frames else None, "prompt": "av_review@1"}
    return _save(out_dir, result)


def _usage(resp: Any) -> dict[str, Any]:
    u = getattr(resp, "usage", None)
    if u is None:
        return {}
    d = u.model_dump() if hasattr(u, "model_dump") else dict(u)
    return {k: d.get(k) for k in ("prompt_tokens", "completion_tokens", "total_tokens")} | {
        "model": getattr(resp, "model", None)}


def _save(out_dir: Path, result: dict[str, Any]) -> dict[str, Any]:
    j = out_dir / "av_review.json"
    md = out_dir / "av_review.md"
    j.write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    md.write_text(render_md(result), encoding="utf-8")
    result["files"] = {"av_review.json": str(j), "av_review.md": str(md)}
    return result


def render_md(r: dict[str, Any]) -> str:
    lines = [f"# A/V review ({r.get('at')})", "", f"Status: **{r.get('status')}**. {r.get('note')}", "",
             f"- Source: `{r.get('source')}` (sha256 {r.get('source_sha256', '-')})",
             f"- Audio model: `{r.get('audio_model')}`; frames model: `{r.get('vision_model')}`"]
    a = r.get("audio_review") or {}
    if a:
        lines += ["", "## Audio"]
        for k in ("energy", "clarity", "pacing", "music_balance"):
            v = a.get(k) or {}
            if isinstance(v, dict):
                lines.append(f"- **{k}:** {v.get('score', '?')}/5 · {v.get('notes', '')}")
        for i in a.get("issues") or []:
            lines.append(f"- issue @ {i.get('at_s')} s ({i.get('severity')}): {i.get('issue')}")
        if a.get("overall"):
            lines += ["", a["overall"]]
        if a.get("unparsed"):
            lines += ["", str(a["unparsed"])[:2000]]
    if r.get("audio_error"):
        lines += ["", f"Audio error: {r['audio_error']}"]
    f = r.get("frames_review")
    if f:
        lines += ["", "## Frames", f"- framing: {f.get('framing', '')}", f"- captions: {f.get('captions', '')}"]
        for i in f.get("issues") or []:
            lines.append(f"- issue @ {i.get('at_s')} s ({i.get('severity')}): {i.get('issue')}")
    elif r.get("frames_note"):
        lines += ["", f"Frames: {r['frames_note']}"]
    if r.get("frames_error"):
        lines += ["", f"Frames error: {r['frames_error']}"]
    return "\n".join(lines) + "\n"
