#!/usr/bin/env python3
"""Print a compact, copy-ready Content OS context packet for a fresh chat.

This captures repository state and selected project files. It cannot read or
resume a Codex chat transcript; add conversation-only decisions with --note.
"""

from __future__ import annotations

import argparse
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def git_output(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "Git status unavailable."
    return result.stdout.strip() or "Clean working tree."


def newest_draft() -> Path | None:
    candidates = list((ROOT / "outputs").glob("**/SCRIPT_DRAFT.md"))
    return max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print a concise handoff packet to paste into a fresh Codex chat."
    )
    parser.add_argument(
        "focus",
        nargs="?",
        help="Project file to include, relative to the repository (defaults to newest script draft).",
    )
    parser.add_argument(
        "--note",
        action="append",
        default=[],
        help="A conversation-only decision or next step to preserve; may be repeated.",
    )
    args = parser.parse_args()

    focus = (ROOT / args.focus).resolve() if args.focus else newest_draft()
    print("# Content OS chat handoff")
    print(f"Generated: {datetime.now().astimezone().isoformat(timespec='minutes')}")
    print(f"Repository: {ROOT}")
    print("\n## Instructions")
    print("Read AGENTS.md and CODEX_WORKFLOW.md first. Continue the unfinished request; do not repeat completed work.")
    print("This packet summarizes repository state only. It cannot recover chat-only context or unuploaded attachments.")

    handoff = ROOT / "HANDOFF.md"
    if handoff.is_file():
        lines = handoff.read_text(encoding="utf-8").splitlines()
        # Keep the opening/current-state section compact; older strategy remains in the repo.
        print("\n## Current project handoff")
        print("\n".join(lines[:35]))

    print("\n## Git working-tree state")
    print("```text")
    print(git_output("status", "--short"))
    print("```")

    if focus:
        try:
            relative = focus.relative_to(ROOT)
        except ValueError:
            parser.error("focus must be inside the Content OS repository")
        if not focus.is_file():
            parser.error(f"focus file does not exist: {relative}")
        print(f"\n## Focus file: {relative}")
        print(focus.read_text(encoding="utf-8").strip())

    if args.note:
        print("\n## Conversation-only notes to carry forward")
        for note in args.note:
            print(f"- {note}")

    print("\n## Next step")
    print("Ask the user what they want to continue, using this state as context.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
