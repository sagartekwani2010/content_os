"""Judge step: editing judgement calls by a Claude model, constrained by the deterministic rules.

Two phases:
- ``takes`` (after score): which eligible take to use per beat, plus visual-timing suggestions.
- ``cuts`` (after cut_review): cuts it would reject and why, plus visual-timing suggestions; it
  also sees the contact-sheet PNGs.

The model only receives text and numbers (beats.json, transcripts of the takes, measured features)
and, for ``cuts``, the contact-sheet images. It is called through the Claude Code CLI in headless
mode (``claude -p --input-format stream-json --output-format stream-json --json-schema ...``), so
it uses the creator's Claude Code login; no API key is read or written. The model name comes from
``judge.model`` in the config.

Deterministic rules win: a take choice is applied only if that take passed every hard check
(complete sentence, no restart, fillers, face, length). Cut rejections are advisory: they are shown
on the review page and recorded with the approval; they never change cuts.json by themselves.
Visual-timing suggestions go to ``work/cue_sheet.suggested.json``; cue_sheet.json is never edited.
"""

from __future__ import annotations

import base64
import json
import subprocess
import tempfile
import time

from .reel import Reel, StageError, load_beats, read_json, schema, write_json
from .score import override

SYSTEM = (
    "You are the editor for a creator's short vertical video (Instagram Reel). Measurements were made by "
    "deterministic scripts; you make the judgement calls they cannot: which delivery is strongest, which "
    "cuts would feel abrupt, and when each beat's visual should appear. Only choose among takes marked "
    "eligible; never propose splicing inside a sentence. Base reasons on the numbers, transcripts and images "
    "given, and say when the evidence is thin (you cannot hear the audio). Answer only through the JSON schema."
)

_VISUAL_TIMING = {
    "type": "array",
    "items": {"type": "object", "additionalProperties": False,
              "required": ["beat", "start_offset_s", "anchor_word", "reason"],
              "properties": {"beat": {"type": "integer"}, "start_offset_s": {"type": "number"},
                             "anchor_word": {"type": "string"}, "reason": {"type": "string"}}},
}

SCHEMAS = {
    "takes": {
        "type": "object", "additionalProperties": False, "required": ["beats", "visual_timing", "notes"],
        "properties": {
            "beats": {"type": "array", "items": {
                "type": "object", "additionalProperties": False, "required": ["beat", "take", "reason", "confidence"],
                "properties": {"beat": {"type": "integer"}, "take": {"type": ["string", "null"]},
                               "reason": {"type": "string"},
                               "confidence": {"type": "string", "enum": ["low", "medium", "high"]}}}},
            "visual_timing": _VISUAL_TIMING,
            "notes": {"type": "string"},
        },
    },
    "cuts": {
        "type": "object", "additionalProperties": False, "required": ["reject_cuts", "visual_timing", "notes"],
        "properties": {
            "reject_cuts": {"type": "array", "items": {
                "type": "object", "additionalProperties": False, "required": ["cut", "reason", "suggested_fix"],
                "properties": {"cut": {"type": "integer"}, "reason": {"type": "string"},
                               "suggested_fix": {"type": "string"}}}},
            "visual_timing": _VISUAL_TIMING,
            "notes": {"type": "string"},
        },
    },
}

_TAKE_FIELDS = ("id", "text", "duration", "wpm", "completeness", "complete", "restart", "fillers", "filler_words",
                "internal_pauses", "loudness_lufs", "loudness_rel_beat_db", "variation", "face", "score",
                "score_parts", "eligible", "ineligible_reasons", "flags")


def build_payload(reel: Reel, phase: str, cfg: dict) -> tuple[str, list[str]]:
    beats = load_beats(reel)
    cue = read_json(reel.cue_sheet_file) if reel.cue_sheet_file.exists() else None
    images: list[str] = []
    if phase == "takes":
        scores = reel.need(reel.scores_file, "score")
        selects = reel.need(reel.selects_file, "score")
        per_beat = []
        for b in beats:
            sel = next((e for e in selects["beats"] if e["beat"] == b["id"]), {})
            per_beat.append({"beat": b["id"], "script": b["text"], "default_pick": sel.get("take"),
                             "takes": [{k: t.get(k) for k in _TAKE_FIELDS} for t in scores["takes"] if t["beat"] == b["id"]]})
        task = ("Choose one take per beat from the eligible takes (or null when none is eligible). The default rule "
                "is the last complete fluent take; change it only when the measurements give a reason (pace, "
                "level, head-pose, pauses, wording closer to the script). Also suggest when each beat's visual "
                "should appear (start_offset_s from the beat start, anchored to a spoken word).")
        body = {"beats": per_beat, "cue_sheet": cue, "thresholds": cfg["score"]}
    elif phase == "cuts":
        cuts = reel.need(reel.cuts_file, "cutpoints")
        review = reel.need(reel.work / "review" / "review.json", "cut_review")
        segs = [{**{k: s[k] for k in ("index", "beat", "take", "out_start", "duration", "gain_db", "lead_s", "tail_s",
                                      "crop_realigned", "text")},
                 # word start times relative to the beat start, for visual timing
                 "word_starts_s": [[w["text"], round(w["start"] - s["out_start"], 2)] for w in s["words"]]}
                for s in cuts["segments"]]
        body = {"beats": beats, "segments": segs, "cuts": review["joins"], "cue_sheet": cue,
                "qa_thresholds": {k: cfg["qa"][k] for k in ("face_jump_warn_pct", "face_jump_fail_pct", "min_clip_s")}}
        task = ("Review every cut (numbered from 1 as in the images). List the cuts you would reject and why "
                "(abrupt face jump, level step, wording that does not flow from the previous beat, framing), with "
                "a concrete fix (other take, re-record, deliberate framing change). Then suggest visual timing per beat.")
        images = [str(reel.resolve(p)) for p in review.get("contact_sheets", [])][: cfg["judge"]["max_images"]]
    else:
        raise StageError("phase must be takes or cuts")
    text = f"{task}\n\nDATA (JSON):\n{json.dumps(body, indent=1, default=str)}"
    return text, images


