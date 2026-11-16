"""Beat lines from the teleprompter (the script's source of truth): "**beat N**" then its lines."""

from __future__ import annotations

import re
from pathlib import Path

_BEAT = re.compile(r"^\*\*beat\s+(\d+)\*\*\s*$", re.I)
_STAGE = re.compile(r"^\(.*\)$")  # stage directions such as "(pause)"


def parse_teleprompter(text: str) -> dict[int, str]:
    beats: dict[int, list[str]] = {}
    cur = None
    for raw in text.splitlines():
        line = raw.strip()
        m = _BEAT.match(line)
        if m:
            cur = int(m.group(1))
            beats[cur] = []
            continue
        if cur is None or not line or _STAGE.match(line):
            continue
        if line.startswith("#") or line.startswith("**"):
            cur = None
            continue
        beats[cur].append(line)
    return {k: " ".join(v) for k, v in beats.items() if v}


def load_lines(path: Path) -> dict[int, str]:
    return parse_teleprompter(Path(path).read_text())
