"""Feedback -> earliest affected stage -> stale marking, gate invalidation, re-run plan, lesson.

1. Classify: the feedback classifier (Claude, model from config) maps the text to the earliest stage
   it concerns; a keyword fallback is used with --no-model or when the model call fails.
2. Record: the feedback, the classification and its provenance go into the ledger and state.
3. Backtrack: that stage and every node after it are marked stale with the reason; approvals of
   gates downstream are moved to approvals_history with ``invalidated_reason`` (never deleted).
4. Plan: the ordered re-run plan up to the next creator gate, then the rest.
5. Learn: a dated feedback/ record and a candidate lesson (memory.add_candidate).
"""

from __future__ import annotations

import json
import re
from typing import Any

from . import graph, memory, modelcall
from .state import Reel, now, short

KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("post_package", ("caption", "hashtag", "cover", "thumbnail")),
    ("render", ("quiet", "loud", "volume", "music", "mix", "master", "sfx", "sound effect", "lufs",
                "subtitle", "captions burn", "clipping", "audio level", "export")),
    ("visuals", ("b-roll", "broll", "visual", "chart", "graphic", "card", "image", "screenshot", "overlay",
                 "on-screen text", "font")),
    ("cutpoints", ("cut", "abrupt", "jump", "splice", "pause", "gap", "timing", "transition", "clipped")),
    ("score", ("take", "better version", "other take")),
    ("record", ("re-record", "rerecord", "energy", "tired", "eye", "framing", "lighting", "delivery",
                "mumble", "look at the lens")),
    ("shoot_plan", ("teleprompter", "shot list", "shoot plan")),
    ("script", ("hook", "script", "line", "wording", "claim", "story", "cta", "payoff", "beat order",
                "boring", "too long", "explain")),
    ("brief", ("topic", "angle", "audience", "thesis", "promise", "idea")),
]


def heuristic(text: str) -> dict[str, Any]:
    low = text.lower()
    ts = _timestamp(low)
    hits = [stage for stage, words in KEYWORDS if any(w in low for w in words)]
    stage = min(hits, key=graph.FEEDBACK_TARGETS.index) if hits else "script"
    # A timestamped "cut" is an edit problem, not a script one.
    if ts is not None and "cutpoints" in hits:
        stage = "cutpoints"
    return {"stage": stage, "timestamp_s": ts, "beat": _beat(low), "reason": f"keyword match: {hits or ['default']}",
            "confidence": "low", "generalizable": False,
            "lesson": {"category": _category(stage), "rule": "", "applies_to": [graph.lesson_scope(stage)]}}


def _timestamp(text: str) -> float | None:
    m = re.search(r"(\d+):(\d{2}(?:\.\d+)?)", text)
    if m:
        return int(m.group(1)) * 60 + float(m.group(2))
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*s(?:ec(?:onds?)?)?\b", text)
    return float(m.group(1)) if m else None


def _beat(text: str) -> int | None:
    m = re.search(r"beat\s*(\d+)", text)
    return int(m.group(1)) if m else None


def _category(stage: str) -> str:
    return {"brief": "content", "script": "content", "shoot_plan": "process", "record": "process",
            "score": "edit", "cutpoints": "edit", "visuals": "visual", "render": "audio",
            "post_package": "content"}.get(stage, "process")


def _context(reel: Reel) -> str:
    parts = [f"REEL: {reel.id}", f"IDEA: {reel.state.get('idea')}",
             "STAGE STATES: " + ", ".join(f"{k}={v.get('status')}" for k, v in reel.state["stages"].items())]
    beats = reel.dir / "beats.json"
    if beats.exists():
        bj = json.loads(beats.read_text(encoding="utf-8"))
        parts.append("BEATS:\n" + "\n".join(f"{b['id']}: {b['text']}" for b in bj["beats"]))
    cuts = reel.media / "work/cuts.json"
    if cuts.exists():
        cj = json.loads(cuts.read_text(encoding="utf-8"))
        parts.append("OUTPUT TIMELINE (beat: start-end s):\n" + "\n".join(
            f"{s['beat']}: {s['out_start']:.2f}-{s['out_start'] + s['duration']:.2f}" for s in cj.get("segments", [])))
    return "\n\n".join(parts)


