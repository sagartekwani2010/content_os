"""Reel directory layout and JSON I/O.

Inputs written by people live at the top of the reel dir (beats.json, cue_sheet.json, raw/,
pipeline.yaml). Everything the pipeline generates goes into ``<reel_dir>/work/``, which gets its own
``.gitignore`` so transcripts, audio and renders can never be committed by accident.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_PREFIX = "content_os.pipeline"


class StageError(RuntimeError):
    """A stage cannot run (missing input, failed gate)."""


@dataclass(frozen=True)
class Reel:
    root: Path

    @classmethod
    def at(cls, path: Path | str) -> "Reel":
        root = Path(path).expanduser().resolve()
        if not root.is_dir():
            raise StageError(f"reel dir not found: {root}")
        reel = cls(root)
        reel.work.mkdir(exist_ok=True)
        gi = reel.work / ".gitignore"
        if not gi.exists():
            gi.write_text("# generated media, audio, transcripts: never commit\n*\n")
        return reel

    @property
    def work(self) -> Path:
        return self.root / "work"

    def p(self, *parts: str) -> Path:
        path = self.work.joinpath(*parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    # inputs
    @property
    def beats_file(self) -> Path:
        return self.root / "beats.json"

    @property
    def cue_sheet_file(self) -> Path:
        return self.root / "cue_sheet.json"

    # generated
    sources_file = property(lambda self: self.p("sources.json"))
    transcript_file = property(lambda self: self.p("transcript.json"))
    takes_file = property(lambda self: self.p("takes.json"))
    scores_file = property(lambda self: self.p("scores.json"))
    selects_file = property(lambda self: self.p("selects.json"))
    cuts_file = property(lambda self: self.p("cuts.json"))
    approvals_file = property(lambda self: self.p("approvals.json"))
    review_html = property(lambda self: self.p("cut_review.html"))
    qa_json = property(lambda self: self.p("qa.json"))
    qa_md = property(lambda self: self.p("qa.md"))
    timings_file = property(lambda self: self.p("timings.json"))

    def rel(self, path: Path | str) -> str:
        path = Path(path)
        try:
            return str(path.resolve().relative_to(self.root))
        except ValueError:
            return str(path)

    def resolve(self, rel_or_abs: str) -> Path:
        p = Path(rel_or_abs).expanduser()
        return p if p.is_absolute() else self.root / p

    def need(self, path: Path, stage_hint: str) -> dict:
        if not path.exists():
            raise StageError(f"{self.rel(path)} missing: run `{stage_hint}` first")
        return read_json(path)

    def record_timing(self, stage: str, seconds: float) -> None:
        f = self.timings_file
        data = read_json(f) if f.exists() else {}
        data[stage] = round(seconds, 2)
        write_json(f, data)


def read_json(path: Path | str) -> Any:
    return json.loads(Path(path).read_text())


def write_json(path: Path | str, data: Any) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def schema(name: str) -> str:
    return f"{SCHEMA_PREFIX}/{name}@1"


def canonical_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_beats(reel: Reel) -> list[dict]:
    data = reel.need(reel.beats_file, "write beats.json")
    beats = data["beats"] if isinstance(data, dict) else data
    out = []
    for b in beats:
        out.append({"id": int(b["id"]), "text": b["text"], **{k: v for k, v in b.items() if k not in ("id", "text")}})
    ids = [b["id"] for b in out]
    if len(set(ids)) != len(ids):
        raise StageError("beats.json has duplicate beat ids")
    return sorted(out, key=lambda b: b["id"])


class Timer:
    def __init__(self, reel: Reel, stage: str):
        self.reel, self.stage = reel, stage

    def __enter__(self):
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, *exc):
        if exc[0] is None:
            self.reel.record_timing(self.stage, time.perf_counter() - self.t0)
        return False
