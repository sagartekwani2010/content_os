"""Orchestrator settings (config/orchestrator.yaml) and filesystem roots.

Environment overrides (used by tests and dry runs so nothing touches the real reels):
CONTENT_OS_OUTPUTS_ROOT, CONTENT_OS_MEDIA_ROOT, CONTENT_OS_ORCH_STATE_DIR,
CONTENT_OS_STATUS_PAGE, CONTENT_OS_MEMORY_DIR, CONTENT_OS_NOTIFY (0 disables notifications).
"""

from __future__ import annotations

import copy
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = PROJECT_ROOT / "config" / "orchestrator.yaml"


@lru_cache(maxsize=1)
def _raw() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}


def load() -> dict[str, Any]:
    return copy.deepcopy(_raw())


def _path(value: str) -> Path:
    p = Path(os.path.expandvars(value)).expanduser()
    return p if p.is_absolute() else PROJECT_ROOT / p


@dataclass(frozen=True)
class Paths:
    outputs_root: Path
    media_root: Path
    state_dir: Path
    status_page: Path
    logs_dir: Path
    memory_dir: Path

    @property
    def queue_db(self) -> Path:
        return self.state_dir / "queue.sqlite"

    def reel_dir(self, reel_id: str) -> Path:
        return self.outputs_root / reel_id

    def media_dir(self, reel_id: str) -> Path:
        return self.media_root / reel_id


def paths() -> Paths:
    cfg = _raw()["paths"]
    mem = _raw()["memory"]
    env = os.environ
    media_root = _path(env.get("CONTENT_OS_MEDIA_ROOT") or cfg["media_root"])
    return Paths(
        outputs_root=_path(env.get("CONTENT_OS_OUTPUTS_ROOT") or cfg["outputs_root"]),
        media_root=media_root,
        state_dir=_path(env.get("CONTENT_OS_ORCH_STATE_DIR") or cfg["state_dir"]),
        status_page=_path(env.get("CONTENT_OS_STATUS_PAGE") or cfg["status_page"]),
        logs_dir=_path(cfg["logs_dir"]),
        memory_dir=_path(env.get("CONTENT_OS_MEMORY_DIR") or mem["records_dir"]),
    )


def tool_path() -> list[str]:
    """Extra PATH entries for ffmpeg/whisper-cli/claude: config, the interpreter's real bin dir
    (the conda env behind .venv ships ffmpeg and whisper-cli) and ~/.local/bin."""
    import sys

    extra = list(_raw()["pipeline"].get("extra_path", []))
    real_bin = str(Path(sys.executable).resolve().parent)
    return [real_bin, *extra, str(Path.home() / ".local/bin")]


def tilde(p: "Path | str") -> str:
    """Home-relative path for anything written into the (public) repo: no username in committed files."""
    s = str(p)
    home = str(Path.home())
    return "~" + s[len(home):] if s.startswith(home) else s
