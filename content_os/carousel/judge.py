"""Blind judge for carousel slide scripts: drafts are shuffled and relabelled, author/angle fields are stripped."""
from __future__ import annotations

import json
import random
from pathlib import Path

WEIGHTS = {"hook": 0.15, "swipe": 0.15, "clarity": 0.10, "save": 0.15, "share": 0.10, "merge": 0.10,
           "proof": 0.10, "accuracy": 0.15}

CRITERIA = """hook = hook stop power (slide 1 alone, as it appears in a feed);
swipe = swipe-through (does each slide make the next one necessary?);
clarity = could a 15-year-old follow it?;
save = save-worthiness; share = share/send-worthiness;
merge = how well the two domains (the everyday analogy world and AI prompting) are merged, with one fixed casting;
proof = the real run, used honestly and visibly;
accuracy = every quote and number matches the REAL RUN; nothing overclaims; personal claims are supported by FACTS."""


def blind(drafts: dict[str, dict], seed: int) -> tuple[dict[str, dict], dict[str, str]]:
    """Return {label: stripped draft} and the key {label: draft id}. Labels are P, Q, R... in shuffled order."""
    ids = list(drafts)
    random.Random(seed).shuffle(ids)
    out, key = {}, {}
    for lab, i in zip("PQRSTU", ids):
        d = {k: v for k, v in drafts[i].items() if k in ("slides", "caption", "pinned_comment")}
        out[lab], key[lab] = d, i
    return out, key


def weighted(scores: dict[str, float]) -> float:
    return round(sum(WEIGHTS[k] * float(scores[k]) for k in WEIGHTS), 2)


def prompt(blinded: dict[str, dict], facts: str, panel: str) -> str:
    body = "\n\n".join(f"## DRAFT {lab}\n{json.dumps(d, ensure_ascii=False, indent=1)}" for lab, d in blinded.items())
    return f"""You are a strict, independent judge of Instagram carousel scripts. You did not write any of these drafts
and you do not know who did. Score each draft 1-10 on each criterion (be strict: an ordinary good carousel scores 5-6).
CRITERIA:
{CRITERIA}

{panel}
For each draft also predict, from the panel above, which persona numbers stop on slide 1, which swipe to the end, and
which save it.

# FACTS (what is true; the only allowed outputs and numbers)
{facts}

# DRAFTS
{body}

Reply with JSON only:
{{"drafts": {{"<label>": {{"scores": {{{", ".join(f'"{k}": int' for k in WEIGHTS)}}}, "stop": [int], "swipe_to_end": [int],
"save": [int], "strengths": [str], "fixes": [str]}}}}, "best": "<label>", "why": str}}
`fixes` = the concrete changes (slide number + what to change) that would raise the score most."""


def score(reply: dict, key: dict[str, str]) -> dict[str, dict]:
    res = {}
    for lab, r in reply["drafts"].items():
        res[key[lab]] = {"label": lab, "weighted": weighted(r["scores"]), **r}
    return res
