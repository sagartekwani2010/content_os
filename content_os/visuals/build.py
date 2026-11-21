"""Render every beat of a reel's visual_cues.json to ``<out>/beat_NN.mp4`` + ``visuals.json``.

Word timings come from ``work/cuts.json`` (the selected takes, output timeline); a beat's clip runs
from its first segment's start to its last segment's end, so clip time 0 == the moment the pipeline
switches to that beat. ``--preview`` without cuts.json uses default lengths and proportional cue times.
"""

from __future__ import annotations

import glob
import json
from pathlib import Path

from content_os.pipeline.reel import canonical_hash

from . import SCHEMA
from .cues import default_duration
from .render import FPS, BeatRenderer, encode, still
from .doodles import load_image
from .facts import load_lunch, load_meals
from .script import beat_line, load_lines

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = "visuals.json"


def load_sheet(path: Path) -> dict:
    """Read the visual spec and attach each beat's line from the teleprompter it names (default
    TELEPROMPTER.md next to it). Lunch facts are registered from the estimates log when configured."""
    path = Path(path)
    sheet = json.loads(path.read_text())
    if sheet.get("schema") != SCHEMA:
        raise ValueError(f"{path}: schema must be {SCHEMA}")
    script = path.parent / sheet.get("script", "TELEPROMPTER.md")
    lines = load_lines(script)
    sheet["_script"] = str(script)
    from . import rough
    rough.set_theme(sheet.get("theme"))  # "paper" (default) | "dark" | "cold" | {"#old": "#new"}
    sheet["_unspecced_beats"] = sorted(set(lines) - {int(b["beat"]) for b in sheet["beats"]})
    for b in sheet["beats"]:
        b["line"] = beat_line(b, lines)
    lunch = sheet.get("params", {}).get("lunch", {})
    if lunch.get("log") and lunch.get("log_id"):
        load_lunch(lunch["log"], lunch["log_id"])
    meals = sheet.get("params", {}).get("meals", {})
    if meals.get("log") and meals.get("ids"):
        load_meals(meals["log"], meals["ids"])
    return sheet


def spoken_line(beat: dict, params: dict | None = None) -> str:
    return beat["line"]


def _resolve_path(p: str | None, reel_dir: Path) -> Path | None:
    if not p:
        return None
    q = Path(p).expanduser()
    if q.is_absolute():
        return q
    for base in (reel_dir, REPO_ROOT):
        if (base / q).exists():
            return base / q
    return REPO_ROOT / q


def resolve_assets(params: dict, reel_dir: Path) -> tuple[dict, dict]:
    """Render context: images by name and the simulated log. Personal photos are read in place."""
    info: dict = {}
    images = {}
    for name, spec in (params.get("images") or {}).items():
        p = _resolve_path(spec, reel_dir) if "*" not in spec else None
        if "*" in spec:
            pattern = spec if Path(spec).expanduser().is_absolute() else str(REPO_ROOT / spec)
            hits = sorted(glob.glob(str(Path(pattern).expanduser())))
            p = Path(hits[0]) if hits else None
        info[name] = str(p) if p and p.exists() else None
        images[name] = load_image(info[name])
    sim = _resolve_path(params.get("simulated_log"), reel_dir)
    ctx = {"images": images, "simulated_log": sim if sim and sim.exists() else None}
    info["simulated_log"] = str(ctx["simulated_log"]) if ctx["simulated_log"] else None
    return ctx, info


def words_from_cuts(cuts: dict) -> dict[int, dict]:
    """Per beat: clip duration and words with times relative to the beat's first frame."""
    out: dict[int, dict] = {}
    for s in cuts["segments"]:
        b = int(s["beat"])
        e = out.setdefault(b, {"start": s["out_start"], "end": s["out_start"] + s["duration"], "words": []})
        e["end"] = max(e["end"], s["out_start"] + s["duration"])
        e["words"] += [dict(w) for w in s["words"]]
    for e in out.values():
        for w in e["words"]:
            w["start"] = round(w["start"] - e["start"], 3)
            w["end"] = round(w.get("end", w["start"]) - e["start"], 3)
        e["duration"] = round(e["end"] - e["start"], 4)
    return out


def render_all(sheet: dict, reel_dir: Path, out_dir: Path, timings: dict[int, dict] | None, *,
               beats: list[int] | None = None, cuts_sha256: str | None = None, contact: bool = True,
               log=print) -> dict:
    params = sheet.get("params", {})
    from . import rough
    rough.set_theme(sheet.get("theme"))
    ctx, asset_info = resolve_assets(params, reel_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"schema": "content_os.visuals/manifest@1", "cues_sha256": canonical_hash(sheet), "script": sheet.get("_script"),
                "cuts_sha256": cuts_sha256, "fps": FPS, "size": [1080, 960], "assets": asset_info, "beats": []}
    stills = []
    for b in sheet["beats"]:
        n = int(b["beat"])
        if beats and n not in beats:
            continue
        line = spoken_line(b, params)
        t = (timings or {}).get(n)
        if t:
            words, dur, source = t["words"], float(t["duration"]), "transcript"
        else:
            words, dur, source = [], float(b.get("default_duration") or default_duration(line)), "default_length"
        rb = BeatRenderer(b, ctx, words, dur)
        clip = encode(rb, out_dir / f"beat_{n:02d}.mp4")
        kt = rb.key_time()
        if contact:
            stills.append((n, still(rb, kt, out_dir / "stills" / f"beat_{n:02d}.png")))
        rep = {"beat": n, "clip": clip["path"], "frames": clip["frames"], "duration": clip["duration"],
               "timing_source": source, "key_time": round(kt, 3), "line": line, **rb.report,
               "cues": [r.as_dict() for r in rb.resolved]}
        manifest["beats"].append(rep)
        log(beat_summary(rep))
    if contact and stills:
        manifest["contact_sheet"] = str(contact_sheet(stills, out_dir / "contact_sheet.png"))
    (out_dir / MANIFEST).write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
    return manifest


def beat_summary(rep: dict) -> str:
    m = rep["methods"]
    out = (f"beat {rep['beat']:2d}: {rep['duration']:.2f} s, {len(rep['cues'])} cues ({m['exact']} exact, "
           f"{m['interpolated']} interpolated, {m['proportional']} proportional)")
    if rep["fallbacks"]:
        out += " fallbacks: " + ", ".join(str(f["on_word"]) for f in rep["fallbacks"])
    if rep["fit_shifts"]:
        out += " moved to fit: " + ", ".join(f"{f['on_word']} {f['shift_s']:+.2f}s" for f in rep["fit_shifts"])
    return out


def contact_sheet(stills: list[tuple[int, Path]], out: Path, cols: int = 4, scale: float = 0.4) -> Path:
    """One frame per beat at its key moment, scaled to roughly phone size (0.4 x 1080 px wide)."""
    from PIL import Image, ImageDraw

    tw, th = int(1080 * scale), int(960 * scale)
    rows = (len(stills) + cols - 1) // cols
    pad = 12
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad + 26) + pad), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for i, (n, p) in enumerate(stills):
        r, c = divmod(i, cols)
        x, y = pad + c * (tw + pad), pad + r * (th + pad + 26)
        sheet.paste(Image.open(p).resize((tw, th), Image.LANCZOS), (x, y + 26))
        d.text((x, y + 6), f"beat {n}", fill=(230, 230, 230))
    sheet.save(out)
    return out
