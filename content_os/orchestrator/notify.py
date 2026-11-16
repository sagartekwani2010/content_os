"""macOS notifications (osascript display notification). Also appended to <state_dir>/notifications.log
so the status page and `log` can show what the creator was told. CONTENT_OS_NOTIFY=0 disables."""

from __future__ import annotations

import json
import os
import subprocess

from . import settings
from .state import now


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def send(title: str, message: str) -> bool:
    p = settings.paths()
    try:
        p.state_dir.mkdir(parents=True, exist_ok=True)
        with open(p.state_dir / "notifications.log", "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": now(), "title": title, "message": message}) + "\n")
    except OSError:
        pass
    if os.environ.get("CONTENT_OS_NOTIFY", "1") == "0" or not settings.load()["runner"].get("notify", True):
        return False
    script = f'display notification "{_escape(message)[:230]}" with title "Content OS" subtitle "{_escape(title)[:80]}"'
    try:
        return subprocess.run(["osascript", "-e", script], capture_output=True, timeout=10).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False
