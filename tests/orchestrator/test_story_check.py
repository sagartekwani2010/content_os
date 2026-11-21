"""Emotion + hook checker: the script stage revises from the checker's notes; beat sheet carries cues."""
from __future__ import annotations

import json

from content_os.orchestrator import modelcall, stages, story_check
from content_os.orchestrator.state import Reel
from content_os.visuals.script import parse_teleprompter

from .test_orchestrator import sandbox  # noqa: F401  (autouse fixture)

SCORES = ("hook", "emotional_arc", "clarity", "retention", "sends", "saves", "comments", "continuity")


def _script(n: int) -> dict:
    return {"title": "T", "promise": "p", "hook": f"Hook {n}", "target_duration_s": 40,
            "emotional_arc": "fear -> surprise -> hope",
            "hook_variants": [{"text": "h", "emotion": "fear", "on_screen_text": "x", "first_frame": "plate"}],
            "save_asset": "four-line card", "comment_trigger": "Comment EVALS",
            "beats": [{"id": 1, "text": f"Hook line {n}.", "section": "hook", "visual": "plate",
                       "emotion": "fear", "delivery": "lean in", "continuity": "start in base pose"},
                      {"id": 2, "text": "Payoff.", "section": "payoff", "visual": "card"}]}


def _check(verdict: str, hook: int) -> dict:
    return {"phase": "script", "verdict": verdict, "scores": {k: hook for k in SCORES},
            "beats": [{"beat": 1, "intended": "fear", "likely_felt": "boredom", "issue": "recap", "fix": "lead with 499",
                       "blocking": verdict == "revise"}],
            "hook_ranking": ["fear hook: concrete number"], "top_fixes": ["Lead with the number."]}


def test_script_revises_once_from_checker(monkeypatch):
    calls = []

    def fake(role, prompt, output_type):
        calls.append((role, prompt))
        if role == "script":
            return _script(sum(1 for r, _ in calls if r == "script")), {"model": "fable"}
        if role == "story_check":
            first = sum(1 for r, _ in calls if r == "story_check") == 1
            return (_check("revise", 4) if first else _check("pass", 8)), {"model": "opus"}
        raise AssertionError(role)

    monkeypatch.setattr(modelcall, "CALLER", fake)
    reel = Reel.create("emo-test", "idea for a test")
    res = stages.run_script(reel)
    roles = [r for r, _ in calls]
    assert roles == ["script", "story_check", "script", "story_check"]
    assert "CHECKER REVIEW" in calls[2][1] and "Lead with the number." in calls[2][1]
    assert res.result["check"] == "pass" and res.provenance["story_check"]["rounds"] == 2
    md = (reel.dir / "SCRIPT.md").read_text()
    assert "Emotional arc" in md and "Hook variants" in md and "lean in" in md
    assert "Rounds: revise (hook 4) -> pass (hook 8)" in (reel.dir / "SCRIPT_CHECK.md").read_text()
    beats = json.loads((reel.dir / "beats.json").read_text())["beats"]
    assert beats[0]["emotion"] == "fear" and "emotion" not in beats[1]

    # teleprompter shows the cues as a stage direction, so the spoken line stays clean for the visuals parser
    stages.run_shoot_plan(reel)
    tp = (reel.dir / "TELEPROMPTER.md").read_text()
    assert "(FEEL: fear · FACE/VOICE: lean in · POSE: start in base pose)" in tp
    assert parse_teleprompter(tp)[1] == "Hook line 2."
    assert "Continuity (so the cuts do not show)" in (reel.dir / "SHOOT_PLAN.md").read_text()


def test_feedback_block_lists_fixes():
    block = story_check.feedback_block(_check("revise", 3))
    assert block.startswith("CHECKER REVIEW") and "beat 1" in block and "lead with 499" in block