def _message(text: str, images: list[str]) -> dict:
    content = [{"type": "text", "text": text}]
    for p in images:
        with open(p, "rb") as fh:
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                        "data": base64.b64encode(fh.read()).decode()}})
    return {"type": "user", "message": {"role": "user", "content": content}}


def _run_cli(cmd: list[str], stdin: str, timeout: float) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:  # run outside the repo so no CLAUDE.md is picked up
        return subprocess.run(cmd, input=stdin, capture_output=True, text=True, timeout=timeout, cwd=tmp)


def call_model(text: str, images: list[str], phase: str, jcfg: dict) -> dict:
    cmd = [jcfg["cli"], "-p", "--model", jcfg["model"], "--output-format", "stream-json", "--verbose",
           "--input-format", "stream-json", "--json-schema", json.dumps(SCHEMAS[phase]), "--tools", "",
           "--no-session-persistence", "--strict-mcp-config", "--system-prompt", SYSTEM]
    if jcfg.get("effort"):
        cmd += ["--effort", jcfg["effort"]]
    if jcfg.get("max_budget_usd"):
        cmd += ["--max-budget-usd", str(jcfg["max_budget_usd"])]
    t0 = time.perf_counter()
    try:
        proc = _run_cli(cmd, json.dumps(_message(text, images)) + "\n", jcfg["timeout_s"])
    except FileNotFoundError as e:
        raise StageError(f"judge CLI not found: {jcfg['cli']}") from e
    result = None
    for line in proc.stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "result":
            result = ev
    if result is None or result.get("is_error"):
        raise StageError(f"judge call failed (exit {proc.returncode}): {(proc.stderr or proc.stdout)[-800:]}")
    out = result.get("structured_output")
    if out is None:
        try:
            out = json.loads(result.get("result", ""))
        except json.JSONDecodeError as e:
            raise StageError("judge returned no structured output") from e
    return {"output": out, "cost_usd": result.get("total_cost_usd"), "duration_s": round(time.perf_counter() - t0, 1),
            "session_id": result.get("session_id")}


def validate_takes(output: dict, reel: Reel) -> list[dict]:
    scores = reel.need(reel.scores_file, "score")
    takes = {t["id"]: t for t in scores["takes"]}
    decisions = []
    for c in output.get("beats", []):
        t = takes.get(c.get("take")) if c.get("take") else None
        ok = t is not None and t["beat"] == c["beat"] and t["eligible"]
        why = None
        if c.get("take") and not ok:
            why = "unknown take" if t is None else ("take belongs to another beat" if t["beat"] != c["beat"]
                                                    else "failed hard checks: " + ", ".join(t["ineligible_reasons"]))
        decisions.append({**c, "accepted": ok, "rejected_because": why})
    return decisions


def suggest_cue_sheet(reel: Reel, suggestions: list[dict], phase: str) -> str | None:
    if not suggestions:
        return None
    cue = read_json(reel.cue_sheet_file) if reel.cue_sheet_file.exists() else {"beats": []}
    by_beat = {int(b["beat"]): b for b in cue.get("beats", [])}
    for s in suggestions:
        entry = by_beat.setdefault(int(s["beat"]), {"beat": int(s["beat"])})
        entry["start_offset"] = round(max(0.0, float(s["start_offset_s"])), 2)
        entry["timing_note"] = f"judge ({phase}): at '{s['anchor_word']}' - {s['reason']}"
    cue["beats"] = sorted(by_beat.values(), key=lambda b: b["beat"])
    path = reel.work / "cue_sheet.suggested.json"
    write_json(path, cue)
    return reel.rel(path)


def run(reel: Reel, cfg: dict, phase: str, apply: bool = True) -> dict:
    jcfg = cfg["judge"]
    text, images = build_payload(reel, phase, cfg)
    write_json(reel.work / f"judge_{phase}_request.json",
               {"model": jcfg["model"], "text": text, "images": [reel.rel(p) for p in images]})
    res = call_model(text, images, phase, jcfg)
    out = res["output"]
    record = {"schema": schema(f"judge_{phase}"), "model": jcfg["model"], "phase": phase, "result": out,
              "cost_usd": res["cost_usd"], "duration_s": res["duration_s"]}
    if phase == "takes":
        decisions = validate_takes(out, reel)
        record["decisions"] = decisions
        if apply:
            sel = read_json(reel.selects_file)
            current = {e["beat"]: e.get("take") for e in sel["beats"]}
            for d in decisions:
                if d["accepted"] and d["take"] != current.get(d["beat"]):
                    override(reel, d["beat"], d["take"], by=f"judge:{jcfg['model']}")
            sel = read_json(reel.selects_file)
            for e in sel["beats"]:
                d = next((d for d in decisions if d["beat"] == e["beat"]), None)
                if d:
                    e["judge"] = {"take": d["take"], "reason": d["reason"], "confidence": d["confidence"],
                                  "accepted": d["accepted"], "rejected_because": d["rejected_because"]}
            write_json(reel.selects_file, sel)
            record["applied"] = True
    record["cue_sheet_suggestion"] = suggest_cue_sheet(reel, out.get("visual_timing", []), phase)
    write_json(reel.work / f"judge_{phase}.json", record)
    return record
