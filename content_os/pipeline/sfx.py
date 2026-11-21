"""Licence-free sound effects synthesised with ffmpeg, and the SFX cue list for finishing in Edits.

``python -m content_os.pipeline sfx [--out DIR]`` regenerates the set (deterministic: fixed noise
seeds, fixed expressions; same ffmpeg build -> identical files) into ``~/Movies/ContentOS/sfx`` by
default, with ``sfx.json`` (sha256, duration, peak, true peak, max momentary loudness per file).
Effects are subtle by design: band-limited, short fades at both ends, sample peak -6 dBFS.

``python -m content_os.pipeline sfx-cues <reel_dir> [--out PATH]`` writes ``deliver/SFX_CUES.md``:
every cue-sheet effect at its exact output time (from cuts.json), for re-doing them with another
library in Edits.
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

import numpy as np

from . import media
from .cue import resolve_music_drops, resolve_sfx, words_overlapping
from .reel import Reel, read_json, write_json

DEFAULT_DIR = Path.home() / "Movies" / "ContentOS" / "sfx"
SR = 48000
PEAK_DBFS = -6.0


def _whoosh_cmds(dur: float, step: float = 0.01) -> str:
    """Band-pass centre: 350 Hz -> 2400 Hz at 0.12 s (the swell peak) -> 700 Hz at the end."""
    lines = []
    for i in range(int(dur / step) + 1):
        t = i * step
        if t <= 0.12:
            f = 350 * (2400 / 350) ** (t / 0.12)
        else:
            f = 2400 * (700 / 2400) ** ((t - 0.12) / (dur - 0.12))
        lines.append(f"{t:.3f} bandpass@bp frequency {f:.1f};")
    return "\n".join(lines) + "\n"


# name -> (duration, filtergraph producing [out]); {cmd} is the asendcmd file for the whoosh
SPECS: dict[str, tuple[float, str]] = {
    "whoosh": (0.35, "anoisesrc=d=0.35:c=pink:r=48000:a=0.8:s=7,asetnsamples=n=96:p=0,asendcmd=f={cmd},"
                     "bandpass@bp=f=350:width_type=q:w=1.4,"
                     "volume='if(lt(t,0.12),pow(t/0.12,2),exp(-(t-0.12)*11))':eval=frame,"
                     "highpass=f=180,lowpass=f=6000,afade=t=in:d=0.005,afade=t=out:st=0.31:d=0.04[out]"),
    "pop": (0.08, "aevalsrc='sin(2*PI*(900*t-3125*t*t))*exp(-t*45)*min(1,t/0.002)':s=48000:d=0.08,"
                  "highpass=f=200,lowpass=f=5000,afade=t=out:st=0.068:d=0.012[out]"),
    "hit": (0.5, "aevalsrc='0.9*sin(2*PI*(110*t-55*t*t))*exp(-t*9)*min(1,t/0.004)':s=48000:d=0.5[a];"
                 "anoisesrc=d=0.5:c=brown:r=48000:a=0.6:s=11,lowpass=f=380,"
                 "volume='exp(-t*25)*min(1,t/0.003)':eval=frame[b];"
                 "[a][b]amix=inputs=2:normalize=0,highpass=f=35,lowpass=f=2000,afade=t=out:st=0.44:d=0.06[out]"),
    "tick": (0.05, "aevalsrc='sin(2*PI*2200*t)*exp(-t*140)*min(1,t/0.0007)':s=48000:d=0.05,"
                   "highpass=f=800,lowpass=f=8000,afade=t=out:st=0.04:d=0.01[out]"),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(out_dir: Path | str = DEFAULT_DIR) -> dict:
    out_dir = Path(out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"schema": "content_os.pipeline/sfx@1", "sample_rate": SR, "peak_dbfs": PEAK_DBFS,
                "generator": "content_os/pipeline/sfx.py", "files": {}}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cmd = tmp / "whoosh_cmds.txt"
        cmd.write_text(_whoosh_cmds(SPECS["whoosh"][0]))
        for name, (dur, graph) in SPECS.items():
            raw = tmp / f"{name}_raw.wav"
            media.ffmpeg("-v", "error", "-filter_complex", graph.replace("{cmd}", str(cmd)), "-map", "[out]",
                         "-ac", "1", "-ar", str(SR), "-c:a", "pcm_f32le", "-bitexact", str(raw))
            x, _ = media.read_wav(raw, SR)
            peak = float(np.max(np.abs(x))) or 1.0
            gain = PEAK_DBFS - 20 * np.log10(peak)
            out = out_dir / f"{name}.wav"
            media.ffmpeg("-v", "error", "-i", str(raw), "-af", f"volume={gain:.4f}dB", "-ac", "1", "-ar", str(SR),
                         "-c:a", "pcm_s24le", "-bitexact", "-map_metadata", "-1", str(out))
            y, _ = media.read_wav(out, SR)
            ld = media.loudness(out)
            manifest["files"][name] = {
                "path": str(out), "sha256": _sha(out), "duration": round(len(y) / SR, 4),
                "peak_dbfs": round(20 * float(np.log10(max(np.max(np.abs(y)), 1e-9))), 2),
                "true_peak_db": ld["true_peak_db"], "momentary_max_lufs": media.momentary_max(out)}
    write_json(out_dir / "sfx.json", manifest)
    return manifest


# ------------------------------------------------------------------ cue list for Edits

def timecode(t: float) -> str:
    """mm:ss.ff with ff = hundredths of a second."""
    t = max(0.0, t)
    cs = int(round(t * 100))
    return f"{cs // 6000:02d}:{(cs // 100) % 60:02d}.{cs % 100:02d}"


def cue_list(reel: Reel, cfg: dict, out: Path | None = None) -> Path:
    cuts = reel.need(reel.cuts_file, "cutpoints")
    cue = read_json(reel.cue_sheet_file) if reel.cue_sheet_file.exists() else None
    fps = cuts["fps"]
    rows = []
    for i, s in enumerate(resolve_sfx(cue, cuts, reel.root), 1):
        dur = SPECS.get(s["type"], (0.3, ""))[0]
        over = words_overlapping(cuts, s["at"], s["at"] + dur)
        level = f"{s['level_db']:+.0f} dB vs voice" if "level_db" in s else f"{s['gain_db']:+.0f} dB (file gain)"
        lands = s["anchor"] + (f" ({s['label']})" if s.get("label") else "")
        rows.append(f"| {i} | {timecode(s['at'])} | {int(round(s['at'] * fps))} | {s['type']} | {s['beat']} | "
                    f"{lands} | {level} | {', '.join(over) or 'gap'} |")
    drops = resolve_music_drops(cue, cuts)
    co = [s for s in cuts["segments"] if s.get("cold_open")]
    lines = [f"# SFX cues: {reel.root.name}", "",
             f"Generated from `work/cuts.json` (sha256 `{cuts['sha256'][:12]}`) and `cue_sheet.json` by "
             "`python -m content_os.pipeline sfx-cues`. Times are on the final output timeline (after the "
             f"cold open and playback speed), total {timecode(cuts['duration'])} ({cuts['duration']:.3f} s, {fps} fps).",
             "Time format mm:ss.ff = minutes:seconds.hundredths; Frame = output frame at "
             f"{fps} fps. Level is relative to the voice (voice mastered to {cfg['master']['target_lufs']} LUFS).",
             "", "| # | Time | Frame | Effect | Beat | Lands on | Suggested level | Words under it |",
             "|---|---|---|---|---|---|---|---|", *rows]
    if co:
        lines += ["", f"Cold open: beat {co[0]['beat']} = beat {co[0]['source_beat']}'s take, "
                      f"{timecode(co[0]['out_start'])} to {timecode(co[0]['out_start'] + co[0]['duration'])}."]
    if drops:
        lines += ["", "## Music drops", "", "| Fade out from | Silent from | Silent until | Back by | Level |",
                  "|---|---|---|---|---|"]
        lines += [f"| {timecode(d['fade_out_start'])} | {timecode(d['hold_start'])} | {timecode(d['hold_end'])} | "
                  f"{timecode(d['fade_in_end'])} | {d['level_db']:.0f} dB |" for d in drops]
    lines += ["", "Effects anchored to a visual cue use the visual clips' resolved times when the clips were "
                  "rendered for this cuts.json; otherwise the spoken-word fallback (see 'Lands on')."]
    out = out or reel.root / "deliver" / "SFX_CUES.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    return out


if __name__ == "__main__":
    import sys

    print(generate(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR)["files"].keys())
