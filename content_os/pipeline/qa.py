"""Stage 8, qa: measured checks on the rendered file -> qa.json + qa.md. Hard failures exit nonzero."""

from __future__ import annotations

import re
import subprocess

import numpy as np

from . import media, textmatch as tm
from .face import get_detector
from .cue import source_beat
from .layouts import build_layout
from .reel import Reel, load_beats, read_json, schema, write_json
from .transcribe import transcribe_file


def _check(name, status, value=None, threshold=None, detail="", hard=True):
    return {"name": name, "status": status, "hard": hard, "value": value, "threshold": threshold, "detail": detail}


def check_streams(path) -> dict:
    info = media.probe(path)
    v, a = info["video"] or {}, info["audio"] or {}
    problems = []
    if (v.get("width"), v.get("height")) != (1080, 1920):
        problems.append(f"size {v.get('width')}x{v.get('height')}")
    if v.get("codec") != "h264":
        problems.append(f"video codec {v.get('codec')}")
    if v.get("pix_fmt") != "yuv420p":
        problems.append(f"pix_fmt {v.get('pix_fmt')}")
    if (v.get("color_primaries"), v.get("color_transfer"), v.get("color_space")) != ("bt709", "bt709", "bt709"):
        problems.append(f"colour tags {v.get('color_primaries')}/{v.get('color_transfer')}/{v.get('color_space')}")
    if a.get("codec") != "aac" or a.get("sample_rate") != 48000:
        problems.append(f"audio {a.get('codec')} {a.get('sample_rate')} Hz")
    return _check("format_h264_aac48k_bt709_1080x1920", "fail" if problems else "pass",
                  f"{v.get('codec')} {v.get('width')}x{v.get('height')} {v.get('pix_fmt')} / {a.get('codec')} {a.get('sample_rate')}",
                  detail="; ".join(problems)), info


def black_frames(path, min_s: float) -> list[list[float]]:
    err = media.ffmpeg("-i", str(path), "-vf", f"blackdetect=d={min_s}:pix_th=0.10", "-an", "-f", "null", "-").stderr
    return [[float(a), float(b)] for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)]


def silences(path, noise_db: float, min_s: float) -> list[list[float]]:
    err = media.ffmpeg("-i", str(path), "-af", f"silencedetect=n={noise_db}dB:d={min_s}", "-f", "null", "-").stderr
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return [[s, ends[i] if i < len(ends) else None] for i, s in enumerate(starts)]


