"""The file contract Codex fills when a carousel is ready for evaluation: outputs/<id>/SUBMISSION.json.

{
  "contract": "carousel_submission@1",
  "id": "carousel-prompting-recipe",
  "version": "v3",                                  # bump on every resubmission
  "media_dir": "~/Movies/ContentOS/carousel-prompting-recipe",
  "post_files": ["POST/01_cover.jpg", "POST/02_x.mp4", ...],   # upload order, relative to media_dir
  "contact_sheet": "contact_sheet.jpg",              # relative to media_dir
  "slides": [{"n": 1, "kind": "cover|still|video|cta", "headline": "...", "body": "...",
              "visual": "what is drawn / how it moves",
              "quotes": [{"text": "verbatim model output, '…' marks cuts", "run": "runs/g1_context__after__run1.md"}]}],
  "caption_file": "CAPTION.txt", "pinned_comment_file": "PINNED_COMMENT.txt",   # relative to outputs/<id>
  "keyword": "TRAINER" | null, "dm_kit_dir": "dm_kit" | null,
  "runs_dir": "runs", "facts_file": "judge/FACTS.md",
  "models_used": ["gpt-..."], "calls": 12, "cost_usd": 3.4,
  "notes_for_evaluator": "optional"
}
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CONTRACT = "carousel_submission@1"
REPO = Path(__file__).resolve().parents[2]
REQUIRED = ("contract", "id", "version", "media_dir", "post_files", "slides", "caption_file", "runs_dir")


@dataclass
class Submission:
    raw: dict
    out_dir: Path      # outputs/<id>
    media_dir: Path

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def version(self) -> str:
        return str(self.raw["version"])

    @property
    def slides(self) -> list[dict]:
        return self.raw["slides"]

    def out(self, rel: str | None) -> Path | None:
        return self.out_dir / rel if rel else None

    def media(self, rel: str) -> Path:
        return self.media_dir / rel

    @property
    def eval_dir(self) -> Path:
        return self.out_dir / "eval" / self.version


def load(carousel: str | Path) -> tuple[Submission | None, list[str]]:
    """Load outputs/<id>/SUBMISSION.json. Returns (submission, blocking problems)."""
    out_dir = Path(carousel)
    if not out_dir.is_absolute():
        out_dir = REPO / (out_dir if str(out_dir).startswith("outputs") else Path("outputs") / out_dir)
    path = out_dir / "SUBMISSION.json"
    if not path.exists():
        return None, [f"missing {path.relative_to(REPO) if path.is_relative_to(REPO) else path}"]
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return None, [f"SUBMISSION.json is not valid JSON: {e}"]
    problems = [f"SUBMISSION.json lacks '{k}'" for k in REQUIRED if k not in raw]
    if raw.get("contract") != CONTRACT:
        problems.append(f"contract must be '{CONTRACT}', got {raw.get('contract')!r}")
    if problems:
        return None, problems
    sub = Submission(raw, out_dir, Path(str(raw["media_dir"])).expanduser())
    return sub, []
