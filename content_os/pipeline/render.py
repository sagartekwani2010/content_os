"""Stage 7, render: speaker panel + per-beat visuals + captions + mastered voice/music/SFX -> one MP4.

``render --draft`` works without approval: placeholder cards per beat, no music, a DRAFT label.
The full render refuses unless ``approvals.json`` records a cut_review approval whose hash
matches the current cuts.json.
"""

from __future__ import annotations

import math
import shutil
import textwrap
from pathlib import Path

from . import media
from .approvals import require_approval
from .captions import chunk_words, write_ass
from .layouts import Layout, build_layout
from .reel import Reel, StageError, read_json, write_json


# ------------------------------------------------------------------ voice

def build_voice(reel: Reel, cuts: dict, sources: dict, out_wav: Path) -> Path:
    """Gain-matched voice with 30 ms crossfades at every join; length == sum of segment durations."""
    segs = cuts["segments"]
    if not segs:
        raise StageError("cuts.json has no segments")
    half = cuts["joins"][0]["crossfade_ms"] / 2000 if cuts["joins"] else 0.015
    args = ["-v", "error"]
    for i, s in enumerate(segs):
        a = s["in"] - (half if i > 0 else 0)
        b = s["out"] + (half if i < len(segs) - 1 else 0)
        args += ["-ss", f"{max(0, a):.4f}", "-t", f"{b - max(0, a):.4f}", "-i", str(reel.resolve(sources[s["source"]]["wav48"]))]
    fg = []
    for i, s in enumerate(segs):
        fg.append(f"[{i}:a]aresample=48000,volume={s['gain_db']}dB[a{i}]")
    last = "a0"
    for i in range(1, len(segs)):
        fg.append(f"[{last}][a{i}]acrossfade=d={2 * half:.3f}:c1=tri:c2=tri[x{i}]")
        last = f"x{i}"
    total = cuts["duration"]
    fg.append(f"[{last}]afade=t=in:d=0.01,afade=t=out:st={max(0, total - 0.03):.3f}:d=0.03,"
              f"apad,atrim=0:{total:.4f}[out]")
    media.ffmpeg(*args, "-filter_complex", ";".join(fg), "-map", "[out]", "-c:a", "pcm_s24le", "-ar", "48000",
                 str(out_wav))
    return out_wav


# ------------------------------------------------------------------ speaker panel

def x264(cfg: dict, draft: bool, intermediate: bool = False) -> list[str]:
    v = cfg["video"]
    if intermediate:
        return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p", *media.BT709_ARGS]
    return ["-c:v", "libx264", "-preset", v["draft_preset"] if draft else v["preset"],
            "-crf", str(v["draft_crf"] if draft else v["crf"]), "-pix_fmt", "yuv420p", "-profile:v", "high",
            *media.BT709_ARGS]


def render_speaker(reel: Reel, cfg: dict, cuts: dict, sources: dict, layout: Layout, rdir: Path) -> Path:
    panel = layout.panels["speaker"]
    fps = cuts["fps"]
    parts = []
    for s in cuts["segments"]:
        src = sources[s["source"]]
        c = s["crop"]
        sdr = media.sdr_filter(src["video"], cfg["ingest"]["hdr_method"])
        vf = (f"{sdr},crop={c['w']}:{c['h']}:{c['x']}:{c['y']},scale={panel.w}:{panel.h}:flags=lanczos,"
              f"fps={fps},setsar=1,tpad=stop_mode=clone:stop_duration=1,format=yuv420p,{media.SETPARAMS_709}")
        out = rdir / f"spk_{s['index']:03d}.mp4"
        media.ffmpeg("-v", "error", "-ss", f"{s['in']:.4f}", "-i", str(reel.resolve(src["path"])), "-map", "0:v:0",
                     "-an", "-vf", vf, "-frames:v", str(s["frames"]), *x264(cfg, False, True), "-r", str(fps), str(out))
        parts.append(out)
    return concat(parts, rdir / "speaker.mp4")


