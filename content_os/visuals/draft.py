"""``draft-spec``: ask claude-fable-5-2 (via the ``claude`` CLI, headless, no tools) to map each
teleprompter beat to a template + params + word-anchored cues, then validate the JSON with the same
checks a render uses (templates, targets, phrases in the line, every number a sourced fact). One repair
round sends the validation errors back. The result goes to ``visual_cues.draft.json`` unless
``--write`` (then visual_cues.json is replaced and the old one kept as ``.bak``).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import SCHEMA
from .build import load_sheet, resolve_assets
from .facts import catalogue as facts_catalogue
from .scenes import validate_spec
from .script import load_lines
from .templates import catalogue_text

SYSTEM = """You design the animated top-panel visuals of a vertical science reel, beat by beat.
Style: simple hand-drawn line diagrams that explain the concept; calm, not flashy. One idea per beat,
at most about 6 words of on-screen text besides numbers, numbers big. Prefer less motion: one or two
meaningful movements per beat (a line or arrow drawing on, a bar growing, a number ticking up); every
other element simply writes or fades in when it is named. No decorative effects: avoid "shake", and
use "emphasis" only for the single key number or word of the beat. Dashboards: one clear chart.
Photos only as evidence (the hidden-chicken dish "dish", the creator's lunch "lunch"); photo
annotation positions are placeholders a person will adjust (you cannot see the photo).

Hard rules (your output is machine-checked; violations are rejected):
1. Use only the templates in the catalogue, with their param names. Every cue "target" must be an
   element id the chosen template creates (see "cue targets").
2. NEVER write a number yourself. Numeric params (value, ci, from, to, lo, hi, mid, n, k, count, shown)
   must be fact references like "@table_mae". Inside text use {fact_key} placeholders, e.g.
   "Fable {fable}". The only digits allowed literally in text are ones spoken in that beat's line.
   If a number you want is not in the fact list, leave it out.
3. Every cue's "on_word" must be a word or phrase copied exactly from that beat's line (or a word index).
   Actions: draw | write | pop | fade | countup | highlight | cross | shake. dur 0.3-0.8 s.
   Mark numbers and key words ("tie", "oracle", "hidden", "knew"...) with "emphasis": true.
   Anchor each element's appearance on the word that names it, in speaking order.
4. Reply with ONLY a JSON object: {"beats": [{"beat": N, "template": "...", "params": {...},
   "cues": [{"on_word": "...", "action": "...", "target": "...", "emphasis": false}]}]}"""


def build_prompt(lines: dict[int, str], examples: list[dict], beats: list[int]) -> str:
    parts = ["# Template catalogue", catalogue_text(), "", "# Facts you may reference (key: display (meaning))",
             facts_catalogue(), "", "# Examples of good beats (from the previous script)",
             json.dumps(examples, ensure_ascii=False, indent=None), "", "# Beats to design (teleprompter lines)"]
    for n in beats:
        parts.append(f"beat {n}: {lines[n]}")
    return "\n".join(parts)


def _beat_emotions(reel_dir: Path) -> dict[int, str]:
    p = Path(reel_dir) / "beats.json"
    try:
        beats = json.loads(p.read_text())["beats"] if p.exists() else []
    except (ValueError, KeyError):
        return {}
    return {int(b["id"]): b["emotion"] for b in beats if b.get("emotion")}


def run_claude(prompt: str, model: str, system: str = SYSTEM, timeout: int = 900) -> dict:
    """One headless call: no tools, no session, from an empty temp dir (no project instructions)."""
    with tempfile.TemporaryDirectory() as d:
        proc = subprocess.run(["claude", "-p", prompt, "--model", model, "--system-prompt", system,
                               "--output-format", "json", "--tools", "", "--no-session-persistence"],
                              cwd=d, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {proc.stderr[-1500:]}")
    return json.loads(proc.stdout)


def extract_json(text: str) -> dict:
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    raw = m.group(1) if m else text[text.find("{"): text.rfind("}") + 1]
    return json.loads(raw)


def draft_spec(reel_dir: Path, *, model: str = "claude-fable-5-2", beats: list[int] | None = None, write: bool = False,
               runner=run_claude, max_rounds: int = 2) -> dict:
    reel_dir = Path(reel_dir)
    spec_path = reel_dir / "visual_cues.json"
    current = json.loads(spec_path.read_text()) if spec_path.exists() else {
        "schema": SCHEMA, "script": "TELEPROMPTER.md", "params": {}, "beats": []}
    lines = load_lines(reel_dir / current.get("script", "TELEPROMPTER.md"))
    todo = beats or sorted(lines)
    examples = [{k: b[k] for k in ("beat", "template", "params", "cues")} for b in current.get("beats", [])
                if b.get("template") in ("flow", "bars", "photo")][:3]
    prompt = build_prompt(lines, examples, todo)
    mbp = Path(reel_dir) / "moodboard.json"
    if mbp.exists():  # the approved mood board: follow its keyframes for each beat
        try:
            kfs = json.loads(mbp.read_text())["keyframes"]
            rows = [f"beat {n}: " + " | ".join(f"{k['id']} {k.get('layout', '')}: {k.get('top_visual') or k.get('shot', '')}"
                                                  f" (template {k.get('template') or '-'}; text '{k.get('on_screen_text', '')}';"
                                                  f" motion {k.get('motion', '')})" for k in kfs if n in (k.get("beats") or []))
                    for n in todo]
            prompt += "\n\n# Approved mood board keyframes per beat (follow them)\n" + "\n".join(r for r in rows if "|" in r or "KF" in r)
        except (ValueError, KeyError):
            pass
    feel = _beat_emotions(reel_dir)
    if feel:  # the script's per-beat target emotion: the visual should carry it, not work against it
        prompt += "\n\n# Target viewer emotion per beat (match it; the twist beat must not look calm)\n" + "\n".join(
            f"beat {n}: {feel[n]}" for n in todo if n in feel)
    keep = [b for b in current.get("beats", []) if int(b["beat"]) not in todo and (int(b["beat"]) in lines or "line_from" in b)]
    errors: list[str] = []
    cost = 0.0
    draft = None
    for attempt in range(1, max_rounds + 1):
        res = runner(prompt if attempt == 1 else
                     prompt + "\n\n# Your previous answer\n" + json.dumps(draft, ensure_ascii=False) +
                     "\n\n# It failed these checks; fix them and reply with the full corrected JSON\n" + "\n".join(errors),
                     model)
        cost += float(res.get("total_cost_usd") or 0)
        try:
            draft = extract_json(res.get("result", ""))
        except (ValueError, json.JSONDecodeError) as e:
            errors = [f"reply was not valid JSON: {e}"]
            continue
        new = {**{k: v for k, v in current.items() if not k.startswith("_")}, "schema": SCHEMA,
               "beats": sorted(keep + [b for b in draft.get("beats", []) if int(b.get("beat", -1)) in todo],
                               key=lambda b: int(b["beat"]))}
        tmp = reel_dir / "visual_cues.draft.json"
        tmp.write_text(json.dumps(new, indent=1, ensure_ascii=False) + "\n")
        sheet = load_sheet(tmp)
        ctx, _ = resolve_assets(sheet.get("params", {}), reel_dir)
        errors = validate_spec(sheet, ctx)
        missing = sorted(set(todo) - {int(b["beat"]) for b in new["beats"]})
        errors += [f"beat {n}: missing from the reply" for n in missing]
        if not errors:
            break
    out = reel_dir / "visual_cues.draft.json"
    if write and not errors:
        if spec_path.exists():
            shutil.copy(spec_path, spec_path.with_suffix(".json.bak"))
        shutil.copy(out, spec_path)
        out = spec_path
    return {"path": str(out), "errors": errors, "attempts": attempt, "cost_usd": round(cost, 4), "model": model}