def classify(reel: Reel, text: str, use_model: bool = True) -> dict[str, Any]:
    if use_model:
        try:
            prompt = (f"{_context(reel)}\n\nALLOWED STAGES: {', '.join(graph.FEEDBACK_TARGETS)}\n\n"
                      f"CREATOR FEEDBACK:\n{text}")
            out, prov = modelcall.call("feedback_classifier", prompt, modelcall.FeedbackOut)
            c = out.model_dump()
            if c["stage"] not in graph.FEEDBACK_TARGETS:
                raise ValueError(f"classifier returned unknown stage {c['stage']!r}")
            return {**c, "classified_by": prov.get("model"), "provenance": prov}
        except Exception as exc:  # noqa: BLE001 - fall back, but say so
            c = heuristic(text)
            return {**c, "classified_by": "keywords (model failed)", "model_error": f"{type(exc).__name__}: {exc}"[:300]}
    return {**heuristic(text), "classified_by": "keywords"}


def plan_from(reel: Reel, stage: str) -> list[str]:
    steps = []
    for name in graph.downstream(stage):
        n = graph.node(name)
        if n.kind == "gate":
            steps.append(f"[creator] approve {n.gate}")
        elif n.kind == "creator":
            steps.append("[creator] re-record affected beats" if n.gate == "recorded" else f"[creator] {n.title}")
        else:
            label = name
            if n.kind == "model":
                try:
                    label += f" ({modelcall.resolved(_role(name))['model']})"
                except Exception:  # noqa: BLE001
                    pass
            steps.append(label)
    return steps


def _role(stage: str) -> str:
    return {"brief": "brief", "script": "script", "post_package": "post_package"}[stage]


def mark_stale(reel: Reel, stage: str, reason: str, feedback_id: str | None = None) -> list[str]:
    """Mark ``stage`` and everything downstream stale; invalidate downstream approvals."""
    touched = []
    for name in graph.downstream(stage):
        n = graph.node(name)
        if n.kind == "gate":
            appr = reel.state["approvals"].pop(n.gate, None)
            if appr:
                why = f"{reason} (feedback {feedback_id}, routed to {stage})" if feedback_id else reason
                reel.state.setdefault("approvals_history", []).append(
                    {**appr, "gate": n.gate, "invalidated_at": now(), "invalidated_reason": why})
                reel.state.setdefault("invalidated", {})[n.gate] = why
                reel.log("approval_invalidated", gate=n.gate, version=short(appr.get("version")), reason=why)
                touched.append(name)
            continue
        rec = reel.state["stages"].get(name)
        if rec and rec.get("version"):
            rec["stale"] = {"reason": reason, "feedback": feedback_id, "root": stage, "at": now()}
            touched.append(name)
    reel.save()
    reel.log("marked_stale", root=stage, nodes=touched, reason=reason, feedback=feedback_id)
    return touched


def feedback(reel_id: str, text: str, *, use_model: bool = True, dry_run: bool = False,
             stage_override: str | None = None) -> dict[str, Any]:
    reel = Reel.load(reel_id)
    c = classify(reel, text, use_model=use_model)
    if stage_override:
        graph.node(stage_override)
        c = {**c, "stage": stage_override, "classified_by": f"creator override (was {c['stage']})"}
    stage = c["stage"]
    plan = plan_from(reel, stage)
    if dry_run:
        return {"dry_run": True, "classification": c, "plan": plan}
    with reel.lock():
        reel.state["feedback_count"] = reel.state.get("feedback_count", 0) + 1
        fid = f"F{reel.state['feedback_count']:03d}"
        reel.state.setdefault("feedback", []).append(
            {"id": fid, "at": now(), "text": text, "stage": stage, "timestamp_s": c.get("timestamp_s"),
             "beat": c.get("beat"), "resolved_in": None})
        reel.save()
        reel.log("feedback", id=fid, text=text, classification={k: v for k, v in c.items() if k != "provenance"},
                 model=(c.get("provenance") or {}).get("model"),
                 prompt_version=(c.get("provenance") or {}).get("prompt_version"))
        touched = mark_stale(reel, stage, f"creator feedback: {text[:120]}", fid)
        reel.log("rerun_plan", feedback=fid, plan=plan)
        reel.set_waiting(None)
    record = memory.write_record(reel.id, fid, text, c, plan, touched)
    lesson_outcome = {"action": "none"}
    if c.get("generalizable") and (c.get("lesson") or {}).get("rule"):
        lesson_outcome = memory.add_candidate(c["lesson"], reel_id=reel.id, feedback_id=f"{reel.id}/{fid}",
                                              record=record)
    reel.log("lesson", feedback=fid, **lesson_outcome)
    return {"feedback_id": fid, "classification": c, "invalidated": touched, "plan": plan,
            "record": str(record), "lesson": lesson_outcome}
