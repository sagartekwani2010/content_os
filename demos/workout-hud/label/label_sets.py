"""Ground-truth labeller for workout clips: Claude Fable 5.2 as a coach, frames only.

This is deliberately independent of the Workout Analyser: it never sees pose keypoints, knee angles
or rep tables. It looks at timestamped frame sheets of a clip and says which lift it is, where each
set starts and ends, and whether each set was good or bad (and why). Its output is the reference the
analyser is scored against.

Usage (from the repo root):
  demos/workout-hud/.venv/bin/python demos/workout-hud/label/label_sets.py CLIP [CLIP ...] [--model claude-fable-5-2]
Writes demos/workout-hud/data/<clip-stem>/sheets/*.jpg and .../label.json (gitignored).
"""
import argparse, json, re, subprocess, sys, tempfile, time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
DEFAULT_MODEL = "claude-fable-5-2"
COLS, ROWS, TILE_W = 4, 3, 300          # 12 frames per sheet
MAX_FRAMES = 288                         # 24 sheets at most per clip

SYSTEM = """You are an experienced strength coach labelling a lifter's own training footage.
Use the Read tool to open every sheet path you are given, in order. Each sheet is a grid of frames
read left to right, top to bottom; the timestamp in seconds is printed on each frame.

Do this:
1. Decide if the clip shows resistance training you can judge. If not (talking, walking, wrong subject,
   too dark or the body is out of frame), say so and stop.
2. Name the lift and the camera view (side, angled side, front, back, other).
3. Find every working set: start and end time, and count the reps you can see.
4. Judge each set as "good", "bad" or "unclear", as a coach would on the gym floor. Look for: partial depth
   or range, depth or range shrinking across reps, hips or lower back leaving the pad or bench, heels
   lifting, knees caving, losing a neutral spine, bouncing, uncontrolled lowering, grinding or failed
   reps. Only report what is visible in the frames. If the frame rate is too low to judge, say "unclear".
5. For a bad set, name the issue(s), the rep numbers where they appear and a timestamp that shows each.

Reply with JSON only, no prose:
{"usable": bool, "unusable_reason": str|null, "lift": str|null, "view": str|null,
 "sets": [{"t0": num, "t1": num, "reps": int, "verdict": "good"|"bad"|"unclear",
           "issues": [{"what": str, "reps": [int], "evidence_t": num}],
           "coach_note": str, "confidence": num}]}
confidence is 0 to 1: how sure you would be if a second coach checked this set."""


def probe_duration(clip):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(clip)],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def make_sheets(clip, out_dir):
    """Sample frames evenly (2 fps for short clips, fewer for long ones) and tile them into sheets."""
    dur = probe_duration(clip)
    fps = min(2.0, MAX_FRAMES / max(dur, 1))
    sheets_dir = out_dir / "sheets"; sheets_dir.mkdir(parents=True, exist_ok=True)
    for old in sheets_dir.glob("*.jpg"):
        old.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(clip), "-vf", f"fps={fps},scale={TILE_W}:-2",
                        "-q:v", "4", f"{tmp}/f_%05d.jpg"], check=True)
        frames = sorted(Path(tmp).glob("f_*.jpg"))
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        except OSError:
            font = ImageFont.load_default()
        per = COLS * ROWS
        for s in range(0, len(frames), per):
            batch = [Image.open(f) for f in frames[s:s + per]]
            th = batch[0].height
            sheet = Image.new("RGB", (COLS * TILE_W, ROWS * th), "black")
            for k, im in enumerate(batch):
                x, y = (k % COLS) * TILE_W, (k // COLS) * th
                sheet.paste(im, (x, y))
                t = (s + k) / fps
                d = ImageDraw.Draw(sheet)
                d.rectangle([x, y, x + 78, y + 28], fill="black")
                d.text((x + 5, y + 3), f"{t:5.1f}s", fill="yellow", font=font)
            sheet.save(sheets_dir / f"sheet_{s // per + 1:02d}.jpg", quality=85)
    return sorted(sheets_dir.glob("sheet_*.jpg")), dur, fps


def claude_call(system, prompt, model, image_dir, timeout=900):
    cmd = ["claude", "-p", prompt, "--system-prompt", system, "--model", model, "--output-format", "json",
           "--no-session-persistence", "--tools", "Read", "--allowedTools", "Read", "--add-dir", str(image_dir)]
    t0 = time.time()
    with tempfile.TemporaryDirectory() as cwd:  # neutral cwd: no project CLAUDE.md is loaded
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    try:
        out = json.loads(p.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"CLI failed rc={p.returncode}: {p.stderr[-500:]} {p.stdout[-500:]}")
    if out.get("is_error"):
        raise RuntimeError(f"CLI error: {out.get('result')}")
    return out.get("result", ""), {"wall_s": round(time.time() - t0, 1), "cost_usd_cli": out.get("total_cost_usd"),
                                   "num_turns": out.get("num_turns")}


def label(clip, model=DEFAULT_MODEL):
    clip = Path(clip).resolve()
    out_dir = DATA / clip.stem; out_dir.mkdir(parents=True, exist_ok=True)
    sheets, dur, fps = make_sheets(clip, out_dir)
    prompt = (f"Clip: {clip.name}, {dur:.1f} s, sampled at {fps:.2f} frames per second into {len(sheets)} sheets.\n"
              "Sheet paths, in time order:\n" + "\n".join(str(s) for s in sheets))
    last = None
    for _ in range(2):
        try:
            text, meta = claude_call(SYSTEM, prompt, model, out_dir / "sheets")
            m = re.search(r"\{.*\}", text, re.S)
            result = json.loads(m.group(0))
            break
        except (RuntimeError, AttributeError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            last = e
    else:
        raise RuntimeError(f"{clip.name}: labelling failed: {last}")
    record = {"clip": clip.name, "duration_s": round(dur, 2), "sample_fps": round(fps, 3), "sheets": len(sheets),
              "labeller": {"model": model, "skill": "form-labeller", "inputs": "frame sheets only, no pose data"},
              "run": meta, "label": result}
    (out_dir / "label.json").write_text(json.dumps(record, indent=1))
    return record


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    a = ap.parse_args()
    for c in a.clips:
        try:
            r = label(c, a.model)
            L = r["label"]
            sets = "; ".join(f"{s['t0']}-{s['t1']}s {s['reps']} reps {s['verdict']}" for s in L.get("sets", []))
            print(f"{r['clip']}: {L.get('lift') or L.get('unusable_reason')} | {L.get('view')} | {sets}", flush=True)
        except Exception as e:  # keep going through the folder
            print(f"{Path(c).name}: ERROR {e}", file=sys.stderr, flush=True)
