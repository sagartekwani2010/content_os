"""``python -m content_os.pipeline <stage> <reel_dir>``"""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

import yaml

from .config import CACHE_DIR, load_config
from .reel import Reel, StageError, Timer

STAGES = ["ingest", "transcribe", "segment", "score", "judge_takes", "cutpoints", "cut_review", "judge_cuts",
          "render", "qa"]

MODELS = {
    "whisper/ggml-small.en.bin": ("https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin",
                                  "c6138d6d58ecc8322097e0f987c32f1be8bb0a18532a3f88f734d1bbf9c41e5d"),
    "whisper/ggml-silero-v5.1.2.bin": ("https://huggingface.co/ggml-org/whisper-vad/resolve/main/ggml-silero-v5.1.2.bin",
                                       "29940d98d42b91fbd05ce489f3ecf7c72f0a42f027e4875919a28fb4c04ea2cf"),
    "models/face_detection_yunet_2023mar.onnx": (
        "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
        "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"),
    # section cards: Barlow Condensed, SIL Open Font License 1.1 (licence file kept next to the fonts)
    "fonts/BarlowCondensed-ExtraBold.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/barlowcondensed/BarlowCondensed-ExtraBold.ttf",
        "724c9c25952d5f4a2d87185d9767aa006144c5f0d944dc05bf7d5d603551c260"),
    "fonts/BarlowCondensed-SemiBold.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/barlowcondensed/BarlowCondensed-SemiBold.ttf",
        "7b619d14bc2327509a9ef32b0890f709626f7ecc9ff61191c2a4314c5499d2d9"),
    "fonts/OFL-BarlowCondensed.txt": ("https://github.com/google/fonts/raw/main/ofl/barlowcondensed/OFL.txt",
                                      "186d750eb496a4c17a76385f82be6aea2ac1cf2de074a811d63786cf374ea73f"),
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def setup() -> None:
    for rel, (url, sha) in MODELS.items():
        dest = CACHE_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and _sha256(dest) == sha:
            print(f"ok       {dest}")
            continue
        print(f"download {url}")
        tmp = dest.with_suffix(dest.suffix + ".part")
        urllib.request.urlretrieve(url, tmp)
        got = _sha256(tmp)
        if got != sha:
            tmp.unlink()
            raise StageError(f"checksum mismatch for {rel}: {got}")
        tmp.rename(dest)
        print(f"ok       {dest}")


def _overrides(items: list[str] | None) -> dict:
    out: dict = {}
    for item in items or []:
        key, _, raw = item.partition("=")
        node = out
        parts = key.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = yaml.safe_load(raw)
    return out


def run_stage(stage: str, reel: Reel, cfg: dict, args) -> object:
    from . import cutpoints, ingest, judge, qa, render, review, score, segment, transcribe

    with Timer(reel, stage if stage not in ("render", "qa") else f"{stage}{'_draft' if getattr(args, 'draft', False) else ''}"):
        if stage == "ingest":
            return ingest.run(reel, cfg, getattr(args, "source", None))
        if stage == "transcribe":
            return transcribe.run(reel, cfg, getattr(args, "engine", None))
        if stage == "segment":
            return segment.run(reel, cfg)
        if stage == "score":
            return score.run(reel, cfg, auditions=not getattr(args, "no_auditions", False))
        if stage == "judge_takes":
            return judge.run(reel, cfg, "takes", apply=not getattr(args, "no_apply", False))
        if stage == "judge_cuts":
            res = judge.run(reel, cfg, "cuts")
            review.run(reel, cfg)  # re-render the page with the judge's notes
            return res
        if stage == "cutpoints":
            return cutpoints.run(reel, cfg)
        if stage == "cut_review":
            return review.run(reel, cfg)
        if stage == "render":
            return render.run(reel, cfg, draft=getattr(args, "draft", False))
        if stage == "qa":
            return qa.run(reel, cfg, draft=getattr(args, "draft", False))
    raise StageError(f"unknown stage {stage}")