def concat(parts: list[Path], out: Path) -> Path:
    lst = out.with_suffix(".txt")
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    media.ffmpeg("-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out))
    return out


# ------------------------------------------------------------------ visual panel

def beat_windows(cuts: dict) -> dict[int, tuple[float, float]]:
    win: dict[int, list[float]] = {}
    for s in cuts["segments"]:
        a, b = s["out_start"], s["out_start"] + s["duration"]
        if s["beat"] in win:
            win[s["beat"]][1] = b
        else:
            win[s["beat"]] = [a, b]
    return {k: (v[0], v[1]) for k, v in win.items()}


def clip_for_beat(cue: dict | None, beat: int, root: Path | None) -> dict | None:
    """Per-beat clip from ``cue_sheet.visual_clips`` (a dir of beat_NN.mp4 rendered by
    ``python -m content_os.visuals render``), used for beats without an explicit visual."""
    d = (cue or {}).get("visual_clips")
    if not d:
        return None
    rel = f"{d.rstrip('/')}/beat_{beat:02d}.mp4"
    path = Path(rel).expanduser() if Path(rel).expanduser().is_absolute() or root is None else root / rel
    return {"type": "clip", "path": rel} if path.exists() else None


def plan_visuals(cuts: dict, cue: dict | None, draft: bool, root: Path | None = None) -> list[dict]:
    """Timeline intervals (frame-exact) of the visual panel. A beat's visual starts at
    beat start + start_offset and holds until the next visual starts."""
    fps = cuts["fps"]
    total_frames = round(cuts["duration"] * fps)
    windows = beat_windows(cuts)
    by_beat = {int(b["beat"]): b for b in (cue or {}).get("beats", [])}
    starts = []
    for beat, (a, b) in sorted(windows.items(), key=lambda kv: kv[1][0]):
        entry = by_beat.get(beat)
        clip = None if draft or (entry and "visual" in entry) else clip_for_beat(cue, beat, root)
        if clip is not None:
            visual, offset = clip, 0.0  # clips are timed from the beat's first frame
        elif draft or entry is None or "visual" not in entry:
            visual = {"type": "placeholder", "text": f"BEAT {beat}"}
            offset = 0.0
        else:
            visual = entry["visual"]
            offset = float(entry.get("start_offset", 0.0))
        offset = min(max(0.0, offset), max(0.0, b - a - 1.0 / fps))
        starts.append((round((a + offset) * fps), beat, visual))
    plan = []
    if starts and starts[0][0] > 0:
        plan.append({"start_frame": 0, "beat": None, "visual": {"type": "blank"}})
    for f, beat, visual in starts:
        plan.append({"start_frame": f, "beat": beat, "visual": visual})
    for i, p in enumerate(plan):
        p["end_frame"] = plan[i + 1]["start_frame"] if i + 1 < len(plan) else total_frames
        p["frames"] = p["end_frame"] - p["start_frame"]
        p["start"] = round(p["start_frame"] / fps, 4)
    return [p for p in plan if p["frames"] > 0]


def _wrap(text: str, width: int) -> str:
    """Wrap each explicit line separately so a "\n" in the cue sheet stays a line break."""
    lines = [w for para in text.split("\n") for w in (textwrap.wrap(para, width=width) or [""])]
    return "\n".join(lines) or " "


def render_visual(reel: Reel, cfg: dict, item: dict, panel, fps: int, out: Path, rdir: Path) -> Path:
    v = item["visual"]
    cards = cfg["cards"]
    n = item["frames"]
    dur = n / fps + 0.5
    kind = v.get("type", "card")
    W, H = panel.w, panel.h
    if kind in ("card", "placeholder", "blank"):
        bg = v.get("bg", cards["bg"]).lstrip("#")
        fg = v.get("fg", cards["fg"]).lstrip("#")
        txt = "" if kind == "blank" else v.get("text", "")
        filt = f"color=c=0x{bg}:s={W}x{H}:r={fps}:d={dur:.3f}"
        if txt:
            tf = rdir / f"{out.stem}.txt"
            tf.write_text(_wrap(txt, int(v.get("wrap_chars", cards["wrap_chars"]))))
            font = rdir / "fonts" / Path(cards["font_file"]).name
            size = int(v.get("font_size", cards["font_size"]))
            filt += (f",drawtext=fontfile=fonts/{font.name}:textfile={tf.name}:expansion=none:fontcolor=0x{fg}:"
                     f"fontsize={size}:line_spacing={size // 4}:text_align=C:x=(w-text_w)/2:y=(h*0.42-text_h/2)")
        args = ["-v", "error", "-f", "lavfi", "-i", filt]
        vf = f"format=yuv420p,setsar=1,{media.SETPARAMS_709}"
    elif kind == "image":
        path = reel.resolve(v["path"])
        args = ["-v", "error", "-loop", "1", "-framerate", str(fps), "-t", f"{dur:.3f}", "-i", str(path)]
        vf = _fit(v.get("fit", "contain"), W, H, v.get("bg", cards["bg"])) + f",fps={fps},format=yuv420p,setsar=1,{media.SETPARAMS_709}"
    elif kind in ("video", "clip"):
        if kind == "clip":  # word-anchored beat clip: starts at the beat's first frame, 1080x960 already
            v = {**v, "start": 0, "loop": False, "fit": v.get("fit", "contain")}
        path = reel.resolve(v["path"])
        info = media.probe(path)["video"]
        args = ["-v", "error"]
        if v.get("loop"):
            args += ["-stream_loop", "-1"]
        args += ["-ss", f"{float(v.get('start', 0)):.3f}", "-i", str(path)]
        vf = (media.sdr_filter(info, cfg["ingest"]["hdr_method"]) + "," + _fit(v.get("fit", "cover"), W, H, v.get("bg", cards["bg"]))
              + f",fps={fps},setsar=1,tpad=stop_mode=clone:stop_duration={dur:.2f},format=yuv420p,{media.SETPARAMS_709}")
    else:
        raise StageError(f"unknown visual type {kind}")
    # cards reference fonts/ and the text file relative to the render dir; everything else is absolute
    _run_in(rdir, args + ["-map", "0:v:0", "-an", "-vf", vf, "-frames:v", str(n), *x264(cfg, False, True),
                          "-r", str(fps), str(out)])
    return out


def _run_in(cwd: Path, args: list[str]) -> None:
    import subprocess

    proc = subprocess.run([media.tool("ffmpeg"), "-hide_banner", "-nostdin", "-y", *args], cwd=cwd,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise media.MediaError(proc.stderr[-2000:])


def _fit(mode: str, W: int, H: int, bg: str) -> str:
    if mode == "cover":
        return f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
    return (f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x{bg.lstrip('#')}")


def render_visual_track(reel: Reel, cfg: dict, cuts: dict, cue: dict | None, layout: Layout, rdir: Path,
                        draft: bool) -> tuple[Path, list[dict]]:
    plan = plan_visuals(cuts, cue, draft, reel.root)
    parts = []
    for i, item in enumerate(plan):
        parts.append(render_visual(reel, cfg, item, layout.panels["visual"], cuts["fps"], rdir / f"vis_{i:03d}.mp4", rdir))
    return concat(parts, rdir / "visual.mp4"), plan


def check_visual_clips(reel: Reel, cue: dict | None, cuts: dict) -> None:
    """Word-anchored clips are only in sync with the cuts they were rendered from."""
    d = (cue or {}).get("visual_clips")
    if not d:
        return
    manifest = reel.resolve(d) / "visuals.json"
    if manifest.exists():
        sha = read_json(manifest).get("cuts_sha256")
        if sha and sha != cuts["sha256"]:
            raise StageError(f"{d} was rendered for different cuts: re-run `python -m content_os.visuals render {reel.root}`")


# ------------------------------------------------------------------ audio master

def _limit_lin(db: float) -> float:
    return round(10 ** (db / 20), 4)


def master_audio(reel: Reel, cfg: dict, voice: Path, cue: dict | None, cuts: dict, out: Path, draft: bool) -> dict:
    m = cfg["master"]
    target = m["target_lufs"]
    total = cuts["duration"]
    v_ld = media.loudness(voice)
    g = target - media.finite(v_ld["integrated_lufs"], target)
    music = (cue or {}).get("music") if not draft else None
    windows = beat_windows(cuts)
    sfx = []
    if not draft:
        for b in (cue or {}).get("beats", []):
            for s in b.get("sfx", []) or []:
                if int(b["beat"]) in windows:
                    sfx.append({"path": reel.resolve(s["path"]), "at": windows[int(b["beat"])][0] + float(s.get("at", 0)),
                                "gain_db": float(s.get("gain_db", -12))})
    music_norm = None
    if music:
        mpath = reel.resolve(music["path"])
        music_norm = media.finite(media.loudness(mpath)["integrated_lufs"], -20)
    tp = m["true_peak_db"]
    report = {"voice_lufs_in": v_ld["integrated_lufs"], "iterations": []}
    for _ in range(3):
        args = ["-v", "error", "-i", str(voice)]
        fg = [f"[0:a]volume={g:.3f}dB,asplit=2[v][vsc]"]
        mix = ["[v]"]
        k = 1
        if music:
            mg = target + float(music.get("gain_db", m["music_gain_db"])) - music_norm
            d = music.get("duck", m["duck"])
            fi, fo = float(music.get("fade_in", 0.5)), float(music.get("fade_out", 2.0))
            args += ["-stream_loop", "-1", "-i", str(reel.resolve(music["path"]))]
            fg.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=mono,atrim=0:{total:.3f},asetpts=PTS-STARTPTS,"
                      f"volume={mg:.2f}dB,afade=t=in:d={fi},afade=t=out:st={max(0, total - fo):.3f}:d={fo}[m0]")
            fg.append(f"[m0][vsc]sidechaincompress=threshold={d['threshold']}:ratio={d['ratio']}:"
                      f"attack={d['attack_ms']}:release={d['release_ms']}[m]")
            mix.append("[m]")
            k += 1
        else:
            fg.append("[vsc]anullsink")
        for s in sfx:
            args += ["-i", str(s["path"])]
            ms = int(round(s["at"] * 1000))
            fg.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=mono,volume={s['gain_db']}dB,"
                      f"adelay={ms}:all=1[s{k}]")
            mix.append(f"[s{k}]")
            k += 1
        fg.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,"
                  f"aresample=192000,alimiter=limit={_limit_lin(tp - 0.5)}:attack=1:release=60:level=0:latency=1,"
                  f"aresample=48000,atrim=0:{total:.4f}[out]")
        media.ffmpeg(*args, "-filter_complex", ";".join(fg), "-map", "[out]", "-ac", "1", "-c:a", "pcm_s24le",
                     "-ar", "48000", str(out))
        ld = media.loudness(out)
        report["iterations"].append({"voice_gain_db": round(g, 2), **ld})
        err = target - media.finite(ld["integrated_lufs"], target)
        if abs(err) <= 0.2:
            break
        g += err
    report.update(media.loudness(out))
    report.update({"music": bool(music), "sfx": len(sfx)})
    return report


