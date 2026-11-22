"""Deterministic checks (no model calls): files, media specs, word limits, verbatim quotes, dm kit."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .contract import Submission

W, H = 1080, 1350
MAX_HEADLINE_WORDS, MAX_BODY_WORDS = 10, 25
MIN_FRAGMENT = 12          # quote fragments shorter than this are not checked (too generic)


def _issue(level: str, where: str, msg: str) -> dict:
    return {"level": level, "where": where, "msg": msg}   # level: block | fix | note


def words(s: str) -> int:
    return len(re.findall(r"[\w'’₹%.,/-]+", s or ""))


def norm(s: str) -> str:
    s = (s or "").lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[*_`#>|]", " ", s)              # markdown noise
    return re.sub(r"\s+", " ", s).strip()


def fragments(quote: str) -> list[str]:
    parts = re.split(r"…|\.\.\.", quote)
    out = []
    for p in parts:
        p = norm(p).strip(' "\'→-–—:;,.')
        if len(p) >= MIN_FRAGMENT:
            out.append(p)
    return out


def ffprobe(path: Path) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                       capture_output=True, text=True)
    return json.loads(r.stdout or "{}")


def check_media(sub: Submission) -> list[dict]:
    issues = []
    files = sub.raw["post_files"]
    if not 2 <= len(files) <= 20:
        issues.append(_issue("block", "POST", f"{len(files)} items; Instagram allows 2-20"))
    if len(files) != len(sub.slides):
        issues.append(_issue("fix", "POST", f"{len(files)} files but {len(sub.slides)} slides in SUBMISSION"))
    for i, rel in enumerate(files, 1):
        p = sub.media(rel)
        where = f"slide {i} ({rel})"
        if not p.exists():
            issues.append(_issue("block", where, "file missing"))
            continue
        suf = p.suffix.lower()
        if suf in (".jpg", ".jpeg"):
            from PIL import Image
            with Image.open(p) as im:
                if im.format != "JPEG":
                    issues.append(_issue("block", where, f"still is {im.format}, Graph API needs JPEG"))
                if im.size != (W, H):
                    issues.append(_issue("block", where, f"size {im.size}, need {W}x{H}"))
        elif suf == ".mp4":
            info = ffprobe(p)
            v = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
            a = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
            dur = float(info.get("format", {}).get("duration", 0))
            if not v:
                issues.append(_issue("block", where, "no video stream"))
                continue
            if (v[0].get("width"), v[0].get("height")) != (W, H):
                issues.append(_issue("block", where, f"size {v[0].get('width')}x{v[0].get('height')}"))
            if v[0].get("codec_name") != "h264":
                issues.append(_issue("block", where, f"codec {v[0].get('codec_name')}, need h264"))
            if not 3 <= dur <= 60:
                issues.append(_issue("block", where, f"duration {dur:.1f}s, need 3-60 s"))
            if not a:
                issues.append(_issue("fix", where, "no audio track (add a silent AAC track)"))
        else:
            issues.append(_issue("block", where, f"unsupported type {suf}"))
    n_video = sum(1 for f in files if f.lower().endswith(".mp4"))
    if files and n_video * 3 < len(files):
        issues.append(_issue("fix", "POST", f"{n_video} video slides of {len(files)}; template wants ≥ 1 in 3"))
    cs = sub.raw.get("contact_sheet")
    if not cs or not sub.media(cs).exists():
        issues.append(_issue("block", "contact_sheet", "missing; the visual review needs it"))
    return issues


def check_text(sub: Submission) -> list[dict]:
    issues = []
    runs_dir = sub.out(sub.raw["runs_dir"])
    run_text_cache: dict[str, str] = {}

    def run_text(rel: str | None) -> str:
        key = rel or "*"
        if key not in run_text_cache:
            if rel:
                p = sub.out(rel)
                run_text_cache[key] = norm(p.read_text()) if p and p.exists() else ""
            else:
                run_text_cache[key] = norm(" ".join(p.read_text() for p in runs_dir.rglob("*.md"))) \
                    if runs_dir and runs_dir.exists() else ""
        return run_text_cache[key]

    for s in sub.slides:
        where = f"slide {s.get('n')}"
        hw, bw = words(s.get("headline", "")), words(s.get("body", ""))
        if hw > MAX_HEADLINE_WORDS:
            issues.append(_issue("fix", where, f"headline {hw} words (≤ {MAX_HEADLINE_WORDS})"))
        if bw > MAX_BODY_WORDS:
            issues.append(_issue("fix", where, f"body {bw} words (≤ {MAX_BODY_WORDS})"))
        for q in s.get("quotes", []) or []:
            src = q.get("run")
            if src and not (sub.out(src) and sub.out(src).exists()):
                issues.append(_issue("block", where, f"quote source {src} does not exist"))
                continue
            hay = run_text(src)
            missing = [f for f in fragments(q.get("text", "")) if f not in hay]
            if missing:
                issues.append(_issue("block", where,
                                     f"quote not verbatim in {src or 'runs/'}: {missing[0][:80]!r}"))
    for key in ("caption_file", "pinned_comment_file"):
        p = sub.out(sub.raw.get(key))
        if not p or not p.exists() or not p.read_text().strip():
            issues.append(_issue("block" if key == "caption_file" else "fix", key, "missing or empty"))
    kw = sub.raw.get("keyword")
    if kw:
        dm = sub.out(sub.raw.get("dm_kit_dir"))
        if not dm or not dm.exists() or not any(dm.iterdir()):
            issues.append(_issue("block", "dm_kit", f"keyword {kw} but no dm_kit"))
        cap = sub.out(sub.raw["caption_file"])
        if cap and cap.exists() and kw.lower() not in cap.read_text().lower():
            issues.append(_issue("fix", "caption", f"caption does not mention keyword {kw}"))
    if not sub.raw.get("facts_file") or not sub.out(sub.raw["facts_file"]).exists():
        issues.append(_issue("fix", "facts_file", "missing FACTS file; the judge scores accuracy without it"))
    return issues


def run_all(sub: Submission) -> list[dict]:
    return check_media(sub) + check_text(sub)
