"""Watch what Codex is doing: changed files on its side, new carousel outputs, spend, and ownership breaches.

`seal` records hashes of the Claude-owned files; `monitor` reports any change to them that Claude did not seal.
State lives in ~/.cache/content_os/carousel_eval/monitor.json (outside the repo).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from .contract import REPO

STATE = Path.home() / ".cache/content_os/carousel_eval/monitor.json"
MEDIA_ROOT = Path.home() / "Movies/ContentOS"
CLAUDE_OWNED = ["content_os/carousel_eval", "tests/carousel_eval", ".agents/skills/carousel-production/SKILL.md"]
CODEX_SIDE = ["content_os/carousel", "tests/carousel"]


def _claude_files() -> list[Path]:
    out = []
    for rel in CLAUDE_OWNED:
        p = REPO / rel
        out += [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file() and "__pycache__" not in x.parts)
    out += sorted((REPO / "outputs").glob("carousel-*/eval/**/*"))
    return [p for p in out if p.is_file()]


def _hashes() -> dict[str, str]:
    return {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in _claude_files()}


def _load() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def _save(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1))


def seal() -> int:
    state = _load()
    state["sealed"] = _hashes()
    state["sealed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _save(state)
    return len(state["sealed"])


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


def report() -> str:
    state = _load()
    since = state.get("last_check", 0.0)
    lines = [f"# Codex monitor · {time.strftime('%d %b %H:%M')}"
             + (f" (changes since {time.strftime('%d %b %H:%M', time.localtime(since))})" if since else "")]

    breaches = []
    sealed = state.get("sealed", {})
    now = _hashes()
    for rel, h in now.items():
        if rel in sealed and sealed[rel] != h:
            breaches.append(f"modified: {rel}")
        elif rel not in sealed and not rel.startswith("outputs/"):
            breaches.append(f"new unsealed file: {rel}")
    breaches += [f"deleted: {rel}" for rel in sealed if rel not in now]
    lines.append("\n## Ownership")
    lines += [f"- BREACH {b}" for b in breaches] or ["- OK: no unsealed change to Claude-owned files"]

    lines.append("\n## Codex code (git)")
    st = _git("status", "--porcelain", "--", *CODEX_SIDE)
    lines.append(f"```\n{st}\n```" if st else "- no uncommitted changes")
    log = _git("log", "--since", f"@{int(since)}" if since else "3 days ago", "--oneline", "--", *CODEX_SIDE)
    if log:
        lines.append(f"Commits:\n```\n{log}\n```")

    lines.append("\n## Carousel outputs touched")
    for root in [REPO / "outputs", MEDIA_ROOT]:
        for d in sorted(root.glob("carousel-*")):
            changed = [p for p in d.rglob("*") if p.is_file() and p.stat().st_mtime > since and "/eval/" not in str(p)]
            if changed:
                sub = (d / "SUBMISSION.json")
                tag = " · SUBMISSION.json present" if sub.exists() else ""
                lines.append(f"- {d.relative_to(root.parent) if root == REPO / 'outputs' else d}: "
                             f"{len(changed)} files changed{tag}")
                lines += [f"    {p.relative_to(d)}" for p in sorted(changed, key=lambda p: -p.stat().st_mtime)[:8]]

    lines.append("\n## Spend (production ledgers)")
    for led in sorted((REPO / "outputs").glob("carousel-*/ledger.jsonl")):
        rows = [json.loads(x) for x in led.read_text().splitlines() if x.strip()]
        new = [r for r in rows if _ts(r.get("at")) > since]
        cost = sum(r.get("cost_usd") or 0 for r in rows)
        lines.append(f"- {led.parent.name}: {len(rows)} calls, ${cost:.2f} total; {len(new)} new since last check")

    state["last_check"] = time.time()
    _save(state)
    return "\n".join(lines)


def review(report_md: str) -> str:
    """Opus reads the monitor report and says what needs the creator's attention (one call; skipped if quiet)."""
    from . import llm
    quiet = "BREACH" not in report_md and "files changed" not in report_md and "Commits:" not in report_md
    if quiet:
        return "Nothing changed since the last check; no review needed."
    prompt = ("You supervise Codex, which builds Instagram carousels in this repo. Claude owns the evaluation code. "
              "From this monitor report, list in at most 8 short bullets: ownership breaches, risky changes, "
              "carousels waiting for evaluation (SUBMISSION.json present), spend concerns, and what the creator "
              "should do next.\n\n" + report_md)
    return llm.ask(llm.OPUS, prompt, role="monitor.review", ledger=STATE.parent / "ledger.jsonl")


def run_scheduled() -> Path:
    """Entry point for the every-2-days launchd job: report + Opus review, saved and notified."""
    out_dir = MEDIA_ROOT / "_monitor"
    out_dir.mkdir(parents=True, exist_ok=True)
    rep = report()
    try:
        rev = review(rep)
    except Exception as e:                                  # keep the report even if the model call fails
        rev = f"(review failed: {e})"
    path = out_dir / f"monitor_{time.strftime('%Y-%m-%d_%H%M')}.md"
    path.write_text(f"{rep}\n\n## Claude review\n{rev}\n")
    flag = "BREACH" if "BREACH" in rep else ("activity" if "files changed" in rep else "quiet")
    subprocess.run(["osascript", "-e", f'display notification "Codex monitor: {flag}. Report in _monitor." '
                    f'with title "Content OS"'], capture_output=True)
    return path


def _ts(at: str | None) -> float:
    try:
        return time.mktime(time.strptime(at or "", "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return 0.0