# ------------------------------------------------------------------ compose

def run(reel: Reel, cfg: dict, draft: bool = False) -> dict:
    cuts = reel.need(reel.cuts_file, "cutpoints")
    if not draft:
        require_approval(reel, "cut_review", cuts["sha256"])
    sources = {s["id"]: s for s in reel.need(reel.sources_file, "ingest")["sources"]}
    cue = read_json(reel.cue_sheet_file) if reel.cue_sheet_file.exists() else None
    if not draft:
        check_visual_clips(reel, cue, cuts)
    layout = build_layout(cfg, cue)
    name = "draft" if draft else "final"
    rdir = reel.work / "render" / name
    if rdir.exists():
        shutil.rmtree(rdir)
    (rdir / "fonts").mkdir(parents=True)
    for f in {cfg["cards"]["font_file"], cfg["captions"]["font_file"]}:
        if Path(f).exists():
            shutil.copy(f, rdir / "fonts" / Path(f).name)
    voice = build_voice(reel, cuts, sources, rdir / "voice.wav")
    audio_out = rdir / "mix.wav"
    loud = master_audio(reel, cfg, voice, cue, cuts, audio_out, draft)
    speaker = render_speaker(reel, cfg, cuts, sources, layout, rdir)
    visual, plan = render_visual_track(reel, cfg, cuts, cue, layout, rdir, draft)
    chunks = chunk_words(cuts["segments"], cfg["captions"]) if cfg["captions"]["enabled"] else []
    write_ass(rdir / "captions.ass", chunks, layout, cfg["captions"])
    fg = ["[0:v]setsar=1[vis]", "[1:v]setsar=1[spk]", layout.compose({"visual": "[vis]", "speaker": "[spk]"})]
    last = "[base]"
    if chunks:
        fg.append(f"{last}subtitles=filename=captions.ass:fontsdir=fonts[cap]")
        last = "[cap]"
    if draft:
        fg.append(f"{last}drawtext=fontfile=fonts/{Path(cfg['cards']['font_file']).name}:text='DRAFT - cuts not approved':"
                  f"expansion=none:fontsize=34:fontcolor=0xC0392B:x=60:y=60[lab]")
        last = "[lab]"
    fg.append(f"{last}format=yuv420p,{media.SETPARAMS_709}[vout]")
    out = rdir / f"{name}.mp4"
    _run_in(rdir, ["-v", "error", "-i", visual.name, "-i", speaker.name, "-i", audio_out.name,
                   "-filter_complex", ";".join(fg), "-map", "[vout]", "-map", "2:a", *x264(cfg, draft),
                   "-r", str(cuts["fps"]), "-c:a", "aac", "-b:a", cfg["video"]["audio_bitrate"], "-ar", "48000",
                   "-ac", "2", "-t", f"{cuts['duration']:.4f}", "-movflags", "+faststart", out.name])
    info = {"output": reel.rel(out), "draft": draft, "duration_planned": cuts["duration"], "layout": layout.describe(),
            "cuts_sha256": cuts["sha256"], "visual_plan": plan, "captions": chunks, "audio": loud,
            "intermediates": {"visual": reel.rel(visual), "speaker": reel.rel(speaker), "voice": reel.rel(voice),
                              "mix": reel.rel(audio_out)}}
    write_json(rdir / "render.json", info)
    return info


def total_frames(duration: float, fps: int) -> int:
    return int(math.floor(duration * fps + 0.5))