def summary(stage: str, result) -> str:
    if not isinstance(result, dict):
        return f"{stage}: done"
    if stage == "segment":
        return f"segment: {len(result['takes'])} takes, cues {len(result['cues'])}, missing beats {result['missing_beats']}"
    if stage == "score":
        sel = result["selects"]
        picks = ", ".join(f"b{e['beat']}={e['take']}{' (close call)' if e.get('close_call') else ''}" for e in sel["beats"])
        return f"score: picks {picks}; re-record {sel['needs_rerecord']}"
    if stage == "cutpoints":
        return f"cutpoints: {len(result['segments'])} segments, {result['duration']:.2f} s"
    if stage == "cut_review":
        return f"cut_review: work/cut_review.html; max face jump {result['max_face_jump_pct_out']}%, " \
               f"max level step {result['max_level_step_db']} dB"
    if stage == "render":
        a = result["audio"]
        return f"render: {result['output']} ({a['integrated_lufs']} LUFS, {a['true_peak_db']} dBTP)"
    if stage == "qa":
        return f"qa: {'PASSED' if result['passed'] else 'FAILED'} {result['hard_failures']} (work/qa.md)"
    if stage.startswith("judge"):
        return f"{stage}: {result['model']} cost ${result.get('cost_usd')} -> work/judge_{result['phase']}.json"
    return f"{stage}: done"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m content_os.pipeline", description="Reel video-editing pipeline")
    ap.add_argument("--set", action="append", metavar="KEY=VALUE", help="config override, e.g. judge.enabled=false")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup", help="download whisper + VAD + face models and card fonts into ~/.cache/content_os")
    p = sub.add_parser("synth", help="generate a synthetic test reel")
    p.add_argument("reel_dir")
    p.add_argument("--hdr", action="store_true")
    p.add_argument("--files", type=int, default=1)
    p.add_argument("--size", default="1280x720")
    for name in ("ingest", "transcribe", "segment", "score", "cutpoints", "cut_review", "render", "qa"):
        p = sub.add_parser(name)
        p.add_argument("reel_dir")
        if name == "ingest":
            p.add_argument("--source", action="append")
        if name == "transcribe":
            p.add_argument("--engine", choices=["whisper_cpp", "openai"])
        if name == "score":
            p.add_argument("--no-auditions", action="store_true")
        if name in ("render", "qa"):
            p.add_argument("--draft", action="store_true")
    p = sub.add_parser("sfx", help="(re)generate the synthesised SFX set (deterministic)")
    p.add_argument("--out", default=None, help="output dir (default ~/Movies/ContentOS/sfx)")
    p = sub.add_parser("sfx-cues", help="write deliver/SFX_CUES.md (SFX at exact output times, for Edits)")
    p.add_argument("reel_dir")
    p.add_argument("--out", default=None)
    p = sub.add_parser("judge", help="Claude judgement step (takes after score, cuts after cut_review)")
    p.add_argument("reel_dir")
    p.add_argument("--phase", choices=["takes", "cuts"], required=True)
    p.add_argument("--no-apply", action="store_true")
    p = sub.add_parser("select", help="override the take for a beat (eligible takes only)")
    p.add_argument("reel_dir")
    p.add_argument("--beat", type=int, required=True)
    p.add_argument("--take", required=True)
    p = sub.add_parser("approve", help="record an approval (cut_review)")
    p.add_argument("reel_dir")
    p.add_argument("gate", choices=["cut_review"])
    p.add_argument("--by", required=True)
    p.add_argument("--note", default="")
    p = sub.add_parser("run", help="run stages in order up to --until (default cut_review)")
    p.add_argument("reel_dir")
    p.add_argument("--from", dest="start", choices=STAGES, default="ingest")
    p.add_argument("--until", choices=STAGES, default="cut_review")
    p.add_argument("--draft", action="store_true", help="render/qa the draft")
    p.add_argument("--no-auditions", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "setup":
            setup()
            return 0
        if args.cmd == "synth":
            from .synth import make_reel

            w, h = (int(v) for v in args.size.split("x"))
            Path(args.reel_dir).mkdir(parents=True, exist_ok=True)
            res = make_reel(Path(args.reel_dir), hdr=args.hdr, files=args.files, size=(w, h))
            print(f"synthetic reel in {args.reel_dir}: {res['files']}")
            return 0
        if args.cmd == "sfx":
            from .sfx import DEFAULT_DIR, generate

            res = generate(args.out or DEFAULT_DIR)
            for name, f in res["files"].items():
                print(f"{name:7s} {f['duration']:.3f} s  peak {f['peak_dbfs']} dBFS  TP {f['true_peak_db']} dBTP  {f['path']}")
            return 0
        reel = Reel.at(args.reel_dir)
        cfg = load_config(reel.root, _overrides(args.set))
        if args.cmd == "sfx-cues":
            from .sfx import cue_list

            print(f"sfx-cues: {cue_list(reel, cfg, Path(args.out) if args.out else None)}")
            return 0
        if args.cmd == "select":
            from .score import override

            override(reel, args.beat, args.take)
            print(f"beat {args.beat} -> {args.take}; re-run cutpoints and cut_review")
            return 0
        if args.cmd == "approve":
            from .approvals import approve

            rec = approve(reel, args.gate, args.by, args.note)
            print(f"approved {args.gate} ({rec['sha256'][:12]}) by {rec['by']}")
            if rec.get("judge_rejections_seen"):
                print(f"note: the judge would reject {rec['judge_rejections_seen']} cut(s); see work/judge_cuts.json")
            return 0
        if args.cmd == "judge":
            res = run_stage(f"judge_{args.phase}", reel, cfg, args)
            print(summary(f"judge_{args.phase}", res))
            return 0
        if args.cmd == "run":
            order = STAGES[STAGES.index(args.start): STAGES.index(args.until) + 1]
            for st in order:
                if st.startswith("judge") and not cfg["judge"]["enabled"]:
                    continue
                res = run_stage(st, reel, cfg, args)
                print(summary(st, res), flush=True)
                if st == "qa" and not res["passed"]:
                    return 2
            return 0
        res = run_stage(args.cmd, reel, cfg, args)
        print(summary(args.cmd, res))
        if args.cmd == "qa" and not res["passed"]:
            return 2
        return 0
    except StageError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