def _frame(path, t: float, w: int, h: int, vf: str = "null", extra_inputs: list[str] | None = None,
           filter_complex: str | None = None):
    if filter_complex:
        args = []
        for p in extra_inputs:
            args += ["-ss", f"{t:.3f}", "-i", str(p)]
        args += ["-filter_complex", filter_complex, "-map", "[base]"]
    else:
        args = ["-ss", f"{t:.3f}", "-i", str(path), "-vf", vf]
    proc = subprocess.run([media.tool("ffmpeg"), "-hide_banner", "-nostdin", "-v", "error", *args, "-frames:v", "1",
                           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True)
    if proc.returncode != 0 or len(proc.stdout) < w * h * 3:
        return None
    return np.frombuffer(proc.stdout[: w * h * 3], np.uint8).reshape(h, w, 3)


def run(reel: Reel, cfg: dict, draft: bool = False) -> dict:
    name = "draft" if draft else "final"
    rdir = reel.work / "render" / name
    rinfo = reel.need(rdir / "render.json", f"render{' --draft' if draft else ''}")
    out = reel.resolve(rinfo["output"])
    cuts = reel.need(reel.cuts_file, "cutpoints")
    q = cfg["qa"]
    cue = read_json(reel.cue_sheet_file) if reel.cue_sheet_file.exists() else None
    layout = build_layout(cfg, cue)
    checks = []

    c, info = check_streams(out)
    checks.append(c)
    dur = info["duration"]
    planned = cuts["duration"]
    checks.append(_check("duration_vs_plan", "pass" if abs(dur - planned) <= q["duration_tolerance_s"] else "fail",
                         round(dur, 3), f"{planned:.3f} +- {q['duration_tolerance_s']}"))
    checks.append(_check("duration_max", "pass" if dur <= q["max_duration_s"] else "fail", round(dur, 2), q["max_duration_s"]))

    blacks = black_frames(out, q["black_min_s"])
    checks.append(_check("black_frames", "fail" if blacks else "pass", len(blacks), 0, detail=str(blacks[:5])))

    voice = reel.resolve(rinfo["intermediates"]["voice"])
    v_lufs = media.finite(media.loudness(voice)["integrated_lufs"], -23)
    gaps = [g for g in silences(voice, round(v_lufs - 30, 1), q["max_silence_s"])
            if g[1] is not None and g[0] > 0.05 and g[1] < planned - 0.05]
    checks.append(_check("silence_gaps_voice", ("fail" if q["silence_hard"] else "warn") if gaps else "pass",
                         len(gaps), f"none > {q['max_silence_s']} s", detail=str(gaps[:5]), hard=q["silence_hard"]))

    ld = media.loudness(out)
    target = cfg["master"]["target_lufs"]
    i_ok = ld["integrated_lufs"] is not None and abs(ld["integrated_lufs"] - target) <= q["lufs_tolerance"]
    checks.append(_check("integrated_loudness", "pass" if i_ok or draft else "fail", ld["integrated_lufs"],
                         f"{target} +- {q['lufs_tolerance']} LUFS"))
    tp_ok = ld["true_peak_db"] is not None and ld["true_peak_db"] <= q["max_true_peak_db"]
    checks.append(_check("true_peak", "pass" if tp_ok else "fail", ld["true_peak_db"], f"<= {q['max_true_peak_db']} dBTP"))
    x, _ = media.read_wav(out, 48000)
    clipped = int(np.sum(np.abs(x) >= 0.999))
    checks.append(_check("clipping", "fail" if clipped else "pass", clipped, 0, detail="samples at full scale"))

    short = [(s["take"], s["duration"]) for s in cuts["segments"] if s["duration"] < q["min_clip_s"]]
    checks.append(_check("clips_min_length", "fail" if short else "pass", min(s["duration"] for s in cuts["segments"]),
                         f">= {q['min_clip_s']} s", detail=str(short)))

    if cfg["captions"]["enabled"]:
        checks.append(captions_check(reel, rinfo, out, layout, rdir))
    else:  # captions are added later in another editor (e.g. Edits); nothing to measure here
        checks.append(_check("captions_present", "pass", "disabled", "captions added downstream", detail="added in Edits",
                             hard=False))
    checks.append(caption_placement_check(layout, cfg, cuts))
    checks += face_jump_checks(reel, cfg, cuts, out, layout)
    if q["transcribe_render"]:
        checks += wer_checks(reel, cfg, cuts, out)

    hard_fail = [c for c in checks if c["hard"] and c["status"] == "fail"]
    data = {"schema": schema("qa"), "render": rinfo["output"], "draft": draft, "duration": round(dur, 3),
            "loudness": ld, "checks": checks, "passed": not hard_fail,
            "hard_failures": [c["name"] for c in hard_fail],
            "not_checked": ["how it sounds (the creator must listen to this exact file)",
                            "caption spelling against the script (only presence is measured)",
                            "gaze: face orientation is a head-pose proxy, not eye tracking"]}
    write_json(reel.qa_json, data)
    reel.qa_md.write_text(to_markdown(data))
    return data


def captions_check(reel: Reel, rinfo: dict, out, layout, rdir) -> dict:
    chunks = rinfo.get("captions") or []
    if not chunks:
        return _check("captions_present", "fail", 0, "> 0 caption events")
    box = layout.caption_box
    W, H = layout.width, layout.height
    inter = rinfo["intermediates"]
    fc = ("[0:v]setsar=1[vis];[1:v]setsar=1[spk];" + layout.compose({"visual": "[vis]", "speaker": "[spk]"}))
    idx = np.linspace(0, len(chunks) - 1, min(8, len(chunks))).round().astype(int)
    seen = 0
    for i in sorted(set(idx.tolist())):
        t = (chunks[i]["start"] + chunks[i]["end"]) / 2
        a = _frame(out, t, W, H)
        b = _frame(None, t, W, H, extra_inputs=[reel.resolve(inter["visual"]), reel.resolve(inter["speaker"])],
                   filter_complex=fc)
        if a is None or b is None:
            continue
        reg = (slice(box.y, box.bottom), slice(box.x, box.right))
        diff = np.abs(a[reg].astype(int) - b[reg].astype(int))
        if (diff.max(axis=2) > 60).mean() > 0.01:
            seen += 1
    n = len(set(idx.tolist()))
    return _check("captions_present", "pass" if seen >= max(1, int(0.9 * n)) else "fail", f"{seen}/{n} sampled",
                  ">= 90% of sampled caption events visible in the caption box")


def caption_placement_check(layout, cfg: dict, cuts: dict) -> dict:
    box = layout.caption_box
    safe = cfg["safe_area"]
    problems, notes = [], []
    low_by_choice = layout.params.get("caption_position") == "bottom_safe"
    if box.bottom > layout.height - safe["bottom"]:
        (notes if low_by_choice else problems).append("enters bottom UI area" + (" (creator-chosen low captions)" if low_by_choice else ""))
    if box.right > layout.width - safe["right"]:
        problems.append("enters right UI area")
    spk = layout.panels["speaker"]
    if box.intersects(spk):
        for seg in cuts["segments"]:
            f = seg["face"]
            if f.get("cy") is None:
                continue
            sw, sh = seg["src_size"]
            c = seg["crop"]
            half = 0.6 * (f.get("w") or 0.15) * sw  # face box ~1.2x its width tall
            to_out = lambda ysrc: spk.y + (ysrc - c["y"]) * spk.h / c["h"]
            face_top, face_bottom = to_out(f["cy"] * sh - half), to_out(f["cy"] * sh + half)
            if box.y < face_bottom and box.bottom > face_top:
                problems.append(f"overlaps the face in segment {seg['index'] + 1}")
                break
    return _check("captions_clear_of_face_and_ui", "fail" if problems else "pass", box.as_dict(),
                  detail="; ".join(problems + notes))


def face_jump_checks(reel: Reel, cfg: dict, cuts: dict, out, layout) -> list[dict]:
    q = cfg["qa"]
    det = get_detector(cfg)
    if det is None or not cuts["joins"]:
        return [_check("max_face_jump_at_cuts", "skipped", detail="no detector or no cuts", hard=False)]
    spk = layout.panels["speaker"]
    fps = cuts["fps"]
    jumps = []
    vf = f"crop={spk.w}:{spk.h}:{spk.x}:{spk.y}"
    for j in cuts["joins"]:
        fa = _frame(out, j["time"] - 1.5 / fps, spk.w, spk.h, vf)
        fb = _frame(out, j["time"] + 0.5 / fps, spk.w, spk.h, vf)
        da = det.detect(fa) if fa is not None else None
        db = det.detect(fb) if fb is not None else None
        if da and db:
            jumps.append({"cut": j["index"] + 1, "jump_pct": round(abs(da.cx - db.cx) * spk.w / layout.width * 100, 2)})
    if not jumps:
        return [_check("max_face_jump_at_cuts", "skipped", detail="no face found at the cuts", hard=False)]
    worst = max(jumps, key=lambda x: x["jump_pct"])
    status = "fail" if worst["jump_pct"] > q["face_jump_fail_pct"] else "warn" if worst["jump_pct"] > q["face_jump_warn_pct"] else "pass"
    return [_check("max_face_jump_at_cuts", status, worst["jump_pct"],
                   f"warn > {q['face_jump_warn_pct']}%, fail > {q['face_jump_fail_pct']}% of frame width", detail=str(jumps))]


def wer_checks(reel: Reel, cfg: dict, cuts: dict, out) -> list[dict]:
    q = cfg["qa"]
    wav = reel.p("qa_asr", "render_16k.wav")
    media.ffmpeg("-v", "error", "-i", str(out), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav))
    try:
        res = transcribe_file(wav, reel.work / "qa_asr" / "chunks", cfg, "whisper_cpp")
    except Exception as e:  # noqa: BLE001 - report, don't crash QA
        return [_check("transcript_vs_script", "skipped", detail=f"ASR unavailable: {e}"[:300], hard=False)]
    words = res["words"]
    beats = {b["id"]: b for b in load_beats(reel)}
    per_beat = []
    worst = 0.0
    for s in cuts["segments"]:
        a, b = s["out_start"], s["out_start"] + s["duration"]
        heard = [w["text"] for w in words if a <= (w["start"] + w["end"]) / 2 < b]
        hyp = [t for w in heard for t in tm.tokens(w)]
        w_script = tm.wer(hyp, tm.tokens(beats[source_beat(s)]["text"]))
        w_take = tm.wer(hyp, tm.tokens(s["text"]))
        per_beat.append({"beat": s["beat"], "wer_vs_script": w_script, "wer_vs_selected_take": w_take,
                         "heard": " ".join(heard)})
        worst = max(worst, w_script)
    status = "fail" if worst > q["wer_fail"] else "warn" if worst > q["wer_warn"] else "pass"
    return [_check("transcript_vs_script_wer", status, worst, f"warn > {q['wer_warn']}, fail > {q['wer_fail']}",
                   detail=per_beat)]


