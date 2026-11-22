"""Two model calls per evaluation:
  1. Fable 5.2, blind engagement judge (text of the slides + caption + facts): weighted score + panel prediction.
  2. Opus 5.5, visual + honesty review: reads the contact sheet and the runs itself (Read tool only).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import llm
from .contract import Submission

WEIGHTS = {"hook": 0.15, "swipe": 0.15, "clarity": 0.10, "save": 0.15, "share": 0.10, "merge": 0.10,
           "proof": 0.10, "accuracy": 0.15}
GATE = 7.0

PANEL = ("16 Indian Instagram viewers scrolling at lunch or 10 pm, English only: TCS support engineer Pune 24; "
         "CA Ahmedabad 31; HR exec Bengaluru 28; bank RM Lucknow 35; school teacher Jaipur 38; final-year B.Tech "
         "Chennai 21; gym regular and sales manager Delhi 29; mother returning to work Hyderabad 33; data analyst "
         "Gurugram 26; startup PM Bengaluru 30; MBA student Mumbai 24; fitness coach Indore 27; government exam "
         "aspirant Patna 23; senior Java developer Kochi 36; content writer Kolkata 25; doctor (resident) Pune 28.")

CREATOR_RULES = """Creator's rules for every carousel:
- Every concept is explained through an easy real-world example; principle-only slides fail.
- Contexts only from very popular worlds (cricket, Ramayan, Bollywood) or the creator's own: gym/fitness first,
  then AI building, careers. Random contexts (kitchen, head chef) fail.
- Simple: a 15-year-old understands each slide in one read; headline ≤ 8-10 words, body ≤ 25 words.
- Two domains merged (AI concept × everyday/creator world). Proof = real model runs, quoted verbatim.
- Light hand-drawn style, short video slides, creator photo on slide 1. English only."""


def _slides_text(sub: Submission) -> str:
    lines = []
    for s in sub.slides:
        lines.append(f"[Slide {s.get('n')} · {s.get('kind')}] {s.get('headline', '')}\n  {s.get('body', '')}")
        if s.get("visual"):
            lines.append(f"  (visual: {s['visual']})")
        for q in s.get("quotes", []) or []:
            lines.append(f"  quote: {q.get('text', '')}")
    return "\n".join(lines)


def _read(p: Path | None) -> str:
    return p.read_text() if p and p.exists() else "(missing)"


def engagement(sub: Submission, ledger: Path) -> dict:
    keys = ", ".join(f'"{k}": <1-10>' for k in WEIGHTS)
    prompt = f"""You are a blind judge of an Instagram carousel. You did not write it. Be strict and specific.

{CREATOR_RULES}

FACTS (what is true and what is not established):
{_read(sub.out(sub.raw.get('facts_file')))}

CAROUSEL:
{_slides_text(sub)}

CAPTION:
{_read(sub.out(sub.raw['caption_file']))}

Score 1-10 on: hook (slide 1 alone stops the scroll), swipe (each slide makes the next necessary), clarity
(15-year-old gets each slide in one read), save (worth keeping), share (worth sending to a friend), merge (AI concept
× real-world example, allowed context), proof (real runs used honestly), accuracy (nothing false or overstated).
Then predict, for this panel, who stops at slide 1, who swipes to the end, who saves: {PANEL}

Reply with ONLY JSON:
{{"scores": {{{keys}}}, "stop": <0-16>, "swipe_to_end": <0-16>, "save": <0-16>,
 "rule_breaks": ["..."], "weakest_slides": [{{"n": <int>, "why": "...", "fix": "..."}}],
 "top_3_fixes": ["...", "...", "..."], "one_line_verdict": "..."}}"""
    reply = llm.parse_json(llm.ask(llm.FABLE, prompt, role="eval.engagement", ledger=ledger))
    reply["weighted"] = round(sum(WEIGHTS[k] * float(reply["scores"][k]) for k in WEIGHTS), 2)
    return reply


def visual(sub: Submission, ledger: Path) -> dict:
    stills = [sub.media(f) for f in sub.raw["post_files"] if f.lower().endswith((".jpg", ".jpeg"))]
    images = [sub.media(sub.raw["contact_sheet"])] + stills[:3]          # contact sheet + cover + 2 stills
    runs_dir = sub.out(sub.raw["runs_dir"])
    runs = "\n\n".join(f"### {p.relative_to(runs_dir)}\n{p.read_text()}"
                        for p in sorted(runs_dir.rglob("*.md")) if "pilot" not in p.parts)[:200_000] \
        if runs_dir and runs_dir.exists() else "(missing)"
    prompt = f"""You review an Instagram carousel's visuals and honesty. The images are: the contact sheet (all slides,
first and last frame of each video), then the cover and up to two stills at full size.

{CREATOR_RULES}

SLIDE TEXT:
{_slides_text(sub)}

REAL MODEL RUNS (the only allowed source for quoted outputs):
{runs}

Check: phone legibility (text big enough at 1080 px wide?), clutter vs simplicity (is it a text wall?), whether each
concept has a simple drawing that explains it, empty or wasted space, the bottom 180 px kept clear (Instagram UI),
the cover photo (face clear, bystanders blurred), video first frames meaningful, any claim the runs do not support.
Reply with ONLY JSON:
{{"visual_score": <1-10>, "legibility_ok": <bool>, "text_wall_slides": [<n>], "issues":
[{{"n": <int>, "severity": "block|fix|note", "issue": "...", "fix": "..."}}], "honesty_flags": ["..."],
"one_line_verdict": "..."}}"""
    return llm.parse_json(llm.ask(llm.OPUS, prompt, role="eval.visual", ledger=ledger, images=images,
                                  cwd=sub.out_dir))


def to_json(x) -> str:
    return json.dumps(x, indent=1, ensure_ascii=False)
