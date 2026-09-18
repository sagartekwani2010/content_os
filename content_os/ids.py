"""Identifier generation.

Every entity carries a prefixed, sortable id. The prefix makes a bare id
self-describing in logs and traces, and the timestamp component means ids sort
chronologically without a join.

The tracking hierarchy the whole system depends on:
    run -> topic -> score -> plan -> content -> creative -> post -> perf -> ad
"""

from __future__ import annotations

import re
import secrets
from datetime import datetime, timezone

_PREFIXES = {
    "run": "run",
    "agent_run": "arun",
    "topic": "top",
    "score": "scr",
    "plan": "pln",
    "content": "cnt",
    "creative": "crv",
    "qa": "qa",
    "performance": "perf",
    "experiment": "exp",
    "ad_test": "ad",
    "approval": "apr",
    "brand_snapshot": "brand",
    "finding": "fnd",
}


def new_id(kind: str) -> str:
    prefix = _PREFIXES.get(kind, kind[:4])
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    return f"{prefix}_{stamp}_{secrets.token_hex(3)}"


def slugify(text: str, max_length: int = 60) -> str:
    """Canonical form used to deduplicate topics across discovery runs.

    Two scouts finding the same story from different sources should collide on
    canonical_topic rather than creating duplicate rows.
    """
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text[:max_length] or "untitled"