def to_markdown(data: dict) -> str:
    icon = {"pass": "PASS", "warn": "WARN", "fail": "FAIL", "skipped": "SKIP"}
    lines = [f"# QA: {data['render']}", "",
             f"Result: **{'PASSED' if data['passed'] else 'FAILED'}** ({len(data['hard_failures'])} hard failures)", "",
             f"Duration {data['duration']} s; integrated {data['loudness']['integrated_lufs']} LUFS; "
             f"true peak {data['loudness']['true_peak_db']} dBTP", "",
             "| Check | Result | Value | Threshold |", "|---|---|---|---|"]
    for c in data["checks"]:
        val = c["value"] if not isinstance(c["value"], dict) else ", ".join(f"{k}={v}" for k, v in c["value"].items())
        lines.append(f"| {c['name']}{'' if c['hard'] else ' (soft)'} | {icon[c['status']]} | {val} | {c['threshold'] or ''} |")
    for c in data["checks"]:
        if c["name"] == "transcript_vs_script_wer" and isinstance(c["detail"], list):
            lines += ["", "## Transcript of the render vs script", "", "| Beat | WER vs script | WER vs take | Heard |", "|---|---|---|---|"]
            for b in c["detail"]:
                lines.append(f"| {b['beat']} | {b['wer_vs_script']} | {b['wer_vs_selected_take']} | {b['heard']} |")
    lines += ["", "## Not checked", ""] + [f"- {x}" for x in data["not_checked"]]
    return "\n".join(lines) + "\n"
