"""``python -m content_os.visuals {setup|render|preview|check} <reel_dir>``"""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

from . import rough
from .build import load_sheet, render_all, resolve_assets, words_from_cuts
from .scenes import validate_spec

CUES_FILE = "visual_cues.json"


def setup() -> None:
    rough.FONT_DIR.mkdir(parents=True, exist_ok=True)
    for name, url, sha in rough.FONTS.values():
        dest = rough.FONT_DIR / name
        if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() == sha:
            print(f"ok       {dest}")
            continue
        print(f"download {url}")
        tmp = dest.with_suffix(".part")
        urllib.request.urlretrieve(url, tmp)
        got = hashlib.sha256(tmp.read_bytes()).hexdigest()
        if got != sha:
            tmp.unlink()
            raise SystemExit(f"checksum mismatch for {name}: {got}")
        tmp.rename(dest)
        print(f"ok       {dest}")
    for name, url in rough.FONT_LICENSES.items():
        if not (rough.FONT_DIR / name).exists():
            urllib.request.urlretrieve(url, rough.FONT_DIR / name)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m content_os.visuals", description="Hand-drawn, word-anchored reel visuals")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup", help="download Kalam + Patrick Hand (SIL OFL 1.1) into ~/.cache/content_os/fonts")
    p = sub.add_parser("check", help="validate the cue sheet (phrases exist in their lines)")
    p.add_argument("reel_dir")
    p = sub.add_parser("render", help="render beat clips to <reel_dir>/work/visuals")
    p.add_argument("reel_dir")
    p.add_argument("--preview", action="store_true", help="no cuts.json needed: default lengths, proportional cue times")
    p.add_argument("--beats", help="comma-separated beat numbers")
    p.add_argument("--out", help="output dir (default <reel_dir>/work/visuals, or work/visuals_preview with --preview)")
    p = sub.add_parser("preview", help="synthetic-voice split-screen preview with sync check")
    p.add_argument("reel_dir")
    p.add_argument("--out", help="output dir (default <reel_dir>/preview)")
    p.add_argument("--voice", default="Samantha")
    p.add_argument("--rate", type=int, default=175)
    p.add_argument("--beats", help="comma-separated beat numbers (quick partial preview)")
    p.add_argument("--name", help="output file stem (default: <reel_dir name>_preview)")
    p = sub.add_parser("draft-spec", help="draft visual_cues.json from TELEPROMPTER.md with claude-fable-5-2")
    p.add_argument("reel_dir")
    p.add_argument("--model", default="claude-fable-5-2")
    p.add_argument("--beats", help="only these beats (others keep their current spec)")
    p.add_argument("--write", action="store_true", help="replace visual_cues.json (old one kept as .bak)")
    args = ap.parse_args(argv)
    if args.cmd == "setup":
        setup()
        return 0
    reel_dir = Path(args.reel_dir).expanduser().resolve()
    if args.cmd == "draft-spec":
        from .draft import draft_spec

        beats = [int(x) for x in args.beats.split(",")] if args.beats else None
        res = draft_spec(reel_dir, model=args.model, beats=beats, write=args.write)
        print(f"draft: {res['path']} ({res['attempts']} model call(s), cost ${res.get('cost_usd')})")
        if res["errors"]:
            print("still invalid:\n" + "\n".join(res["errors"]), file=sys.stderr)
            return 1
        return 0
    sheet = load_sheet(reel_dir / CUES_FILE)
    ctx, _ = resolve_assets(sheet.get("params", {}), reel_dir)
    errs = validate_spec(sheet, ctx)
    if sheet.get("_unspecced_beats"):
        print(f"warning: teleprompter beats without a visual: {sheet['_unspecced_beats']}", file=sys.stderr)
    if errs:
        print("\n".join(errs), file=sys.stderr)
        return 1
    if args.cmd == "check":
        print(f"{CUES_FILE}: {len(sheet['beats'])} beats, "
              f"{sum(len(b.get('cues', [])) for b in sheet['beats'])} cues, all phrases found")
        return 0
    if args.cmd == "preview":
        from .preview import build_preview

        only = [int(x) for x in args.beats.split(",")] if args.beats else None
        name = (args.name or f"{reel_dir.name.replace('-', '_')}_preview") + (f"_beats_{'-'.join(map(str, only))}" if only else "")
        m = build_preview(sheet, reel_dir, Path(args.out).expanduser() if args.out else reel_dir / "preview", voice=args.voice, rate=args.rate,
                          beats_only=only, name=name)
        print(f"preview: {m['preview']} ({m['preview_duration']} s)\ncontact sheet: {m.get('contact_sheet')}")
        return 0
    from content_os.pipeline.reel import Reel, StageError, read_json

    reel = Reel.at(reel_dir)  # creates work/ with its .gitignore
    beats = [int(x) for x in args.beats.split(",")] if args.beats else None
    if args.preview:
        out = Path(args.out).expanduser() if args.out else reel.work / "visuals_preview"
        timings, sha = None, None
    else:
        cuts_file = reel.work / "cuts.json"
        if not cuts_file.exists():
            raise SystemExit("work/cuts.json missing: run the pipeline up to cutpoints, or use --preview")
        cuts = read_json(cuts_file)
        timings, sha = words_from_cuts(cuts), cuts.get("sha256")
        out = Path(args.out).expanduser() if args.out else reel.work / "visuals"
    try:
        m = render_all(sheet, reel_dir, out, timings, beats=beats, cuts_sha256=sha)
    except (ValueError, StageError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"{len(m['beats'])} clips in {out}; contact sheet {m.get('contact_sheet')}")
    if not args.preview:
        print('cue_sheet.json: add  "visual_clips": "work/visuals"  to use them in the render stage')
    return 0
