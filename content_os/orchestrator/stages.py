"""Stage implementations. Each returns (files, provenance, result, status, note) and never decides
approvals; the engine records the run in the ledger.

Text artifacts are written to outputs/<reel-id>/; media and the pipeline's work/ dir live in the
reel's media dir (~/Movies/ContentOS/<reel-id>/), which is also the pipeline's <reel_dir>.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import graph, memory, modelcall, moodboard, settings, story_check
from .state import Reel, sha256_file, sha256_json

MEDIA_EXT = {".mov", ".mp4", ".m4v"}


class StageFailed(RuntimeError):
    pass


@dataclass
class StageResult:
    files: dict[str, Path] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
    status: str = "done"  # done | skipped
    note: str = ""


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _json(path: Path, obj: Any) -> Path:
    return _write(path, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def open_feedback(reel: Reel, stage: str) -> list[dict[str, Any]]:
    """Unresolved creator feedback routed to this stage (fed into its next run)."""
    return [f for f in reel.state.get("feedback", []) if f.get("stage") == stage and not f.get("resolved_in")]


def _feedback_block(reel: Reel, stage: str) -> str:
    items = open_feedback(reel, stage)
    if not items:
        return ""
    return ("CREATOR FEEDBACK TO ADDRESS IN THIS REVISION (verbatim):\n"
            + "\n".join(f"- [{f['id']}] {f['text']}" for f in items))


def _brand_context() -> str:
    from content_os.config import load_brand

    b = load_brand()
    pillars = "\n".join(f"- {p.key}: {p.name}" for p in b.brand_pillars)
    principles = "\n".join(f"- {' '.join(p.split())}" for p in b.communication_principles[:6])
    return f"POSITIONING: {b.positioning}\nPILLARS:\n{pillars}\nCOMMUNICATION PRINCIPLES:\n{principles}"


# --------------------------------------------------------------------------- idea / brief / script
def run_idea(reel: Reel) -> StageResult:
    p = _write(reel.dir / "idea.md", f"# Idea: {reel.id}\n\n{reel.state['idea']}\n")
    return StageResult(files={"idea.md": p}, provenance={"kind": "auto"})


def run_brief(reel: Reel) -> StageResult:
    idea = reel.state["idea"]
    lessons, ids = memory.prompt_block("brief", idea)
    prompt = "\n\n".join(x for x in [
        f"REEL ID: {reel.id}\nIDEA FROM THE CREATOR:\n{idea}", _brand_context(), lessons,
        _feedback_block(reel, "brief"), _previous(reel, "brief.md")] if x)
    out, prov = modelcall.call("brief", prompt, modelcall.BriefOut)
    b = out.model_dump()
    md = (f"# Brief: {reel.id}\n\nStatus: **awaiting creator approval** "
          f"(`python -m content_os.orchestrator approve {reel.id} brief`).\n\n"
          f"- **Topic:** {b['topic']}\n- **Core thesis:** {b['core_thesis']}\n"
          f"- **Learning objective:** {b['learning_objective']}\n- **Format:** {b['format']}\n"
          f"- **Brand pillar:** {b['brand_pillar']}\n- **Audience:** {b['audience']}\n"
          f"- **Promise:** {b['promise']}\n- **Same-day takeaway:** {b['takeaway']}\n"
          f"- **Target length:** {b['target_duration_s']} s\n\n## Sections\n\n"
          + "\n".join(f"{i}. {s}" for i, s in enumerate(b["sections"], 1))
          + ("\n\n## Open questions (verify before scripting)\n\n" + "\n".join(f"- {q}" for q in b["open_questions"])
             if b["open_questions"] else "") + "\n")
    files = {"brief.md": _write(reel.dir / "brief.md", md), "brief.json": _json(reel.dir / "brief.json", b)}
    return StageResult(files=files, provenance={**prov, "lessons": ids}, result={"topic": b["topic"]})


def _previous(reel: Reel, name: str) -> str:
    p = reel.dir / name
    if p.exists() and reel.stage(name.split(".")[0].lower()).get("version"):
        return f"PREVIOUS VERSION ({name}) TO REVISE:\n{p.read_text(encoding='utf-8')[:6000]}"
    return ""


def run_script(reel: Reel) -> StageResult:
    brief = reel.dir / "brief.json"
    brief_text = brief.read_text(encoding="utf-8") if brief.exists() else f"(no brief; idea) {reel.state['idea']}"
    prev = reel.dir / "SCRIPT.md"
    previous = f"PREVIOUS SCRIPT TO REVISE (keep what the feedback does not touch):\n{prev.read_text(encoding='utf-8')[:8000]}" if prev.exists() else ""
    lessons, ids = memory.prompt_block("script", brief_text + " " + reel.state["idea"])
    prompt = "\n\n".join(x for x in [f"REEL ID: {reel.id}\nAPPROVED BRIEF:\n{brief_text}", _brand_context(),
                                    lessons, _feedback_block(reel, "script"), previous] if x)
    out, prov = modelcall.call("script", prompt, modelcall.ScriptOut)
    s = out.model_dump()
    # Independent emotion + hook check (Opus); Fable revises from its notes up to max_revisions times.
    rounds: list[dict[str, Any]] = []
    check, cprov = story_check.check_script(s, brief_text)
    rounds.append(check)
    for _ in range(int(story_check.cfg()["max_revisions"])):
        if check["verdict"] == "pass":
            break
        revise = "\n\n".join([prompt, "YOUR PREVIOUS DRAFT:\n" + json.dumps(s, ensure_ascii=False),
                               story_check.feedback_block(check)])
        out, prov = modelcall.call("script", revise, modelcall.ScriptOut)
        s = out.model_dump()
        check, cprov = story_check.check_script(s, brief_text)
        rounds.append(check)
    files = write_script_files(reel, s, provenance_note=f"{prov.get('model')} / {prov.get('prompt_version')}")
    files.update(story_check.write_report(reel.dir, "SCRIPT_CHECK", f"{s.get('title') or reel.id}: emotion + hook check",
                                          check, rounds, cprov.get("model", "")))
    return StageResult(files=files, provenance={**prov, "lessons": ids, "story_check": {
                           "model": cprov.get("model"), "prompt_version": cprov.get("prompt_version"),
                           "rounds": len(rounds), "verdict": check["verdict"], "scores": check["scores"]}},
                       result={"beats": len(s["beats"]), "words": sum(len(b["text"].split()) for b in s["beats"]),
                               "check": check["verdict"], "hook_score": check["scores"]["hook"]},
                       note=f"story check: {check['verdict']} after {len(rounds)} round(s), hook {check['scores']['hook']}/10")


BEAT_EXTRA = ("emotion", "delivery", "continuity")


def write_script_files(reel: Reel, s: dict[str, Any], provenance_note: str = "") -> dict[str, Path]:
    beats = [{"id": b["id"], "text": b["text"], "section": b.get("section", "body"),
              **{k: b[k] for k in BEAT_EXTRA if b.get(k)}} for b in s["beats"]]
    words = sum(len(b["text"].split()) for b in beats)
    rows = "\n".join(f"| {b['id']} | \"{b['text']}\" | {b.get('visual', '')} |" for b in s["beats"])
    feel = [b for b in s["beats"] if any(b.get(k) for k in BEAT_EXTRA)]
    feel_md = ("\n## Emotion, delivery and continuity\n\n| # | Viewer feels | Delivery | Continuity |\n|---|---|---|---|\n"
               + "\n".join(f"| {b['id']} | {b.get('emotion', '')} | {b.get('delivery', '')} | {b.get('continuity', '')} |"
                           for b in feel) + "\n") if feel else ""
    hooks = s.get("hook_variants") or []
    hooks_md = ("\n## Hook variants (Trial Reels)\n\n| # | Emotion | Spoken | On screen | First frame |\n|---|---|---|---|---|\n"
                + "\n".join(f"| {i} | {h['emotion']} | {h['text']} | {h['on_screen_text']} | {h['first_frame']} |"
                            for i, h in enumerate(hooks, 1)) + "\n") if hooks else ""
    md = (f"# {s.get('title') or reel.id}: script\n\nStatus: **draft for creator approval** "
          f"(`python -m content_os.orchestrator approve {reel.id} script`). {provenance_note}\n\n"
          f"- **Promise:** {s.get('promise', '')}\n- **Hook:** {s.get('hook', '')}\n"
          + (f"- **Emotional arc:** {s['emotional_arc']}\n" if s.get("emotional_arc") else "")
          + (f"- **Save asset:** {s['save_asset']}\n" if s.get("save_asset") else "")
          + (f"- **Comment trigger:** {s['comment_trigger']}\n" if s.get("comment_trigger") else "")
          + f"- **Length:** about {words} spoken words, target {s.get('target_duration_s')} s.\n\n"
          "| # | Spoken line | Top-half visual |\n|---|---|---|\n" + rows + "\n" + feel_md + hooks_md
          + ("\n## Open questions\n\n" + "\n".join(f"- {q}" for q in s.get("open_questions", [])) + "\n"
             if s.get("open_questions") else "")
          + ("\n## Caption notes\n\n" + "\n".join(f"- {q}" for q in s.get("caption_notes", [])) + "\n"
             if s.get("caption_notes") else ""))
    return {
        "SCRIPT.md": _write(reel.dir / "SCRIPT.md", md),
        "beats.json": _json(reel.dir / "beats.json", {"reel_id": reel.id,
                                                      "target_duration_s": s.get("target_duration_s") or 60,
                                                      "beats": beats}),
        "beat_visuals.json": _json(reel.dir / "beat_visuals.json",
                                   {"beats": [{"beat": b["id"], "visual": b.get("visual", "")} for b in s["beats"]]}),
    }


def parse_script_md(text: str) -> dict[str, Any]:
    """Parse an existing SCRIPT.md beat table (| # | Spoken line | visual |) into the script shape."""
    beats = []
    for line in text.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|(.+?)\|(.*)\|\s*$", line)
        if not m:
            continue
        spoken = m.group(2).strip().strip('"').strip("“”").strip()
        beats.append({"id": int(m.group(1)), "text": spoken, "visual": m.group(3).strip()})
    if not beats:
        raise StageFailed("no beat table (| # | Spoken line | visual |) found in SCRIPT.md")
    for b in beats:
        b["section"] = "hook" if b["id"] == beats[0]["id"] else ("payoff" if b is beats[-1] else "body")
    title = next((l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("# ")), "")
    promise = next((l.split(":", 1)[1].strip(" *") for l in text.splitlines() if "**Promise:**" in l), "")
    words = sum(len(b["text"].split()) for b in beats)
    return {"title": title, "promise": promise, "hook": beats[0]["text"], "beats": beats,
            "target_duration_s": round(words / 2.5)}


# --------------------------------------------------------------------------- mood board
def run_moodboard(reel: Reel) -> StageResult:
    """Fable designs the look: palette, type, sound, keyframes per beat and the shot list. The creator
    approves it at gate:moodboard; shoot plan, visuals and the edit follow it."""
    existing = reel.dir / "moodboard.json"
    if reel.state.get("adopted") and not existing.exists():
        return StageResult(files={}, status="skipped", provenance={"kind": "adopted"},
                           note="adopted reel without a mood board; visuals follow visual_cues.json as written")
    parts = [f"REEL ID: {reel.id}"]
    for name in ("SCREENPLAY.md", "SCRIPT.md"):
        f = reel.dir / name
        if f.exists():
            parts.append(f"{name}:\n{f.read_text(encoding='utf-8')[:14000]}")
    bj = reel.dir / "beats.json"
    if bj.exists():
        parts.append("BEATS (ids to reference):\n" + bj.read_text(encoding="utf-8")[:6000])
    lessons, ids = memory.prompt_block("moodboard", reel.state.get("idea", ""))
    prompt = "\n\n".join(x for x in [*parts, lessons, _feedback_block(reel, "moodboard"), _previous(reel, "moodboard.json")] if x)
    out, prov = modelcall.call("moodboard", prompt, modelcall.MoodboardOut)
    mb = out.model_dump()
    files = moodboard.write_board(reel.dir, mb, f"{reel.id}: mood board")
    if moodboard.render_frames(reel.dir, mb):
        files = moodboard.write_board(reel.dir, mb, f"{reel.id}: mood board")
    return StageResult(files=files, provenance={**prov, "lessons": ids},
                       result={"keyframes": len(mb["keyframes"]), "shots": len(mb["shot_list"])},
                       note=f"{len(mb['keyframes'])} keyframes; open MOODBOARD.html")


# --------------------------------------------------------------------------- shoot plan
# Printed on every teleprompter and shoot plan. Learned from Ep 2 (Meal Analyser), where cuts between
# takes showed: same chin-on-hand pose for 81 s, energy and hand position changing across a cut.
CONTINUITY_RULES = (
    "Reset to the base pose before every take: sit back, hands resting together in the lap (or on the table), "
    "shoulders square to the lens.",
    "Hold 1 s looking at the lens before you speak and 1 s after the last word; do not look away or "
    "move your hands until the second has passed.",
    "Start each beat at the energy the previous beat ended on; the FEEL line says where it goes from there.",
    "Gestures happen mid-line and return to the base pose before the last word.",
    "Record beats in order in one sitting; same clothes, hair, glasses, light and chair position.",
    "When a beat's POSE note says the energy changes sharply, still finish in the base pose: the edit will "
    "cover that cut with a full-frame visual or a punch-in.",
    "Vary the bottom half on purpose, not by accident: lean-ins and pose changes only where the script asks.",
)

def run_shoot_plan(reel: Reel) -> StageResult:
    adopted = (reel.state.get("adopted") or {}).get("shoot_plan_for_script")
    existing = {k: reel.dir / k for k in ("SHOOT_PLAN.md", "TELEPROMPTER.md")}
    if adopted and adopted == reel.stage("script").get("version") and all(p.exists() for p in existing.values()):
        return StageResult(files=existing, provenance={"kind": "adopted"},
                           note="hand-written shoot plan kept (script unchanged since adoption)")
    beats =_read_json(reel.dir / "beats.json")["beats"]
    visuals = {}
    bv = reel.dir / "beat_visuals.json"
    if bv.exists():
        visuals = {v["beat"]: v["visual"] for v in _read_json(bv)["beats"]}
    tp = [f"# Teleprompter: {reel.id}\n",
          "Say \"beat N\", read the line, look at the lens, say it. Pause 2 s. Say it again. Third time if needed.\n",
          "Continuity: " + " ".join(CONTINUITY_RULES[:3]) + "\n"]
    for b in beats:
        lines = re.split(r"(?<=[.?!:])\s+", b["text"].strip())
        cues = " · ".join(x for x in (f"FEEL: {b['emotion']}" if b.get("emotion") else "",
                                      f"FACE/VOICE: {b['delivery']}" if b.get("delivery") else "",
                                      f"POSE: {b['continuity']}" if b.get("continuity") else "") if x)
        tp.append(f"**beat {b['id']}**\n" + (f"({cues})\n" if cues else "") + "\n".join(lines) + "\n")
    plan = [f"# Shoot plan: {reel.id}\n",
            f"Footage goes in `{settings.tilde(reel.media)}/raw/` (outside the repo). When every beat is recorded run\n"
            f"`python -m content_os.orchestrator approve {reel.id} recorded`.\n",
            "## Recording checklist\n",
            "- iPhone landscape 16:9, camera locked, lens at eye level; same framing for every beat.",
            "- Quiet room, mic clipped or phone within 1 m; 5 s of room tone at the start.",
            "- Say \"beat N\" before each beat; 2-3 takes per line with a short pause; no slate needed.",
            "- See `production/RECORDING_KIT.md`.\n",
            "## Continuity (so the cuts do not show)\n", *[f"- {r}" for r in CONTINUITY_RULES], "",
            *_moodboard_shots(reel),
            "## Beats, emotion and planned visuals\n",
            "| Beat | Line | Viewer feels | Face/voice | Pose/continuity | Visual (top half) |",
            "|---|---|---|---|---|---|"]
    plan += [f"| {b['id']} | {b['text']} | {b.get('emotion', '')} | {b.get('delivery', '')} | {b.get('continuity', '')} "
             f"| {visuals.get(b['id'], '')} |" for b in beats]
    files = {"TELEPROMPTER.md": _write(reel.dir / "TELEPROMPTER.md", "\n".join(tp)),
             "SHOOT_PLAN.md": _write(reel.dir / "SHOOT_PLAN.md", "\n".join(plan) + "\n")}
    return StageResult(files=files, provenance={"kind": "auto", "generator": "shoot_plan@1"},
                       result={"beats": len(beats)})


def _moodboard_shots(reel: Reel) -> list[str]:
    mb = moodboard.load(reel.dir)
    if not mb:
        return []
    out = ["## Shot list from the mood board (film these too)\n", *[f"{i}. {s}" for i, s in enumerate(mb["shot_list"], 1)], "",
           "## Keyframes to match (see MOODBOARD.html)\n", "| KF | Time | Beats | Layout | Shot | Creator |", "|---|---|---|---|---|---|"]
    out += [f"| {k['id']} | {k['time_s']:.0f}s | {','.join(map(str, k.get('beats', [])))} | {k.get('layout', '')} | "
            f"{k.get('shot', '')} | {k.get('creator_direction', '')} |" for k in mb["keyframes"]]
    return out + [""]


# --------------------------------------------------------------------------- creator nodes
def raw_manifest(reel: Reel) -> list[dict[str, Any]]:
    raw = reel.media / "raw"
    if not raw.is_dir():
        return []
    return [{"name": p.name, "bytes": p.stat().st_size, "mtime": int(p.stat().st_mtime)}
            for p in sorted(raw.iterdir()) if p.suffix.lower() in MEDIA_EXT]


# --------------------------------------------------------------------------- pipeline delegation
PIPELINE_KEY_FILES = {
    "ingest": ["work/sources.json"],
    "transcribe": ["work/transcript.json"],
    "segment": ["work/takes.json"],
    "score": ["work/selects.json", "work/judge_takes.json"],
    "cutpoints": ["work/cuts.json"],
    "cut_review": ["work/review/review.json", "work/cut_review.html", "work/judge_cuts.json"],
    "draft_render": ["work/render/draft/render.json", "work/qa.json"],
    "render": ["work/render/final/render.json", "work/render/final/final.mp4"],
    "qa": ["work/qa.json", "work/qa.md"],
}


def pipeline_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([*settings.tool_path(), env.get("PATH", "")])
    return env


def sync_pipeline_inputs(reel: Reel) -> None:
    reel.media.mkdir(parents=True, exist_ok=True)
    for name in ("beats.json", "cue_sheet.json", "pipeline.yaml", "visual_cues.json", "moodboard.json"):
        src = reel.dir / name
        if src.exists():
            shutil.copy2(src, reel.media / name)


def _pipeline_cmd(step: str, media: Path) -> list[str]:
    base = [sys.executable, "-m", "content_os.pipeline"]
    if not settings.load()["pipeline"].get("judge_enabled", True):
        base += ["--set", "judge.enabled=false"]
    if step in ("judge_takes", "judge_cuts"):
        return base + ["run", str(media), "--from", step, "--until", step]
    if step.endswith(":draft"):
        return base + [step.split(":")[0], str(media), "--draft"]
    return base + [step, str(media)]


def run_pipeline(reel: Reel, node: graph.Node) -> StageResult:
    sync_pipeline_inputs(reel)
    log_lines = []
    for step in node.pipeline:
        cmd = _pipeline_cmd(step, reel.media)
        proc = subprocess.run(cmd, cwd=settings.PROJECT_ROOT, env=pipeline_env(), capture_output=True,
                              text=True, timeout=settings.load()["runner"]["job_timeout_seconds"])
        log_lines.append(f"$ {' '.join(cmd[2:])}\n{proc.stdout[-1500:]}{proc.stderr[-1500:]}")
        if proc.returncode != 0:
            raise StageFailed(f"pipeline {step} exited {proc.returncode}: "
                              f"{(proc.stderr or proc.stdout).strip()[-800:]}")
    files = {rel: reel.media / rel for rel in PIPELINE_KEY_FILES.get(node.name, []) if (reel.media / rel).exists()}
    result: dict[str, Any] = {}
    if node.name in ("qa", "draft_render") and (reel.media / "work/qa.json").exists():
        qa = _read_json(reel.media / "work/qa.json")
        result = {"qa_passed": qa.get("passed")}
    return StageResult(files=files, provenance={"kind": "pipeline", "steps": list(node.pipeline),
                                                "pipeline_config": _pipeline_config_hash(reel)},
                       result=result, note=log_lines[-1][-300:] if log_lines else "")


def _pipeline_config_hash(reel: Reel) -> str:
    parts = {}
    for p in [settings.PROJECT_ROOT / "content_os/pipeline/config.py", reel.media / "pipeline.yaml"]:
        if p.exists():
            parts[p.name] = sha256_file(p)
    return sha256_json(parts)


# --------------------------------------------------------------------------- visuals
def run_visuals(reel: Reel) -> StageResult:
    """Delegate to ``python -m content_os.visuals`` (check, then render) when the reel has a
    visual_cues.json; otherwise skip and let the final render use cue_sheet.json as written."""
    cues = reel.dir / "visual_cues.json"
    if importlib.util.find_spec("content_os.visuals") is None or not cues.exists():
        why = "content_os.visuals not installed" if not cues.exists() and importlib.util.find_spec(
            "content_os.visuals") is None else "no visual_cues.json for this reel"
        cue = reel.dir / "cue_sheet.json"
        return StageResult(files={"cue_sheet.json": cue} if cue.exists() else {}, status="skipped",
                           provenance={"kind": "auto"}, note=f"{why}; render uses cue_sheet.json as written")
    sync_pipeline_inputs(reel)
    out = []
    vcheck = run_visuals_check(reel)
    if vcheck["verdict"] != "pass" and story_check.cfg()["visuals_blocking"]:
        raise StageFailed(f"visuals story check: {vcheck['verdict']}; see VISUALS_CHECK.md")
    for step in ("check", "render"):
        cmd = [sys.executable, "-m", "content_os.visuals", step, str(reel.media)]
        proc = subprocess.run(cmd, cwd=settings.PROJECT_ROOT, env=pipeline_env(), capture_output=True, text=True,
                              timeout=settings.load()["runner"]["job_timeout_seconds"])
        out.append((proc.stdout + proc.stderr).strip()[-400:])
        if proc.returncode != 0:
            raise StageFailed(f"visuals {step} exited {proc.returncode}: {out[-1]}")
    files = {"visual_cues.json": cues}
    manifest = reel.media / "work/visuals/visuals.json"
    if manifest.exists():
        files["work/visuals/visuals.json"] = manifest
    return StageResult(files=files, provenance={"kind": "visuals", "module": "content_os.visuals"}, note=out[-1][-300:])


def run_visuals_check(reel: Reel) -> dict[str, Any]:
    """Opus checks the visual plan against each beat's spoken line and intended emotion."""
    beats_p = reel.dir / "beats.json"
    beats = _read_json(beats_p)["beats"] if beats_p.exists() else []
    spec = _read_json(reel.dir / "visual_cues.json")
    check, prov = story_check.check_visuals(beats, spec)
    story_check.write_report(reel.dir, "VISUALS_CHECK", f"{reel.id}: visual plan emotion + hook check", check, None,
                             prov.get("model", ""))
    return check


# --------------------------------------------------------------------------- av review / post
def final_mp4(reel: Reel) -> Path:
    return reel.media / "work/render/final/final.mp4"


def run_av_review(reel: Reel) -> StageResult:
    from . import av_review

    res = av_review.review(final_mp4(reel), reel.dir)
    files = {k: Path(v) for k, v in res.pop("files", {}).items()}
    # Only a completed review counts as done; "skipped: no key" and errors leave the gate to the creator.
    status = "done" if res.get("status") == "done" else "skipped"
    return StageResult(files=files, status=status, result=res,
                       provenance={"kind": "external", **res.get("provenance", {})}, note=res.get("status", ""))


def run_post_package(reel: Reel) -> StageResult:
    script = (reel.dir / "SCRIPT.md").read_text(encoding="utf-8")
    lessons, ids = memory.prompt_block("post_package", script[:2000])
    prompt = "\n\n".join(x for x in [f"REEL ID: {reel.id}\nFINAL SCRIPT:\n{script}", lessons,
                                    _feedback_block(reel, "post_package")] if x)
    out, prov = modelcall.call("post_package", prompt, modelcall.PostOut)
    p = out.model_dump()
    cover = _extract_cover(reel, p["cover_beat"])
    md = (f"# Post package: {reel.id}\n\nContent OS never posts. After posting by hand run\n"
          f"`python -m content_os.orchestrator approve {reel.id} posting --note <url>`.\n\n"
          f"## Caption\n\n{p['caption']}\n\n{' '.join(p['hashtags'])}\n\n## Cover\n\n"
          f"- Text: **{p['cover_text']}**\n- Frame: beat {p['cover_beat']}"
          + (f" -> `{settings.tilde(cover)}`" if cover else " (extract by hand; ffmpeg or cuts.json missing)") + "\n"
          f"- Final file: `{settings.tilde(final_mp4(reel))}`\n")
    files = {"POST.md": _write(reel.dir / "POST.md", md), "post.json": _json(reel.dir / "post.json", p)}
    return StageResult(files=files, provenance={**prov, "lessons": ids}, result={"cover": str(cover or "")})


def _extract_cover(reel: Reel, beat: int) -> Path | None:
    ffmpeg = shutil.which("ffmpeg", path=pipeline_env()["PATH"])
    cuts = reel.media / "work/cuts.json"
    if not ffmpeg or not cuts.exists() or not final_mp4(reel).exists():
        return None
    seg = next((s for s in _read_json(cuts).get("segments", []) if s.get("beat") == beat), None)
    if not seg:
        return None
    out = reel.media / "cover.jpg"
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-ss", f"{seg['out_start'] + 0.5:.2f}", "-i",
                    str(final_mp4(reel)), "-frames:v", "1", str(out)], check=False)
    return out if out.exists() else None


RUNNERS = {"idea": run_idea, "brief": run_brief, "script": run_script, "moodboard": run_moodboard,
           "shoot_plan": run_shoot_plan,
           "visuals": run_visuals, "av_review": run_av_review, "post_package": run_post_package}


def run_node(reel: Reel, name: str) -> StageResult:
    node = graph.node(name)
    if node.kind == "pipeline":
        return run_pipeline(reel, node)
    if name in RUNNERS:
        return RUNNERS[name](reel)
    raise StageFailed(f"{name} is a {node.kind} node and cannot be run automatically")
