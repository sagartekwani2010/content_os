"""Creator taste model: Fable mines every past correction, rejection and approval into rules a critic can apply.

Sources (local only; sent to Claude, never to OpenAI):
  - the creator's own messages in Claude Code session transcripts (~/.claude/projects/*/*.jsonl)
  - change lists and inputs in outputs/*/creator_*.md
  - scripted vs spoken beats of shot reels (~/Movies/ContentOS/*/beats.scripted.json vs beats.json)
  - memory rules, REEL_DEFAULTS.md and the script-writing skill
Output: production/CREATOR_TASTE.md (rules only, no personal details: the repository is public).
"""
from __future__ import annotations

import json
from pathlib import Path

from .llm import REPO, call

HOME = Path.home()
TASTE = REPO / "production" / "CREATOR_TASTE.md"
MEMORY = HOME / ".claude/projects/-Users-sagartekwani/memory"
MAX_MSG_CHARS = 220_000

PROMPT = """You are building a TASTE MODEL of an Instagram creator (AI engineer + fitness, India, English-only
reels about building and testing AI systems). Below is everything they have said while we made their reels:
their messages, change lists, the lines they actually spoke versus what was scripted, and the rules already
written down. Your job: predict their reactions so future drafts need no back-and-forth.

Write Markdown with these sections:
# Creator taste model
## Non-negotiables (they reject a draft that breaks these)
## Strong preferences (they ask for these again and again)
## What they cut or rewrite (with the pattern behind it, e.g. generic tips, hedges, invented numbers)
## Voice (words and sentence shapes they use when they reword lines on camera; words they never say)
## Hooks and structure they approved vs rejected
## Accuracy lines they hold vs where they accept simplification
## Predicting their change list (a checklist a critic runs on any draft, 15-25 items, each testable)
## Open tensions (places their asks conflict; how they resolved it last time)

Rules: each item is one line, concrete and testable, followed by "(evidence: <short paraphrase, source>)".
Rank within sections by how often it came up. No personal details (no email, employer, family, health);
this file is public. Do not invent preferences that are not in the evidence.
{previous}
EVIDENCE
{evidence}
"""


def _user_messages() -> list[str]:
    msgs: list[tuple[str, str]] = []
    for f in sorted((HOME / ".claude/projects").glob("*/*.jsonl")):
        try:
            lines = f.read_text(errors="ignore").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") != "user" or d.get("isMeta"):
                continue
            c = (d.get("message") or {}).get("content")
            if isinstance(c, list):
                c = " ".join(p.get("text", "") for p in c if isinstance(p, dict) and p.get("type") == "text")
            if not isinstance(c, str):
                continue
            c = c.strip()
            if not c or c.startswith("<") or c.startswith("This session is being continued") or len(c) < 3:
                continue
            msgs.append((d.get("timestamp", ""), c[:3000]))
    msgs.sort()
    seen, out = set(), []
    for ts, c in msgs:
        if c in seen:
            continue
        seen.add(c)
        out.append(f"[{ts[:10]}] {c}")
    return out


def _spoken_vs_scripted() -> list[str]:
    out = []
    for scripted in sorted((HOME / "Movies/ContentOS").glob("*/beats.scripted.json")):
        spoken = scripted.with_name("beats.json")
        if not spoken.exists():
            continue
        try:
            a, b = json.loads(scripted.read_text()), json.loads(spoken.read_text())
        except ValueError:
            continue
        a = a.get("beats", a) if isinstance(a, dict) else a
        b = b.get("beats", b) if isinstance(b, dict) else b
        for x, y in zip(a, b):
            tx, ty = (x.get("text") or x.get("line") or ""), (y.get("text") or y.get("line") or "")
            if tx.strip() != ty.strip():
                out.append(f"{scripted.parent.name}: SCRIPTED: {tx}\n  SPOKEN: {ty}")
    return out


def gather() -> str:
    parts = []
    msgs = _user_messages()
    text, total = [], 0
    for m in reversed(msgs):  # newest first until the budget is used
        if total + len(m) > MAX_MSG_CHARS:
            break
        text.append(m)
        total += len(m)
    parts.append("## Creator messages (oldest first)\n" + "\n".join(reversed(text)))
    for f in sorted(REPO.glob("outputs/*/creator_*.md")):
        parts.append(f"## {f.relative_to(REPO)}\n{f.read_text()[:20000]}")
    sv = _spoken_vs_scripted()
    if sv:
        parts.append("## Lines as scripted vs as the creator actually said them\n" + "\n".join(sv))
    for f in sorted(MEMORY.glob("*.md")):
        if f.name != "MEMORY.md":
            parts.append(f"## memory rule {f.stem}\n{f.read_text()}")
    for rel in ("production/REEL_DEFAULTS.md", ".agents/skills/reel-script-writing/SKILL.md"):
        p = REPO / rel
        if p.exists():
            parts.append(f"## {rel}\n{p.read_text()}")
    return "\n\n".join(parts)


def build(ledger: Path | None = None) -> Path:
    prev = f"\nPREVIOUS VERSION (update it; keep what still holds):\n{TASTE.read_text()}\n" if TASTE.exists() else ""
    out = call("taste_miner", PROMPT.format(previous=prev, evidence=gather()), ledger=ledger)
    TASTE.write_text(out.strip() + "\n")
    return TASTE


def load() -> str:
    return TASTE.read_text() if TASTE.exists() else "(no taste model yet: run `python -m content_os.factory taste`)"
