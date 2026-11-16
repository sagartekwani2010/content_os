"""Teleprompter parsing and draft-spec (model call replaced by a fake runner: no network)."""

import json
from pathlib import Path

import pytest

from content_os.visuals import rough
from content_os.visuals.script import parse_teleprompter

ROOT = Path(__file__).resolve().parents[2]


def test_parse_teleprompter():
    text = "# T\n\nSay beat N.\n\n**beat 1**\nFirst line.\nSecond line.\n\n**beat 2**\nA.\n(pause)\nB.\n"
    assert parse_teleprompter(text) == {1: "First line. Second line.", 2: "A. B."}


fonts_missing = any(not (rough.FONT_DIR / f[0]).exists() for f in rough.FONTS.values())


@pytest.mark.skipif(fonts_missing, reason="fonts not cached")
def test_draft_spec_validates_and_repairs(tmp_path):
    from content_os.visuals.draft import draft_spec

    (tmp_path / "TELEPROMPTER.md").write_text("**beat 1**\nThe lazy version matched it at 77.\n")
    (tmp_path / "visual_cues.json").write_text(json.dumps({"schema": "content_os.visuals/spec@2", "script": "TELEPROMPTER.md",
                                                           "params": {}, "beats": []}))
    good = {"beats": [{"beat": 1, "template": "bars", "params": {"bars": [
        {"id": "lazy", "label": "one prompt", "value": "@direct_mae", "ci": "@direct_ci", "shown": "@direct_mae_spoken"}]},
        "cues": [{"on_word": "77", "action": "countup", "target": "lazy_v", "emphasis": True},
                 {"on_word": "lazy", "action": "draw", "target": "lazy"}]}]}
    bad = json.loads(json.dumps(good))
    bad["beats"][0]["params"]["bars"][0]["value"] = 77.3          # invented literal
    bad["beats"][0]["cues"][0]["target"] = "nonexistent"
    calls = []

    def runner(prompt, model):
        calls.append(prompt)
        return {"result": "```json\n" + json.dumps(bad if len(calls) == 1 else good) + "\n```", "total_cost_usd": 0.01}

    res = draft_spec(tmp_path, beats=None, write=True, runner=runner)
    assert res["errors"] == [] and res["attempts"] == 2
    assert "must be a fact reference" in calls[1] and "nonexistent" in calls[1]
    assert "direct_mae: 77.3" in calls[0] and "## bars" in calls[0]  # facts and catalogue are in the prompt
    spec = json.loads((tmp_path / "visual_cues.json").read_text())
    assert spec["beats"][0]["template"] == "bars" and (tmp_path / "visual_cues.json.bak").exists()
