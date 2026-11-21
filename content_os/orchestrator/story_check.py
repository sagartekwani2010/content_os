"""Emotion + hook checker: an independent model (config: orchestrator_story_check, Opus) reviews the
Fable-written script, and later the visual plan, for emotions, hooks and continuity.

The script stage calls ``check_script`` after each draft and lets Fable revise from the notes up to
``story_check.max_revisions`` times; the visuals stage calls ``check_visuals`` before rendering.
Reports land next to the reel as SCRIPT_CHECK.md / VISUALS_CHECK.md plus JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import modelcall, settings


def cfg() -> dict[str, Any]:
    return {"max_revisions": 1, "visuals_blocking": False, **(settings.load().get("story_check") or {})}


def _script_payload(s: dict[str, Any]) -> str:
    keep = ("title", "promise", "hook", "target_duration_s", "emotional_arc", "hook_variants", "save_asset",
            "comment_trigger", "beats")
    words = sum(len(b["text"].split()) for b in s.get("beats", []))
    return (f"PHASE: script\nSpoken words: {words} (about {round(words / 2.5)} s at 1.0x)\n\n"
            + json.dumps({k: s.get(k) for k in keep}, indent=1, ensure_ascii=False))


def check_script(s: dict[str, Any], brief_text: str = "") -> tuple[dict[str, Any], dict[str, Any]]:
    prompt = (f"BRIEF:\n{brief_text[:4000]}\n\n" if brief_text else "") + _script_payload(s)
    out, prov = modelcall.call("story_check", prompt, modelcall.StoryCheckOut)
    return out.model_dump(), prov


def check_visuals(beats: list[dict[str, Any]], visual_spec: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    lines = [{k: b.get(k) for k in ("id", "text", "emotion", "delivery") if b.get(k) is not None} for b in beats]
    prompt = ("PHASE: visuals\nSPOKEN BEATS (with intended emotion):\n" + json.dumps(lines, indent=1, ensure_ascii=False)
              + "\n\nVISUAL PLAN (top panel; cues fire on the named word):\n"
              + json.dumps(visual_spec, indent=1, ensure_ascii=False)[:30000])
    out, prov = modelcall.call("story_check", prompt, modelcall.StoryCheckOut)
    return out.model_dump(), prov


def feedback_block(check: dict[str, Any]) -> str:
    """The checker's notes, formatted for the writer's revision prompt."""
    rows = [f"- beat {b['beat']}: intended {b['intended']}, likely felt {b['likely_felt']}. {b['issue']} FIX: {b['fix']}"
            for b in check["beats"] if b.get("issue") or b.get("fix")]
    return ("CHECKER REVIEW (independent model; apply these fixes):\n"
            f"Scores: {json.dumps(check['scores'])}\nHook ranking: {check.get('hook_ranking')}\n"
            "Top fixes:\n" + "\n".join(f"{i}. {f}" for i, f in enumerate(check.get("top_fixes", []), 1))
            + ("\nBeat notes:\n" + "\n".join(rows) if rows else ""))


def report_md(check: dict[str, Any], title: str, history: list[dict[str, Any]] | None = None,
              model: str = "") -> str:
    s = check["scores"]
    out = [f"# {title}\n", f"Checker: {model or 'story_check'}. Verdict: **{check['verdict']}**.\n",
           "| Hook | Arc | Clarity | Retention | Sends | Saves | Comments | Continuity |",
           "|---|---|---|---|---|---|---|---|",
           "| " + " | ".join(str(s[k]) for k in ("hook", "emotional_arc", "clarity", "retention", "sends", "saves",
                                                  "comments", "continuity")) + " |\n"]
    if history:
        out.append("Rounds: " + " -> ".join(f"{h['verdict']} (hook {h['scores']['hook']})" for h in history) + "\n")
    if check.get("top_fixes"):
        out += ["## Top fixes\n"] + [f"{i}. {f}" for i, f in enumerate(check["top_fixes"], 1)] + [""]
    if check.get("hook_ranking"):
        out += ["## Hook ranking\n"] + [f"{i}. {h}" for i, h in enumerate(check["hook_ranking"], 1)] + [""]
    if check.get("likely_drop_offs"):
        out += ["## Likely drop-offs\n"] + [f"- {d}" for d in check["likely_drop_offs"]] + [""]
    out += ["## Per beat\n", "| Beat | Intended | Likely felt | Issue | Fix |", "|---|---|---|---|---|"]
    for b in check["beats"]:
        flag = " **(blocking)**" if b.get("blocking") else ""
        out.append(f"| {b['beat']} | {b['intended']} | {b['likely_felt']} | {b.get('issue', '')}{flag} | {b.get('fix', '')} |")
    return "\n".join(out) + "\n"


def write_report(dir_: Path, stem: str, title: str, check: dict[str, Any], history: list[dict[str, Any]] | None,
                 model: str = "") -> dict[str, Path]:
    md = dir_ / f"{stem}.md"
    js = dir_ / f"{stem.lower()}.json"
    md.write_text(report_md(check, title, history, model), encoding="utf-8")
    js.write_text(json.dumps({"final": check, "rounds": history or [check]}, indent=2, ensure_ascii=False), encoding="utf-8")
    return {md.name: md, js.name: js}
